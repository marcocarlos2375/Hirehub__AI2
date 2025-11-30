"""
LangGraph workflow for adaptive question answering.
Orchestrates the multi-step intelligent question flow.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from core.answer_flow_state import AdaptiveAnswerState
from core.answer_flow_nodes import (
    generate_deep_dive_prompts_node,
    generate_answer_from_inputs_node,
    evaluate_quality_node,
    refine_answer_node,
    route_after_experience_check,
    route_after_quality_eval
)
from core.state_persistence import (
    generate_session_id,
    save_state_snapshot,
    load_state_snapshot,
    get_state_summary
)


class AdaptiveQuestionWorkflow:
    """
    LangGraph workflow for adaptive question answering.

    Flow:
        START
          ↓
        [User selects: Yes/No]
          ↓
        ┌──────────────┬──────────────┐
        ↓              ↓              ↓
      YES             NO          (skip)
        ↓              ↓              ↓
    DEEP_DIVE         END            END
        ↓
    GENERATE_ANSWER
        ↓
    EVALUATE_QUALITY
        ↓
      Good? ──No→ REFINE ──┐
        │                  │
        Yes                ↓
        ↓            EVALUATE_QUALITY
        ↓                  │
        └──────────────────┘
                ↓
               END

    Smart Skipping:
    - "No" responses skip directly to END (saves 1-2s LLM call)
    - Only "yes" triggers deep-dive prompts generation
    """

    def __init__(self):
        """Initialize the workflow graph."""
        self.workflow = StateGraph(AdaptiveAnswerState)
        self._build_graph()
        self.memory = MemorySaver()  # For checkpointing/resume

    def _build_graph(self):
        """Build the LangGraph workflow."""

        # Add nodes
        self.workflow.add_node("generate_deep_dive", generate_deep_dive_prompts_node)
        self.workflow.add_node("generate_answer", generate_answer_from_inputs_node)
        self.workflow.add_node("evaluate_quality", evaluate_quality_node)
        self.workflow.add_node("refine_answer", refine_answer_node)

        # Set entry point (conditional based on experience_check_response)
        self.workflow.add_conditional_edges(
            START,  # Virtual start node
            route_after_experience_check,
            {
                "deep_dive": "generate_deep_dive",
                "skip": END  # Smart skip: No experience
            }
        )

        # After deep dive prompts → generate answer
        self.workflow.add_edge("generate_deep_dive", "generate_answer")

        # After generate answer → evaluate quality
        self.workflow.add_edge("generate_answer", "evaluate_quality")

        # After quality evaluation → conditional routing
        self.workflow.add_conditional_edges(
            "evaluate_quality",
            route_after_quality_eval,
            {
                "complete": END,
                "refinement": "refine_answer"
            }
        )

        # After refinement → back to quality evaluation
        self.workflow.add_edge("refine_answer", "evaluate_quality")

    def compile(self):
        """Compile the workflow into an executable graph."""
        return self.workflow.compile(
            checkpointer=self.memory,
            interrupt_before=[],
            # Interrupt after these nodes to wait for user input
            interrupt_after=["generate_deep_dive"]
        )

    async def run_async(self, initial_state: Dict[str, Any]) -> AdaptiveAnswerState:
        """
        Run the workflow asynchronously.

        Args:
            initial_state: Initial state dictionary

        Returns:
            Final state after workflow completion
        """
        # Add metadata
        initial_state["started_at"] = datetime.utcnow()
        initial_state["refinement_iteration"] = 0
        initial_state["answer_accepted"] = False

        # Compile and run
        app = self.compile()
        config = {"configurable": {"thread_id": initial_state.get("question_id", "default")}}

        # Run workflow
        final_state = None
        async for state in app.astream(initial_state, config):
            final_state = state

        # Add completion metadata
        if final_state:
            final_state["completed_at"] = datetime.utcnow()
            if "started_at" in final_state:
                duration = (final_state["completed_at"] - final_state["started_at"]).total_seconds()
                final_state["total_time_seconds"] = duration

        return final_state

    def run_sync(self, initial_state: Dict[str, Any], enable_persistence: bool = True) -> AdaptiveAnswerState:
        """
        Run the workflow synchronously.

        Args:
            initial_state: Initial state dictionary
            enable_persistence: Save state snapshots for resumption (Quick Win #5)

        Returns:
            Final state after workflow completion
        """
        # Add session ID if not present (Quick Win #5)
        if "session_id" not in initial_state or not initial_state["session_id"]:
            initial_state["session_id"] = generate_session_id()

        # Add metadata
        initial_state["started_at"] = datetime.utcnow()
        initial_state["refinement_iteration"] = 0
        initial_state["answer_accepted"] = False

        # Save initial state snapshot (Quick Win #5)
        if enable_persistence:
            try:
                save_state_snapshot(initial_state)
            except Exception as e:
                print(f"⚠️  Failed to save initial snapshot: {e}")

        # Compile and run
        app = self.compile()
        config = {"configurable": {"thread_id": initial_state.get("question_id", "default")}}

        # Use invoke() to get the final state directly
        final_state = app.invoke(initial_state, config)

        # Add completion metadata
        if final_state:
            final_state["completed_at"] = datetime.utcnow()
            if "started_at" in final_state:
                duration = (final_state["completed_at"] - final_state["started_at"]).total_seconds()
                final_state["total_time_seconds"] = duration

            # Save final state snapshot (Quick Win #5)
            if enable_persistence:
                try:
                    save_state_snapshot(final_state)
                except Exception as e:
                    print(f"⚠️  Failed to save final snapshot: {e}")

        return final_state

    def resume_from_snapshot(self, session_id: str, question_id: str) -> Optional[AdaptiveAnswerState]:
        """
        Resume workflow from saved snapshot (Quick Win #5).

        Args:
            session_id: Session UUID
            question_id: Question identifier

        Returns:
            Loaded state or None if snapshot not found
        """
        print(f"🔄 Attempting to resume session {session_id}, question {question_id}...")

        # Load snapshot
        state = load_state_snapshot(session_id, question_id)

        if state:
            print(f"✅ Snapshot loaded successfully")
            print(f"   Current step: {state.get('current_step')}")
            print(f"   Time elapsed: {state.get('total_time_seconds', 0):.2f}s")
            return state
        else:
            print(f"⚠️  No snapshot found for session {session_id}, question {question_id}")
            return None

    def visualize(self, output_path: str = "workflow_graph.png"):
        """
        Generate a visual representation of the workflow.
        Requires graphviz installed.
        """
        try:
            from langchain.graphs.graph_visualizer import visualize_graph
            app = self.compile()
            visualize_graph(app, output_path=output_path)
            print(f"✅ Workflow visualization saved to {output_path}")
        except ImportError:
            print("⚠️  graphviz not installed. Run: pip install graphviz")
        except Exception as e:
            print(f"❌ Failed to visualize: {str(e)}")


# ========================================
# Convenience Functions
# ========================================

def create_initial_state(
    question_id: str,
    question_text: str,
    question_data: Dict[str, Any],
    gap_info: Dict[str, Any],
    user_id: str,
    parsed_cv: Dict[str, Any],
    parsed_jd: Dict[str, Any],
    experience_check_response: str,  # "yes" or "no"
    language: str = "english"
) -> Dict[str, Any]:
    """
    Create initial state for the workflow.

    Args:
        question_id: Unique question ID
        question_text: The question text
        question_data: Full question object
        gap_info: Gap information from scoring phase
        user_id: User identifier
        parsed_cv: Parsed CV data
        parsed_jd: Parsed job description data
        experience_check_response: "yes" or "no"
        language: Content language

    Returns:
        Initial state dictionary
    """
    return {
        "question_id": question_id,
        "question_text": question_text,
        "question_data": question_data,
        "gap_info": gap_info,
        "user_id": user_id,
        "parsed_cv": parsed_cv,
        "parsed_jd": parsed_jd,
        "experience_check_response": experience_check_response,
        "language": language,
        "current_step": "start"
    }


def add_structured_inputs_to_state(
    state: AdaptiveAnswerState,
    structured_data: Dict[str, Any]
) -> AdaptiveAnswerState:
    """
    Update state with user's structured input responses.

    Args:
        state: Current state
        structured_data: User responses to deep dive prompts

    Returns:
        Updated state
    """
    state["structured_inputs"] = structured_data
    return state


def add_refinement_data_to_state(
    state: AdaptiveAnswerState,
    refinement_data: Dict[str, Any]
) -> AdaptiveAnswerState:
    """
    Update state with refinement data from user.

    Args:
        state: Current state
        refinement_data: Additional data for answer improvement

    Returns:
        Updated state
    """
    state["refinement_data"] = refinement_data
    return state


# ========================================
# Example Usage
# ========================================

if __name__ == "__main__":
    """Test the workflow with a sample question."""

    # Sample data
    initial_state = create_initial_state(
        question_id="q1",
        question_text="Do you have experience with AWS Lambda?",
        question_data={
            "id": "q1",
            "priority": "CRITICAL",
            "impact": "+15%"
        },
        gap_info={
            "title": "AWS Lambda Experience",
            "description": "Missing serverless computing experience",
            "impact": "-15%"
        },
        user_id="user123",
        parsed_cv={"technical_skills": ["Python", "React"]},
        parsed_jd={"hard_skills_required": [{"skill": "AWS Lambda", "priority": "critical"}]},
        experience_check_response="yes",  # Change to "no" or "willing_to_learn" to test other paths
        language="english"
    )

    # Run workflow
    workflow = AdaptiveQuestionWorkflow()

    print("\n🚀 Starting Adaptive Question Workflow")
    print("=" * 60)

    final_state = workflow.run_sync(initial_state)

    print("\n✅ Workflow Complete!")
    print("=" * 60)
    print(f"Current Step: {final_state.get('current_step')}")
    print(f"Quality Score: {final_state.get('quality_score')}")
    print(f"Final Answer: {final_state.get('final_answer')}")
    print(f"Total Time: {final_state.get('total_time_seconds', 0):.2f}s")

    if final_state.get('error'):
        print(f"\n⚠️  Error: {final_state['error']}")

    print("=" * 60)

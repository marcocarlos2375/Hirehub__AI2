-- Migration 001: Learning Resources System
-- Creates tables for adaptive question learning resources and user learning plans

-- ==================================================
-- Learning Resources Table
-- Stores courses, projects, certifications that users can access
-- ==================================================
CREATE TABLE IF NOT EXISTS learning_resources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL CHECK (type IN ('course', 'project', 'certification', 'challenge', 'tutorial')),
    provider VARCHAR(100),  -- e.g., 'Udemy', 'Coursera', 'freeCodeCamp', 'GitHub'
    url TEXT,
    duration_days INTEGER NOT NULL CHECK (duration_days > 0),
    difficulty VARCHAR(50) CHECK (difficulty IN ('beginner', 'intermediate', 'advanced')),
    cost VARCHAR(50) CHECK (cost IN ('free', 'paid', 'freemium')),
    skills_covered JSONB NOT NULL DEFAULT '[]'::jsonb,  -- Array of skill strings
    prerequisites JSONB DEFAULT '[]'::jsonb,  -- Array of prerequisite skills
    completion_certificate BOOLEAN DEFAULT FALSE,
    rating DECIMAL(3,2) CHECK (rating >= 0 AND rating <= 5),  -- 0-5 stars
    language VARCHAR(50) DEFAULT 'english',  -- Content language
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for common queries
CREATE INDEX idx_learning_resources_type ON learning_resources(type);
CREATE INDEX idx_learning_resources_difficulty ON learning_resources(difficulty);
CREATE INDEX idx_learning_resources_duration ON learning_resources(duration_days);
CREATE INDEX idx_learning_resources_cost ON learning_resources(cost);
CREATE INDEX idx_learning_resources_skills ON learning_resources USING GIN (skills_covered);

-- ==================================================
-- User Learning Plans Table
-- Tracks learning resources saved/in-progress/completed by users
-- ==================================================
CREATE TABLE IF NOT EXISTS user_learning_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,  -- From frontend auth (email or user ID)
    gap_id VARCHAR(255),  -- Reference to gap from scoring phase
    gap_title VARCHAR(255),  -- Title of the gap being addressed
    gap_description TEXT,  -- Description of the gap
    resource_ids JSONB NOT NULL DEFAULT '[]'::jsonb,  -- Array of learning_resource UUIDs
    status VARCHAR(50) NOT NULL DEFAULT 'suggested' CHECK (status IN ('suggested', 'in_progress', 'completed', 'abandoned')),
    notes TEXT,  -- User notes about the learning plan
    target_completion_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for user queries
CREATE INDEX idx_user_learning_plans_user_id ON user_learning_plans(user_id);
CREATE INDEX idx_user_learning_plans_status ON user_learning_plans(status);
CREATE INDEX idx_user_learning_plans_gap_id ON user_learning_plans(gap_id);

-- ==================================================
-- User Resource Progress Table
-- Tracks individual resource completion within a learning plan
-- ==================================================
CREATE TABLE IF NOT EXISTS user_resource_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    learning_plan_id UUID REFERENCES user_learning_plans(id) ON DELETE CASCADE,
    resource_id UUID REFERENCES learning_resources(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'not_started' CHECK (status IN ('not_started', 'in_progress', 'completed', 'skipped')),
    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    notes TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, resource_id)  -- User can't have duplicate progress for same resource
);

-- Indexes for progress tracking
CREATE INDEX idx_user_resource_progress_user_id ON user_resource_progress(user_id);
CREATE INDEX idx_user_resource_progress_plan_id ON user_resource_progress(learning_plan_id);
CREATE INDEX idx_user_resource_progress_status ON user_resource_progress(status);

-- ==================================================
-- Answer Quality Logs Table
-- Tracks answer quality evaluation and refinement iterations
-- ==================================================
CREATE TABLE IF NOT EXISTS answer_quality_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255),
    question_id VARCHAR(255) NOT NULL,
    gap_id VARCHAR(255),  -- Related gap
    original_answer TEXT NOT NULL,
    quality_score INTEGER CHECK (quality_score >= 1 AND quality_score <= 10),
    quality_issues JSONB DEFAULT '[]'::jsonb,  -- Array of issue strings
    improvement_suggestions JSONB DEFAULT '[]'::jsonb,  -- Array of suggestion objects
    refined_answer TEXT,  -- Final improved answer
    iteration_count INTEGER DEFAULT 1,  -- How many refinement iterations
    accepted_by_user BOOLEAN DEFAULT FALSE,  -- Did user accept the refined answer
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for quality analysis
CREATE INDEX idx_answer_quality_logs_user_id ON answer_quality_logs(user_id);
CREATE INDEX idx_answer_quality_logs_question_id ON answer_quality_logs(question_id);
CREATE INDEX idx_answer_quality_logs_quality_score ON answer_quality_logs(quality_score);

-- ==================================================
-- Trigger to update updated_at timestamp
-- ==================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers
CREATE TRIGGER update_learning_resources_updated_at BEFORE UPDATE ON learning_resources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_learning_plans_updated_at BEFORE UPDATE ON user_learning_plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_resource_progress_updated_at BEFORE UPDATE ON user_resource_progress
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_answer_quality_logs_updated_at BEFORE UPDATE ON answer_quality_logs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==================================================
-- Sample Data (Optional - for testing)
-- ==================================================
-- Insert a few sample learning resources
-- These will be replaced by the seed script with 100+ real resources

INSERT INTO learning_resources (title, description, type, provider, url, duration_days, difficulty, cost, skills_covered, completion_certificate, rating, language) VALUES
('AWS Fundamentals Course', 'Learn AWS basics including EC2, S3, Lambda, and RDS', 'course', 'freeCodeCamp', 'https://www.youtube.com/watch?v=SOTamWNgDKc', 3, 'beginner', 'free', '["AWS", "EC2", "S3", "Lambda", "Cloud Computing"]'::jsonb, true, 4.8, 'english'),
('Build a Serverless REST API', 'Create a production-ready serverless API with AWS Lambda, API Gateway, and DynamoDB', 'project', 'GitHub', 'https://github.com/serverless/examples/tree/master/aws-python-rest-api-with-dynamodb', 5, 'intermediate', 'free', '["AWS Lambda", "API Gateway", "DynamoDB", "Python", "Serverless"]'::jsonb, false, 4.5, 'english'),
('AWS Certified Cloud Practitioner', 'Prepare for AWS Cloud Practitioner certification exam', 'certification', 'AWS', 'https://aws.amazon.com/certification/certified-cloud-practitioner/', 7, 'beginner', 'paid', '["AWS", "Cloud Computing", "Cloud Architecture"]'::jsonb, true, 4.9, 'english'),
('LangChain Crash Course', 'Build AI applications with LangChain and LLMs', 'course', 'YouTube', 'https://www.youtube.com/watch?v=LbT1yp6quS8', 2, 'intermediate', 'free', '["LangChain", "OpenAI", "LLMs", "Python", "AI"]'::jsonb, false, 4.7, 'english'),
('React Advanced Patterns', 'Master advanced React patterns and best practices', 'course', 'Udemy', 'https://www.udemy.com/course/react-advanced/', 4, 'advanced', 'paid', '["React", "JavaScript", "Frontend", "State Management"]'::jsonb, true, 4.6, 'english')
ON CONFLICT DO NOTHING;

-- End of migration

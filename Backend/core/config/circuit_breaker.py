"""
Circuit Breaker Pattern for External Service Resilience.
Prevents cascading failures by failing fast when external services are unhealthy.

States:
- CLOSED: Normal operation, requests flow through
- OPEN: Service is failing, requests fail immediately
- HALF_OPEN: Testing if service has recovered

Features:
- Async-native implementation
- Per-service circuit breakers
- Automatic recovery with exponential backoff
- Metrics tracking for monitoring
"""

import asyncio
import time
from enum import Enum
from typing import Callable, TypeVar, Optional, Dict, Any
from functools import wraps
from dataclasses import dataclass, field

from core.config.logging_config import logger
from core.config.settings import settings

T = TypeVar('T')


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitStats:
    """Statistics for circuit breaker monitoring."""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    consecutive_failures: int = 0
    consecutive_successes: int = 0


@dataclass
class CircuitBreaker:
    """
    Circuit breaker for a single service.
    Thread-safe implementation using asyncio locks.
    """
    name: str
    failure_threshold: int = field(default_factory=lambda: settings.circuit_breaker_failure_threshold)
    recovery_timeout: float = field(default_factory=lambda: settings.circuit_breaker_recovery_timeout)
    half_open_requests: int = field(default_factory=lambda: settings.circuit_breaker_half_open_requests)

    # Internal state
    _state: CircuitState = field(default=CircuitState.CLOSED, init=False)
    _stats: CircuitStats = field(default_factory=CircuitStats, init=False)
    _last_state_change: float = field(default_factory=time.time, init=False)
    _half_open_successes: int = field(default=0, init=False)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)

    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        return self._state

    @property
    def stats(self) -> Dict[str, Any]:
        """Get circuit statistics for monitoring."""
        return {
            "name": self.name,
            "state": self._state.value,
            "total_calls": self._stats.total_calls,
            "successful_calls": self._stats.successful_calls,
            "failed_calls": self._stats.failed_calls,
            "rejected_calls": self._stats.rejected_calls,
            "consecutive_failures": self._stats.consecutive_failures,
            "last_failure_time": self._stats.last_failure_time,
            "last_success_time": self._stats.last_success_time,
        }

    async def _should_allow_request(self) -> bool:
        """Determine if a request should be allowed through."""
        async with self._lock:
            if self._state == CircuitState.CLOSED:
                return True

            if self._state == CircuitState.OPEN:
                # Check if recovery timeout has elapsed
                elapsed = time.time() - self._last_state_change
                if elapsed >= self.recovery_timeout:
                    self._state = CircuitState.HALF_OPEN
                    self._half_open_successes = 0
                    self._last_state_change = time.time()
                    logger.info(f"Circuit breaker '{self.name}' transitioned to HALF_OPEN")
                    return True
                return False

            if self._state == CircuitState.HALF_OPEN:
                # Allow limited requests in half-open state
                return True

            return False

    async def _record_success(self) -> None:
        """Record a successful call."""
        async with self._lock:
            self._stats.total_calls += 1
            self._stats.successful_calls += 1
            self._stats.consecutive_successes += 1
            self._stats.consecutive_failures = 0
            self._stats.last_success_time = time.time()

            if self._state == CircuitState.HALF_OPEN:
                self._half_open_successes += 1
                if self._half_open_successes >= self.half_open_requests:
                    self._state = CircuitState.CLOSED
                    self._last_state_change = time.time()
                    logger.info(f"Circuit breaker '{self.name}' CLOSED after successful recovery")

    async def _record_failure(self, error: Exception) -> None:
        """Record a failed call."""
        async with self._lock:
            self._stats.total_calls += 1
            self._stats.failed_calls += 1
            self._stats.consecutive_failures += 1
            self._stats.consecutive_successes = 0
            self._stats.last_failure_time = time.time()

            if self._state == CircuitState.HALF_OPEN:
                # Immediately open circuit on failure in half-open state
                self._state = CircuitState.OPEN
                self._last_state_change = time.time()
                logger.warning(
                    f"Circuit breaker '{self.name}' OPENED after half-open failure: {error}"
                )
            elif self._state == CircuitState.CLOSED:
                if self._stats.consecutive_failures >= self.failure_threshold:
                    self._state = CircuitState.OPEN
                    self._last_state_change = time.time()
                    logger.warning(
                        f"Circuit breaker '{self.name}' OPENED after {self.failure_threshold} "
                        f"consecutive failures: {error}"
                    )

    async def _record_rejection(self) -> None:
        """Record a rejected call (circuit open)."""
        async with self._lock:
            self._stats.total_calls += 1
            self._stats.rejected_calls += 1

    async def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        Execute a function through the circuit breaker.

        Args:
            func: Async function to execute
            *args, **kwargs: Arguments to pass to the function

        Returns:
            Result from the function

        Raises:
            CircuitBreakerOpenError: If circuit is open
            Exception: If the underlying function fails
        """
        if not settings.enable_circuit_breaker:
            # Circuit breaker disabled, pass through
            return await func(*args, **kwargs)

        if not await self._should_allow_request():
            await self._record_rejection()
            raise CircuitBreakerOpenError(
                f"Circuit breaker '{self.name}' is OPEN. "
                f"Service unavailable, try again in {self.recovery_timeout}s"
            )

        try:
            result = await func(*args, **kwargs)
            await self._record_success()
            return result
        except Exception as e:
            await self._record_failure(e)
            raise

    def reset(self) -> None:
        """Manually reset the circuit breaker to closed state."""
        self._state = CircuitState.CLOSED
        self._stats = CircuitStats()
        self._last_state_change = time.time()
        self._half_open_successes = 0
        logger.info(f"Circuit breaker '{self.name}' manually reset to CLOSED")


class CircuitBreakerOpenError(Exception):
    """Raised when a request is rejected due to open circuit."""
    pass


# Global circuit breaker registry
_circuit_breakers: Dict[str, CircuitBreaker] = {}
_registry_lock = asyncio.Lock()


async def get_circuit_breaker(name: str) -> CircuitBreaker:
    """
    Get or create a circuit breaker for a service.

    Args:
        name: Service name (e.g., "gemini", "openai", "redis")

    Returns:
        CircuitBreaker instance for the service
    """
    if name not in _circuit_breakers:
        async with _registry_lock:
            if name not in _circuit_breakers:
                _circuit_breakers[name] = CircuitBreaker(name=name)
                logger.debug(f"Created circuit breaker for service: {name}")
    return _circuit_breakers[name]


def get_all_circuit_breaker_stats() -> Dict[str, Dict[str, Any]]:
    """Get statistics for all circuit breakers."""
    return {name: cb.stats for name, cb in _circuit_breakers.items()}


def circuit_breaker(service_name: str):
    """
    Decorator to wrap an async function with circuit breaker protection.

    Usage:
        @circuit_breaker("gemini")
        async def call_gemini_api(prompt: str) -> str:
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            cb = await get_circuit_breaker(service_name)
            return await cb.call(func, *args, **kwargs)
        return wrapper
    return decorator


__all__ = [
    'CircuitBreaker',
    'CircuitState',
    'CircuitBreakerOpenError',
    'get_circuit_breaker',
    'get_all_circuit_breaker_stats',
    'circuit_breaker',
]

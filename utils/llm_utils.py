from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import json
from langchain_core.exceptions import OutputParserException
import openai

def create_retry_decorator(max_attempts: int = 3):
    """
    Creates a tenacity retry decorator for LLM calls.
    Retries on:
    - OpenAI API errors (ServiceUnavailable, RateLimit, APIError)
    - JSON parsing errors (OutputParserException)
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((
            openai.APIError,
            openai.RateLimitError,
            openai.APIConnectionError,
            openai.InternalServerError,
            OutputParserException,
            json.JSONDecodeError,
            ValueError # Catch pydantic validation errors often
        )),
        reraise=True
    )

# Pre-configured decorator
llm_retry = create_retry_decorator()

from app.exceptions.base import AppException


class LLMConfigurationNotFoundError(
    AppException,
):
    status_code = 400

    error_code = (
        "LLM_CONFIGURATION_NOT_FOUND"
    )

    message = (
        "No active LLM configuration "
        "is available for this "
        "knowledge base."
    )


class LLMAuthenticationError(
    AppException,
):
    status_code = 502

    error_code = (
        "LLM_AUTHENTICATION_FAILED"
    )

    message = (
        "The configured LLM credentials "
        "are invalid."
    )


class LLMRateLimitError(
    AppException,
):
    status_code = 429

    error_code = (
        "LLM_RATE_LIMITED"
    )

    message = (
        "The LLM provider rate limit "
        "has been reached. "
        "Please try again later."
    )


class LLMTimeoutError(
    AppException,
):
    status_code = 504

    error_code = (
        "LLM_TIMEOUT"
    )

    message = (
        "The LLM provider did not "
        "respond within the expected "
        "time."
    )


class LLMConnectionError(
    AppException,
):
    status_code = 502

    error_code = (
        "LLM_CONNECTION_FAILED"
    )

    message = (
        "The configured LLM provider "
        "could not be reached."
    )


class LLMProviderError(
    AppException,
):
    status_code = 502

    error_code = (
        "LLM_PROVIDER_ERROR"
    )

    message = (
        "The LLM provider returned "
        "an error."
    )
class AppError(Exception):
    status_code = 500
    public_message = "Internal server error."


class ConfigurationError(AppError):
    status_code = 503
    public_message = "AI service is not configured."


class AIServiceError(AppError):
    status_code = 502
    public_message = "AI service failed to generate SQL."


class DataLoadError(AppError):
    status_code = 500
    public_message = "Unable to load dataset."


class QueryExecutionError(AppError):
    status_code = 400
    public_message = "Unable to execute SQL query."

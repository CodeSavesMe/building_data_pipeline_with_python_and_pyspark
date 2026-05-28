class PipelineError(Exception):
    """Base exception for pipeline failures."""


class ExtractError(PipelineError):
    """Raised when data extraction fails."""


class TransformError(PipelineError):
    """Raised when data transformation fails."""


class LoadError(PipelineError):
    """Raised when data loading fails."""

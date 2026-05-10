class PharmaWatchError(Exception):
    """Base for all domain errors."""


class ToolNotFoundError(PharmaWatchError):
    pass


class ToolExecutionError(PharmaWatchError):
    pass


class DrapDataError(PharmaWatchError):
    pass


class AgentTimeoutError(PharmaWatchError):
    pass

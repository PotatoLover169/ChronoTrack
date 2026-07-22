class TimerAlreadyRunningError(Exception):
    """
    Raised when a user attempts to start a new timer
    while another timer is already running.
    """

    def __init__(
        self,
        message="You already have a running timer.",
    ):
        super().__init__(message)


class NoRunningTimerError(Exception):
    """
    Raised when a user attempts to stop a timer,
    but no running timer exists.
    """

    def __init__(
        self,
        message="You don't have a running timer.",
    ):
        super().__init__(message)
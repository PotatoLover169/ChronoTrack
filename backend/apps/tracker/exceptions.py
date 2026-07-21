class TimerAlreadyRunningError(Exception):
    """
    Raised when a user attempts to start a new timer
    while another timer is already running.
    """

    default_message = "You already have a running timer."

    def __init__(self, message=None):
        super().__init__(message or self.default_message)
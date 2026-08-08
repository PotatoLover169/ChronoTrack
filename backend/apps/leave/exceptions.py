class LeaveRequestAlreadyReviewedError(Exception):
    pass


class PendingLeaveRequestExistsError(Exception):
    pass


class InsufficientLeaveBalanceError(Exception):
    pass


class InvalidLeaveDatesError(Exception):
    pass


class LeaveRequestPermissionError(Exception):
    pass
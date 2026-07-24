class PendingEditRequestExistsError(Exception):
    """
    Raised when a Time Entry already has
    a pending edit request.
    """
    pass

class EditRequestAlreadyReviewedError(Exception):
    """
    Raised when an edit request has already been reviewed.
    """
    pass
from rest_framework.permissions import BasePermission


class IsEmployee(BasePermission):
    """
    Allows any authenticated employee to create, view,
    and cancel their own edit requests.
    """

    message = (
        "Authentication is required."
    )

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
        )


class IsManagerOrAdmin(BasePermission):
    """
    Allows only managers or administrators.
    """

    message = (
        "Only managers or administrators may perform this action."
    )

    def has_permission(self, request, view):
        user = request.user

        return (
            user
            and user.is_authenticated
            and (
                user.is_staff
                or user.is_superuser
            )
        )
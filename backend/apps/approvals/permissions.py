from rest_framework.permissions import BasePermission


class IsEmployee(BasePermission):
    """
    Allows authenticated users to access employee-level
    edit-request endpoints.
    """

    message = "Authentication is required."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
        )


class IsManagerOrAdmin(BasePermission):
    """
    Allows only users assigned to the Manager or Admin role.
    Superusers are also allowed.
    """

    message = (
        "Only managers or administrators may perform this action."
    )

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return (
            user.is_superuser
            or user.groups.filter(
                name__in=["Manager", "Admin"],
            ).exists()
        )
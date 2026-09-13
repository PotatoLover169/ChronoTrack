from rest_framework.permissions import BasePermission


class IsAdminUserRole(BasePermission):
    """
    Allows access only to superusers.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_superuser
        )


class IsManagerOrAdminRole(BasePermission):
    """
    Allows access to Managers and Administrators.
    """

    def has_permission(self, request, view):
        if not (
            request.user
            and request.user.is_authenticated
        ):
            return False

        return (
            request.user.is_superuser
            or request.user.groups.filter(
                name__in=["Manager", "Admin"]
            ).exists()
        )
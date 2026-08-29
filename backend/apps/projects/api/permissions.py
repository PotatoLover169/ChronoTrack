from rest_framework.permissions import BasePermission


class ProjectPermission(BasePermission):
    """
    Project access rules.

    Authenticated users:
        - Can view projects.

    Managers and Admins:
        - Can create projects.
        - Can update projects.
        - Can delete projects.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Authenticated users can view projects.
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True

        # Django superusers always have permission.
        if user.is_superuser:
            return True

        # Only Managers and Admins can modify projects.
        return user.groups.filter(
            name__in=["Manager", "Admin"]
        ).exists()
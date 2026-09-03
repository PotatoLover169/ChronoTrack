from rest_framework.permissions import BasePermission


class TaskPermission(BasePermission):
    """
    Task access rules.

    Managers and Admins:
        - Can view all tasks.
        - Can create tasks.
        - Can update tasks.
        - Can delete tasks.

    Employees:
        - Can view tasks assigned to them.
        - Can update their assigned tasks.
        - Cannot create tasks.
        - Cannot delete tasks.
        - Cannot reassign tasks.
    """

    def _is_manager_or_admin(self, user):
        return (
            user.is_superuser
            or user.groups.filter(name__in=["Manager", "Admin"]).exists()
        )

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Managers and Admins have full task permissions.
        if self._is_manager_or_admin(user):
            return True

        # Employees can view tasks.
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True

        # Allow detail-level modification requests to reach
        # has_object_permission(), where ownership/assignment
        # is checked.
        if request.method in ["PATCH", "PUT", "DELETE"]:
            return True

        # Employees cannot create tasks.
        if request.method == "POST":
            return False

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Managers and Admins have full access.
        if self._is_manager_or_admin(user):
            return True

        # Employees can only access tasks assigned to them.
        if obj.assigned_to_id != user.id:
            return False

        # Employees can view and update their assigned tasks.
        if request.method in ["GET", "HEAD", "OPTIONS", "PATCH", "PUT"]:
            return True

        # Employees cannot delete tasks.
        return False
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

        # Everyone authenticated can access the endpoint.
        # Object-level rules below determine what an Employee
        # can actually access.
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Manager/Admin can manage every task.
        if self._is_manager_or_admin(user):
            return True

        # Employee can only access tasks assigned to them.
        if obj.assigned_to_id != user.id:
            return False

        # Employee can view/update assigned tasks.
        if request.method in ["GET", "HEAD", "OPTIONS", "PATCH", "PUT"]:
            return True

        # Employee cannot delete assigned tasks.
        return False
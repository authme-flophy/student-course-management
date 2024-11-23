from rest_framework import permissions

class IsInstructor(permissions.BasePermission):
    """
    Custom permission to only allow instructors to perform certain actions.
    """
    def has_permission(self, request, view):
        return request.user and hasattr(request.user, 'instructor')

class IsInstructorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow instructors to edit courses.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to instructors
        return request.user and hasattr(request.user, 'instructor') 
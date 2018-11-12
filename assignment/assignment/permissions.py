from rest_framework import permissions


class IsStaff(permissions.BasePermission):
    """
    Permission to allow access for Active Drivers.
    """

    def has_permission(self, request, view):

        return request.user.is_authenticated() and request.user.is_staff

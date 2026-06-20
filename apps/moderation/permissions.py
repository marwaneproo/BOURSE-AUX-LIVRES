from rest_framework import permissions

from apps.accounts.models import Profile


class IsAdminProfile(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        try:
            return request.user.profile.est_administrateur or request.user.is_staff
        except Profile.DoesNotExist:
            return request.user.is_staff

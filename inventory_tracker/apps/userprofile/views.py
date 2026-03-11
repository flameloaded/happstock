from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Profile
from .serializers import ProfileSerializer


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Allow owners to view/edit their own profile; admins can manage all.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Profile.objects.all()  # Admins can view all
        return Profile.objects.filter(user=user)  # Regular users only see their own

    def create(self, request, *args, **kwargs):
        """
        Disable profile creation through the API,
        since profiles are auto-created via signals.
        """
        return Response(
            {"detail": "Profile creation is not allowed. It is automatically created when a user registers."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def perform_update(self, serializer):
        # Ensure users can only update their own profile (admins can update all)
        if not self.request.user.is_staff and serializer.instance.user != self.request.user:
            return Response(
                {"detail": "You are not allowed to edit another user's profile."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()

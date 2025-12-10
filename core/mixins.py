from django.core.exceptions import PermissionDenied


class OwnerOrPermissionMixin:
    owner_field = "owner"
    required_permissions = None

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        owner = getattr(obj, self.owner_field, None)

        # Доступ владельцу
        if owner == request.user:
            return super().dispatch(request, *args, **kwargs)

        # Доступ по permissions
        if self.required_permissions:
            if any(request.user.has_perm(perm) for perm in self.required_permissions):
                return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied("Нет доступа")

from django.core.exceptions import PermissionDenied


class PermissionRequiredMixin:
    required_permissions = None  # список разрешений

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied("Необходимо войти в систему")

        if not self.required_permissions:
            return super().dispatch(request, *args, **kwargs)

        for perm in self.required_permissions:
            if not request.user.has_perm(perm):
                raise PermissionDenied("Недостаточно прав")

        return super().dispatch(request, *args, **kwargs)

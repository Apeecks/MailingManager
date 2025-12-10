from django.core.exceptions import PermissionDenied

class OwnerOrStaffReadMixin:
    """Просмотр: владелец или менеджер"""

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()

        # Менеджер видит всё
        if request.user.is_staff:
            return super().dispatch(request, *args, **kwargs)

        # Пользователь видит только свои записи
        if obj.owner == request.user:
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied


class OwnerOnlyEditMixin:
    """Редактирование/удаление: только владелец"""

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()

        # Менеджеру редактировать нельзя
        if request.user.is_staff and obj.owner != request.user:
            raise PermissionDenied

        # Владелец может
        if obj.owner == request.user:
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied

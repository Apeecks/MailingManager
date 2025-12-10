from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        User = get_user_model()

        user_admin, created = User.objects.get_or_create(
            email="admin@admin.ru", username="admin"
        )
        user_admin.set_password("admin123")
        user_admin.is_staff = True
        user_admin.is_superuser = True
        user_admin.save()
        self.stdout.write(
            self.style.SUCCESS(f"Админ создан или найден. email: {user_admin.email}")
        )
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        User = get_user_model()

        user_admin, created = User.objects.get_or_create(
            email="admin@mail.ru", username="admin"
        )
        user_admin.set_password("qwerty1.")
        user_admin.is_staff = True
        user_admin.is_superuser = True
        user_admin.save()
        self.stdout.write(
            self.style.SUCCESS(f"Админ создан или найден. email: {user_admin.email}")
        )

        user1, created = User.objects.get_or_create(
            email="user1@mail.ru", username="user1"
        )
        user1.set_password("qwerty1.")
        user1.save()
        self.stdout.write(
            self.style.SUCCESS(f"User создан или найден. email: {user1.email}")
        )

        user2, created = User.objects.get_or_create(
            email="user2@mail.ru", username="user2"
        )
        user2.set_password("qwerty1.")
        user2.save()
        self.stdout.write(
            self.style.SUCCESS(f"User создан или найден. email: {user2.email}")
        )

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

ROLE_PERMISSIONS = {
    "managers": [
        "can_disable_mailing",
        "can_view_all_mailings",
        "can_manage_messages",
        "can_manage_recipients",
        "can_view_users",
        "can_block_users",
    ],
}


class Command(BaseCommand):
    help = "Создаёт группу 'managers' и назначает permissions"

    def handle(self, *args, **options):

        for role_name, perm_codenames in ROLE_PERMISSIONS.items():

            group, created = Group.objects.get_or_create(name=role_name)

            permissions = Permission.objects.filter(codename__in=perm_codenames)

            group.permissions.set(permissions)

            self.stdout.write(
                self.style.SUCCESS(f"Группа '{role_name}' обновлена. Прав: {permissions.count()}")
            )

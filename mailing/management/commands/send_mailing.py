from django.core.management.base import BaseCommand
from django.utils import timezone

from mailing.models import Mailing
from mailing.services import MailingServices


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        now = timezone.now()
        mailings = Mailing.objects.filter(start__lte=now, end__gte=now)

        for mailing in mailings:
            MailingServices.send_mailing(mailing)
        self.stdout.write(self.style.SUCCESS("Рассылки отправлены"))

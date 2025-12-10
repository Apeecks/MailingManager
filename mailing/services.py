from django.core.mail import send_mail
from django.utils import timezone

from .models import MailingIsSuccess


class MailingServices:
    @staticmethod
    def calculate_status(mailing):
        now = timezone.now()
        if now < mailing.start:
            return 'Создана'
        if mailing.start <= now <= mailing.end:
            return 'Запущена'
        return 'Завершена'

    @staticmethod
    def update_mailing_status(mailing):

        if mailing.status == "Отключена админом":
            return mailing.status

        new_status = MailingServices.calculate_status(mailing)
        if mailing.status != new_status:
            mailing.status = new_status
            mailing.save(update_fields=['status'])
        return new_status

    @staticmethod
    def can_send_now(mailing):
        now = timezone.now()
        return mailing.start <= now <= mailing.end

    @staticmethod
    def send_mailing(mailing, from_email='Apeecks@mail.ru', fail_silently=False):
        """
        Отправляет письма всем получателям рассылки.
        Создаёт записи MailingIsSuccess для каждой попытки.
        """
        sent = 0
        failed = 0
        msg = mailing.message
        recipients = mailing.recipients.all()

        for r in recipients:
            try:
                send_mail(
                    subject=msg.header,
                    message=msg.body,
                    from_email=from_email,
                    recipient_list=[r.email],
                    fail_silently=fail_silently,
                )
                MailingIsSuccess.objects.create(
                    status='Успешно',
                    answer='OK',
                    mailing=mailing
                )
                sent += 1
            except Exception as exc:
                MailingIsSuccess.objects.create(
                    status='Не успешно',
                    answer=str(exc),
                    mailing=mailing
                )
                failed += 1

        MailingServices.update_mailing_status(mailing)

        return {'sent': sent, 'failed': failed}

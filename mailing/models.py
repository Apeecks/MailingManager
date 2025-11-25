from django.db import models


class MailingRecipients(models.Model):
    """Получатели рассылки"""

    email = models.CharField(
        unique=True,
        max_length=50,
        verbose_name='email',
    )
    full_name = models.CharField(
        max_length=100,
        verbose_name='Ф.И.О.'
    )
    comment = models.TextField(
        verbose_name='Comment',
    )

    def __str__(self):
        return self.full_name


    class Meta:
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"
        ordering = [
            "email",
        ]
        db_table = "MailingRecipients"


class Message(models.Model):
    """Текст рассылки"""

    header = models.CharField(
        max_length=100,
        verbose_name='Тема',
    )
    body = models.TextField(
        verbose_name='Тело письма',
    )

    def __str__(self):
        return self.header


    class Meta:
        verbose_name = "Текст"
        verbose_name_plural = "Текст"
        ordering = [
            "header",
        ]
        db_table = "Message"


class Mailing(models.Model):
    """Инфо о рассылки"""

    start = models.DateTimeField(
        verbose_name='Начало'
    )
    end = models.DateTimeField(
        verbose_name='Конец'
    )
    status = models.CharField(
        max_length=10,
        verbose_name='Статус'
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='mailings',
    )
    recipients = models.ManyToManyField(
        MailingRecipients,
        related_name='recipients'
    )

    def __str__(self):
        return f"Рассылка {self.id}, {self.status}"


    class Meta:
        verbose_name = "Инфо"
        verbose_name_plural = "Инфо"
        ordering = [
            "status",
            "start",
        ]
        db_table = "Mailing"


class MailingIsSuccess(models.Model):
    """Попытка рассылки"""

    date_mailing = models.DateTimeField(
        auto_now_add=True
    )
    status = models.CharField(
        max_length=10,
        verbose_name='Успешно/Не успешно'
    )
    answer = models.CharField(
        max_length=500,
        verbose_name='Ответ почтового сервера'
    )
    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        related_name='attempts'
    )

    def __str__(self):
        return f"Попытка {self.id}, {self.status}"


    class Meta:
        verbose_name = "Попытка"
        verbose_name_plural = "Попытки"
        ordering = [
            "date_mailing",
        ]
        db_table = "MailingIsSuccess"

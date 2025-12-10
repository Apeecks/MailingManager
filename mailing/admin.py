# yourapp/admin.py
from django.contrib import admin
from django.core.management import call_command
from .models import MailingRecipients, Message, Mailing, MailingIsSuccess


@admin.register(MailingRecipients)
class MailingRecipientsAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email',)
    search_fields = ('email', 'full_name',)
    ordering = ('email',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('header',)
    search_fields = ('header', )
    ordering = ('header',)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'start', 'end', 'message')
    list_filter = ('status',)
    filter_horizontal = ('recipients',)
    search_fields = ('status', 'message__header',)
    actions = ['run_mailing_now']


@admin.register(MailingIsSuccess)
class MailingIsSuccessAdmin(admin.ModelAdmin):
    list_display = ('mailing', 'date_mailing', 'status',)
    list_filter = ('status',)
    search_fields = ('answer',)
    ordering = ('-date_mailing',)

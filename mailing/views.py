from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from core.mixins import OwnerOrStaffReadMixin, OwnerOnlyEditMixin
from .forms import MailingRecipientsForm, MessageForm, MailingForm
from .models import MailingRecipients, Message, Mailing, MailingIsSuccess
from django.views import View
from django.contrib import messages
from .services import MailingServices
from django.utils import timezone


@method_decorator(cache_page(60 * 5), name='dispatch')
class IndexView(TemplateView):
    template_name = 'mailing/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()

        context['total_mailings'] = Mailing.objects.count()

        context['active_mailings'] = Mailing.objects.filter(
            start__lte=now,
            end__gte=now,
            status='Запущена'
        ).count()

        context['unique_recipients'] = MailingRecipients.objects.count()

        # Новое для шага 8
        context['attempts_success'] = MailingIsSuccess.objects.filter(status='Успешно').count()
        context['attempts_failed'] = MailingIsSuccess.objects.filter(status='Не успешно').count()
        context['attempts_total'] = MailingIsSuccess.objects.count()

        return context


class MailingSendView(LoginRequiredMixin, View):
    """Ручная отправка рассылки"""

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)

        MailingServices.update_mailing_status(mailing)

        if not MailingServices.can_send_now(mailing):
            messages.error(request, "Отправка запрещена в текущее время (вне окна start..end).")
            return redirect('mailing:mailing_detail', pk=pk)

        result = MailingServices.send_mailing(mailing, from_email='Apeecks@mail.ru')

        messages.success(
            request,
            f"Рассылка обработана. Успешно: {result['sent']}, Ошибки: {result['failed']}"
        )
        return redirect('mailing:mailing_detail', pk=pk)


@method_decorator(cache_page(60), name='dispatch')
class RecipientListView(LoginRequiredMixin, ListView):
    model = MailingRecipients
    template_name = 'recipients/list.html'
    context_object_name = 'recipients'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(owner=self.request.user)


class RecipientDetailView(LoginRequiredMixin, OwnerOrStaffReadMixin, DetailView):
    model = MailingRecipients
    template_name = 'recipients/detail.html'
    context_object_name = 'recipient'


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = MailingRecipients
    form_class = MailingRecipientsForm
    template_name = 'recipients/form.html'
    success_url = reverse_lazy('mailing:recipient_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientUpdateView(LoginRequiredMixin, OwnerOnlyEditMixin, UpdateView):
    model = MailingRecipients
    form_class = MailingRecipientsForm
    template_name = 'recipients/form.html'
    success_url = reverse_lazy('mailing:recipient_list')


class RecipientDeleteView(LoginRequiredMixin, OwnerOnlyEditMixin, DeleteView):
    model = MailingRecipients
    template_name = 'recipients/confirm_delete.html'
    success_url = reverse_lazy('mailing:recipient_list')


@method_decorator(cache_page(60), name='dispatch')
class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'message/list.html'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'message/form.html'
    success_url = reverse_lazy('mailing:message_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageDetailView(LoginRequiredMixin, OwnerOrStaffReadMixin, DetailView):
    model = Message
    template_name = 'message/detail.html'


class MessageUpdateView(LoginRequiredMixin, OwnerOnlyEditMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'message/form.html'
    success_url = reverse_lazy('mailing:message_list')


class MessageDeleteView(LoginRequiredMixin, OwnerOnlyEditMixin, DeleteView):
    model = Message
    template_name = 'message/confirm_delete.html'
    success_url = reverse_lazy('mailing:message_list')


@method_decorator(cache_page(60), name='dispatch')
class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailing/list.html'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(owner=self.request.user)


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, OwnerOnlyEditMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/form.html'
    success_url = reverse_lazy('mailing:mailing_list')


class MailingDeleteView(LoginRequiredMixin, OwnerOnlyEditMixin, DeleteView):
    model = Mailing
    template_name = 'mailing/confirm_delete.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        MailingServices.update_mailing_status(obj)
        return obj


class MailingDetailView(LoginRequiredMixin, OwnerOrStaffReadMixin, DetailView):
    model = Mailing
    template_name = 'mailing/detail.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        MailingServices.update_mailing_status(obj)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailing = self.object

        context["attempts_success"] = mailing.attempts.filter(status="Успешно").count()
        context["attempts_failed"] = mailing.attempts.filter(status="Не успешно").count()
        context["attempts_total"] = mailing.attempts.count()

        return context

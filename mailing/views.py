from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  TemplateView, UpdateView)

from core.mixins import OwnerOrPermissionMixin
from core.permisions import PermissionRequiredMixin

from .forms import MailingForm, MailingRecipientsForm, MessageForm
from .models import Mailing, MailingIsSuccess, MailingRecipients, Message
from .services import MailingServices


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
        print("DEBUG: SEND VIEW EXECUTED", mailing.id)
        print("DEBUG: CAN SEND =", MailingServices.can_send_now(mailing))
        print("DEBUG: NOW =", timezone.now())
        print("DEBUG: START =", mailing.start)
        print("DEBUG: END =", mailing.end)

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


class AttemptListView(LoginRequiredMixin, ListView):
    model = MailingIsSuccess
    template_name = "attempts/list.html"
    paginate_by = 30

    def get_queryset(self):
        qs = super().get_queryset()

        # Менеджер видит всё
        if self.request.user.has_perm("mailing.can_view_all_mailings"):
            return qs

        # Пользователь — только свои рассылки
        return qs.filter(mailing__owner=self.request.user)


class DisableMailingView(PermissionRequiredMixin, View):
    permission_required = "mailing.can_disable_mailing"

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        mailing.status = "Отключена админом"
        mailing.save(update_fields=["status"])
        messages.success(request, "Рассылка отключена менеджером.")
        return redirect("mailing:mailing_detail", pk=pk)


# ===== Recipient =====
@method_decorator(cache_page(60), name='dispatch')
class RecipientListView(LoginRequiredMixin, ListView):
    model = MailingRecipients
    template_name = 'recipients/list.html'
    context_object_name = 'recipients'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset()

        # менеджер видит всё
        if self.request.user.has_perm("mailing.can_manage_recipients"):
            return qs

        # обычный пользователь только свое
        return qs.filter(owner=self.request.user)


class RecipientDetailView(LoginRequiredMixin, OwnerOrPermissionMixin, DetailView):
    model = MailingRecipients
    template_name = 'recipients/detail.html'
    context_object_name = 'recipient'
    required_permissions = ["mailing.can_manage_recipients"]


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = MailingRecipients
    form_class = MailingRecipientsForm
    template_name = 'recipients/form.html'
    success_url = reverse_lazy('mailing:recipient_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientUpdateView(LoginRequiredMixin, OwnerOrPermissionMixin, UpdateView):
    model = MailingRecipients
    form_class = MailingRecipientsForm
    template_name = 'recipients/form.html'
    success_url = reverse_lazy('mailing:recipient_list')
    required_permissions = ["mailing.can_manage_recipients"]


class RecipientDeleteView(LoginRequiredMixin, OwnerOrPermissionMixin, DeleteView):
    model = MailingRecipients
    template_name = 'recipients/confirm_delete.html'
    success_url = reverse_lazy('mailing:recipient_list')
    required_permissions = ["mailing.can_manage_recipients"]


# ===== Message =====
@method_decorator(cache_page(60), name='dispatch')
class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'message/list.html'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset()

        if self.request.user.has_perm("mailing.can_manage_messages"):
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


class MessageDetailView(LoginRequiredMixin, OwnerOrPermissionMixin, DetailView):
    model = Message
    template_name = 'message/detail.html'
    required_permissions = ["mailing.can_manage_messages"]


class MessageUpdateView(LoginRequiredMixin, OwnerOrPermissionMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'message/form.html'
    success_url = reverse_lazy('mailing:message_list')
    required_permissions = ["mailing.can_manage_messages"]


class MessageDeleteView(LoginRequiredMixin, OwnerOrPermissionMixin, DeleteView):
    model = Message
    template_name = 'message/confirm_delete.html'
    success_url = reverse_lazy('mailing:message_list')
    required_permissions = ["mailing.can_manage_messages"]


# ===== Mailing =====
@method_decorator(cache_page(60), name='dispatch')
class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailing/list.html'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset()

        if self.request.user.has_perm("mailing.can_view_all_mailings"):
            return qs

        return qs.filter(owner=self.request.user)


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)

        user = self.request.user

        # менеджер видит всё
        if user.has_perm("mailing.can_manage_mailings"):
            return form

        # обычный пользователь видит только свои данные
        form.fields['message'].queryset = form.fields['message'].queryset.filter(owner=user)
        form.fields['recipients'].queryset = form.fields['recipients'].queryset.filter(owner=user)

        return form

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)



class MailingUpdateView(LoginRequiredMixin, OwnerOrPermissionMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/form.html'
    success_url = reverse_lazy('mailing:mailing_list')
    required_permissions = ["mailing.can_view_all_mailings"]


class MailingDeleteView(LoginRequiredMixin, OwnerOrPermissionMixin, DeleteView):
    model = Mailing
    template_name = 'mailing/confirm_delete.html'
    success_url = reverse_lazy('mailing:mailing_list')
    required_permissions = ["mailing.can_view_all_mailings"]

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        MailingServices.update_mailing_status(obj)
        return obj


class MailingDetailView(LoginRequiredMixin, OwnerOrPermissionMixin, DetailView):
    model = Mailing
    template_name = 'mailing/detail.html'
    required_permissions = ["mailing.can_view_all_mailings"]

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

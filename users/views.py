from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from django.views.generic import DetailView, ListView, UpdateView
from django.views.generic.edit import CreateView

from mailing.models import Mailing

from .forms import CustomUserCreationForm, UserProfileForm
from .models import CustomUser


class BlockUserView(UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        user.is_active = False
        user.save()
        messages.success(request, f"Пользователь {user.email} заблокирован.")
        return redirect("users:user_list")


class UserListView(UserPassesTestMixin, ListView):
    model = CustomUser
    template_name = "users/user_list.html"
    context_object_name = "users"

    def test_func(self):
        return self.request.user.is_staff


class ActivateView(View):
    """
    Активирует аккаунт по uidb64 + token и (опционально) логинит пользователя.
    URL: /users/activate/<uidb64>/<token>/
    """
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            # логиним и редиректим (если хочешь — оставь без логина)
            login(request, user)
            return render(request, 'users/activate_done.html', {'user': user})
        else:
            return render(request, 'users/activate_invalid.html')


class RegisterView(CreateView):
    template_name = "users/register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("users:register_done")

    def form_valid(self, form):
        user: CustomUser = form.save(commit=False)
        user.is_active = False
        user.save()
        self.send_activation_email(user, self.request)
        return super().form_valid(form)

    def send_activation_email(self, user, request):
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        activation_path = reverse_lazy('users:activate', kwargs={'uidb64': uid, 'token': token})
        activation_link = request.build_absolute_uri(activation_path)

        subject = "Подтвердите ваш Email"
        message = (
            f"Здравствуйте!\n\n"
            f"Чтобы подтвердить регистрацию, перейдите по ссылке:\n\n{activation_link}\n\n"
            f"Если вы не регистрировались — проигнорируйте это письмо."
        )
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        recipient_list = [user.email]
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)


class RegisterDoneView(CreateView):
    template_name = "users/register_done.html"


class CustomLoginView(LoginView):
    template_name = "users/login.html"

    def form_valid(self, form):
        user = form.get_user()
        self.send_welcome_email(user.email)
        return super().form_valid(form)

    def send_welcome_email(self, email):
        subject = "Уведомление о входе"
        message = "Вы успешно вошли в систему. Если это были не вы — смените пароль."
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("mailing:index")


class ProfileView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = "users/profile.html"

    def get_object(self):
        return self.request.user


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UserProfileForm
    template_name = "users/profile_edit.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self):
        return self.request.user

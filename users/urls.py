from django.urls import path
from django.contrib.auth import views as auth_views
from .views import RegisterView, CustomLoginView, CustomLogoutView, RegisterDoneView, ActivateView, UserListView, \
    BlockUserView, DisableMailingView

app_name = 'users'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('register/done/', RegisterDoneView.as_view(template_name='users/register_done.html'), name='register_done'),
    path('activate/<uidb64>/<token>/', ActivateView.as_view(), name='activate'),

    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    # встроенные представления
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),

    path("users/", UserListView.as_view(), name="user_list"),
    path("users/block/<int:pk>/", BlockUserView.as_view(), name="block_user"),
    path("mailings/<int:pk>/disable/", DisableMailingView.as_view(), name="mailing_disable"),


]

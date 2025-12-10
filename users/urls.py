from django.urls import path

from .views import (ActivateView, BlockUserView, CustomLoginView,
                    CustomLogoutView, ProfileUpdateView,
                    ProfileView, RegisterDoneView, RegisterView, UserListView)

app_name = 'users'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('register/done/', RegisterDoneView.as_view(template_name='users/register_done.html'), name='register_done'),
    path('activate/<uidb64>/<token>/', ActivateView.as_view(), name='activate'),

    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/edit/", ProfileUpdateView.as_view(), name="profile_edit"),

    path("users/", UserListView.as_view(), name="user_list"),
    path("users/block/<int:pk>/", BlockUserView.as_view(), name="block_user"),
]

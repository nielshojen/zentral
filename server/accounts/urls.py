from django.urls import path

from . import views

app_name = "users"
urlpatterns = [
    path('', views.UsersView.as_view(),
         name="list"),
    path('nginx/auth_request/', views.NginxAuthRequestView.as_view(),
         name="nginx_auth_request"),
    path('invite/', views.InviteUserView.as_view(),
         name="invite"),
    path('create_service_account/', views.CreateServiceAccountView.as_view(),
         name="create_service_account"),
    path('<int:pk>/', views.UserView.as_view(),
         name="user"),
    path('<int:pk>/update/', views.UpdateUserView.as_view(),
         name="update"),
    path('<int:pk>/delete/', views.DeleteUserView.as_view(),
         name="delete"),
    path('<int:pk>/api_token/create/', views.CreateUserAPITokenView.as_view(),
         name="create_user_api_token"),
    path('<int:pk>/api_token/view/', views.UserAPITokenView.as_view(),
         name="user_api_token"),
    path('<int:pk>/api_token/delete/', views.DeleteUserAPITokenView.as_view(),
         name="delete_user_api_token"),
    path('verification_devices/', views.UserVerificationDevicesView.as_view(),
         name="verification_devices"),
    path('add_totp/', views.AddTOTPView.as_view(),
         name="add_totp"),
    path('totp/<int:pk>/delete/', views.DeleteTOTPView.as_view(),
         name="delete_totp"),
    path('u2f_devices/register/', views.RegisterU2FDeviceView.as_view(),
         name="register_u2f_device"),
    path('u2f_devices/<int:pk>/delete/', views.DeleteU2FDeviceView.as_view(),
         name="delete_u2f_device"),
]

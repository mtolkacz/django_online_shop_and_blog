from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [
    path('', login, name='login'),
    path('login', login, name='login'),
    path('profile', profile, name='profile'),
    path('profile/favorite/', favorite, name='favorite'),
    path('logout/', logout, name='logout'),
    path('successful/', successful_registration, name='successful_registration'),
    re_path('^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', activate,
            name='activate'),

    # Django contrib auth views
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='accounts/password_change.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name='password_change_done'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'),
         name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/reset_done.html'), name='password_reset_complete'),
]

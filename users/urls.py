from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from .views import *
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('login', login, name = 'login'),
    path('registration', registration, name = 'registration'),
    path('save-draft-job/', save_draft_job, name='save_draft_job'),
    path('forgot-password', forgot_password, name = 'forgot_password'),
    path('check-mobile/<str:mobile_no>', check_mobile, name='check-mobile'),
    path('check-email/<str:email>', check_email, name='check-email'),
    path('logout', logoutUser, name='logout'),
    path('resend-otp', resend_otp, name='resend-otp'),

    # social login urls
    path('oauth/', include('social_django.urls', namespace='social')),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

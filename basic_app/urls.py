from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from .views import *


urlpatterns = [
    path('basic', basic, name='basic'),
    path('get-pincode-details/<str:pincode>', getpincodedetails, name='getpincodedetails'),    
    path('newsletter', newsletter, name='newsletter'),
    path('add-inquiry', add_inquiry, name='add-inquiry'),
    path('add-review', add_review, name='add-review'),
    path('teacher-faqs', teacher_faq, name = 'teacher_faq'),
    path('institute-faqs', institute_faq, name = 'institute_faq'),
    path('error', error, name = 'error'),
    path('thankyou', thankyou, name = 'thankyou'),
    path('privacy-policy', privacy, name = 'privacy'),
    path('terms-condition', terms_condition, name = 'terms_condition'),
    path('refund-cancellation-policy', refund_cancellation_policy, name = 'refund-cancellation-policy'),
    path('blog-detail', blog_detail, name = 'blog_detail'),
    path('about', about, name = 'about'),
    path('team', team, name='team'),
    path('job-alerts', landing_page, name='landing_page'),
    path('summernote/', include('django_summernote.urls')),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

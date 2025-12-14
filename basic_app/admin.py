from django.contrib import admin
from .models import *
from django_summernote.admin import SummernoteModelAdmin

class NewsletterAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Newsletter._meta.fields]
    list_editable = []

admin.site.register(Newsletter, NewsletterAdmin)

class TestimonialsAdmin(SummernoteModelAdmin):
    list_display = ['id','name','image','rating','designation','sequences']
    list_editable = []
    summernote_fields = ["testimonial"]

admin.site.register(Testimonials, TestimonialsAdmin)

class FaqAdmin(admin.ModelAdmin):
    list_display = ["id","question"]
    list_editable = []
    
admin.site.register(Faq, FaqAdmin)

class InquiryAdmin(SummernoteModelAdmin):
    list_display = ["id","name","email","mobile_no"]
    list_editable = []
    summernote_fields = ["message"]

admin.site.register(Inquiry, InquiryAdmin)

class BannerAdmin(admin.ModelAdmin):
    list_display = ["id","image","title"]
    list_editable = []

admin.site.register(Banner, BannerAdmin)

class TeamAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Team._meta.fields]
    list_editable = []

admin.site.register(Team, TeamAdmin)

class BlogsAdmin(SummernoteModelAdmin):
    list_display = ("id","title","image","date","author","tag","location")
    list_editable = []
    summernote_fields = ["blog"]
    exclude = ["slug"]

admin.site.register(Blogs, BlogsAdmin)

class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id",'name','email','image','rating','date','is_verified')
    list_editable = ["is_verified"]

admin.site.register(Review, ReviewAdmin)

class TermsAndConditionsAdmin(SummernoteModelAdmin):
    list_display = ("title",)
    list_editable = []
    summernote_fields = ["terms"]

admin.site.register(TermsAndConditions, TermsAndConditionsAdmin)
class PrivacyPolicyAdmin(SummernoteModelAdmin):
    list_display = ("title",)
    list_editable = []
    summernote_fields = ["policy"]

admin.site.register(PrivacyPolicy, PrivacyPolicyAdmin)
class RefundCancellationPolicyAdmin(SummernoteModelAdmin):
    list_display = ("title",)
    list_editable = []
    summernote_fields = ["policy"]

admin.site.register(RefundCancellationPolicy, RefundCancellationPolicyAdmin)


from django.contrib import admin
from .models import *
from .models import (
    Teacher, School, PostJob, TeacherFormData, State, District,
    TeacherPlanAmenities, SchoolPlanAmenities, TeacherSubscriptionPlan,
    SchoolSubscriptionPlan, PaymentDetails, TeacherPaymentDetails,WalkinPlanAmenities,
    Grade, Subject, TeacherGrade, TeacherSubject, JobAlert,
    Subscription, TeacherSubscription, JobFormData, JobApplicant,
    TrustedBy, WhatsAppMessages, Labels, ShortlistedTeachers,
    FacultyMe_Permission, Statistics, HowItWorkTeacher, HowItWorkSchool,
    WalkInSubscriptionPlan, SchoolWalkinSubscription, SchoolWalkinPaymentDetails,
    Lead
)
from django_summernote.admin import SummernoteModelAdmin
from django_summernote.utils import get_attachment_model
from django.contrib.auth.models import Group
from import_export.admin import ImportExportModelAdmin

admin.site.unregister(get_attachment_model())
admin.site.unregister(Group)

class TeacherAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Teacher._meta.fields]
    list_editable = []
    search_fields = ('user__name', 'user__mobile_no', 'user__alt_mobile_no')

admin.site.register(Teacher, TeacherAdmin)

class SchoolAdmin(ImportExportModelAdmin):
    list_display = [f.name for f in School._meta.fields]
    list_editable = []

admin.site.register(School, SchoolAdmin)

class PostJobAdmin(admin.ModelAdmin):
    list_display = [f.name for f in PostJob._meta.fields]
    list_editable = []
    search_fields = [f.name for f in PostJob._meta.fields]

admin.site.register(PostJob, PostJobAdmin)

class WalkinJobAdmin(admin.ModelAdmin):
    list_display = [f.name for f in WalkinJob._meta.fields]
    list_editable = []
    search_fields = [f.name for f in WalkinJob._meta.fields]

admin.site.register(WalkinJob, WalkinJobAdmin)

class TeacherFormDataAdmin(admin.ModelAdmin):
    list_display = [f.name for f in TeacherFormData._meta.fields]
    list_editable = []
    search_fields = ('data_type', 'info')
    list_filter = ('data_type',)

admin.site.register(TeacherFormData, TeacherFormDataAdmin)

class StateAdmin(ImportExportModelAdmin):
    list_display = [f.name for f in State._meta.fields]
    list_editable = []

admin.site.register(State, StateAdmin)

class DistrictAdmin(ImportExportModelAdmin):
    list_display = [f.name for f in District._meta.fields]
    list_editable = []

admin.site.register(District, DistrictAdmin)

class TeacherPlanAmenitiesInline(admin.TabularInline):
    model = TeacherPlanAmenities
    extra = 0
    min_num = 1

class SchoolPlanAmenitiesInline(admin.TabularInline):
    model = SchoolPlanAmenities
    extra = 0
    min_num = 1

class WalkinPlanAmenitiesInline(admin.TabularInline):
    model = WalkinPlanAmenities 
    extra = 0
    min_num = 1
    
class TeacherSubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = [f.name for f in TeacherSubscriptionPlan._meta.fields]
    list_editable = []
    inlines = [TeacherPlanAmenitiesInline,]

admin.site.register(TeacherSubscriptionPlan, TeacherSubscriptionPlanAdmin)

class SchoolSubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = [f.name for f in SchoolSubscriptionPlan._meta.fields]
    list_editable = []
    inlines = [SchoolPlanAmenitiesInline,]

admin.site.register(SchoolSubscriptionPlan, SchoolSubscriptionPlanAdmin)

class WalkInSubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = [f.name for f in WalkInSubscriptionPlan._meta.fields]
    list_editable = ['is_active']
    search_fields = ['plan_name']

admin.site.register(WalkInSubscriptionPlan, WalkInSubscriptionPlanAdmin)

class SchoolWalkinSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['school', 'plan_name', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active', 'start_date', 'end_date']
    search_fields = ['school__name', 'plan_name']

admin.site.register(SchoolWalkinSubscription, SchoolWalkinSubscriptionAdmin)

class SchoolWalkinPaymentDetailsAdmin(admin.ModelAdmin):
    list_display = ['school', 'amount', 'payment_status', 'created_at']
    list_filter = ['payment_status', 'created_at']
    search_fields = ['school__name']

admin.site.register(SchoolWalkinPaymentDetails, SchoolWalkinPaymentDetailsAdmin)

class PaymentDetailsAdmin(admin.ModelAdmin):
    list_display = ["id", "razorpay_payment_id", "razorpay_order_id", "status", "plan", "subscription_plan", "user", "amount", "timestamp"]
    list_editable = []
    list_filter = ('timestamp',)  # Add date filter

admin.site.register(PaymentDetails, PaymentDetailsAdmin)

class TeacherPaymentDetailsAdmin(admin.ModelAdmin):
    list_display = ["id", "razorpay_payment_id", "razorpay_order_id", "status", "plan", "subscription_plan", "user", "amount", "timestamp"]
    list_editable = []
    list_filter = ('timestamp',)  # Add date filter

admin.site.register(TeacherPaymentDetails, TeacherPaymentDetailsAdmin)

class GradeAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Grade._meta.fields]
    list_editable = []

admin.site.register(Grade, GradeAdmin)

class SubjectAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Subject._meta.fields]
    list_editable = []

admin.site.register(Subject, SubjectAdmin)

class TeacherGradeAdmin(admin.ModelAdmin):
    list_display = [f.name for f in TeacherGrade._meta.fields]
    list_editable = []

admin.site.register(TeacherGrade, TeacherGradeAdmin)

class TeacherSubjectAdmin(admin.ModelAdmin):
    list_display = [f.name for f in TeacherSubject._meta.fields]
    list_editable = []

admin.site.register(TeacherSubject, TeacherSubjectAdmin)

class JobAlertAdmin(admin.ModelAdmin):
    list_display = [f.name for f in JobAlert._meta.fields]
    list_editable = []

admin.site.register(JobAlert, JobAlertAdmin)

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Subscription._meta.fields]
    list_editable = []

admin.site.register(Subscription, SubscriptionAdmin)

class TeacherSubscriptionAdmin(admin.ModelAdmin):
    list_display = [f.name for f in TeacherSubscription._meta.fields]
    list_editable = []

admin.site.register(TeacherSubscription, TeacherSubscriptionAdmin)

class JobFormDataAdmin(admin.ModelAdmin):
    list_display = [f.name for f in JobFormData._meta.fields]
    list_editable = []
    search_fields = ('data_type', 'info')
    list_filter = ('data_type',)

admin.site.register(JobFormData, JobFormDataAdmin)

class JobApplicantAdmin(admin.ModelAdmin):
    list_display = [f.name for f in JobApplicant._meta.fields]
    list_editable = []

admin.site.register(JobApplicant, JobApplicantAdmin)

class TrustedByAdmin(admin.ModelAdmin):
    list_display = [f.name for f in TrustedBy._meta.fields]
    list_editable = []

admin.site.register(TrustedBy, TrustedByAdmin)

class WhatsAppMessagesAdmin(ImportExportModelAdmin):
    list_display = [f.name for f in WhatsAppMessages._meta.fields]
    list_editable = []

admin.site.register(WhatsAppMessages, WhatsAppMessagesAdmin)

class LabelsAdmin(ImportExportModelAdmin):
    list_display = [f.name for f in Labels._meta.fields]
    list_editable = []

admin.site.register(Labels, LabelsAdmin)

class ShortlistedTeachersAdmin(ImportExportModelAdmin):
    list_display = [f.name for f in ShortlistedTeachers._meta.fields]
    list_editable = []

admin.site.register(ShortlistedTeachers, ShortlistedTeachersAdmin)

class FacultyMePermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'free_to_apply_job', 'free_to_post_job', 'timestamp')
    list_filter = ('free_to_apply_job', 'free_to_post_job', 'timestamp')  # Add timestamp filter
    search_fields = ('id',)

admin.site.register(FacultyMe_Permission, FacultyMePermissionAdmin)

class StatisticsAdmin(admin.ModelAdmin):
    list_display = ['name', 'value', 'is_active']  # Columns to display in the admin panel
    list_editable = ['value', 'is_active']  # Allow quick editing
    search_fields = ['name']  # Add a search bar for names
    list_filter = ['is_active']  # Add a filter for active/inactive status

admin.site.register(Statistics, StatisticsAdmin)

class HowItWorkTeacherAdmin(admin.ModelAdmin):
    list_display = ['step_no', 'value', 'is_active']  # Updated field name
    list_editable = ['value', 'is_active']
    search_fields = ['step_no']  # Updated field name
    list_filter = ['is_active']

admin.site.register(HowItWorkTeacher, HowItWorkTeacherAdmin)

class HowItWorkSchoolAdmin(admin.ModelAdmin):
    list_display = ['step_no', 'value', 'is_active']  # Updated field name
    list_editable = ['value', 'is_active']
    search_fields = ['step_no']  # Updated field name
    list_filter = ['is_active']

admin.site.register(HowItWorkSchool, HowItWorkSchoolAdmin)


class LeadAdmin(admin.ModelAdmin):
    list_display = ["name", "whatsapp", "grades", "subjects", "location", "created_at"]
    list_filter = ["grades", "subjects", "location", "created_at"]
    search_fields = ["name", "whatsapp", "grades", "subjects", "location"]
    ordering = ("-created_at",)
    
admin.site.register(Lead, LeadAdmin)

from django.db import models
from users.models import *
from django.utils.text import slugify 
from PIL import Image
from io import BytesIO
from django.core.files import File
from datetime import timedelta
from django.utils import timezone

def in_fifteen_days():
    return timezone.now() + timedelta(days=15)

def in_seven_days():
    return timezone.now() + timedelta(days=7)

def in_thirty_days():
    return timezone.now() + timedelta(days=30)

teacher_status = (
    ('New', 'New'),
    ('Approved', 'Approved'),
    ('Expired', 'Expired'),
    ('Disabled', 'Disabled'),
    )

class Teacher(models.Model):

    user = models.ForeignKey(NewUser, on_delete=models.SET_NULL, unique=True, null=True, blank=True)
    gender = models.CharField(max_length=15,default=None,blank=True,null=True)
    qualification = models.CharField(max_length=100,default=None,blank=True,null=True)
    dob = models.CharField(max_length=50,default=None,blank=True,null=True)
    subject_of_specialization = models.CharField(max_length=100,default=None,blank=True,null=True)
    experience_type = models.CharField(max_length=20,default=None,blank=True,null=True)
    experience_in = models.CharField(max_length=100,default=None,blank=True,null=True)
    subject_of_experience = models.CharField(max_length=100,default=None,blank=True,null=True)
    years_of_experience = models.CharField(max_length=100,default=None,blank=True,null=True)
    current_salary = models.CharField(max_length=50,default=None,blank=True,null=True)
    want_to_teach_for = models.CharField(max_length=100,default=None,blank=True,null=True,verbose_name='I want to teach for(Fresher)')
    subject_i_teach = models.CharField(max_length=100,default=None,blank=True,null=True,verbose_name='Subject i can teach(Fresher)')
    expected_salary = models.CharField(max_length=50,default=None,blank=True,null=True)
    preferred_location_state = models.CharField(max_length=50,default=None,blank=True,null=True)
    preferred_location_district = models.TextField(default=None,blank=True,null=True)
    address_pincode = models.CharField(max_length=6,default=None,blank=True,null=True)
    address_state = models.CharField(max_length=50,default=None,blank=True,null=True)
    address_district = models.CharField(max_length=50,default=None,blank=True,null=True)
    address = models.CharField(max_length=200,default=None,blank=True,null=True)
    status = models.CharField(max_length=50,choices=teacher_status, default='New')
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    plan = models.CharField(max_length=50, default='Basic')
    label = models.CharField(max_length=100,default=None,blank=True,null=True)
    payment_status = models.CharField(max_length=50, default='Unpaid')
    payment_status = models.CharField(max_length=50, default='Unpaid')

    def __str__(self):
        return str(self.id)
    class Meta:
        verbose_name_plural = "Teachers"

school_status = (
    ('New', 'New'),
    ('Approved', 'Approved'),
    ('Disabled', 'Disabled'),
    )
class School(models.Model):

    user = models.ForeignKey(NewUser, on_delete=models.SET_NULL, unique=True, null=True, blank=True)
    school_name = models.CharField(max_length=200,default=None,blank=True,null=True)
    school_email = models.CharField(max_length=50,default=None,blank=True,null=True)
    website = models.CharField(max_length=255,default=None,blank=True,null=True)
    institute_type = models.CharField(max_length=150,default=None,blank=True,null=True)
    contact_person_name = models.CharField(max_length=50,default=None,blank=True,null=True)
    contact_person_designation = models.CharField(max_length=50,default=None,blank=True,null=True)
    pincode = models.CharField(max_length=6,default=None,blank=True,null=True)
    state = models.CharField(max_length=50,default=None,blank=True,null=True)
    district = models.CharField(max_length=200,default=None,blank=True,null=True)
    address = models.CharField(max_length=200,default=None,blank=True,null=True)
    primary_mobile = models.CharField(max_length=50,default=None,blank=True,null=True)
    secondary_mobile = models.CharField(max_length=50,default=None,blank=True,null=True)
    status = models.CharField(max_length=50,choices=school_status, default='New')
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    plan = models.CharField(max_length=50, default='Basic')
    label = models.CharField(max_length=100,default=None,blank=True,null=True)
    payment_status = models.CharField(max_length=50, default='Unpaid')

    class Meta:
        verbose_name_plural = "Schools"


teacher_data_choices = (
    ('Experienced in', 'Experienced in'),
    ('Subject of Experience', 'Subject of Experience'),
    ('Years of experience', 'Years of experience'),
    ('Current Salary', 'Current Salary'),
    ('I want to teach for', 'I want to teach for'),
    ('Subject i can teach', 'Subject i can teach'),
    ('Expected Salary', 'Expected Salary'),
    ('Experience Type', 'Experience Type'),
    ('Qualification', 'Qualification'),
    ('Subject Specialzation', 'Subject Specialzation')
    )
class TeacherFormData(models.Model):

    data_type = models.CharField(max_length=200,choices=teacher_data_choices, default=None, blank=True,null=True)
    info = models.CharField(max_length=200,default=None,blank=True,null=True)

    def __str__(self):
        return self.data_type
        
    class Meta:
        verbose_name_plural = "Teacher Form Data"

class Statistics(models.Model):
    name = models.CharField(max_length=255, unique=True,default=None)  # e.g., "Total Users", "Active Plans"
    value = models.TextField(default=None)  # The  value of the statistic
    description = models.TextField(blank=True, null=True,default=None)  # Optional description
    is_active = models.BooleanField(default=True)  # To control visibility on the frontend

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "FacultyMe Statistics"

class HowItWorkTeacher(models.Model):
    step_no = models.IntegerField()  # Step title
    value = models.TextField(blank=True, null=True,default=None)  # Step number or identifier
    is_active = models.BooleanField(default=True)  # To control visibility on the frontend

    def __str__(self):
        return str(self.step_no)

    class Meta:
        verbose_name_plural = "How It Works for Teacher"


class HowItWorkSchool(models.Model):
    step_no = models.IntegerField()  # Step title
    value = models.TextField(default=None,blank=True, null=True)  # Step number or identifier
    is_active = models.BooleanField(default=True)  # To control visibility on the frontend

    def __str__(self):
        return str(self.step_no)

    class Meta:
        verbose_name_plural = "How It Works for School"


class TeacherFormExperiencedIn(models.Model):

    info = models.CharField(max_length=200,default=None,blank=True,null=True)

    def __str__(self):
        return self.info
        
    class Meta:
        verbose_name_plural = "Teacher Form Data - Experienced In"

class State(models.Model):

    name = models.CharField(max_length=50,default=None,blank=True,null=True)

    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name_plural = "State"

class District(models.Model):

    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True,blank=True)
    name = models.CharField(max_length=50,default=None,blank=True,null=True)

    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name_plural = "District"

class TeacherGrade(models.Model):

    name = models.CharField(max_length=50,default=None,blank=True,null=True)

    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name_plural = "Teacher Grade"

class TeacherSubject(models.Model):

    grade = models.ForeignKey(TeacherGrade, on_delete=models.SET_NULL, null=True,blank=True)
    name = models.CharField(max_length=50,default=None,blank=True,null=True)

    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name_plural = "Teacher Subject"


class Grade(models.Model):

    name = models.CharField(max_length=50,default=None,blank=True,null=True)
    ishidden = models.BooleanField(default=False)

    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name_plural = "Grade"

class Subject(models.Model):

    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True,blank=True)
    name = models.CharField(max_length=50,default=None,blank=True,null=True)

    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name_plural = "Subject"

class TeacherSubscriptionPlan(models.Model):

    plan_name = models.CharField(max_length=200,default=None,blank=True,null=True)
    display_price = models.DecimalField(max_digits=10, decimal_places=0, default=0,null=True,blank=True)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=0, default=0,null=True,blank=True)
    allow_number_of_job_apply = models.PositiveIntegerField(default=0, null=True, blank=True)
    is_acitve=models.BooleanField(default=False)
    display_sequence=models.IntegerField(default=1, null=True, blank=True)
    def __str__(self):
        return self.plan_name

    class Meta:
        verbose_name_plural = "Teacher Subscription Plans"

class TeacherPlanAmenities(models.Model):
    
    plan = models.ForeignKey(TeacherSubscriptionPlan, on_delete=models.SET_NULL, null=True,blank=True)
    info = models.CharField(max_length=200,default=None,blank=True,null=True)

    def __str__(self):
        return self.plan.plan_name
        
    class Meta:
        verbose_name_plural = "Teacher Plan Amenities"

class SchoolSubscriptionPlan(models.Model):

    plan_name = models.CharField(max_length=200,default=None,blank=True,null=True)
    display_price = models.DecimalField(max_digits=10, decimal_places=0, default=0,null=True,blank=True)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=0, default=0,null=True,blank=True)
    allow_number_of_job_post = models.PositiveIntegerField(default=0, null=True, blank=True)
    is_acitve=models.BooleanField(default=False)
    display_sequence=models.IntegerField(default=1, null=True, blank=True)

    def __str__(self):
        return self.plan_name

    class Meta:
        verbose_name_plural = "School Subscription Plans"

class SchoolPlanAmenities(models.Model):
    
    plan = models.ForeignKey(SchoolSubscriptionPlan, on_delete=models.SET_NULL, null=True,blank=True)
    info = models.CharField(max_length=200,default=None,blank=True,null=True)

    def __str__(self):
        return self.plan.plan_name
        
    class Meta:
        verbose_name_plural = "School Plan Amenities"

class WalkInSubscriptionPlan(models.Model):
    id = models.AutoField(primary_key=True)
    plan_name = models.CharField(max_length=100)
    plan_description = models.TextField(null=True, blank=True)
    price = models.IntegerField()
    duration_days = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.plan_name

    class Meta:
        db_table = 'cog_static_app_walkin_subscription_plan'
        verbose_name_plural = "Walk-in Subscription Plans"

class WalkinPlanAmenities(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255) 
    info = models.TextField()  

    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name_plural = "Walkin Plan Amenities"
        db_table = 'cog_static_app_walkinplanamenities'
        
class SchoolWalkinSubscription(models.Model):
    school = models.ForeignKey(NewUser, on_delete=models.CASCADE)
    plan_name = models.CharField(max_length=100)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=lambda: timezone.now() + timedelta(days=30))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    subscription_plan = models.ForeignKey(WalkInSubscriptionPlan, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.school.name} - {self.plan_name}"

    class Meta:
        #verbose_name_plural = "School Walk-in Subscriptions"
        db_table = 'cog_static_app_school_walkin_subscription'

class SchoolWalkinPaymentDetails(models.Model):
    school = models.ForeignKey(NewUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    order_id = models.CharField(max_length=100, null=True, blank=True)
    payment_status = models.CharField(max_length=20, default='pending')
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    data = models.TextField(blank=True, null=True)
    subscription_plan = models.ForeignKey(WalkInSubscriptionPlan, on_delete=models.CASCADE, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length= 55 , default=" ", null=True, blank=True)
    razorpay_order_id = models.CharField(max_length=55 , default=" ", null=True,blank=True)

    def __str__(self):
        return f"{self.school.name} - {self.amount}"

    class Meta:
        #verbose_name_plural = "School Walk-in Payment Details"
        db_table='cog_static_app_school_walkin_payment_details'

class PaymentDetails(models.Model):

    razorpay_payment_id = models.CharField(max_length= 55 , default=" ", null=True, blank=True)
    razorpay_order_id = models.CharField(max_length=55 , default=" ", null=True,blank=True)
    status = models.CharField(max_length=55, default=" ",null=True, blank=True )
    plan = models.CharField(max_length=200,null=True, blank=True)
    subscription_plan = models.ForeignKey(SchoolSubscriptionPlan, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(NewUser, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.IntegerField(null=True,blank=True)
    data = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)
	
    class Meta:
        verbose_name_plural = "School Payment Details"

class Subscription(models.Model):

    user = models.ForeignKey(NewUser, on_delete=models.SET_NULL, null=True, blank=True)
    plan = models.CharField(max_length=200,null=True, blank=True)
    subscription_plan = models.ForeignKey(SchoolSubscriptionPlan, on_delete=models.CASCADE, null=True, blank=True)
    remaining_job_post = models.PositiveIntegerField(default=0)
    date = models.DateField(auto_now_add=True,null=True, blank=True)
    # expiration_date = models.DateTimeField()
    def __str__(self):
        return self.user.name
    def is_subscription_valid(self):
        """
        Check if the subscription is still valid for job application.
        """
        if self.subscription_plan:
            # Check if the remaining job apply count is greater than zero
            return self.remaining_job_post > 0
        return False
    class Meta:
        verbose_name_plural = "School Subscriptions"
class TeacherPaymentDetails(models.Model):

    razorpay_payment_id = models.CharField(max_length= 55 , default=" ", null=True, blank=True)
    razorpay_order_id = models.CharField(max_length=55 , default=" ", null=True,blank=True)
    status = models.CharField(max_length=55, default=" ",null=True, blank=True )
    plan = models.CharField(max_length=200,null=True, blank=True)
    subscription_plan = models.ForeignKey(TeacherSubscriptionPlan, on_delete=models.CASCADE)
    user = models.ForeignKey(NewUser, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.IntegerField(null=True,blank=True)
    data = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)
	
    class Meta:
        verbose_name_plural = "Teacher Payment Details"

class TeacherSubscription(models.Model):

    user = models.ForeignKey(NewUser, on_delete=models.SET_NULL, null=True, blank=True)
    plan = models.CharField(max_length=200,null=True, blank=True)
    subscription_plan = models.ForeignKey(TeacherSubscriptionPlan, on_delete=models.CASCADE)
    remaining_job_apply = models.PositiveIntegerField(default=0)
    date = models.DateField(auto_now_add=True,null=True, blank=True)
    # expiration_date = models.DateTimeField()
    def __str__(self):
        return self.user.name
    def is_subscription_valid(self):
        """
        Check if the subscription is still valid for job application.
        """
        if self.subscription_plan:
            # Check if the remaining job apply count is greater than zero
            return self.remaining_job_apply> 0
        return False
    class Meta:
        verbose_name_plural = "Teacher Subscriptions"
job_status = (
    ('New', 'New'),
    ('Approved', 'Approved'),
    ('ReApproval', 'ReApproval'),
    ('Expired', 'Expired'),
    ('Disabled', 'Disabled'),
    )
class PostJob(models.Model):

    user = models.ForeignKey(NewUser, on_delete=models.SET_NULL, null=True, blank=True)
    job_code = models.CharField(max_length=50,default=None,blank=True,null=True)
    teacher_grade = models.CharField(max_length=50,default=None,blank=True,null=True)
    subject = models.CharField(max_length=50,default=None,blank=True,null=True)
    highest_qualification = models.CharField(max_length=100,default=None,blank=True,null=True)
    experienced_required = models.CharField(max_length=100,default=None,blank=True,null=True)
    salary_offered = models.CharField(max_length=50,default=None,blank=True,null=True)
    joining_date = models.DateField(blank=True,null=True)
    expiry_date = models.DateField(blank=True,null=True)
    joining = models.TextField(default=None,blank=True,null=True)
    benifits_compensation = models.TextField(default=None,blank=True,null=True)
    pincode = models.CharField(max_length=6,default=None,blank=True,null=True)
    state = models.CharField(max_length=50,default=None,blank=True,null=True)
    district = models.CharField(max_length=50,default=None,blank=True,null=True)
    address = models.CharField(max_length=200,default=None,blank=True,null=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    status = models.CharField(max_length=50,choices=job_status, default='New')
    promo_applied = models.BooleanField(default=False)
    free_to_apply=models.BooleanField(default=False)
    description=models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.id)
        
    class Meta:
        verbose_name_plural = "Post a Job"


job_data_choices = (
    ('Teacher Grade', 'Teacher Grade'),
    ('Subject', 'Subject'),
    ('Highest Qualification', 'Highest Qualification'),
    ('Experience Required', 'Experience Required'),
    ('Salary offered', 'Salary offered'),
    ('Benefits & compensation', 'Benefits & compensation')
    )

class WalkinJob(models.Model):
    user = models.CharField(max_length=255)
    teacher_grade = models.CharField(max_length=1000, blank=True, null=True)
    subject = models.CharField(max_length=3000, blank=True, null=True)
    contact_name = models.CharField(max_length=100, blank=True, null=True)
    contact_designation = models.CharField(max_length=100, blank=True, null=True)
    contact_mobile = models.CharField(max_length=100, blank=True, null=True)
    alternative_mobile = models.CharField(max_length=100, blank=True, null=True)

    salary_range = models.CharField(max_length=50, blank=True, null=True)
    walkin_date = models.DateField(blank=True, null=True)
    payment_pricing = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    status = models.CharField(max_length=50, choices=job_status, default='New')
    promo_applied = models.BooleanField(default=False)
    free_to_apply = models.BooleanField(default=False)
    job_code = models.CharField(max_length=50, default=None, blank=True, null=True)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        import datetime
        
        # Validate walkin date is at least 6 days after current date
        if self.walkin_date:
            min_date = datetime.date.today() + datetime.timedelta(days=6)
            if self.walkin_date < min_date:
                raise ValidationError({'walkin_date': 'Walk-in date must be at least 6 days after the current date.'})
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return str(self.id)
        
    class Meta:
        db_table = 'cog_static_app_walkin_job'

        
class JobFormData(models.Model):

    data_type = models.CharField(max_length=200,choices=job_data_choices, default=None, blank=True,null=True)
    info = models.CharField(max_length=200,default=None,blank=True,null=True)

    def __str__(self):
        return self.data_type
        
    class Meta:
        verbose_name_plural = "Job Form Data"

class JobAlert(models.Model):

    name = models.CharField(max_length=55, default=None, blank=True,null=True)
    mobile_no = models.CharField(max_length=55,default=None,blank=True,null=True)
    alternative_mobile_no = models.CharField(max_length=55,default=None,blank=True,null=True)
    job_category = models.CharField(max_length=55,default=None,blank=True,null=True)
    subject = models.CharField(max_length=110,default=None,blank=True,null=True)
    prefered_location = models.TextField()
    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name_plural = "Job Alert"

job_app_status = (
    ('New', 'New'),
    ('Approved', 'Approved'),
    ('Applied', 'Applied'),
    ('In Review', 'In Review'),
    ('Interview Call Request', 'Interview Call Request'),
    ('Interview Call', 'Interview Call'),
    ('Interview Done', 'Interview Done'),
    ('Rejected', 'Rejected'),
    )
class JobApplicant(models.Model):
    
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True,blank=True)
    job = models.ForeignKey(PostJob, on_delete=models.SET_NULL, null=True,blank=True)
    walkin_job = models.ForeignKey(WalkinJob, on_delete=models.SET_NULL, null=True, blank=True)
    interview_date = models.DateField(null=True, blank=True)
    interview_time = models.TimeField(null=True, blank=True)
    contact_person = models.CharField(max_length=100,null=True, blank=True)
    contact_person_mobile = models.CharField(max_length=110,null=True, blank=True)
    status = models.CharField(max_length=50,choices=job_app_status, default='New')
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Job Applicants"

    @property
    def job_instance(self):
        if self.job is not None:
            return self.job
        elif self.walkin_job is not None:
            return self.walkin_job
        else:
            return None

class TrustedBy(models.Model):

    image = models.ImageField(null=True, blank=False)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = "Trusted By"


class WhatsAppMessages(models.Model):

    mobile_no = models.CharField(max_length=20,blank=True,null=True)
    msg = models.TextField(null=False,blank=False)    
    status = models.CharField(max_length=20,blank=True,null=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.mobile_no

    class Meta:
        verbose_name_plural = "WhatsApp Messages History"

class Labels(models.Model):
  
    name = models.CharField(max_length=100,blank=True,null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Labels"

class JobPromotions(models.Model):

    user = models.ForeignKey(NewUser, on_delete=models.SET_NULL, null=True,blank=True)
    job = models.ForeignKey(PostJob, on_delete=models.SET_NULL, null=True,blank=True)
    start_date = models.DateField(default=None,blank=True,null=True)
    end_date = models.DateField(default=None,blank=True,null=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    def __str__(self):
        return str(self.job.job_code)
        
    class Meta:
        verbose_name_plural = "Job Promotions"

class ShortlistedTeachers(models.Model):

    teacher = models.IntegerField(blank=True,null=True)
    school = models.IntegerField(blank=True,null=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_review=models.BooleanField(default=False)
    def __str__(self):
        return str(self.teacher)
        
    class Meta:
        verbose_name_plural = "Short Listed Teachers"


class WelcomeMessageControl(models.Model):
    is_welcome_message_enabled = models.BooleanField(default=False)


class DailyVisitorCount(models.Model):
    date=models.DateField()
    user = models.ForeignKey(NewUser, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    count=models.PositiveIntegerField(default=0)


class FacultyMe_Permission(models.Model):
    free_to_apply_job=models.BooleanField(default=False)
    free_to_post_job=models.BooleanField(default=False)
    offer_time = models.TimeField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    class Meta:
        verbose_name_plural = "FacultyMe Permission"


class Lead(models.Model):
    name = models.CharField(max_length=150)
    whatsapp = models.CharField(max_length=15)
    grades = models.CharField(max_length=100)
    subjects = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

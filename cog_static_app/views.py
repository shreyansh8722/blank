from django.shortcuts import redirect, render, reverse
from django.core.paginator import Paginator
from types import SimpleNamespace
from django.shortcuts import render, redirect
from django.db.models import Q, Count
import csv
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from .models import Teacher, Labels, TeacherFormData, TeacherGrade, TeacherSubject, State, District, PostJob
from django.contrib.auth.decorators import login_required
from .models import Teacher, Labels, TeacherFormData, TeacherGrade, TeacherSubject, State, District, PostJob
import os
from django.contrib import messages
from .models import *
from basic_app.models import *
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import razorpay
from django.views.decorators.csrf import csrf_exempt
import num2words
from datetime import datetime, timedelta
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Q
from .models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
import requests
import json
from django.http import HttpResponseRedirect
from msg91 import send_sms_via_msg91, PIN_TEMPLATE_ID, REG_TEMPLATE_ID
from django.db.models import Q, Sum, Count
from django.contrib.auth.hashers import make_password
import csv
from django.contrib.admin.models import LogEntry
from urllib3.exceptions import InsecureRequestWarning
import random,string
from django.core import serializers
from django.http import HttpResponse
from requests.exceptions import RequestException
from background_task import background
from django.shortcuts import render
from django.utils.timezone import now
from django.shortcuts import render
from django.utils.timezone import now
from .models import *
from datetime import datetime,date, time
from django.utils import timezone

from django.shortcuts import render
from django.utils import timezone
from .models import JobApplicant, Teacher  # Import other models as needed
from django.core import serializers
from django.db.models import F, ExpressionWrapper, DateTimeField


def count_records_on_date(request):
    page_title = "Count Records on Date"
    selected_date = request.GET.get('date')
    
    job_applications_count = 0
    teachers_count = 0

    try:
        if selected_date:
            # Filter the records by the selected date
            job_applications_count = JobApplicant.objects.filter(timestamp__date=selected_date).count()
            teachers_count = Teacher.objects.filter(timestamp__date=selected_date).count()  # Assuming `timestamp` exists in Teacher model
        else:
            raise ValueError("No date provided")
    except Exception as e:
        # Handle the exception and log the error message
        print(f"Error occurred: {e}")
        messages.error(request, "An error occurred while counting records. Please try again.")

    context = {
        'page_title': page_title,
        'job_applications_count': job_applications_count,
        'teachers_count': teachers_count,
        'selected_date': selected_date,
    }
    return render(request, 'admin-dashboard/count_records_on_date.html', context)
    
def custom_whatsapp_form(request):
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

    # Retrieve job ID and teachers list from request
    job_id = request.POST.get('job_id')
    teachers = request.GET.get('teachers')

    if not job_id or not teachers:
        return JsonResponse({'error': 'Missing job_id or teachers parameter'}, status=400)

    teachers_array = teachers.split(",")
    try:
        job = PostJob.objects.get(pk=int(job_id))
        job_code = job.job_code
        location = f"{job.district}, {job.state}"
    except PostJob.DoesNotExist:
        try:
            job = WalkinJob.objects.get(pk=int(job_id))
            job_code = job.job_code
            new_user = NewUser.objects.filter(mobile_no=job.user).first()
            school = School.objects.filter(user_id=new_user).first()
            location = f"{school.district}, {school.state}"
        except WalkinJob.DoesNotExist:
               return JsonResponse({'error': 'Invalid job_id'}, status=404)
        
    # New API details
    api_url = "https://waba.wapionline.com/api/be6a71dc-8c39-4dc7-bb3c-69c3f76bf4eb/contact/send-template-message?token=QRj3nWECCsifuqnEyTtHRldRP6iQKSicoosF6TVRvZgbj01qkRyptnxeeq58qw8Y"
    template_name = "new_job_alert_for_teacher"
    template_language = "en"

    for teacher_id in teachers_array:
        try:
            teacher = Teacher.objects.get(id=teacher_id)
            whatsapp_no = teacher.user.mobile_no
            teacher_name = teacher.user.name

            if not whatsapp_no:
                continue

            # Prepare the payload for the new API
            payload = {
                "from_phone_number_id":"579680011898278", # 9663384666
                "phone_number": f"91{whatsapp_no}",  # Add country code prefix
                "template_name": template_name,  # Template for job alert
                "template_language": template_language,  # Language of the template
                "field_1": teacher_name,  # Teacher's name
                "field_2":job.subject,  # Job details link
                "field_3": location,  # Job location
                "button_0":job_code
            }

            headers = {
                "Content-Type": "application/json"
            }

            # Send POST request
            response = requests.post(api_url, headers=headers, data=json.dumps(payload))

            # Determine message status
            msg_status = 'Success' if response.status_code == 200 else f'Failed ({response.status_code})'

            # Log message and status
            WhatsAppMessages.objects.create(mobile_no=whatsapp_no, msg=json.dumps(payload), status=msg_status)

        except Teacher.DoesNotExist:
            print(f"Teacher with ID {teacher_id} does not exist")
            continue
        except RequestException as e:
            print(f"Request error: {e}")
        except Exception as e:
            print(f"General error: {e}")

    return JsonResponse(True, safe=False)

def custom_whatsapp_form_job_alert(request):
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

    # Retrieve job ID and teachers list from request
    job_id = request.POST.get('job_id')
    teachers = request.GET.get('teachers')

    if not job_id or not teachers:
        return JsonResponse({'error': 'Missing job_id or teachers parameter'}, status=400)

    teachers_array = teachers.split(",")
    try:
        job = PostJob.objects.get(pk=int(job_id))
        job_code = job.job_code
        location = f"{job.district}, {job.state}"
    except PostJob.DoesNotExist:
        try:
            job = WalkinJob.objects.get(pk=int(job_id))
            job_code = job.job_code
            new_user = NewUser.objects.filter(mobile_no=job.user).first()
            school = School.objects.filter(user_id=new_user).first()
            location = f"{school.district}, {school.state}"
        except WalkinJob.DoesNotExist:
               return JsonResponse({'error': 'Invalid job_id'}, status=404)
        

    # New API details
    api_url = "https://waba.wapionline.com/api/be6a71dc-8c39-4dc7-bb3c-69c3f76bf4eb/contact/send-template-message?token=QRj3nWECCsifuqnEyTtHRldRP6iQKSicoosF6TVRvZgbj01qkRyptnxeeq58qw8Y"
    template_name = "new_job_alert_for_teacher"
    template_language = "en"

    for teacher_id in teachers_array:
        try:
            res = JobAlert.objects.get(id=teacher_id)
            whatsapp_no = res.mobile_no
            teacher_name = res.name

            if not whatsapp_no:
                continue

            # Prepare the payload for the new API
            payload = {
                "from_phone_number_id":"579680011898278", # 9663384666
                "phone_number": f"91{whatsapp_no}",  # Add country code prefix
                "template_name": template_name,  # Template for job alert
                "template_language": template_language,  # Language of the template
                "field_1": teacher_name,  # Teacher's name
                "field_2":job.subject,
                "field_3": location,  # Job location
                "button_0":job_code
            }

            headers = {
                "Content-Type": "application/json"
            }

            # Send POST request
            response = requests.post(api_url, headers=headers, data=json.dumps(payload))

            # Determine message status
            msg_status = 'Success' if response.status_code == 200 else f'Failed ({response.status_code})'

            # Log message and status
            WhatsAppMessages.objects.create(mobile_no=whatsapp_no, msg=json.dumps(payload), status=msg_status)

        except JobAlert.DoesNotExist:
            print(f"Teacher with ID {teacher_id} does not exist")
            continue
        except RequestException as e:
            print(f"Request error: {e}")
        except Exception as e:
            print(f"General error: {e}")

    return JsonResponse(True, safe=False)

def send_whatsapp_cfi(whatsapp_no, job_code, school_name, interview_date, interview_time, contact_person, contact_person_contact, teacher_name):
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

    # Ensure mobile number is provided
    if not whatsapp_no:
        return JsonResponse({'error': 'Missing mobile number'}, status=400)

    # New API URL
    api_url = "https://waba.wapionline.com/api/be6a71dc-8c39-4dc7-bb3c-69c3f76bf4eb/contact/send-template-message?token=QRj3nWECCsifuqnEyTtHRldRP6iQKSicoosF6TVRvZgbj01qkRyptnxeeq58qw8Y"
    
    # Prepare request payload
    payload = {
        "phone_number": f"91{whatsapp_no}",  # Mobile number with country code
        "template_name": "interview_schedule_facultyme",  # Adjust template name as per the configuration
        "template_language": "en",  # Language of the template
        "field_1": teacher_name,  # Placeholder for teacher's name
        "field_2": school_name,  # Placeholder for school name
        "field_3": job_code,  # Placeholder for job code
        "field_4": interview_date,  # Placeholder for interview date
        "field_5": interview_time,  # Placeholder for interview time
        "field_6": contact_person,  # Placeholder for contact person name
        "field_7": contact_person_contact  # Placeholder for contact person's contact
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        # Send POST request
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))

        # Determine message status
        msg_status = 'Success' if response.status_code == 200 else f'Failed ({response.status_code})'

        # Log the message and status
        WhatsAppMessages.objects.create(mobile_no=whatsapp_no, msg=json.dumps(payload), status=msg_status)

        return JsonResponse({"status": msg_status}, safe=False)

    except RequestException as e:
        print(f"Request error: {e}")
        return JsonResponse({'error': 'Request failed'}, status=500)
    except Exception as e:
        print(f"General error: {e}")
        return JsonResponse({'error': 'An error occurred'}, status=500)

def send_whatsapp_school_welcome(request, whatsapp_no=None, name=None):
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

    # Retrieve mobile number and name if not provided
    if not (whatsapp_no and name):
        whatsapp_no = request.GET.get('mobile_no')
        name = request.GET.get('name')
    
    if not whatsapp_no or not name:
        return JsonResponse({'error': 'Missing mobile number or name'}, status=400)

    # New API URL and template details
    api_url = "https://waba.wapionline.com/api/be6a71dc-8c39-4dc7-bb3c-69c3f76bf4eb/contact/send-template-message?token=QRj3nWECCsifuqnEyTtHRldRP6iQKSicoosF6TVRvZgbj01qkRyptnxeeq58qw8Y"
    template_name = "welcome_school"  # Adjust based on your configuration
    template_language = "en"

    # Prepare the request payload for the new API
    payload = {
        "phone_number": f"91{whatsapp_no}",  # Mobile number with country code
        "template_name": template_name,  # Name of the message template
        "template_language": template_language,  # Language of the template
        "field_1": name  # Placeholder for the school contact person's name
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        # Send the POST request to the new API
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        print(response.status_code)

        msg_status = "Success" if response.status_code == 200 else f"Failed ({response.status_code})"

        # Log the message and status in the database
        WhatsAppMessages.objects.create(mobile_no=whatsapp_no, msg=json.dumps(payload), status=msg_status)

        return JsonResponse({"status": msg_status}, safe=False)

    except RequestException as e:
        print(f"Request error: {e}")
        return JsonResponse({"error": "An error occurred"}, status=500)
    except Exception as e:
        print(f"General error: {e}")
        return JsonResponse({"error": "An error occurred"}, status=500)


def send_whatsapp_teacher_welcome(request, whatsapp_no=None, name=None):
    # Retrieve mobile number and name if not provided
    if not (whatsapp_no and name):
        whatsapp_no = request.GET.get('mobile_no')
        name = request.GET.get('name')
    
    if not whatsapp_no or not name:
        return JsonResponse({'error': 'Missing mobile number or name'}, status=400)

    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

    # New API URL and template details
    api_url = "https://waba.wapionline.com/api/be6a71dc-8c39-4dc7-bb3c-69c3f76bf4eb/contact/send-template-message?token=QRj3nWECCsifuqnEyTtHRldRP6iQKSicoosF6TVRvZgbj01qkRyptnxeeq58qw8Y"
    template_name = "account_createsas_teacher"  # Adjust based on your configuration
    template_language = "en"
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")  # Format: 2025-04-27
    current_time = now.strftime("%H:%M:%S")  # Format: 14:23:45


    # Prepare the request payload
    payload = {
        "phone_number": f"91{whatsapp_no}",  # Mobile number with country code
        "template_name": template_name,  # Template for teacher welcome message
        "template_language": template_language,  # Language of the template
        "header_field_1":name,
        "field_1": name,  # Placeholder for teacher's name
        "field_2": current_date,
        "field_3": current_time
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        # Send the POST request to the new API
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        
        # Check response status
        msg_status = 'Success' if response.status_code == 200 else f'Failed ({response.status_code})'

        # Log the message and status in the database
        WhatsAppMessages.objects.create(mobile_no=whatsapp_no, msg=json.dumps(payload), status=msg_status)

        return JsonResponse({"status": msg_status}, safe=False)

    except RequestException as e:
        print(f"Request error: {e}")
        return JsonResponse({'error': 'Request failed'}, status=500)
    except Exception as e:
        print(f"General error: {e}")
        return JsonResponse({'error': 'An error occurred'}, status=500)

def send_whatsapp_school(request):
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
    whatsapp_no = request.GET.get('mobile_no')
    for_ts = request.GET.get('for')  # Role: 'school' or 'teacher'
    type = request.GET.get('type')  # Message type: 'pin', 'short', etc.
    school_id = request.GET.get('school', '')
    
    api_url = "https://waba.wapionline.com/api/be6a71dc-8c39-4dc7-bb3c-69c3f76bf4eb/contact/send-template-message?token=QRj3nWECCsifuqnEyTtHRldRP6iQKSicoosF6TVRvZgbj01qkRyptnxeeq58qw8Y"
    headers = {"Content-Type": "application/json"}
    print(type)
    if whatsapp_no:
        if for_ts == 'school':
            # School-specific credentials and template
            template_name = "school_welcome_to_facultyme_pin"
            field_1 = "FacultyMe School"
            if school_id:
                school = School.objects.filter(id=school_id).first()

        elif for_ts == 'teacher':
            # Teacher-specific credentials and template
            template_name = "teacher_welcome_to_facultyme_pin"
            field_1 = "FacultyMe Teacher"
        
        # OTP Message for Login (PIN)
        # if type == 'pin':
        #     otp_code = ''.join(random.choice(string.digits) for _ in range(4))
        #     password = make_password(otp_code)
        #     NewUser.objects.filter(mobile_no=whatsapp_no).update(password=password, is_mobile_no_verified=True)

        #     # Customize the message field for OTP
        #     payload = {
        #         "phone_number": f"91{whatsapp_no}",
        #         "template_name": template_name,
        #         "template_language": "en",
        #         "field_1": otp_code  # Sending OTP as field_1
        #     }

        #     try:
        #         response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        #         msg_status = 'Success' if response.status_code == 200 else f'Failed ({response.status_code})'
        #     except RequestException as e:
        #         msg_status = f"Error: {str(e)}"

        #     WhatsAppMessages.objects.create(mobile_no=whatsapp_no, msg=json.dumps(payload), status=msg_status)

        # Shortlisting Message
            if type == 'short':
                

                mobile_nos = request.GET.get('mobile_no').split(',')
                school_ids = request.GET.get('school').split(',')
                for mobile_no, school_id in zip(mobile_nos, school_ids):
                    #print(school_id)
                    school = School.objects.filter(user_id=school_id).first()
                    newuser = NewUser.objects.filter(mobile_no=mobile_no).first()
                    if not school:
                        continue
                    #print(school)
                    field_1 = f"{school.user.name if school.user else ''}"  # School/Employer name
                    payload = {
                        "from_phone_number_id":"579680011898278", # 9663384666
                        "phone_number": f"91{mobile_no}",
                        "template_name": "profile_shortlisted",
                        "template_language": "en",
                        "field_1": newuser.name,
                        "field_2": school.user.name,  # Customize based on template
                        "field_3": school.state,
                        "field_4": school.user.mobile_no
                    }
                    #print(payload)
                    try:
                        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
                        msg_status = 'Success' if response.status_code == 200 else f'Failed ({response.status_code})'
                    except RequestException as e:
                        msg_status = f"Error: {str(e)}"

                    WhatsAppMessages.objects.create(mobile_no=mobile_no, msg=json.dumps(payload), status=msg_status)

    return JsonResponse(True, safe=False)

def read_csv_file(request):
    with open('E:/django/facultyme/static/teachers.csv', 'r',encoding="utf-8") as file:
        reader = csv.reader(file)

        for row in reader:
            # Access each row data
            # print(row[0].strip())												
            id = row[0].strip()
            password = row[1].strip()
            last_login = row[2].strip()
            is_superuser = row[3].strip()
            groups = row[4]
            user_permissions = row[5]
            name = row[6].strip()
            mobile_no = row[7].strip()
            alt_mobile_no = row[8].strip()
            profile_pic = row[9].strip()
            user_type = row[10].strip()
            is_active = row[11].strip()
            is_mobile_no_verified = row[12].strip()
            is_staff = row[13].strip()
            joining_date = row[14].strip()
            
            experience_in = row[16].strip()
            subject_of_experience = row[17].strip()
            years_of_experience = row[18].strip()
            highest_qualification = row[19].strip()
            current_salary = row[20].strip()
            expected_salary = row[21].strip()
            preferred_location_district = row[22].strip()

            try:
                new_user = Teacher.objects.filter(user__mobile_no__iexact=mobile_no).first()
                if new_user:
                    res = Teacher.objects.filter(user__mobile_no__iexact=mobile_no).update(expected_salary=expected_salary,current_salary=current_salary,preferred_location_district=preferred_location_district,years_of_experience=years_of_experience,qualification=highest_qualification,experience_in=experience_in,subject_of_experience=subject_of_experience)
                    
                else:
                    user = NewUser.objects.create(id=id,password=password,last_login=last_login,is_superuser=is_superuser,name=name,mobile_no=mobile_no,alt_mobile_no=alt_mobile_no,profile_pic=profile_pic,user_type=user_type,is_active=is_active,is_mobile_no_verified=is_mobile_no_verified,is_staff=is_staff,joining_date=joining_date)
                    Teacher.objects.create(user=user,expected_salary=expected_salary,current_salary=current_salary,preferred_location_district=preferred_location_district,years_of_experience=years_of_experience,qualification=highest_qualification,experience_in=experience_in,subject_of_experience=subject_of_experience)
            except:
                pass


def index(request):
    page_title = "Home | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""
    path = request.path

    trusted_by = TrustedBy.objects.all()
    testimonials = Testimonials.objects.all()
    statistics = Statistics.objects.all()
    how_it_work_teacher = HowItWorkTeacher.objects.all().order_by('step_no')
    how_it_work_school = HowItWorkSchool.objects.all().order_by('step_no')

    

    context = {
        'page_title': page_title,
        'meta_desc': meta_desc,
        'keyword': keyword,
        'schema': schema,
        'trusted_by': trusted_by,
        'testimonials': testimonials,
        'statistics': statistics,
        'how_it_work_teacher': how_it_work_teacher,
        'how_it_work_school': how_it_work_school,
        'path': path
    }

    return render(request, 'index.html', context)


@background(schedule=7200)  # Runs every day
def disable_expired_jobs():
    print("Background task triggered")
    # Get the current date
    current_date = datetime.now().date()

    # Update the status of expired jobs
    current_datetime = timezone.now()

    # Calculate expiration based on timestamp + 30 days
    expired_jobs = PostJob.objects.annotate(
        expiry_calc=ExpressionWrapper(
            F('timestamp') + timedelta(days=30),
            output_field=DateTimeField()
        )
    ).filter(expiry_calc__lt=current_datetime)

    # Update their status
    expired_jobs.update(status='Expired') 

    # Optionally, log or print the result
    print(f"Disabled {expired_jobs.count()} expired jobs.")

@background(schedule=7200)  # Runs every day
def disable_expired_promotions():
    print("Expired Promotion Background task triggered")
    # Get the current date
    current_date = datetime.now().date()

    # Get all JobPromotions where the end_date has passed or is today
    expired_promotions = JobPromotions.objects.filter(end_date__lte=current_date)

    # Update the corresponding PostJob's promo_applied field to False
    for promotion in expired_promotions:
        if promotion.job:  # Ensure the job exists
            promotion.job.promo_applied = False
            promotion.job.save()

    # Optionally log the result
    print(f"Processed {expired_promotions.count()} expired promotions.")

@csrf_exempt
def app_details(request):
    teacher = request.GET.get('teacher')    
    teacher_obj = Teacher.objects.get(id=teacher)

    job_app = JobApplicant.objects.filter(teacher=teacher_obj)
    new_array = []

    for ja in job_app:
        temp_dic = {
            'id':ja.id,
            'job_code':ja.job.job_code,
            'school':ja.job.user.name,
            'timestamp':ja.job.timestamp.strftime("%d-%m-%y"),
            'teacher_grade':ja.job.teacher_grade,
            'subject':ja.job.subject,
            'highest_qualification':ja.job.highest_qualification,
            'experienced_required':ja.job.experienced_required,
            'salary_offered':ja.job.salary_offered,
            'joining_date':ja.job.joining_date.strftime("%d-%m-%y") ,
            'benifits_compensation':ja.job.benifits_compensation,
            'district':ja.job.district,
            'state':ja.job.state,
            'status':ja.status,

        }
        new_array.append(temp_dic)

    context= {
        'job_app':new_array
    }

    # response = serializers.serialize("json", job_app)
    # return HttpResponse(context, content_type='application/json')
    return JsonResponse(context, safe=False)

def send_interview_details(request):
    job_app_id = request.GET.get('job_app_id')

    job_app = JobApplicant.objects.get(id=job_app_id)

    mobile_no = job_app.teacher.user.mobile_no
    contact_person = job_app.contact_person
    contact_person_mobile = job_app.contact_person_mobile


    if mobile_no:
        api_key = 'NGY3MzZhNjU3MTYyNzQ0NjQ2NzM2NzZjN2E1MTMzNjc='
        sender = 'FCLTME'
        message = ''

        # Set the API endpoint and parameters
        url = 'https://api.textlocal.in/send/'
        params = {
            'apikey': api_key,
            'numbers': mobile_no, 
            'message': message,
            'sender': sender
        }

        # Send the HTTP request and print the response
        response = requests.post(url, params=params)
        messages.success(request, 'Interview Details Send')  

    return JsonResponse(True, safe=False)

def send_pin_teacher(request):
    teachers = request.GET.get('teachers')
    type = request.GET.get('type')
    teachers_array = teachers.split(",")

    for teacher in teachers_array:
        if type == 'teacher':
            teacher = Teacher.objects.get(id=teacher)
        else:
            teacher = School.objects.get(id=teacher)

        mobile_no = teacher.user.mobile_no
        otp_code = ''.join(random.choice(string.digits) for _ in range(4))
        # Use set_password on the model instance to ensure password hashing and any signals are applied
        user_obj = NewUser.objects.filter(mobile_no=mobile_no).first()
        if user_obj:
            user_obj.set_password(otp_code)
            user_obj.is_mobile_no_verified = True
            user_obj.save()
            # Debug: confirm that password was set correctly (server log only)
            try:
                pw_ok = user_obj.check_password(otp_code)
                print(f'[DEBUG] forgot_password_pin: password set check for {mobile_no}: {pw_ok} (otp={otp_code})')
            except Exception as e:
                print(f'[DEBUG] forgot_password_pin: error checking password for {mobile_no}: {e}')

        if mobile_no:
            try:
                status, response_text = send_sms_via_msg91(mobile_no, template_id=PIN_TEMPLATE_ID, template_vars={'OTP': otp_code})
                #print(f'MSG91 send (send_pin_teacher) response: status={status}, body={response_text}')
                messages.success(request, 'New PIN send')
            except Exception as e:
                #print('SMS send failed (send_pin_teacher):', e)
                messages.error(request, 'Unable to send PIN right now.')

    return JsonResponse(True, safe=False)

def approve_teacher(request):
    teachers = request.GET.get('teachers')
    type = request.GET.get('type')
    teachers_array = teachers.split(",")
    payload = {}
    mobile_no = 0
    api_url = "https://waba.wapionline.com/api/be6a71dc-8c39-4dc7-bb3c-69c3f76bf4eb/contact/send-template-message?token=QRj3nWECCsifuqnEyTtHRldRP6iQKSicoosF6TVRvZgbj01qkRyptnxeeq58qw8Y"
    headers = {"Content-Type": "application/json"}

    for teacher in teachers_array:
        if type == 'teacher':
             Teacher.objects.filter(id=teacher).update(status='Approved')
            # teacher = Teacher.objects.filter(id=teacher).first()
            # payload = {
            #             "from_phone_number_id":"579680011898278", # 9663384666
            #             "phone_number": f"91{teacher.user.mobile_no}",
            #             "template_name": "teacher_welcome_message",
            #             "template_language": "en",
            #             "field_1": teacher.user.name,
            #             "field_2": teacher.subject_of_specialization,
            #             "field_3": teacher.want_to_teach_for
            # }
            # mobile_no = teacher.user.mobile_no
        elif type == 'school':
            School.objects.filter(id=teacher).update(status='Approved')
            school = School.objects.filter(id=teacher).first()
            payload = {
                        "phone_number": f"91{school.user.mobile_no}",
                        "template_name": "hello_school_post_a_job",
                        "template_language": "en",
                        "field_1": school.contact_person_name if school.contact_person_name else school.user.name,
                        "field_2": school.user.name,
                        "field_3": school.user.mobile_no
            }
            mobile_no = school.user.mobile_no
        elif type == 'job':
            if not WalkinJob.objects.filter(id=teacher).exists():
                PostJob.objects.filter(id=teacher).update(status='Approved')
                job = PostJob.objects.filter(id=teacher).first()
                
                payload = {
                    "phone_number": f"91{job.user.mobile_no}",
                    "template_name": "jobs_are_live",
                    "template_language": "en",
                    "field_1": job.user.name,
                    "button_0": "?jobcode="+job.job_code
                }
                mobile_no = job.user.mobile_no
            else:
                WalkinJob.objects.filter(id=teacher).update(status='Approved')
                job = WalkinJob.objects.filter(id=teacher).first()
                
                payload = {
                    "phone_number": f"91{int(job.user)}",  
                    "template_name": "jobs_are_live",
                    "template_language": "en",
                    "field_1": job.contact_name,  
                    "button_0": "?jobcode="+job.job_code
                }
                mobile_no = int(job.user)
                
        elif type == 'job_app':
            JobApplicant.objects.filter(id=teacher).update(status='Approved')
            job_applicant = JobApplicant.objects.get(id=teacher)
            job_id = job_applicant.job.id if job_applicant.job else job_applicant.walkin_job.id
            teacher_id = job_applicant.teacher.id
            ShortlistedTeachers.objects.filter(teacher=teacher_id, school=job_id).update(is_review=True)
            applicant = JobApplicant.objects.filter(id=teacher).first()
            payload = {
                    "from_phone_number_id":"579680011898278", # 9663384666
                    "phone_number": f"91{applicant.teacher.user.mobile_no}",
                    "template_name": "job_applied_successfull",
                    "template_language": "en",
                    "field_1": applicant.teacher.user.name,
                    "field_2": applicant.job.teacher_grade,
                    "field_3": applicant.job.subject,
                    "field_4": applicant.job.user.name
            }
            mobile_no = applicant.teacher.user.mobile_no
            api_url = "https://waba.wapionline.com/api/be6a71dc-8c39-4dc7-bb3c-69c3f76bf4eb/contact/send-template-message?token=QRj3nWECCsifuqnEyTtHRldRP6iQKSicoosF6TVRvZgbj01qkRyptnxeeq58qw8Y"
            template_name2 = "new_applications_for_manual_sending"  # Adjust based on your configuration
            payload2= {
                "phone_number": f"91{applicant.job.user.mobile_no}",  # Mobile number with country code
                "template_name": template_name2,  # Template for teacher welcome message
                "template_language": "en",  # Language of the template
                "field_1": applicant.job.user.name,  # Placeholder for teacher's name
                "field_2":applicant.job.subject,
                "field_3":applicant.teacher.user.name,
                "field_4":applicant.teacher.subject_i_teach if applicant.teacher.subject_i_teach else applicant.teacher.subject_of_experience,
                "field_5":applicant.teacher.user.mobile_no
            }
            headers2 = {"Content-Type": "application/json"}
            try:
                response = requests.post(api_url, headers=headers2, data=json.dumps(payload2))
                msg_status = 'Success' if response.status_code == 200 else f'Failed ({response.status_code})'
            except RequestException as e:
                msg_status = f"Error: {str(e)}"

            WhatsAppMessages.objects.create(mobile_no=applicant.job.user.mobile_no, msg=json.dumps(payload), status=msg_status)

        else:
            pass
    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        msg_status = 'Success' if response.status_code == 200 else f'Failed ({response.status_code})'
    except RequestException as e:
        msg_status = f"Error: {str(e)}"

    WhatsAppMessages.objects.create(mobile_no=mobile_no, msg=json.dumps(payload), status=msg_status)

    return JsonResponse(True, safe=False)

def change_labels(request):
    teacher = request.GET.get('teacher')
    label = request.GET.get('label')
    type = request.GET.get('type')

    if type=='teacher':
        Teacher.objects.filter(id=teacher).update(label=label)
    else:
        School.objects.filter(id=teacher).update(label=label)

    return JsonResponse(True, safe=False)


def disable_teacher(request):
    teachers = request.GET.get('teachers')
    type = request.GET.get('type')

    teachers_array = teachers.split(",")

    for teacher in teachers_array:
        if type == 'teacher':
            Teacher.objects.filter(id=teacher).update(status='Disabled')
        elif type == 'school':
            School.objects.filter(id=teacher).update(status='Disabled')
        elif type == 'job':
            if PostJob.objects.filter(id=teacher).exists():
                PostJob.objects.filter(id=teacher).update(status='Disabled')
            else:
                WalkinJob.objects.filter(id=teacher).update(status='Disabled')
            
        elif type == 'job_app':
            JobApplicant.objects.filter(id=teacher).update(status='Rejected')
        else:
            pass
    return JsonResponse(True, safe=False)

def approve_application(request):
    teachers = request.GET.get('teachers')
    teachers_array = teachers.split(",")
    
    for teacher in teachers_array:
        JobApplicant.objects.filter(id=teacher).update(status='Approved')
        job_applicant = JobApplicant.objects.get(id=teacher)
        job_id = job_applicant.job.id
        teacher_id = job_applicant.teacher.id
        ShortlistedTeachers.objects.filter(teacher=teacher_id, school=job_id).update(is_review=True)
       
    return JsonResponse(True, safe=False)

def teacher_pricing(request):
    page_title = "Teacher Pricing | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    # Allow unauthenticated users to view pricing. Selection/purchase is blocked server-side.
    # If the user is logged in and is a School, redirect to institute pricing.
    if request.user.is_authenticated:
        if getattr(request.user, 'user_type', None) == 'School':
            return redirect('/institute-pricing')

    teacher_plans = TeacherSubscriptionPlan.objects.order_by('display_sequence')
    active_teacher_plans = TeacherSubscriptionPlan.objects.filter(is_acitve=True).order_by('display_sequence')
    active_plan_ids = set(active_teacher_plans.values_list('id', flat=True))

    # Only fetch subscription details for authenticated users
    subscription_detail = None
    pack_detail = None
    has_free_plan = False
    if request.user.is_authenticated:
        subscription_detail = Subscription.objects.filter(user_id=request.user.id).first()
        has_free_plan = TeacherSubscription.objects.filter(
            plan__icontains = "FREE",
            user_id=request.user.id
        ).exists()

        if subscription_detail and "Teacher Plan/" in subscription_detail.plan:
            plan_name = subscription_detail.plan.replace("Teacher Plan/","")
            pack_detail = TeacherSubscriptionPlan.objects.filter(plan_name__icontains = plan_name).first()

    if has_free_plan:      
        teacher_plans = TeacherSubscriptionPlan.objects.exclude(plan_name__icontains="FREE")
  
    final_teacher_plans = teacher_plans.filter(is_acitve=True)
    for x in  final_teacher_plans :
        x.amenities = TeacherPlanAmenities.objects.filter(plan_id=x.id)

    context = {
        'page_title':page_title,
        'meta_desc':meta_desc,
        'keyword':keyword,
        'schema':schema,
        'teacher_plans': final_teacher_plans ,
        'pack_detail':pack_detail,
        'has_free_plan':has_free_plan,
        'jobcode':request.GET.get('jobcode')
    }

    return render(request,'teacher_pricing.html', context) 

def institute_pricing(request):
    page_title = "Institute/School Pricing | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""
    # Allow unauthenticated users to view institute pricing. Selection/purchase is blocked server-side.
    # If the user is logged in and is a Teacher, redirect to teacher pricing.
    if request.user.is_authenticated:
        if getattr(request.user, 'user_type', None) == 'Teacher':
            return redirect('/teacher-pricing')

    school_plans = SchoolSubscriptionPlan.objects.order_by('display_sequence')

    # Only fetch subscription details for authenticated users
    subscription_detail = None
    pack_detail = None
    has_free_plan = False
    if request.user.is_authenticated:
        subscription_detail = Subscription.objects.filter(user_id=request.user.id).first()
        has_free_plan = Subscription.objects.filter(
            plan__icontains = "FREE",
            user_id=request.user.id
        ).exists()

        if subscription_detail and "Institute Plan/" in subscription_detail.plan:
            plan_name = subscription_detail.plan.replace("Institute Plan/","")
            pack_detail = SchoolSubscriptionPlan.objects.filter(plan_name__icontains = plan_name).first()

    if has_free_plan:
        school_plans = SchoolSubscriptionPlan.objects.exclude(plan_name__icontains="FREE")

    final_school_plans = school_plans.filter(is_acitve=True).order_by('display_sequence')
    for x in final_school_plans:
        x.amenities = SchoolPlanAmenities.objects.filter(plan_id=x.id)
    context = {
        'page_title':page_title,
        'meta_desc':meta_desc,
        'keyword':keyword,
        'schema':schema,
        'school_plans':final_school_plans,
        'pack_detail':pack_detail,
    }

    return render(request,'institute_pricing.html', context) 

@login_required
def walkin_pricing(request):
    page_title = "Walk-in Pricing | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    if not request.user.is_authenticated:
        return redirect('/login')

    if request.user.user_type == 'Teacher':
        return redirect('/teacher-pricing')

    walkin_plans = WalkInSubscriptionPlan.objects.filter(is_active=True)
    for plan in walkin_plans:
        plan.amenities = WalkinPlanAmenities.objects.filter(id=plan.id)
        
        # Split description and remove numbers
        if plan.plan_description:
            import re
            pattern = r'\d+\.'
            
            parts = re.split(pattern, plan.plan_description)
            
            # Remove empty strings and strip whitespace
            plan.description_points = [part.strip() for part in parts if part.strip()]
        else:
            plan.description_points = []

    subscription_detail = Subscription.objects.filter(user_id=request.user.id).first()
    pack_detail = None
    
    if subscription_detail and "Walk-in Plan/" in subscription_detail.plan:
        plan_name = subscription_detail.plan.replace("Walk-in Plan/","")
        pack_detail = WalkInSubscriptionPlan.objects.filter(plan_name__icontains=plan_name).first()
        
        # Add remaining job posts information to the context
        if pack_detail:
            pack_detail.remaining_days = subscription_detail.remaining_job_post
       
    context = {
        'page_title': page_title,
        'meta_desc': meta_desc,
        'keyword': keyword,
        'schema': schema,
        'walkin_plans': walkin_plans,
        'pack_detail': pack_detail,
    }

    return render(request, 'walkin_pricing.html', context)

@login_required(login_url='/login')
def teacher_account(request):
    page_title = "Teacher Account | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    if request.user.user_type == 'School':
        return redirect('/school-account')
    
    applied_job_count = 0
    interview_job_count = 0
    review_job_count = 0
    rejected_job_count = 0
    shortlisted_job_count = 0

    if request.user.id:
        UserLog.objects.create(user=request.user,action='Teacher Account View')

        teacher = Teacher.objects.get(user_id=request.user.id)
        job_applicant = JobApplicant.objects.filter(teacher=teacher)
    
    for ja in job_applicant:
        if ja.status == 'Applied' or ja.status == 'New' or ja.status == 'Approved':
            applied_job_count = applied_job_count+1
        if ja.status == 'New':
            review_job_count = review_job_count+1
        if ja.status == 'Interview Call':
            interview_job_count = interview_job_count+1
        if ja.status == 'Rejected':
            rejected_job_count = rejected_job_count+1
        
    
        shortlisted_job_count = ShortlistedTeachers.objects.filter(teacher=teacher.id, is_review=True).count()
         
    context = {
        'page_title':page_title,
        'meta_desc':meta_desc,
        'keyword':keyword,
        'schema':schema,
        'applied_job_count':applied_job_count,
        'review_job_count':review_job_count,
        'interview_job_count':interview_job_count,
        'rejected_job_count':rejected_job_count,
        'shortlisted_job_count':shortlisted_job_count,
        'path': request.path
    }

    return render(request,'teacher_account.html', context) 

@login_required(login_url='/login')
def institute_account(request):
    page_title = "Institute Account | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    if request.user.user_type == 'Teacher':
        return redirect('/teacher-account')

    context = {
        'page_title':page_title,
        'meta_desc':meta_desc,
        'keyword':keyword,
        'schema':schema,
        'path': request.path
    }

    return render(request,'institute_account.html', context) 

def only_district_data(request):

    state = request.GET.get('state')
    district_data = District.objects.filter(state__name__iexact=state).order_by('name')

    option_str = ''
    for dd in district_data:
        option_str = option_str + '<li><div class="form-check"><input class="form-check-input" style="width:1rem;height:1rem;" type="checkbox" name="preferred_location_district_job_alert" value="'+str(dd.name)+'" id="d'+dd.name+'"><label class="form-check-label" for="d'+dd.name+'">'+dd.name+'</label></div></li>'
    
    context = {
        'district_list':option_str,
    }
    return JsonResponse(context)

def district_data(request):
    state = request.GET.get('state')
    user_id = request.user.id
    
    district_data = District.objects.filter(state__name__iexact=state).order_by('name')
    res_cities = []

    try:
        teacher_info = Teacher.objects.get(user_id=user_id)
        districts_list = teacher_info.preferred_location_district.split(',') if teacher_info.preferred_location_district else []
        res_cities = districts_list
    except Teacher.DoesNotExist:
        res_cities = []  # Default empty list if no matching teacher is found 
    option_str = ''
    for dd in district_data:
        selected = ""
        if dd.name in res_cities:
            selected = "checked"
        option_str += '<li><div class="form-check"><input class="form-check-input" '+selected+' style="width:1rem;height:1rem;" type="checkbox" name="preferred_location_district" value="'+str(dd.name)+'" id="d'+dd.name+'"><label class="form-check-label" for="d'+dd.name+'">'+dd.name+'</label></div></li>'
    
    context = {
        'district_list': option_str,
    }
    return JsonResponse(context)

def edit_location_db_job_alert(request):
    
    state = request.GET.get('state')

    
    district_data = District.objects.filter(state__name__iexact=state).order_by('name')
    
        
    option_str = ''
    for dd in district_data:
        option_str = option_str + '<li><div class="form-check"><input class="form-check-input" style="width:1rem;height:1rem;" type="checkbox" name="preferred_location_district" value="'+str(dd.name)+'" id="d'+dd.name+'"><label class="form-check-label" for="d'+dd.name+'">'+dd.name+'</label></div></li>'
    
    context = {
        'district_list':option_str,
    }
    return JsonResponse(context)


def edit_location_db(request):
    state = request.GET.get('state')
    user_id = request.user.id

    # Retrieve district data for the state
    district_data = District.objects.filter(state__name__iexact=state).order_by('name')
    # Initialize res_cities as an empty list to safely iterate later
    res_cities = []

    # Fetch the teacher's preferred location information
    teacher_info = Teacher.objects.get(user_id=user_id)
    print(teacher_info.preferred_location_district)
    if teacher_info.preferred_location_district:
        try:
            # Properly parse the JSON string
            preferred_locations = json.loads(teacher_info.preferred_location_district)
            # Retrieve cities for the given state
            res_cities = preferred_locations.get(state, [])
        except json.JSONDecodeError:
            # Log the error or send a message to a monitoring system
            print(f"Error decoding JSON for user {user_id}")

    # Constructing the option string
    option_str = ''
    for district in district_data:
        selected = 'checked' if district.name in res_cities else ''
        option_str += '<li><div class="form-check"><input class="form-check-input" ' + selected + ' style="width:1rem;height:1rem;" type="checkbox" name="preferred_location_district" value="' + str(district.name) + '" id="d' + district.name + '"><label class="form-check-label" for="d' + district.name + '">' + district.name + '</label></div></li>'

    context = {'district_list': option_str}
    return JsonResponse(context)




def add_location_db(request):
    location = request.GET.get('location')
    state = request.GET.get('state')

    # Assuming location is a comma-separated string of district names
    preferred_location_district = {state: location.split(",") if location else []}

    user_id = request.user.id
    teacher_info = Teacher.objects.get(user_id=user_id)
    
    # Initialize with an empty dict if no existing preferred locations
    existing_locations = {}

    if teacher_info.preferred_location_district:
        # Ensure the stored string is valid JSON
        try:
            existing_locations = json.loads(teacher_info.preferred_location_district)
        except json.JSONDecodeError:
            print("Failed to decode JSON. Starting with an empty dictionary.")

    # Update or add new locations for the state
    existing_locations[state] = preferred_location_district[state]

    # Convert the updated locations back to a JSON string for storage
    updated_locations_json = json.dumps(existing_locations)

    # Update the teacher's preferred locations
    Teacher.objects.filter(user_id=user_id).update(preferred_location_district=updated_locations_json)

    # Prepare the response
    context = {'district_list': existing_locations}
    
    return JsonResponse(context)

def add_only_location_db(request):
    
    location = request.GET.get('location')
    state = request.GET.get('state')

    preferred_location_district = {
        state:location.split(",")
    }
    
    context = {
        'district_list':preferred_location_district,
    }
    return JsonResponse(context)


def teacher_profile(request):
    page_title = "Teacher Profile | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    # Allow unauthenticated users to view institute pricing. Selection/purchase is blocked server-side.
    # If the user is logged in and is a Teacher, redirect to teacher pricing.
    # if request.user.is_authenticated:
    #     if getattr(request.user, 'user_type', None) == 'Teacher':
    #         return redirect('/teacher-pricing')

   # school_plans = SchoolSubscriptionPlan.objects.order_by('display_sequence')
    if request.user.is_authenticated:
        if request.user.user_type == 'School':
            return redirect('/login')
    else:
        return redirect('/login')

    user_id = request.user.id
    UserLog.objects.create(user=request.user,action='Teacher Profile View')

    teacher_info = Teacher.objects.filter(user_id=user_id).first()
    preferred_location_district_list = []     
    # Only fetch subscription details for authenticated users
    subscription_detail = None
    pack_detail = None

    if teacher_info:
        try:
            if teacher_info.preferred_location_district:
                location_dict = json.loads(teacher_info.preferred_location_district)
                if location_dict: 
                    preferred_location_district_list = [{state: set(districts)} for state, districts in location_dict.items()]
                else:
                    preferred_location_district_list = []
            else:
                preferred_location_district_list = []     
            teacher_info.preferred_location_district = preferred_location_district_list
        except:
            pass
    
    qualification_data = TeacherFormData.objects.filter(data_type='Qualification')
    specialization_data =  TeacherFormData.objects.filter(data_type='Subject Specialzation')
    experience_type_data = TeacherFormData.objects.filter(data_type='Experience Type')
    expected_salary_data = TeacherFormData.objects.filter(data_type='Expected Salary')
    experience_in_data = TeacherGrade.objects.all()
    experience_subject_data = TeacherFormData.objects.filter(data_type='Subject of Experience')
    experience_year_data = TeacherFormData.objects.filter(data_type='Years of experience')
    current_salary_data = TeacherFormData.objects.filter(data_type='Current Salary')
    experience_in_fresher_data = TeacherGrade.objects.all()
    subject_teach_fresher_data = TeacherFormData.objects.filter(data_type='Subject i can teach')
    state_data = State.objects.all().order_by('name')
    district_data = District.objects.all().order_by('name')

    if teacher_info and teacher_info.want_to_teach_for == 'None':
        teacher_info.want_to_teach_for = ''
    
    if teacher_info and teacher_info.subject_i_teach == 'None':
        teacher_info.subject_i_teach = ''


    context = {
        'page_title':page_title,
        'meta_desc':meta_desc,
        'keyword':keyword,
        'jobcode':request.GET.get('jobcode',None),
        'schema':schema,
        'district_data':district_data,
        'teacher_info':teacher_info,
        'state_data':state_data,
        'qualification_data':qualification_data,
        'specialization_data':specialization_data,
        'experience_type_data':experience_type_data,
        'expected_salary_data':expected_salary_data,
        'experience_in_data':experience_in_data,
        'experience_subject_data':experience_subject_data,
        'experience_year_data':experience_year_data,
        'current_salary_data':current_salary_data,
        'subject_teach_fresher_data':subject_teach_fresher_data,
        'experience_in_fresher_data':experience_in_fresher_data,
        'preferred_location_district_list':preferred_location_district_list
    }
    
    return render(request,'teacher_profile.html', context) 

@login_required
def delete_district(request):
    if request.method == 'POST':
        state = request.POST.get('state')
        district = request.POST.get('district')
        user_id = request.user.id
        
        try:
            # Get the teacher object
            teacher_info = Teacher.objects.filter(user_id=user_id).first()
            
            if teacher_info and teacher_info.preferred_location_district and state and district:
                # Get current locations
                locations = json.loads(teacher_info.preferred_location_district)
                
                # Remove the district if it exists
                if state in locations and district in locations[state]:
                    locations[state].remove(district)
                    
                    # If no districts left, remove the state too
                    if not locations[state]:
                        del locations[state]
                    
                    # Save updated locations back to database
                    teacher_info.preferred_location_district = json.dumps(locations)
                    teacher_info.save()
                    
                    # Log the action
                    UserLog.objects.create(user=request.user, action=f'District {district} Removed')
                
            return redirect('/teacher-profile')  # Adjust this URL as needed
            
        except Exception as e:
            messages.error(request, f"Error removing district: {str(e)}")
            return redirect('/teacher-profile')
    
    return redirect('/teacher-profile')
    
@login_required
def delete_location(request):
    if request.method == 'POST':
        state = request.POST.get('state')
        user_id = request.user.id
        
        try:
            # Get the teacher object using the same method as in teacher_profile
            teacher_info = Teacher.objects.filter(user_id=user_id).first()
            
            if teacher_info and teacher_info.preferred_location_district:
                # Get current locations
                locations = json.loads(teacher_info.preferred_location_district)
                
                # Remove the state if it exists
                if state in locations:
                    del locations[state]
                    
                # Save updated locations back to database
                teacher_info.preferred_location_district = json.dumps(locations)
                teacher_info.save()
                
                # Log the action
                UserLog.objects.create(user=request.user, action='Location Removed')
                
            return redirect('/teacher-profile')  # Adjust this URL as needed
            
        except Exception as e:
            messages.error(request, f"Error removing location: {str(e)}")
            return redirect('/teacher-profile')
    
    return redirect('/teacher-profile')

@login_required
def delete_all_locations(request):
    if request.method == 'POST':
        user_id = request.user.id
        
        try:
            # Get the teacher object using the same method as in teacher_profile
            teacher_info = Teacher.objects.filter(user_id=user_id).first()
            
            if teacher_info:
                # Clear all locations
                teacher_info.preferred_location_district = '{}'
                teacher_info.save()
                
                # Log the action
                UserLog.objects.create(user=request.user, action='All Locations Removed')
            
            return redirect('/teacher-profile')  # Adjust this URL as needed
            
        except Exception as e:
            messages.error(request, f"Error removing all locations: {str(e)}")
            return redirect('/teacher-profile')
    
    return redirect('/teacher-profile')

def get_teacher_subjects(request):
    grades = request.GET.get('grade')
    grades = grades.split(",")
    grade_list = []
    for grade in grades:
        dis_data = TeacherSubject.objects.filter(grade__name__iexact=grade).order_by('name')
        for g in dis_data:
            grade_list.append(g.name)
        
        dis_data_1 = Subject.objects.filter(grade__name__iexact=grade).order_by('name')
        for gg in dis_data_1:
            grade_list.append(gg.name)

    grade_list = [*set(grade_list)]
    return JsonResponse(grade_list, safe=False)

def teacher_search_apply(request):
    page_title = "Teacher Account | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    context = {
        'page_title':page_title,
        'meta_desc':meta_desc,
        'keyword':keyword,
        'schema':schema,
    }

    return render(request,'teacher_search_apply.html', context) 

def my_jobs(request):
    page_title = "Jobs | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = "All"
    status =  request.GET.get('status', '')

    if request.user.id:
        UserLog.objects.create(user=request.user,action='Teacher My Job View')

        teacher = Teacher.objects.get(user_id=request.user.id)
        job_applicant = JobApplicant.objects.filter(teacher=teacher)
        for job in job_applicant:
            if  job.walkin_job:
                job.job_code = job.walkin_job.job_code
                print(job.walkin_job.user) 
                job.user = School.objects.filter(user=job.walkin_job.user).first()
        if status != 'All':
            job_applicant = JobApplicant.objects.filter(teacher=teacher).filter(status__iexact=status).order_by('-timestamp')
        else:
            job_applicant = JobApplicant.objects.filter(teacher=teacher).order_by('-timestamp')

    context = {
        'page_title':page_title,
        'meta_desc':meta_desc,
        'keyword':keyword,
        'schema':schema,
        'jobs':job_applicant,
        'status':status
    }
 
    return render(request,'my_jobs.html', context) 

def teacher_job_review(request):
    page_title = "Teacher Account | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    context = {
        'page_title':page_title,
        'meta_desc':meta_desc,
        'keyword':keyword,
        'schema':schema,
    }

    return render(request,'teacher_job_review.html', context) 

def teacher_interview_call(request):
    page_title = "Teacher Account | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    context = {
        'page_title':page_title,
        'meta_desc':meta_desc,
        'keyword':keyword,
        'schema':schema,
    }

    return render(request,'teacher_interview_call.html', context) 

def teacher_pricing_plan(request):
    page_title = "Teacher Account | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""
   
    if not request.user.is_authenticated:
        return redirect('/login')
    if request.user.user_type == 'School':
        return redirect('/institute-pricing')
   
    subscription_detail = TeacherSubscription.objects.filter(user=request.user).first()
   
    expiry_date = None
    pack_detail = None

    if subscription_detail and "Teacher Plan/" in subscription_detail.plan:
        plan_name = subscription_detail.plan.replace("Teacher Plan/", "")
        pack_detail = TeacherSubscriptionPlan.objects.filter(plan_name__icontains=plan_name).first()
        expiry_date = subscription_detail.date + timedelta(days=365)
        

    if not pack_detail:
        pack_detail = TeacherSubscriptionPlan.objects.filter(plan_name__icontains="FREE").first()
        
    context = {
        'page_title': page_title,
        'meta_desc': meta_desc,
        'keyword': keyword,
        'schema': schema,
        'subscription_detail': subscription_detail,
        'pack_detail': pack_detail,
        'expiry_date': expiry_date,
    }
    
    return render(request, 'teacher_pricing_plan.html', context)

def add_job_alert(request):
        
    if request.method == 'POST':
        mobile_no = request.POST.get('mobile_no')
        name = request.POST.get('name')
        alternate_mobile_no = request.POST.get('alternate_mobile_no')
        job_category = request.POST.get('job_category')
        subject = request.POST.get('subject')
        pre_job_location = request.POST.get('pre_job_location')
            
        if JobAlert.objects.filter(mobile_no=mobile_no).exists():
            pass
        else:
            JobAlert.objects.create(
                mobile_no=mobile_no,
                name=name,
                alternative_mobile_no=alternate_mobile_no,
                job_category=job_category,
                subject=subject,
                prefered_location=pre_job_location,
                )

        messages.success(request, 'Job alert request received.')

    return redirect('/job-alert') 


def add_teacher_profile(request):
        
    page_title = "Teacher Account | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    if request.method == 'POST':

        user_id = request.user.id

        gender = request.POST.get('gender')
        qualification = request.POST.get('qualification')
        subject_of_specialization = request.POST.get('subject_of_specialization')
        experience_type = request.POST.get('experience_type')
        experience_in = ','.join(request.POST.getlist('experience_in'))
        subject_of_experience = ','.join(request.POST.getlist('subject_of_experience'))
        years_of_experience = request.POST.get('years_of_experience')
        current_salary = request.POST.get('current_salary')
        dob = request.POST.get('dob')
        expected_salary = request.POST.get('expected_salary')
        preferred_location_state = '|'.join(request.POST.getlist('preferred_location_state'))
        # preferred_location_district = '|'.join(request.POST.getlist('preferred_location_district'))
        address_pincode = request.POST.get('address_pincode')
        address_state = request.POST.get('address_state')
        address_district = request.POST.get('address_district')
        pre_job_location = request.POST.get('pre_job_location')
        address = request.POST.get('address')
        want_to_teach_for = ','.join(request.POST.getlist('want_to_teach_for'))
        subject_i_teach = ','.join(request.POST.getlist('subject_i_teach'))

        whatsapp_template_subject = ''
        whatsapp_template_grade = ''

        if experience_type == 'Fresher':            
            subject_of_experience = ''
            experience_in = ''
            whatsapp_template_subject = subject_i_teach
            whatsapp_template_grade = want_to_teach_for
        if experience_type == 'Experienced':
            want_to_teach_for = ''
            subject_i_teach = ''
            whatsapp_template_grade = experience_in
            whatsapp_template_subject = subject_of_experience
            
        if Teacher.objects.filter(user_id=user_id).exists():

            Teacher.objects.filter(user_id=user_id).update(
                gender=gender,
                qualification=qualification,
                subject_of_specialization=subject_of_specialization,
                experience_type=experience_type,
                experience_in=experience_in,
                subject_of_experience=subject_of_experience,
                years_of_experience=years_of_experience,
                current_salary=current_salary,
                expected_salary=expected_salary,
                dob=dob,
        #        preferred_location_state='',
        #        preferred_location_district=pre_job_location,
                address_pincode=address_pincode,
                address_state=address_state,
                address_district=address_district,
                address=address,
                want_to_teach_for=want_to_teach_for,
                subject_i_teach=subject_i_teach
                )
        else:

            Teacher.objects.create(
                user_id=user_id,
                gender=gender,
                qualification=qualification,
                subject_of_specialization=subject_of_specialization,
                experience_type=experience_type,
                experience_in=experience_in,
                subject_of_experience=subject_of_experience,
                years_of_experience=years_of_experience,
                current_salary=current_salary,
                expected_salary=expected_salary,
                preferred_location_state=preferred_location_state,
                address_pincode=address_pincode,
                address_state=address_state,
                address_district=address_district,
                address=address,
                want_to_teach_for=want_to_teach_for,
                subject_i_teach=subject_i_teach
                )

            details = Teacher.objects.filter(user_id=user_id).first()
            api_url = "https://waba.wapionline.com/api/be6a71dc-8c39-4dc7-bb3c-69c3f76bf4eb/contact/send-template-message?token=QRj3nWECCsifuqnEyTtHRldRP6iQKSicoosF6TVRvZgbj01qkRyptnxeeq58qw8Y"
            template_name = "teacher_welcome_message"  # Adjust based on your configuration
            template_language = "en"
            payload = {
                "from_phone_number_id":"579680011898278", # 9663384666
                "phone_number": f"91{details.user.mobile_no}",  # Mobile number with country code
                "template_name": template_name,  # Template for teacher welcome message
                "template_language": template_language,  # Language of the template
                "field_1": details.user.name,  # Placeholder for teacher's name
                "field_2": whatsapp_template_subject,
                "field_3": whatsapp_template_grade
            }
            headers = {"Content-Type": "application/json"}
            try:
                response = requests.post(api_url, headers=headers, data=json.dumps(payload))
                msg_status = 'Success' if response.status_code == 200 else f'Failed ({response.status_code})'
            except RequestException as e:
                msg_status = f"Error: {str(e)}"

            WhatsAppMessages.objects.create(mobile_no=details.user.mobile_no, msg=json.dumps(payload), status=msg_status)


        messages.success(request, 'Your profile is updated successfully')

    jobcode = request.POST.get('jobcode')
    free_to_apply_job = False
    try:
        facultyme_permission= FacultyMe_Permission.objects.first()
        free_to_apply_job=facultyme_permission.free_to_apply_job
    except Exception as e:
        pass
    if jobcode:
        if not TeacherSubscription.objects.filter(user_id=request.user.id).exists():
            return redirect(reverse('teacher_pricing')+'?jobcode='+jobcode)
        subscription=TeacherSubscription.objects.get(user_id=request.user.id)
        if not subscription.is_subscription_valid():
            return redirect(reverse('teacher_pricing')+'?jobcode='+jobcode)
        return redirect('/current-vacancies?jobcode='+jobcode)
    return redirect('/teacher-account') 

def school_profile(request):
    page_title = "School Profile | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    if request.user.is_authenticated:
        if request.user.user_type == 'Teacher':
            return redirect('/login')
    else:
        return redirect('/login')

    user_id = request.user.id

    school_info = School.objects.filter(user_id=user_id).first()

    state_data = State.objects.all()

    context = {
        'page_title':page_title,
        'meta_desc':meta_desc,
        'keyword':keyword,
        'schema':schema,
        'school_info':school_info,
        'state_data':state_data,
    }

    return render(request,'school_profile.html',context) 


@login_required(login_url='/login')
def request_for_interview(request):
    teacher = request.GET.get('teacher','')
    school = School.objects.filter(user_id=request.user.id).first()  
    print(request.user.id)
    print("schoo;",school.id)
    exist = ShortlistedTeachers.objects.filter(school=school.id).filter(teacher=teacher).first()
    print("exist",exist)
    # if not Subscription.objects.filter(user_id=request.user.id).exists():
    #     return redirect(reverse('institute_pricing'))
    if not exist:
        res_upd = ShortlistedTeachers.objects.create(school=school.id, teacher=teacher)

        if res_upd:
            return JsonResponse(True, safe=False)
        else:
            return JsonResponse(False, safe=False)
    else:
        return JsonResponse(False, safe=False)

@login_required(login_url='/login')
def call_for_interview_school(request):
    job_app_id = request.GET.get('apid')
    res_upd = JobApplicant.objects.filter(id=job_app_id).update(status='Interview Call Request')
    
    messages.success(request, 'Interview Call Requested')
     
    try:
        if res_upd:
            return JsonResponse(True, safe=False)
    except:
            return JsonResponse(False, safe=False)
    
@login_required(login_url='/login')
def call_for_interview_submit(request):
    job_app_id = request.GET.get('job_app_ids','')
    interview_date = request.POST.get('interview_date','')
    contact_person = request.POST.get('contact_per','')
    interview_time = request.POST.get('interview_time','')
    contact_person_mobile = request.POST.get('contact_per_mob','')

    job_app_id_array = job_app_id.split(",")

    for job_app_id_obj in job_app_id_array:

        res_upd = JobApplicant.objects.filter(id=job_app_id_obj).update(status='Interview Call',interview_date=interview_date,interview_time=interview_time,contact_person=contact_person,contact_person_mobile=contact_person_mobile)
        res = JobApplicant.objects.get(id=job_app_id_obj)
        
        whatsapp_no = res.teacher.user.mobile_no
        job_code = res.job.job_code
        school_name = res.job.user.name
        interview_date = res.interview_date
        interview_time = res.interview_time
        contact_person = res.contact_person
        contact_person_contact = res.contact_person_mobile
        teacher_name = res.teacher.user.name
        send_whatsapp_cfi(whatsapp_no,job_code,school_name,interview_date,interview_time,contact_person,contact_person_contact,teacher_name )
    try:
        if res_upd:
            return JsonResponse(True, safe=False)
    except:
            return JsonResponse(False, safe=False)


# @login_required(login_url='/login')
# def reject_application(request):
#     job_id = request.GET.get('job','')
#     JobApplicant.objects.filter(id=job_id).update(status='Rejected')

#     return redirect('/application-received?job='+job_id)

@login_required(login_url='/login')
def reject_application(request):
    job_app_id = request.GET.get('apid')
    JobApplicant.objects.filter(id=job_app_id).update(status='Rejected')
    
    messages.success(request, 'Application Rejected')
     
    return JsonResponse(True, safe=False)

@login_required(login_url='/login')
def admin_approve(request):
    job_app_id = request.GET.get('job_app_id')
    JobApplicant.objects.filter(id=job_app_id).update(status='Approved')
    
    messages.success(request, 'Application Approved')
     
    return JsonResponse(True, safe=False)

@login_required(login_url='/login')
def school_account(request):
    page_title = "School Account | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    if request.user.user_type == 'Teacher':
        return redirect('/teacher-account')

    posted_jobs_count = 0
    applied_jobs_count = 0
    inteview_jobs_count = 0
    rejected_jobs_count = 0
    review_jobs_count = 0
    approve_jobs_count = 0
    app_res = 0
    shortlisted_count = 0
    
    school = School.objects.filter(user_id=request.user.id).first()
    shortlisted = ShortlistedTeachers.objects.filter(school=school.id)
    shortlisted_count = shortlisted.count()
    posted_jobs = PostJob.objects.filter(user_id=request.user.id)
    walkin_jobs = WalkinJob.objects.filter(user=school.user)
    jobs_count = posted_jobs.count()
    jobs_count += walkin_jobs.count()

    for pj in posted_jobs:
        job_applicant = JobApplicant.objects.filter(job=pj)
        for ja in job_applicant:   
            if ja.status == 'Approved':
                app_res = app_res + 1        
            if ja.status == 'Interview Call' or ja.status == 'Interview Call Request':
                inteview_jobs_count = inteview_jobs_count + 1
        if pj.status == 'Approved':
            applied_jobs_count = applied_jobs_count + 1
        if pj.status == 'New':
            review_jobs_count = review_jobs_count + 1
        if pj.status == 'Expired' or pj.status == 'ReApproval':
            rejected_jobs_count = rejected_jobs_count + 1
    
    for wj in walkin_jobs:
        job_applicant = JobApplicant.objects.filter(walkin_job=wj)
        for ja in job_applicant:   
            if ja.status == 'Approved':
                app_res = app_res + 1        
            if ja.status == 'Interview Call' or ja.status == 'Interview Call Request':
                inteview_jobs_count = inteview_jobs_count + 1
        if wj.status == 'Approved':
            applied_jobs_count = applied_jobs_count + 1
        if wj.status == 'New':
            review_jobs_count = review_jobs_count + 1
        if wj.status == 'Expired' or wj.status == 'ReApproval':
            rejected_jobs_count = rejected_jobs_count + 1
    
    posted_jobs_count = posted_jobs.count() + walkin_jobs.count()

    context = {
        'page_title':page_title,
        'meta_desc':meta_desc,
        'keyword':keyword,
        'schema':schema,
        'posted_jobs_count':posted_jobs_count,
        'applied_jobs_count':applied_jobs_count,
        'rejected_jobs_count':rejected_jobs_count,
        'inteview_jobs_count':inteview_jobs_count,
        'review_jobs_count':review_jobs_count,
        'jobs_count':jobs_count,
        'app_res':app_res,
        'shortlisted_count':shortlisted_count,
        'shortlisted':shortlisted
    }

    return render(request,'school_account.html',context) 

def edit_job(request):
    page_title = "Edit a job | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    if not request.user.is_authenticated:

        return redirect('/login')

    grade_data = JobFormData.objects.filter(data_type='Teacher Grade')
    subject_data = JobFormData.objects.filter(data_type='Subject')
    qualification_data = JobFormData.objects.filter(data_type='Highest Qualification')
    experience_data = JobFormData.objects.filter(data_type='Experience Required')
    salary_data = JobFormData.objects.filter(data_type='Salary offered')
    benifits_data = JobFormData.objects.filter(data_type='Benefits & compensation')

    job = {}
    job_id = request.GET.get('job','')
    if job_id:
        job = PostJob.objects.get(pk=int(job_id))

    benifits_compensation = (job.benifits_compensation).split(",")
    context = {
        'page_title':page_title,
        'meta_desc':meta_desc,
        'keyword':keyword,
        'schema':schema,
        'grade_data':grade_data,
        'subject_data':subject_data,
        'qualification_data':qualification_data,
        'experience_data':experience_data,
        'salary_data':salary_data,
        'benifits_data':benifits_data,
        'job':job,
        'benifits_compensation':benifits_compensation
    }

    return render(request,'edit_job.html',context)
    

def post_job(request):
    page_title = "Post a job | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    if not request.user.is_authenticated:

        return redirect('/login')

    grade_data = Grade.objects.all()
    subject_data = JobFormData.objects.filter(data_type='Subject')
    qualification_data = JobFormData.objects.filter(data_type='Highest Qualification')
    experience_data = JobFormData.objects.filter(data_type='Experience Required')
    salary_data = JobFormData.objects.filter(data_type='Salary offered')
    benifits_data = JobFormData.objects.filter(data_type='Benefits & compensation')
    free_to_post_job=False
    try:
        facultyme_permission= FacultyMe_Permission.objects.first()
        free_to_post_job=facultyme_permission.free_to_post_job

    except Exception as e:
        pass
    if free_to_post_job == False:
        if not Subscription.objects.filter(user_id=request.user.id).exists():
            return redirect(reverse('institute_pricing'))
        subscription=Subscription.objects.get(user_id=request.user.id)
        if not subscription.is_subscription_valid():
            return redirect(reverse('institute_pricing'))
    context = {
        'page_title':page_title,
        'meta_desc':meta_desc,
        'keyword':keyword,
        'schema':schema,
        'grade_data':grade_data,
        'subject_data':subject_data,
        'qualification_data':qualification_data,
        'experience_data':experience_data,
        'salary_data':salary_data,
        'benifits_data':benifits_data,
    }

    return render(request,'post_job.html',context)
    
def walkin_job(request):
    page_title = "Post a Walk-in Job | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    if not request.user.is_authenticated:
        return redirect('/login')

    grade_data = Grade.objects.all()
    subject_data = JobFormData.objects.filter(data_type='Subject')
    salary_data = JobFormData.objects.filter(data_type='Salary offered')
    
    # Get existing walkin job for this user if any
    existing_job = None
    if request.method == 'GET' and 'job_id' in request.GET:
        job_id = request.GET.get('job_id')
        try:
            # edit any job 
            existing_job = WalkinJob.objects.get(id=job_id)
        except WalkinJob.DoesNotExist:
            existing_job = None  # Explicitly set to None for clarity
    
    free_to_post_walkin = False
    facultyme_permission = FacultyMe_Permission.objects.first()
    if facultyme_permission:
        if hasattr(facultyme_permission, 'free_to_post_walkin_job'):
            free_to_post_walkin = facultyme_permission.free_to_post_walkin_job

    if not free_to_post_walkin and not request.user.is_superuser:
        subscription = SchoolWalkinSubscription.objects.filter(school_id=request.user.id).first()
        if not subscription:
            return redirect(reverse('walkin_pricing'))
    
    payment_price = 0
    payment_settings = PaymentDetails.objects.first()
    if payment_settings:
        # Check if the attribute exists before accessing it
        if hasattr(payment_settings, 'walkin_job_price'):
            payment_price = payment_settings.price
        

    context = {
        'page_title': page_title,
        'meta_desc': meta_desc,
        'keyword': keyword,
        'schema': schema,
        'grade_data': grade_data,
        'subject_data': subject_data,
        'salary_data': salary_data,
        'payment_price': payment_price,
        'min_walkin_date': (datetime.now().date() + timedelta(days=6)).strftime('%Y-%m-%d'),
        'existing_job': existing_job,
    }

    return render(request, 'walkin_job.html', context)

from django.views.decorators.http import require_GET

@require_GET
def subjects_by_grade(request, grade_id):
    """
    API endpoint to return subjects associated with a specific grade
    """
    try:
        # Get the grade
        grade = Grade.objects.get(id=grade_id)
        
        # Get subjects for this grade
        subjects = list(Subject.objects.filter(grade=grade).values_list('name', flat=True).distinct())
        
        # For empty subject lists, return a message
        if not subjects:
            return JsonResponse({
                'success': True,
                'grade_name': grade.name,
                'subjects': [],
                'message': 'No subjects found for this grade'
            })
        
        return JsonResponse({
            'success': True,
            'grade_name': grade.name,
            'subjects': subjects
        })
    except Grade.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Grade not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
                 
def job_posted(request):
    page_title = "Job Posted & Application Received | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""
    posted_jobs_count = 0
    status = request.GET.get('status')
    job_applicant = {}
    
    school = School.objects.filter(user_id=request.user.id).first()
    
    if status:
        if status == 'Expired':        
            posted_jobs = PostJob.objects.filter(user_id=request.user.id).filter(Q(status__iexact=status) | Q(status__iexact='ReApproval') )
            walkin_jobs = WalkinJob.objects.filter(user=school.user).filter(Q(status__iexact=status) | Q(status__iexact='ReApproval') )
        else:
            posted_jobs = PostJob.objects.filter(user_id=request.user.id).filter(status__iexact=status)
            walkin_jobs = WalkinJob.objects.filter(user=school.user).filter(status__iexact=status)
    else:
        posted_jobs = PostJob.objects.filter(user_id=request.user.id)
        walkin_jobs = WalkinJob.objects.filter(user=school.user)

    for pj in posted_jobs:
        job_applicant = JobApplicant.objects.filter(job=pj).filter(Q(status='Approved') | Q(status='Interview Call')).count()
        pj.job_applicant = job_applicant
        
    for wj in walkin_jobs:
        job_applicant = JobApplicant.objects.filter(walkin_job=wj).filter(Q(status='Approved') | Q(status='Interview Call')).count()
        wj.job_applicant = job_applicant
    
    posted_jobs_count = posted_jobs.count() + walkin_jobs.count()
    
    context = {
        'page_title':page_title,
        'meta_desc':meta_desc,
        'keyword':keyword,
        'schema':schema,
        'posted_jobs':list(posted_jobs) + list(walkin_jobs),
        'posted_jobs_count':posted_jobs_count,
        'status':status
    }

    return render(request,'job_posted.html',context)
    
def job_posted_all(request):
    page_title = "All Job Posted | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""
    posted_jobs_count = 0
    status = request.GET.get('status')
    job_applicant = {}
    
    school = School.objects.filter(user_id=request.user.id).first()
    if status:
        if status == 'Expired':            
            posted_jobs = PostJob.objects.filter(user_id=request.user.id).filter(Q(status__iexact=status) | Q(status__iexact='ReApproval') )
            walkin_jobs = WalkinJob.objects.filter(user=school.user).filter(Q(status__iexact=status) | Q(status__iexact='ReApproval') )
        else:
            posted_jobs = PostJob.objects.filter(user_id=request.user.id).filter(status__iexact=status)
            walkin_jobs = WalkinJob.objects.filter(user=school.user).filter(status__iexact=status)
    else:
        posted_jobs = PostJob.objects.filter(user_id=request.user.id)
        walkin_jobs = WalkinJob.objects.filter(user=school.user)

    all_jobs = list(posted_jobs) + list(walkin_jobs)
    
    for pj in posted_jobs:
        job_applicant = JobApplicant.objects.filter(job=pj).count()
        pj.job_applicant = job_applicant
        
    for pj in walkin_jobs:
        job_applicant = JobApplicant.objects.filter(walkin_job=pj).count()
        pj.job_applicant = job_applicant
    
    posted_jobs_count = len(all_jobs)
    
    context = {
        'page_title':page_title,
        'meta_desc':meta_desc,
        'keyword':keyword,
        'schema':schema,
        'posted_jobs':all_jobs,
        'posted_jobs_count':posted_jobs_count,
        'status':status
    }

    return render(request,'job_posted_all.html',context)
  
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import (
    NewUser, SchoolSubscriptionPlan, TeacherSubscriptionPlan, WalkInSubscriptionPlan, 
    PaymentDetails, SchoolWalkinPaymentDetails, Subscription, TeacherSubscription
)
import razorpay

def add_subscription(request):
    # Handle POST purchase attempts. Allow pricing pages to be viewed by guests,
    # but require authentication for selecting/purchasing a plan.
    if request.method == 'POST':
        # If the user is not authenticated, return 401 for AJAX requests so
        # client-side code can handle it, or redirect to login for normal
        # form submits while preserving the referer and plan id.
        if not request.user.is_authenticated:
            is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
            if is_ajax:
                return JsonResponse({'error': 'Authentication required. Please login to select a plan.'}, status=401)
            referer = request.META.get('HTTP_REFERER', request.path)
            plan_id = request.POST.get('plan_id') or request.POST.get('plan')
            # Quote the referer so it can be embedded as the next= parameter
            from urllib.parse import quote
            login_url = f"/login?next={quote(referer, safe='')}"
            if plan_id:
                login_url = f"{login_url}&plan={plan_id}"
            return redirect(login_url)

        counter = 0  # Reset counter at the beginning

        key_id = 'rzp_live_uwg8pkPaoISrGY'
        key_secret = 'hxA68zNj0k0vkyIqVlcmbFdg'
        #key_id='rzp_test_QM9mfvGIXkvMX8' #test
        #key_secret='MjMLzC9nrl0ve0c246KS2AeE' #test

        plan = request.POST.get('plan')
        plan_id = request.POST.get('plan_id')
        jobcode = request.POST.get('jobcode', 'None')
        user_id = request.user.id
        flag = request.POST.get('flag', '0')

        try:
            amount = round(float(request.POST.get('amount')) * 100, 2)
        except ValueError:
            return JsonResponse({'error': 'Invalid amount value'}, status=400)

        exact_amount = amount / 100
        gst_amount = (18 / 100) * exact_amount
        pay_amount = exact_amount + gst_amount
        amount += (gst_amount * 100)

        try:
            user_details = NewUser.objects.get(id=user_id)
        except NewUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=400)

        subscription_plan = None
        remaining_job_post = 0
        remaining_job_apply = 0
        is_walkin_plan = False

        # **Find the right subscription plan based on user type**
        try:
            if user_details.user_type == "School":
                subscription_plan = SchoolSubscriptionPlan.objects.get(id=plan_id)
                remaining_job_post = subscription_plan.allow_number_of_job_post
            elif user_details.user_type == "Teacher":
                subscription_plan = TeacherSubscriptionPlan.objects.get(id=plan_id)
                remaining_job_apply = subscription_plan.allow_number_of_job_apply
        except (SchoolSubscriptionPlan.DoesNotExist, TeacherSubscriptionPlan.DoesNotExist):
            try:
                subscription_plan = WalkInSubscriptionPlan.objects.get(id=plan_id)
                counter = 1  # If found in WalkInSubscriptionPlan, set counter to 1
                is_walkin_plan = True
            except WalkInSubscriptionPlan.DoesNotExist:
                return JsonResponse({'error': 'Invalid Plan ID'}, status=400)

        # **If it's a Walk-in plan, save in SchoolWalkinPaymentDetails**
        if counter == 1:
            SchoolWalkinPaymentDetails.objects.create(
                school=user_details,
                amount=pay_amount,
                subscription_plan=subscription_plan,
                payment_status='pending'
            )

        # **If the plan is free, process the subscription directly**
        if exact_amount == 0.0:
            if is_walkin_plan:
                walkin_sub, created = WalkInSubscriptionPlan.objects.get_or_create(
                    user_id=user_id, subscription_plan=subscription_plan
                )
                walkin_sub.plan = subscription_plan.plan_name
                walkin_sub.save()
                return redirect('/walkin-job')

            elif user_details.user_type == "School":
                school_sub, created = Subscription.objects.get_or_create(
                    user_id=user_id, subscription_plan=subscription_plan
                )
                school_sub.plan = subscription_plan.plan_name
                school_sub.remaining_job_post += remaining_job_post
                school_sub.save()
                return redirect('/post-job' if school_sub.plan == 'FREE PLAN' else '/school-account')

            elif user_details.user_type == "Teacher":
                teacher_sub, created = TeacherSubscription.objects.get_or_create(
                    user_id=user_id, subscription_plan=subscription_plan
                )
                teacher_sub.plan = subscription_plan.plan_name
                teacher_sub.remaining_job_apply += remaining_job_apply
                teacher_sub.save()
                return redirect('/current-vacancies?jobcode=' + jobcode if jobcode != 'None' else '/teacher-account')

        # **If the plan requires payment, initiate Razorpay payment**
        # We need to handle different types of payments depending on the plan type
        if is_walkin_plan:
            # For walk-in plans, store payment details without subscription_plan field
            # (already created a SchoolWalkinPaymentDetails record above)
            # Get the recently created record to use its ID in the payment
            details = SchoolWalkinPaymentDetails.objects.filter(
                school=user_details,
                subscription_plan=subscription_plan,
                payment_status='pending',
                amount=pay_amount
            ).order_by('-created_at').first()
            
            if not details:
                return JsonResponse({'error': 'Failed to create payment record'}, status=500)
        elif user_details.user_type == "School":
            # For school subscriptions, we use PaymentDetails
            details = PaymentDetails.objects.create(
                plan=plan,
                subscription_plan=subscription_plan,  # This expects SchoolSubscriptionPlan
                user_id=user_id,
                amount=pay_amount,
                status='Payment Failed'
            )


            api_url = "https://waba.wapionline.com/api/be6a71dc-8c39-4dc7-bb3c-69c3f76bf4eb/contact/send-template-message?token=QRj3nWECCsifuqnEyTtHRldRP6iQKSicoosF6TVRvZgbj01qkRyptnxeeq58qw8Y"
            template_name = "payment_failure"  # Adjust based on your configuration
            template_language = "en"
            payload = {
                "phone_number": f"91{details.user.mobile_no}",  # Mobile number with country code
                "template_name": template_name,  # Template for teacher welcome message
                "template_language": template_language,  # Language of the template
                "field_1": details.user.name,  # Placeholder for teacher's name
                "field_2": pay_amount,
            }
            headers = {"Content-Type": "application/json"}
            try:
                response = requests.post(api_url, headers=headers, data=json.dumps(payload))
                msg_status = 'Success' if response.status_code == 200 else f'Failed ({response.status_code})'
            except RequestException as e:
                msg_status = f"Error: {str(e)}"

            WhatsAppMessages.objects.create(mobile_no=details.user.mobile_no, msg=json.dumps(payload), status=msg_status)

            
        elif user_details.user_type == "Teacher":
            # For teacher subscriptions
            details = TeacherPaymentDetails.objects.create(
                plan=plan,
                subscription_plan=subscription_plan,  # Assuming this field accepts TeacherSubscriptionPlan
                user_id=user_id,
                amount=pay_amount,
                status='Payment Failed'
            )
            api_url = "https://waba.wapionline.com/api/be6a71dc-8c39-4dc7-bb3c-69c3f76bf4eb/contact/send-template-message?token=QRj3nWECCsifuqnEyTtHRldRP6iQKSicoosF6TVRvZgbj01qkRyptnxeeq58qw8Y"
            template_name = "payment_failure"  # Adjust based on your configuration
            template_language = "en"
            payload = {
                "from_phone_number_id":"579680011898278", # 9663384666
                "phone_number": f"91{details.user.mobile_no}",  # Mobile number with country code
                "template_name": template_name,  # Template for teacher welcome message
                "template_language": template_language,  # Language of the template
                "field_1": details.user.name,  # Placeholder for teacher's name
                "field_2": pay_amount,
            }
            headers = {"Content-Type": "application/json"}
            try:
                response = requests.post(api_url, headers=headers, data=json.dumps(payload))
                msg_status = 'Success' if response.status_code == 200 else f'Failed ({response.status_code})'
            except RequestException as e:
                msg_status = f"Error: {str(e)}"

            WhatsAppMessages.objects.create(mobile_no=details.user.mobile_no, msg=json.dumps(payload), status=msg_status)

        else:
            return JsonResponse({'error': 'Invalid user type'}, status=400)

        client = razorpay.Client(auth=(key_id, key_secret))
        data = {
            "amount": amount, "currency": "INR", "receipt": f"order_rcptid_{details.id}",
            "notes": {
                "order_id": details.id, "name": user_details.name,
                "mobile_no": user_details.mobile_no, "user_type": user_details.user_type,
                "is_walkin": 1 if is_walkin_plan else 0,
                "flag": flag,
                "jobcode":jobcode
            }
        }
        payment = client.order.create(data=data)
        return JsonResponse(payment, content_type="application/json")

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def add_walkin_subscription(request):
    if request.method == 'POST':
        # Require authentication to select/purchase a walk-in plan.
        # Return 401 for AJAX, or redirect to login for normal form submits.
        if not request.user.is_authenticated:
            is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
            if is_ajax:
                return JsonResponse({'error': 'Authentication required. Please login to select a plan.'}, status=401)
            referer = request.META.get('HTTP_REFERER', request.path)
            plan_id = request.POST.get('plan_id') or request.POST.get('plan')
            from urllib.parse import quote
            login_url = f"/login?next={quote(referer, safe='')}"
            if plan_id:
                login_url = f"{login_url}&plan={plan_id}"
            return redirect(login_url)
        key_id = 'rzp_live_uwg8pkPaoISrGY'
        key_secret = 'hxA68zNj0k0vkyIqVlcmbFdg'

        plan = request.POST.get('plan')
        plan_id = request.POST.get('plan_id')
        user_id = request.user.id
        amount = round((int(request.POST.get('amount'))*100),2)
        exact_amount = amount/100
        gst_amount = (18/100)*exact_amount
        pay_amount = exact_amount + gst_amount
        amount += (gst_amount*100)
        user_details = NewUser.objects.get(id=user_id)

        if exact_amount == 0.0:
            subscription_plan = WalkInSubscriptionPlan.objects.get(id=plan_id)
            if not Subscription.objects.filter(user_id=request.user.id, plan__startswith='Walk-in Plan/').exists():
                subscription_added, created = Subscription.objects.get_or_create(
                    user_id=user_id, 
                    subscription_plan=subscription_plan
                )
                Subscription.objects.filter(id=subscription_added.id).update(
                    plan=subscription_plan.plan_name,
                    remaining_job_post=subscription_plan.duration_days
                )
            else:
                subscription_update = Subscription.objects.get(user_id=request.user.id, plan__startswith='Walk-in Plan/')
                subscription_update.subscription_plan = subscription_plan
                subscription_update.plan = subscription_plan.plan_name
                subscription_update.remaining_job_post += subscription_plan.duration_days
                subscription_update.save()
            return redirect('walkin_job_form')  # Redirect to job form instead of school-account
        else:
            subscription_plan = WalkInSubscriptionPlan.objects.get(id=plan_id)
            details = PaymentDetails.objects.create(
                plan=plan,
                subscription_plan=subscription_plan,
                user_id=user_id,
                amount=pay_amount,
                status='Payment Failed'
            )
            api_url = "https://waba.wapionline.com/api/be6a71dc-8c39-4dc7-bb3c-69c3f76bf4eb/contact/send-template-message?token=QRj3nWECCsifuqnEyTtHRldRP6iQKSicoosF6TVRvZgbj01qkRyptnxeeq58qw8Y"
            template_name = "payment_failure"  # Adjust based on your configuration
            template_language = "en"
            payload = {
                "phone_number": f"91{details.user.mobile_no}",  # Mobile number with country code
                "template_name": template_name,  # Template for teacher welcome message
                "template_language": template_language,  # Language of the template
                "field_1": details.user.name,  # Placeholder for teacher's name
                "field_2": pay_amount,
            }
            headers = {"Content-Type": "application/json"}
            try:
                response = requests.post(api_url, headers=headers, data=json.dumps(payload))
                msg_status = 'Success' if response.status_code == 200 else f'Failed ({response.status_code})'
            except RequestException as e:
                msg_status = f"Error: {str(e)}"

            WhatsAppMessages.objects.create(mobile_no=details.user.mobile_no, msg=json.dumps(payload), status=msg_status)

            client = razorpay.Client(auth=(key_id, key_secret))
            data = { 
                "amount": amount, 
                "currency": "INR", 
                "receipt": "order_rcptid_11", 
                "notes": {
                    "order_id": details.id,
                    "name": user_details.name,
                    "mobile_no": user_details.mobile_no, 
                    "user_type": user_details.user_type,
                    "walkin": 1,
                } 
            }
            payment = client.order.create(data=data)
            return JsonResponse(payment, content_type="application/json")
    return redirect('walkin_pricing')

@login_required
def walkin_job_form(request):
    # Check if user has an active subscription
    try:
        subscription = SchoolWalkinSubscription.objects.get(school_id=request.user.id)
        if not subscription:
            messages.error(request, "You have no job postings left in your current plan. Please purchase a new plan.")
            return redirect('walkin_pricing')
        
        context = {
            'subscription': subscription,
        }

       
        return render(request, 'walkin_job.html', context)
    except Subscription.DoesNotExist:
        messages.error(request, "You need to purchase a walk-in plan before posting a job.")
        return redirect('walkin_pricing')

@login_required
def post_walkin_job(request):
    print(request)
    if request.method == 'POST':
        try:
            subscription = SchoolWalkinSubscription.objects.get(school_id=request.user.id)
            
            if not subscription:
                messages.error(request, "You have no job postings left in your current plan.")
                return redirect('walkin_pricing')
            
            grade_ids = request.POST.getlist('teacher_grade[]')
            grade_queryset = Grade.objects.filter(id__in=grade_ids)
            grade_names = [grade.name for grade in grade_queryset] 
            grade_string = str(grade_names)
            # Process the job posting form data
            code=''.join(random.choice(string.digits) for _ in range(3))
            # Create a new WalkinJob instance
            new_job = WalkinJob(
                user=request.user,
                description=request.POST.get('description'),
                teacher_grade=grade_string,
                subject=request.POST.getlist('subject[]'),
                walkin_date=datetime.strptime(request.POST.get('walkin_date'),"%Y-%m-%d").date(),
                contact_name=request.POST.get('contact_name'),
                contact_designation=request.POST.get('contact_designation'),
                contact_mobile=request.POST.get('contact_mobile'),
                alternative_mobile=request.POST.get('alternative_mobile'),
                salary_range=request.POST.get('salary_range'),
                job_code = str(request.user.id)+'W'+code
            )
            new_job.save()
            
          #  subscription.save()
            
            messages.success(request, "Walk-in job posted successfully!")
            return redirect('school_account') 
            
        except Subscription.DoesNotExist:
            messages.error(request, "You need to purchase a walk-in plan before posting a job.")
            return redirect('walkin_pricing')
    
    return redirect('walkin_job')

# Function to get walkin plans for the modal
def get_walkin_plans_context(request):
    walkin_plans = WalkInSubscriptionPlan.objects.all()
    pack_detail = None
    
    if request.user.is_authenticated:
        try:
            pack_detail = Subscription.objects.get(user_id=request.user.id, plan__startswith='Walk-in Plan/')
        except Subscription.DoesNotExist:
            pass
    
    return {
        'walkin_plans': walkin_plans,
        'pack_detail': pack_detail
    }

@method_decorator(csrf_exempt, name='dispatch')
def razor_pay_webhook(request):
 
    client = razorpay.Client(auth=("rzp_live_uwg8pkPaoISrGY", "hxA68zNj0k0vkyIqVlcmbFdg"))        
    resp_json = {}
    payload = {}

    payment_id = request.POST['payment_id']
    user_type = request.POST['user_type']
    resp = client.payment.fetch(payment_id)    
    resp_json[0] = resp   
    status = resp_json[0]["status"]
    amount = resp_json[0]["amount"]
    razorpay_order_id = resp_json[0]["order_id"]
    amount = amount/100
    walkin = request.POST['walkin']
    mobile_no = 0
    if status == 'captured':
        status = 'Payment Successful'
    
    if resp_json[0]["notes"]["order_id"]:
        order_id=resp_json[0]["notes"]["order_id"]
        if user_type == "School":
        
            if walkin:
                SchoolWalkinPaymentDetails.objects.filter(pk=order_id).update(data=resp,payment_id =resp_json[0]["id"], order_id  =razorpay_order_id, razorpay_payment_id=resp_json[0]["id"],razorpay_order_id=razorpay_order_id,amount=amount,status=status,payment_status=status)
                details = SchoolWalkinPaymentDetails.objects.get(pk=order_id)
                subscription_plan=WalkInSubscriptionPlan.objects.get(id=details.subscription_plan.id)
                payload = {
                    "phone_number": f"91{details.school.mobile_no}",
                    "template_name": "payment_successfull",
                    "template_language": "en",
                    "field_1": details.school.name,
                    "field_2":details.amount,  # Customize based on template
                  
                }
                mobile_no = details.school.mobile_no
                if not SchoolWalkinSubscription.objects.filter(school_id=request.user.id).exists():
                    subscription_added, created = SchoolWalkinSubscription.objects.get_or_create(school_id=details.school.id, subscription_plan=subscription_plan)
                    SchoolWalkinSubscription.objects.filter(id=subscription_added.id).update(plan_name=details.subscription_plan.plan_name)
                else:
                    subscription_update=SchoolWalkinSubscription.objects.get(school_id=request.user.id)
                    subscription_update.subscription_plan=subscription_plan
                    subscription_update.plan_name=details.subscription_plan.plan_name
                    subscription_update.save()
            else:
                PaymentDetails.objects.filter(pk=order_id).update(data=resp,razorpay_payment_id=resp_json[0]["id"],razorpay_order_id=razorpay_order_id,amount=amount,status=status)
                details = PaymentDetails.objects.get(pk=order_id)
                subscription_plan=SchoolSubscriptionPlan.objects.get(id=details.subscription_plan.id)
                remaining_job_post=details.subscription_plan.allow_number_of_job_post
                payload = {
                    "phone_number": f"91{details.user.mobile_no}",
                    "template_name": "payment_successfull",
                    "template_language": "en",
                    "field_1": details.user.name,
                    "field_2":details.amount,  # Customize based on template
                  
                }
                mobile_no = details.user.mobile_no
                if not Subscription.objects.filter(user_id=request.user.id).exists():
                    subscription_added, created = Subscription.objects.get_or_create(user_id=details.user.id, subscription_plan=subscription_plan)
                    Subscription.objects.filter(id=subscription_added.id).update(plan=details.plan,remaining_job_post=remaining_job_post)
                else:
                    subscription_update=Subscription.objects.get(user_id=request.user.id)
                    subscription_update.subscription_plan=subscription_plan
                    subscription_update.plan=details.plan
                    subscription_update.remaining_job_post += remaining_job_post
                    subscription_update.save()
        elif user_type == "Teacher": 
            TeacherPaymentDetails.objects.filter(pk=order_id).update(data=resp,razorpay_payment_id=resp_json[0]["id"],razorpay_order_id=razorpay_order_id,amount=amount,status=status)
            details = TeacherPaymentDetails.objects.get(pk=order_id)
            subscription_plan=TeacherSubscriptionPlan.objects.get(id=details.subscription_plan.id)
            remaining_job_apply=details.subscription_plan.allow_number_of_job_apply
            payload = {
                    "from_phone_number_id":"579680011898278", # 9663384666
                    "phone_number": f"91{details.user.mobile_no}",
                    "template_name": "payment_successfull",
                    "template_language": "en",
                    "field_1": details.user.name,
                    "field_2":details.amount,  # Customize based on template
            }
            mobile_no = details.user.mobile_no
            if not TeacherSubscription.objects.filter(user_id=request.user.id).exists():
                subscription_added, created = TeacherSubscription.objects.get_or_create(user_id=details.user.id, subscription_plan=subscription_plan)
                TeacherSubscription.objects.filter(id=subscription_added.id).update(plan=details.plan,remaining_job_apply=remaining_job_apply)
            else:
                subscription_update=TeacherSubscription.objects.get(user_id=request.user.id)
                subscription_update.subscription_plan=subscription_plan
                subscription_update.plan=details.plan
                subscription_update.remaining_job_apply += remaining_job_apply
                subscription_update.save()
            

        payment_details = details
        api_url = "https://waba.wapionline.com/api/be6a71dc-8c39-4dc7-bb3c-69c3f76bf4eb/contact/send-template-message?token=QRj3nWECCsifuqnEyTtHRldRP6iQKSicoosF6TVRvZgbj01qkRyptnxeeq58qw8Y"
        headers = {"Content-Type": "application/json"}
        total_in_words = num2words.num2words(payment_details.amount)
        try:
            response = requests.post(api_url, headers=headers, data=json.dumps(payload))
            msg_status = 'Success' if response.status_code == 200 else f'Failed ({response.status_code})'
        except RequestException as e:
            msg_status = f"Error: {str(e)}"

        WhatsAppMessages.objects.create(mobile_no=mobile_no, msg=json.dumps(payload), status=msg_status)

        # context = {
        #     'name': details.name,
        #     'amount': details.amount,
        #     'payment_details': payment_details,
        #     'total_in_words': total_in_words,
        # }

        # html_message = render_to_string('mail_thankyou.html',context)
        # from_email = 'Inaayat Foundation <'+settings.EMAIL_HOST_USER+'>'
        # subject = "Inaayat Foundation - Thank you for your contribution"
        # message = EmailMultiAlternatives(
        #     subject=subject,
        #     body="",
        #     from_email=from_email,
        #     to=[details.email],
        #     bcc=['']
        #     )
        # message.attach_alternative(html_message, "text/html")
        # message.send(fail_silently=True)
        
        # invoice_page = render_to_string('invoice.html', context)
        # invoice_from_email = 'Inaayat Foundation <'+settings.EMAIL_HOST_USER+'>'
        # invoice_subject = "Inaayat Foundation - Invoice"
        # invoice_message = EmailMultiAlternatives(
        #     subject=invoice_subject,
        #     body="",
        #     from_email=invoice_from_email,
        #     to=[donation_details.email],
        #     bcc=['help@inaayatfoundation.com','yogeshsharmaa17@gmail.com']
        #     )
        # invoice_message.attach_alternative(invoice_page, "text/html")
        # invoice_message.send(fail_silently=True)

    return  JsonResponse({'result':"true"})


def success_razor_pay_payment(request):
    page_title = "Payment Success"
    meta_desc = ""
    keyword = ""
    schema = ""
    return render(request,'static-pages/payment_success.html', {'page_title':page_title,'meta_desc':meta_desc,'keyword':keyword,'schema':schema }) 


def fail_razor_pay_payment(request):
    page_title = "Payment Failed"
    meta_desc = ""
    keyword = ""
    schema = ""
    return render(request,'static-pages/payment_failed.html', {'page_title':page_title,'meta_desc':meta_desc,'keyword':keyword,'schema':schema }) 


def add_school_profile(request):
        
    page_title = "School Account | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    if request.method == 'POST':

        user_id = request.user.id

        website = request.POST.get('website')
        school_email = request.POST.get('school_email')
        institute_type = request.POST.get('institute_type')
        contact_person_name = request.POST.get('contact_person_name')
        contact_person_designation = request.POST.get('contact_person_designation')
        pincode = request.POST.get('pincode')
        state = request.POST.get('state')
        district = request.POST.get('district')
        address = request.POST.get('address')
        primary_mobile=request.POST.get('primary_mobile')
        print( district, " district")
        if School.objects.filter(user_id=user_id).exists():

            School.objects.filter(user_id=user_id).update(
                school_email=school_email,
                website=website,
                institute_type=institute_type,
                contact_person_name=contact_person_name,
                contact_person_designation=contact_person_designation,
                pincode=pincode,
                state=state,
                district=district,
                address=address,
                primary_mobile=primary_mobile,
                )
        else:

            School.objects.create(
                user_id=user_id,
                website=website,
                school_email=school_email,
                institute_type=institute_type,
                contact_person_name=contact_person_name,
                contact_person_designation=contact_person_designation,
                pincode=pincode,
                state=state,
                district=district,
                address=address,
                primary_mobile=primary_mobile,
                )

        messages.success(request, 'Your profile is updated successfully')

    return redirect('/school-account') 

def add_job(request):
        
    page_title = "Add Job | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    if request.method == 'POST':
        
        free_to_post_job=False
        try:
            facultyme_permission= FacultyMe_Permission.objects.first()
            free_to_post_job=facultyme_permission.free_to_post_job

        except Exception as e:
           pass
        if free_to_post_job == False:
            if not Subscription.objects.filter(user_id=request.user.id).exists():
                return redirect(reverse('institute_pricing'))
            subscription=Subscription.objects.get(user_id=request.user.id)
            if not subscription.is_subscription_valid():
                return redirect(reverse('institute_pricing'))
                
        user_id = request.user.id
        UserLog.objects.create(user=request.user,action='New Job Added')

        teacher_grade = request.POST.get('teacher_grade')
        subject = request.POST.get('subject')
        highest_qualification = request.POST.get('highest_qualification')
        experienced_required = request.POST.get('experienced_required')
        salary_offered = request.POST.get('salary_offered')
        joining_date = request.POST.get('joining_date')
        joining = request.POST.get('joining')

        if joining_date:
            try:
                joining_date = datetime.strptime(joining_date, '%d-%m-%Y')
            except:
                joining_date = datetime.strptime(joining_date, '%d/%m/%Y')

            joining_date = joining_date.strftime("%Y-%m-%d")
        benifits_compensation = request.POST.get('benifits_compensation')
        # benifits_compensation = ','.join(benifits_compensation)
        pincode = request.POST.get('pincode')
        state = request.POST.get('state')
        district = request.POST.get('district')
        address = request.POST.get('address')
        expiry_date= datetime.now() + timedelta(days=45)
        description=request.POST.get('description')
        job_code = ''.join(random.choice(string.digits) for _ in range(3))
        job_code = str(user_id)+'J'+job_code
        PostJob.objects.create(
            user_id=user_id,
            teacher_grade=teacher_grade,
            subject=subject,
            highest_qualification=highest_qualification,
            experienced_required=experienced_required,
            salary_offered=salary_offered,
            joining=joining,
            expiry_date=expiry_date,
            benifits_compensation=benifits_compensation,
            pincode=pincode,
            state=state,
            district=district,
            address=address,
            job_code = job_code,
            description=description,
        )
        if free_to_post_job == False:
            subscription.remaining_job_post -= 1
            subscription.save()
        messages.success(request, 'Job is posted successfully')

    return redirect(request.META['HTTP_REFERER'])

def edit_job_submit(request):
        
    page_title = "Add Job | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    if request.method == 'POST':
        job = request.GET.get('job')
        user_id = request.user.id
        UserLog.objects.create(user=request.user,action=str(job)+' Job Updated')

        teacher_grade = request.POST.get('teacher_grade')
        subject = request.POST.get('subject')
        highest_qualification = request.POST.get('highest_qualification')
        experienced_required = request.POST.get('experienced_required')
        salary_offered = request.POST.get('salary_offered')
        joining_date = request.POST.get('joining_date')
        if joining_date:
            joining_date = datetime.strptime(joining_date, '%d-%m-%Y')
            joining_date = joining_date.strftime("%Y-%m-%d")
        benifits_compensation = request.POST.get('benifits_compensation')
        pincode = request.POST.get('pincode')
        state = request.POST.get('state')
        district = request.POST.get('district')
        address = request.POST.get('address')
        joining = request.POST.get('joining')

        PostJob.objects.filter(id=job).update(
            teacher_grade=teacher_grade,
            subject=subject,
            highest_qualification=highest_qualification,
            experienced_required=experienced_required,
            salary_offered=salary_offered,
            joining_date=joining_date,
            joining=joining,
            benifits_compensation=benifits_compensation,
            pincode=pincode,
            state=state,
            district=district,
            address=address,
        )

        messages.success(request, 'Job is updated successfully')

    return redirect(request.META['HTTP_REFERER'])


def application_received(request):
    page_title = "Application Received | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    job_id = request.GET.get('job','')


    if job_id:       
        if JobApplicant.objects.filter(job_id=job_id).exists():
            job_applicant = JobApplicant.objects.filter(job_id=job_id).filter(Q(status='Rejected') | Q(status='Approved') | Q(status='Interview Call')).filter(job__user__id=request.user.id)
        else:
            school = School.objects.filter(user__id= request.GET.get('school')).first()
            job_applicant = JobApplicant.objects.filter(walkin_job_id=job_id).filter(Q(status='Rejected') | Q(status='Approved') | Q(status='Interview Call')).filter(job__user__id=school.user)
        
    context={
        'job_applicant':job_applicant
    }
    return render(request,'application_received.html',context)

def invited_for_interview(request):
    page_title = "Candidates Invited For Interview | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""
    
    posted_jobs = PostJob.objects.filter(user_id=request.user.id).values_list('id', flat=True)
    
    job_applicant = JobApplicant.objects.filter(job_id__in=posted_jobs).filter(Q(status__iexact='Interview Call Request') | Q(status__iexact='Interview Call') | Q(status__iexact='Interview Done') | Q(status__iexact='In Review'))

    context={
        'job_applicant':job_applicant
    }
    return render(request,'invited_for_interview.html', context)

@login_required(login_url='/login')
def teacher_shortlisted(request):
    page_title = "Short Listed by Schools | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""
    number, x = 0, 0

    teacher = Teacher.objects.get(user_id=request.user.id)
    shortlisted = ShortlistedTeachers.objects.filter(teacher=teacher.id, is_review=True).order_by('-timestamp')

    for short in shortlisted:
        school_data = None
        job_id = short.school 
        post_job = PostJob.objects.filter(id=job_id).first()
        if post_job:
            school=School.objects.filter(user_id=post_job.user).first()
            school_data = school
        else:
            walkin = WalkinJob.objects.filter(id=job_id).first()
            if walkin:
                x+=1
                school = School.objects.filter(user=int(walkin.user))
                school_data = school
                
        short.school_data = school_data
        number += 1

    context = {
        'shortlisted': shortlisted,
        'path': request.path,
        'number': number,
        'x': x,
    }

    return render(request, 'teacher-shortlisted.html', context)

@login_required(login_url='/login')
def school_shortlisted(request):
    page_title = "Short Listed Teachers | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    school = School.objects.filter(user_id=request.user.id).first()
    
    shortlisted = ShortlistedTeachers.objects.filter(school=school.id).order_by('-id')
    
    for short in shortlisted:
        school_data = Teacher.objects.filter(id=int(short.teacher)).first()
        short.teacher_data = school_data
    context={
        'shortlisted':shortlisted,
        'path':request.path
    }

    
    return render(request,'school-shortlisted.html',context)
    

@login_required(login_url='/login')
def shortlisted(request):
    page_title = "Short Listed Teachers | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""
   
    # Get all shortlisted teachers
    all_shortlisted = ShortlistedTeachers.objects.filter(is_review=False).order_by('-timestamp')
    
    # Pagination - 20 items per page
    paginator = Paginator(all_shortlisted, 20)
    page_number = request.GET.get('page', 1)
    shortlisted = paginator.get_page(page_number)
   
    # Add additional data to each shortlisted object
    for sl in shortlisted:
        school = School.objects.filter(id=int(sl.school)).first()  
        sl.school = school
        teacher = Teacher.objects.filter(id=sl.teacher).first()
        sl.teacher = teacher
   
    context = {
        'shortlisted': shortlisted,
        'page_title': page_title,
        'meta_desc': meta_desc,
        'keyword': keyword,
        'schema': schema,
        'path': request.path
    }
    
    if request.user.user_type == 'Admin':
        return render(request, 'admin-dashboard/shortlisted.html', context)
    else:
        return redirect('/login')

@login_required(login_url='/login')
def old_shortlisted(request):
    page_title = "Short Listed Teachers | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""
   
    # Get all shortlisted teachers
    all_shortlisted = ShortlistedTeachers.objects.filter(is_review=True).order_by('-id')
    
    # Pagination - 20 items per page
    paginator = Paginator(all_shortlisted, 20)
    page_number = request.GET.get('page', 1)
    shortlisted = paginator.get_page(page_number)
   
    # Add additional data to each shortlisted object
    for sl in shortlisted:
        school = School.objects.filter(id=int(sl.school)).first()  
        sl.school = school

        teacher = Teacher.objects.filter(id=sl.teacher).first()
        sl.teacher = teacher
   
    context={
        'shortlisted':shortlisted,
        'path':request.path
    }
    if request.user.user_type == 'Admin':
        return render(request,'admin-dashboard/old_shortlisted.html',context)
    else:
        return redirect('/login')




def job_pending(request):
    page_title = "Jobs pending for approval  | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    return render(request,'job_pending.html')

def expired_jobs_reapproval_request(request):
    page_title = "Expired Jobs &  Reapprovals Request  | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    return render(request,'expired_jobs_reapproval_request.html')

def institute_pricing_plan(request):
    page_title = "School/Institute Pricing Plan | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    if not request.user.is_authenticated:
        return redirect('/login')

    if request.user.user_type == 'Teacher':
        return redirect('/teacher-pricing')

    # Get subscription details for the current user
    subscription_detail = Subscription.objects.filter(user_id=request.user.id).first()
    walkinsubscription_detail = SchoolWalkinSubscription.objects.filter(school_id=request.user.id).first()
    
    # Initialize
    user_plans = []
    
    # Check for regular subscription plan
    if subscription_detail:
        if "Institute Plan/" in subscription_detail.plan:
            plan_name = subscription_detail.plan.replace("Institute Plan/", "")
            # Find the user's current plan
            current_plan = SchoolSubscriptionPlan.objects.filter(plan_name__icontains=plan_name).first()
            if current_plan:
                # Add amenities to the current plan
                current_plan.amenities = SchoolPlanAmenities.objects.filter(plan_id=current_plan.id)
                user_plans.append(current_plan)
    
    # Check if the user has a FREE plan
    has_free_plan = Subscription.objects.filter(
        plan__icontains="FREE",
        user_id=request.user.id
    ).exists()

    # If no plan is selected or only a free plan is available, set free plan as current
    if not user_plans and has_free_plan:
        free_plan = SchoolSubscriptionPlan.objects.filter(plan_name__icontains="FREE").first()
        if free_plan:
            free_plan.amenities = SchoolPlanAmenities.objects.filter(plan_id=free_plan.id)
            user_plans.append(free_plan)
    
    # Add walk-in subscription plan if it exists
    if walkinsubscription_detail:
        walkin_plan = WalkInSubscriptionPlan.objects.filter(plan_name=walkinsubscription_detail.plan_name).first()
        if walkin_plan:
            walkin_plan.amenities = WalkinPlanAmenities.objects.filter(id=walkin_plan.id)
            walkin_plan.is_walkin = True  # Mark as walk-in for template handling if needed
            user_plans.append(walkin_plan)
    
    # Job count for the current user
    posted_jobs = PostJob.objects.filter(user_id=request.user.id)
    count = []
    count.append(len(posted_jobs.filter(status='Approved')))
    count.append(len(posted_jobs.filter(status='Expired')))
    count.append(len(posted_jobs.filter(status='New')))
    count.append(len(posted_jobs.filter(status='Pending')))
    context = {
        'page_title': page_title,
        'meta_desc': meta_desc,
        'keyword': keyword,
        'schema': schema,
        'school_plans': user_plans,  # Pass all user plans including walk-in if it exists
        'subscription_detail': subscription_detail,
        'walkinsubscription_detail': walkinsubscription_detail,
        'approved_job_count': count[0],
        'expired_job_count': count[1],
        'new_job_count': count[2],
        'pending_job_count': count[3],
        'wj_approved_job_count': WalkinJob.objects.filter(user=request.user, status='Approved').count(),
        'wj': WalkinJob.objects.filter(user=request.user).count(),
        'wj_new_job_count': WalkinJob.objects.filter(user=request.user, status='New').count(),
        
    }

    return render(request,'institute_pricing_plan.html',context)

def help_support(request):
    page_title = "Help & Support | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    return render(request,'help_support.html')


def forgot_password_pin(request):
    try:

        mobile_no = request.POST.get('mobile_no', '')
        new_user = NewUser.objects.get(mobile_no=mobile_no)
        otp_code = ''.join(random.choice(string.digits) for _ in range(4))
        # Update password via model instance to ensure proper hashing
        user_obj = NewUser.objects.filter(mobile_no=mobile_no).first()
        if user_obj:
            user_obj.set_password(otp_code)
            user_obj.is_mobile_no_verified = True
            user_obj.is_active = True
            user_obj.save()
            
        if new_user:
            UserLog.objects.create(user=new_user,action='Forgot PIN')

            try:
                status, response_text = send_sms_via_msg91(mobile_no, template_id=PIN_TEMPLATE_ID, template_vars={'OTP': otp_code})
                print(f'MSG91 send (forgot PIN) response: status={status}, body={response_text}')
                messages.success(request, 'PIN reset please use it for login')
                return redirect('/login')
            except Exception as e:
                print('SMS send failed (forgot PIN):', e)
                messages.error(request, 'Unable to send PIN right now. Please try again later.')
                return redirect('/forgot-password')
        else:
            messages.error(request, 'PIN change not done')
            return redirect('/forgot-password')
    except:
        messages.success(request, 'You are not registered')
        return redirect('/forgot-password')

def set_promotion(request):
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    job_id = request.GET.get('job', '')
    job = PostJob.objects.get(id=job_id)
    res = JobPromotions.objects.update_or_create(job=job,start_date=start_date,end_date=end_date)
    PostJob.objects.filter(id=job_id).update(promo_applied=True)
    if res:
        return JsonResponse(True, safe=False)
    else:
        return JsonResponse(False, safe=False)
    
def apply_for_job(request):
    job = request.GET.get('job', '')
    jobcode = request.GET.get('jobcode','')

    teacher = Teacher.objects.filter(user_id=request.user.id).first()
    free_to_apply_job=False
    if PostJob.objects.filter(id=job).exists():
        job_obj=PostJob.objects.get(id=job)
        free_to_apply =job_obj.free_to_apply
    else:
        job_obj=WalkinJob.objects.get(id=job)
        free_to_apply = job_obj.free_to_apply
    subscription=False


    # print(teacher)
    if teacher == None:
        return HttpResponseRedirect('/teacher-profile?job='+job+'&jobcode='+jobcode)
    else :  
        try:
            facultyme_permission= FacultyMe_Permission.objects.first()
            free_to_apply_job=facultyme_permission.free_to_apply_job
        except Exception as e:
            pass
        if free_to_apply == False:
                if request.user.user_type != "Admin":
                    if not TeacherSubscription.objects.filter(user_id=request.user.id).exists():
                        return redirect(reverse('teacher_pricing')+'?job='+job+'&jobcode='+jobcode)
                    subscription=TeacherSubscription.objects.get(user_id=request.user.id)
                    if not subscription.is_subscription_valid():
                        return redirect(reverse('teacher_pricing')+'?job='+job+'&jobcode='+jobcode)
        if (teacher.gender and teacher.qualification and teacher.subject_of_specialization and teacher.experience_type and teacher.expected_salary):
            if ((teacher.experience_in and teacher.subject_of_experience and teacher.years_of_experience and teacher.current_salary) or (teacher.want_to_teach_for and teacher.subject_i_teach) ):
                if PostJob.objects.filter(id=job).exists():
                    res = JobApplicant.objects.update_or_create(teacher=teacher, job_id=job)
                else:
                    res = JobApplicant.objects.update_or_create(teacher=teacher, walkin_job_id=job)
                UserLog.objects.create(user=request.user,action='Job Application')
                if not free_to_apply  and request.user.user_type != "Admin" and subscription:
                    if subscription.remaining_job_apply is not None and subscription.remaining_job_apply > 0:
                        subscription.remaining_job_apply -= 1
                        subscription.save()
                    else:
                        messages.warning(request, "You have no remaining job applications left in your subscription.")
                ShortlistedTeachers.objects.update_or_create(teacher=teacher.id,school=job, is_review=False)
                messages.success(request, 'Applied successfully')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER')) 
            else:
                return HttpResponseRedirect('/teacher-profile?job='+job+'&jobcode='+jobcode)
                
        else:    
            return HttpResponseRedirect('/teacher-profile?job='+job+'&jobcode='+jobcode)
from django.utils import timezone
def get_sort_key(job):
    dt = job.timestamp  # This could be a datetime.date or datetime.datetime

    # Convert date to datetime if needed
    if isinstance(dt, datetime.date) and not isinstance(dt, datetime.datetime):
        dt = datetime.datetime.combine(dt, datetime.datetime.min.time())

    # Now check if it's naive and make it aware
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt)

    return dt


def current_vacancies(request):  
    page_title = "Current Vacancies | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""
    
    # Get filter parameters 
    grades = request.GET.getlist('grade', [])  
    subject = request.GET.getlist('subject', []) 
    state = request.GET.get('state', '')
    job_code = request.GET.get('jobcode', '')
    
    # Get the page number from the request
    page = request.GET.get('page', 1)
    try:
        page = int(page)
    except ValueError:
        page = 1
    
    current_date = timezone.now().date()

    grade_categories = Grade.objects.all().order_by('name')
    salary_offered = JobFormData.objects.filter(data_type='Salary offered')
    qualification = JobFormData.objects.filter(data_type='Highest Qualification')
    subjects = JobFormData.objects.filter(data_type='Subject')
    experience = JobFormData.objects.filter(data_type='Experience Required')

    jobs = PostJob.objects.filter(Q(status__iexact='Approved') | Q(status__iexact ='Expired')).order_by('-promo_applied','-id')
    walkin_jobs = WalkinJob.objects.filter(Q(status__iexact='Approved') | Q(status__iexact ='Expired') | Q(walkin_date__gte=current_date)).order_by('-promo_applied','-id')
    
    if grades:
        grade_filter = Q()
        for grade in grades:
            grade_filter |= Q(teacher_grade__icontains=grade)
        jobs = jobs.filter(grade_filter)
        
        walkin_grade_filter = Q()
        for grade in grades:
            walkin_grade_filter |= Q(teacher_grade__icontains=grade)
        walkin_jobs = walkin_jobs.filter(walkin_grade_filter)
        
    if subject:
        # Filter jobs that match any of the selected subjects
        subject_filter = Q()
        for sub in subject:
            subject_filter |= Q(subject__icontains=sub)
        jobs = jobs.filter(subject_filter)
        
        walkin_subject_filter = Q()
        for sub in subject:
            walkin_subject_filter |= Q(subject__icontains=sub)
        walkin_jobs = walkin_jobs.filter(walkin_subject_filter)
        
    if state:
        jobs = jobs.filter(state__iexact=state)
        # walkin_jobs = walkin_jobs.filter(state__iexact=state) 
    if job_code and job_code != 'None':
        jobs = jobs.filter(job_code__iexact=job_code)
        walkin_jobs = walkin_jobs.filter(job_code__iexact=job_code)
    
    # Attach school information to walkin jobs AFTER filtering
    schools=[]
    for job in walkin_jobs:
        new_user = NewUser.objects.filter(mobile_no=job.user).first()
        school = School.objects.filter(user_id=new_user).first()
        if school:
            school_data = SimpleNamespace(
                            id=school.id,
                            school_name=school.user.name,
                            school_email=school.school_email,
                            website=school.website,
                            institute_type=school.institute_type,
                            contact_person_name=school.contact_person_name,
                            contact_person_designation=school.contact_person_designation,
                            pincode=school.pincode,
                            state=school.state,
                            district=school.district,
                            address=school.address,
                            primary_mobile=school.primary_mobile,
                            secondary_mobile=school.secondary_mobile
                        )
            schools.append(school_data)
            job.user = school_data
            
    state_data = State.objects.all()
    job_applicant_list = []
    if request.user.id:
        try:
            UserLog.objects.create(user=request.user, action='Job Search')
            teacher = Teacher.objects.get(user_id=request.user.id)
            job_applicant = JobApplicant.objects.filter(teacher=teacher)
            for job_applicant in job_applicant:
                job_applicant_list.append(job_applicant.job.id)
        except:
            pass
    
    job_list = list(jobs)
    walkin_job_list = list(walkin_jobs)
    
    for job in job_list:
        job.job_type = 'regular'
        if job.id in job_applicant_list:
            job.is_applied = True
        else:
            job.is_applied = False
    
    for job in walkin_job_list:
        job.job_type = 'walkin'
        job.is_applied = True 
        
        if hasattr(job, 'teacher_grade') and job.teacher_grade:
            if isinstance(job.teacher_grade, str) and job.teacher_grade.startswith("["):
                try:
                    job.teacher_grade = ', '.join(eval(job.teacher_grade))
                except:
                    pass
            elif isinstance(job.teacher_grade, list):
                job.teacher_grade = ', '.join(job.teacher_grade)
    
    combined_jobs = job_list + walkin_job_list
    
    # Sort by timestamp (newest first) -
    def get_sort_key(obj):
        # For regular jobs that have a timestamp attribute
        if hasattr(obj, 'timestamp') and obj.timestamp is not None:
            dt = obj.timestamp
        # For walkin jobs
        elif hasattr(obj, 'walkin_date') and obj.walkin_date is not None:
            dt = datetime.combine(obj.walkin_date, datetime.min.time())
        else:
            dt = timezone.now()

        # Ensure datetime is timezone-aware
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt)
        return dt
    
    combined_jobs.sort(key=get_sort_key, reverse=True)
    jobs_count = len(combined_jobs)

    paginator = Paginator(combined_jobs, 18) 
    
    try:
        paginated_jobs = paginator.page(page)
    except EmptyPage:
        # If page is out of range, deliver last page
        paginated_jobs = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        paginated_jobs = paginator.page(1)

    state_district = {}
    # Now use paginated_jobs instead of jobs for the loop
    for job in paginated_jobs:
        # Only process state/district for regular jobs
        if hasattr(job, 'state') and job.state:
            try:
                if not state_district.get(job.state):            
                    state_district.update({ job.state : []})
            except:
                state_district.update({ job.state : []})

            if hasattr(job, 'district') and job.district and job.district not in state_district[job.state]:
                state_district[job.state].append(job.district)
      
        if hasattr(job, 'teacher_grade') and job.teacher_grade:
            if isinstance(job.teacher_grade, list):
                job.teacher_grade = ', '.join(job.teacher_grade)
            elif isinstance(job.teacher_grade, str) and job.teacher_grade.startswith("["):
                try:
                    job.teacher_grade = ', '.join(eval(job.teacher_grade))  # Safely convert stringified list to str
                except:
                    pass
            findgrade = grade_categories.filter(name__iexact=job.teacher_grade).first()
            if findgrade and findgrade.ishidden:
                job.teacher_grade = ""
        
        # Clean up subject if it's a list
        if hasattr(job, 'subject') and job.subject:
            if isinstance(job.subject, list):
                job.subject = ', '.join(job.subject)
            elif isinstance(job.subject, str) and job.subject.startswith("["):
                try:
                    job.subject = ', '.join(eval(job.subject))
                except:
                    pass
    
    grade_list = []
    for gradei in grade_categories:
        dis_data = TeacherSubject.objects.filter(grade__name__iexact=gradei.name).order_by('name')
        for g in dis_data:
            if not subject or g.name != subject:
                grade_list.append(g.name)
        
        dis_data_1 = Subject.objects.filter(grade__name__iexact=gradei.name).order_by('name')
        for gg in dis_data_1:
            if not subject or gg.name != subject:
                grade_list.append(gg.name)

    grade_list = list(set(grade_list))
  
    context = {
        'jobs': paginated_jobs,  # Now using paginated jobs
        'jobs_count': jobs_count,
        'grade_categories': grade_categories,
        'salary_offered': salary_offered,
        'subjects': sorted(grade_list),
        'experience': experience,
        'qualification': qualification,
        'grades': sorted(grades), 
        'subject_s': subject,
        'job_applicant_list': job_applicant_list,
        'state_data': state_data,
        'state_s': state,
        'page_title': page_title,
        'paginator': paginator,  # paginator 
        'page_obj': paginated_jobs,  # page object
    }
    return render(request, 'current_vacancies.html', context)

def find_teachers(request):
    page_title = "Find Teachers | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""
    per_page = 50  # Items per page
    page = request.GET.get('page', 1)

    if request.user.is_authenticated:
        UserLog.objects.create(user=request.user, action='Teacher Search')

    # Fetching and filtering teachers
    teachers_query = Teacher.objects.exclude(
        user__name__isnull=True
    ).exclude(
        experience_in__isnull=True
    ).exclude(
        qualification__isnull=True
    ).exclude(
        current_salary__isnull=True
    ).exclude(
        expected_salary__isnull=True
    ).exclude(
        preferred_location_district__isnull=True
    ).filter(status__iexact='Approved')

    experience_in = request.GET.get('experience_in', '')
    subject = request.GET.get('subject', '')
    state = request.GET.get('state', '')
    
    # Track if any filter is applied
    filter_applied = bool(experience_in or subject or state)

    if experience_in:
        teachers_query = teachers_query.filter(
            Q(experience_in__icontains=experience_in) |
            Q(want_to_teach_for__icontains=experience_in)
        )

    if subject:
        teachers_query = teachers_query.filter(
            Q(subject_of_experience__icontains=subject) |
            Q(subject_i_teach__icontains=subject)
        )

    if state:
        teachers_query = teachers_query.filter(preferred_location_district__icontains=state)
        
    posted_jobs = PostJob.objects.filter(user_id=request.user.id)
    jobs_count = posted_jobs.count()

    # Get total count first
    total_teachers = teachers_query.count()
    
    # Apply pagination only if no filter is applied, otherwise show all results
    paginator = Paginator(teachers_query, per_page)
    try: 
        page = int(page)
        if page < 1:
            page = 1
        elif page > paginator.num_pages:
            page = paginator.num_pages
    except ValueError:
        page = 1
            
    teachers_data = paginator.get_page(page)
    
    
    # Other data fetching for the form
    qualification_data = TeacherFormData.objects.filter(data_type='Qualification')
    specialization_data = TeacherFormData.objects.filter(data_type='Subject Specialzation')
    experience_type_data = TeacherFormData.objects.filter(data_type='Experience Type')
    expected_salary_data = TeacherFormData.objects.filter(data_type='Expected Salary')
    experience_in_data = TeacherGrade.objects.all().order_by('name')
    experience_subject_data = TeacherFormData.objects.filter(data_type='Subject of Experience')
    experience_year_data = TeacherFormData.objects.filter(data_type='Years of experience')
    current_salary_data = TeacherFormData.objects.filter(data_type='Current Salary')
    experience_in_fresher_data = TeacherFormData.objects.filter(data_type='I want to teach for')
    subject_teach_fresher_data = TeacherFormData.objects.filter(data_type='Subject i can teach')
    state_data = State.objects.all()
    subject_data = TeacherSubject.objects.filter(grade__name=experience_in).order_by('name').distinct('name')
    
    state_district = {}
    for job in teachers_data:
        school = School.objects.filter(user_id=request.user.id).first()  

        is_short = ShortlistedTeachers.objects.filter(teacher__iexact=str(job.id)).filter(school=school.id).first() if school else None
 
        if is_short:
            job.is_short = True
        else:
            job.is_short = False

        try:
            birth = datetime.datetime.strptime(job.dob, '%Y-%m-%d').date()
            age = (date.today() - birth) // timedelta(days=365.2425)
            job.age = int(age)
        except:
             job.age = 1
        try:
            if not state_district.get(job.address_state):            
                state_district.update({ job.address_state : []})
        except:
            state_district.update({ job.address_state : []})
        if not job.address_district in state_district[job.address_state]:
            state_district[job.address_state].append(job.address_district)
    
    # Construct pagination URL parameters
    get_params = request.GET.copy()
    if 'page' in get_params:
        del get_params['page']
    query_string = get_params.urlencode()
    pagination_base_url = f"?{query_string}&" if query_string else "?"

    context = {
        'teachers_data': teachers_data,
        'teachers_data_count': total_teachers,
        'total_teachers': total_teachers,
        'qualification_data': qualification_data,
        'specialization_data': specialization_data,
        'experience_type_data': experience_type_data,
        'expected_salary_data': expected_salary_data,
        'experience_in_data': experience_in_data,
        'experience_subject_data': experience_subject_data,
        'experience_year_data': experience_year_data,
        'current_salary_data': current_salary_data,
        'experience_in_fresher_data': experience_in_fresher_data,
        'subject_teach_fresher_data': subject_teach_fresher_data,
        'subject_s': subject,
        'experience_in_s': experience_in,
        'state_data': state_data,
        'state_s': state,
        'page_title': page_title,
        'subject_data': subject_data,
        'pagination_base_url': pagination_base_url,
        'filter_applied': filter_applied,
        'page': page,
        'per_page': per_page,
        'jobs_count': jobs_count
    }

    return render(request, 'find_teachers.html', context)

def load_subject(request):
    grade = request.GET.get('grade')
    dis_data = Subject.objects.filter(grade__name=grade).order_by('name')
    
    new_dict=[]
    for dd in dis_data:
        new_dict.append(dd.name)

    return JsonResponse(new_dict, safe=False)


def get_district(request):
    state = request.GET.get('state')
    dis_data = District.objects.filter(state__name=state)
 
    new_dict=[]
    for dd in dis_data:
        new_dict.append(dd.name)

    return JsonResponse(new_dict, safe=False)

def job_alert(request):
    page_title = "Job Alert | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""
    subject_list = []
    state_data = State.objects.all()
    grade_data = TeacherGrade.objects.all().order_by('name')
    subject_data = TeacherSubject.objects.all().order_by('name')

    for sd in subject_data:
        subject_list.append(sd.name)
    subject_list = [*set(subject_list)]

    context = {
        'state_data':state_data,
        'grade_data':grade_data,
        'subject_data':subject_list
    }
    return render(request,'job_alert.html', context)

def teacher_application_rejected(request):
    page_title = "Application Rejected | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    return render(request,'teacher_application_rejected.html')

@login_required(login_url='/login')
def admin_dashboard(request):
    # Get the filter date from request
    #filter_date = request.GET.get('date')
    from_date=request.GET.get('from_date')
    to_date=request.GET.get('to_date')
    if not from_date :
        from_date = datetime.now().strftime('%Y-%m-%d')
    if not to_date :
        to_date = datetime.now().strftime('%Y-%m-%d')
    
    
      # Base query sets
    teachers = Teacher.objects.all()
    schools = School.objects.all()
    job_applicants = JobApplicant.objects.all()
    jobs = PostJob.objects.all()
    shortlisted = ShortlistedTeachers.objects.all()
    total_visitor= DailyVisitorCount.objects.all()
    expired_teacher = teachers.filter(status__iexact='Expired').count()
    expired_jobs = jobs.filter(Q(status__iexact='Expired') | Q(status__iexact='Disabled') | Q(expiry_date__lte=timezone.now().date())).count()

    # Apply date filter if provided
    if from_date and to_date:
        try:
            #filter_date = datetime.strptime(filter_date, '%Y-%m-%d').date()
            fd=datetime.strptime(from_date, '%Y-%m-%d').date()
            td=datetime.strptime(to_date, '%Y-%m-%d').date()
            teachers = teachers.filter(timestamp__date__range=[fd,td]).filter(status__iexact='New')
            schools = schools.filter(timestamp__date__range=[fd,td]).filter(status__iexact='New')
            job_applicants = job_applicants.filter(timestamp__date__range=[fd,td]).filter(status__iexact='New')
            jobs = jobs.filter(timestamp__date__range=[fd,td]).filter(status__iexact='New')
            expired_teacher = teachers.filter(status__iexact='Expired', timestamp__date__range=[fd,td]).count()
            expired_jobs = jobs.filter(Q(status__iexact='Expired') | Q(status__iexact='Disabled') | Q(expiry_date__lte=timezone.now().date()), timestamp__date__range=[fd,td]).count()
            total_visitor= total_visitor.filter(date__range=[fd,td])
            shortlisted = shortlisted.filter(timestamp__date__range=[fd,td]).filter(is_review=False)

        except ValueError:
            # Handle invalid date format
            pass

    # If no filter date is provided, use the original logic
    if not from_date and not to_date:
        current_date = timezone.now().date()
        current_date1 = timezone.now()
        one_week_ago = current_date1 - timezone.timedelta(weeks=1)

        teacher_count = teachers.filter(status__iexact='New').count()
        school_count = schools.filter(status__iexact='New').count()
        job_applicant_count = job_applicants.filter(status__iexact='New').count()
        new_job_count = jobs.filter(status__iexact='New').count()
        interview_calls_count = job_applicants.filter(status__iexact='Interview Call Request').count()
        expired_teacher_count = expired_teacher.count()
        expired_job_count = expired_jobs.count()
        shortlisted_count = shortlisted.filter(is_review=False).count()
        total_visitor_count = DailyVisitorCount.objects.all().count()
    else:
        # If filter date is provided, use the filtered querysets - Update it will get call everytime :)
        teacher_count = teachers.filter(status__iexact='New').count()
        school_count = schools.filter(status__iexact='New').count()
        job_applicant_count = job_applicants.filter(status__iexact='New').count()
        interview_calls_count = job_applicants.filter(status__iexact='Interview Call Request').count()
        expired_teacher_count = teachers.filter(status__iexact='Expired').count()
        expired_job_count = jobs.filter(Q(status__iexact='Expired') | Q(status__iexact='Disabled') | Q(expiry_date__lte=timezone.now().date())).count()
        shortlisted_count = shortlisted.count()
        total_visitor_count = total_visitor.count()
        new_job_count = jobs.filter(status__iexact='New').count()
        expired_teacher_count = teachers.filter(status__iexact='Expired').count()
        expired_job_count = jobs.filter(Q(status__iexact='Expired') | Q(status__iexact='Disabled') | Q(expiry_date__lte=timezone.now().date())).count()
        #total_visitor_count = DailyVisitorCount.objects.all().count()
    context = {
        'page_title': 'Admin Dashboard',
        'teacher_count': teacher_count,#
        'school_count': school_count,#
        'job_applicant_count': job_applicant_count,#
        'total_visitor_count': total_visitor_count,#
        'new_job_count': new_job_count,
        'expired_job_count': expired_job_count,
        'expired_teacher_count': expired_teacher_count,
        'interview_calls_count': interview_calls_count,
        'shortlisted_count': shortlisted_count,
        'filter_date':  {'from_date':from_date,'to_date':to_date},
        
    }

    return render(request, 'admin-dashboard/admin_dashboard.html', context)

@login_required(login_url='/login')
def current_application(request):
    path = request.path
    page_title = "New Applications | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""
    
    try:
        if request.GET.get('school'):
            school = request.GET.get('school')
            school_first = School.objects.filter(user__name=school).first()
            if JobApplicant.objects.filter(job__user_id=school_first.user.id).exists():
                job_applications = JobApplicant.objects.filter(job__user_id=school_first.user.id).filter(status__iexact='New').order_by('-timestamp')
            else:
                job_applications = JobApplicant.objects.filter(walkin_job__user_id=school_first.user.id).filter(status__iexact='New').order_by('-timestamp')
        else:
            job_applications = JobApplicant.objects.filter(status__iexact='New').order_by('-timestamp')
    except:
        job_applications = JobApplicant.objects.filter(status__iexact='New').order_by('-timestamp')
    
    context = {
        'path': path,
        'job_applications':job_applications,
        'page_title':page_title,
    }

    if request.user.user_type == 'Admin':
        return render(request,'admin-dashboard/current_application.html',context)
    else:
        return redirect('/login')
    
@login_required(login_url='/login')
def approved_application(request):
    path = request.path
    page_title = "Approved Applications | Faculty Me"
    items_per_page = 10
    
    try:
        # Check if school filter is applied
        if request.GET.get('school'):
            school = request.GET.get('school')
            school_first = School.objects.filter(user__name=school).first()
            post_job_applications = JobApplicant.objects.filter(job__user_id=school_first.user.id, status__iexact='Approved').order_by('-timestamp')
            walkin_job_applications = JobApplicant.objects.filter(walkin_job__user_id=school_first.user.id, status__iexact='Approved').order_by('-timestamp')
            
            job_applications = list(post_job_applications) + list(walkin_job_applications)
        else:
            job_applications = JobApplicant.objects.filter(status__iexact='Approved').order_by('-timestamp')
        
        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(job_applications, items_per_page)
        
        try:
            job_applications = paginator.page(page)
        except PageNotAnInteger:
            job_applications = paginator.page(1)
        except EmptyPage:
            job_applications = paginator.page(paginator.num_pages)
        
    except Exception as e:
        job_applications = JobApplicant.objects.filter(status__iexact='Approved').order_by('-timestamp')
        page = request.GET.get('page', 1)
        paginator = Paginator(job_applications, items_per_page)
        
        try:
            job_applications = paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            job_applications = paginator.page(1)
    
    context = {
        'path': path,
        'job_applications': job_applications,
        'page_title': page_title,
        'paginator': paginator 
    }
    
    if request.user.user_type == 'Admin':
        return render(request, 'admin-dashboard/approved_application.html', context)
    else:
        return redirect('/login')
      
@login_required(login_url='/login')
def rejected_applications(request):
    path = request.path
    page_title = "Rejected Applications | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    try:
        if request.GET.get('school'):
            school = request.GET.get('school')
            school_first = School.objects.filter(user__name=school).first()
            job_applications = JobApplicant.objects.filter(job__user_id=school_first.user.id).filter(status__iexact='Approved')
        else:
            job_applications = JobApplicant.objects.filter(status__iexact='Approved')
    except:
        job_applications = JobApplicant.objects.filter(status__iexact='Approved')

    context = {
        'path': path,
        'job_applications':job_applications,
        'page_title':page_title,
    }

    if request.user.user_type == 'Admin':
        return render(request,'admin-dashboard/rejected_applications.html',context)
    else:
        return redirect('/login')
    
@login_required(login_url='/login')
def job_application_candidate(request):
    path = request.path
    page_title = "Applications | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""
    job_id = request.GET.get('job_id')
    
    post_job = PostJob.objects.get(id=job_id)
    job_applications = JobApplicant.objects.filter(job=post_job)
    
    context = {
        'path': path,
        'job_applications':job_applications,
        'page_title':page_title,
        'job_code':post_job.job_code,
        'school':post_job.user.name,
        'job':post_job
    }

    if request.user.user_type == 'Admin':
        return render(request,'admin-dashboard/job_application_candidate.html',context)
    else:
        return redirect('/login')

@login_required(login_url='/login')
def new_interview_calls(request):
    path = request.path
    page_title = "New Interview Calls | Faculty Me"

    # Use case-insensitive contains to catch variations
    job_applications = JobApplicant.objects.filter(
        Q(status__icontains='interview') | 
        Q(status__icontains='call') | 
        Q(status='Interview Call')
    ).select_related(
        'teacher', 
        'teacher__user', 
        'job', 
        'job__user'
    )
    #print("Available status values:", JobApplicant.objects.values_list('status', flat=True).distinct())
    # print(f"Total matching applications: {job_applications.count()}")
    # if not job_applications.exists():
    #     print("No job applications found matching interview call criteria")
    context = {
        'path': path,
        'job_applications': job_applications,
        'page_title': page_title,
    }

    if request.user.user_type == 'Admin':
        return render(request, 'admin-dashboard/new_interview_calls.html', context)
    else:
        return redirect('/login')

@login_required(login_url='/login')
def approved_interview_calls(request):
    path = request.path
    page_title = "Approved Interview Calls | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""
    school_list=[]

    try:
        if request.GET.get('school'):
            school = request.GET.get('school')
            school_first = School.objects.filter(user__name=school).first()
            job_applications = JobApplicant.objects.filter(job__user_id=school_first.user.id).filter(status__iexact='Interview Call').order_by('-timestamp')
        else:
            job_applications = JobApplicant.objects.filter(status__iexact='Interview Call').order_by('-timestamp')
    except:
        job_applications = JobApplicant.objects.filter(status__iexact='Interview Call').order_by('-timestamp')
        
    context = {
        'path': path,
        'job_applications':job_applications,
        'page_title':page_title,
        'school_list':school_list
    }

    if request.user.user_type == 'Admin':
        return render(request,'admin-dashboard/approved_interview_calls.html',context)
    else:
        return redirect('/login')
        
@login_required(login_url='/login')
def interview_calls_school(request):
    path = request.path
    page_title = "Interview Calls | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""
    school_list=[]

    schools = School.objects.all()
    for school in schools:
        temp_dic = {} 
        # try:
        job_applications = JobApplicant.objects.filter(job__user=school.user)
        if job_applications:
            # new_job_applicant_count = JobApplicant.objects.filter(job__user=school.user).filter(status__iexact='New').count()
            new_job_applicant_count = JobApplicant.objects.filter(job__user=school.user, status__iexact='New').count()
            approved_job_applicant_count = JobApplicant.objects.filter(job__user=school.user).filter(status__iexact='Approved').count()

            new_interview_count = JobApplicant.objects.filter(job__user=school.user).filter(status__iexact='Interview Call Request').count()
            approved_interview_count = JobApplicant.objects.filter(job__user=school.user).filter(status__iexact='Interview Call').count()

            new_job_count = PostJob.objects.filter(user=school.user).filter(status__iexact='New').count()
            approved_job_count = PostJob.objects.filter(user=school.user).filter(status__iexact='Approved').count()
       

            # interview_calls_count = JobApplicant.objects.filter(status__iexact='Interview Call').count()
            # expired_teacher_count = Teacher.objects.filter(status__iexact='Expired').count()
            # expired_job_count = PostJob.objects.filter(status__iexact='Expired').count()

            context={
                'new_job_count':new_job_count,
                'approved_job_count':approved_job_count,
                'new_interview_count':new_interview_count,
                'approved_interview_count':approved_interview_count,
                'new_job_applicant_count':new_job_applicant_count,
                'approved_job_applicant_count':approved_job_applicant_count,
                'page_title':page_title,
                'path':path 
            }
            try:
                temp_dic[school.user.name] = context
            except:
                pass
            school_list.append(temp_dic)
        # except:
        #     pass
    
    context = {
        'path': path,
        'job_applications':job_applications,
        'page_title':page_title,
        'school_list':school_list
    }

    if request.user.user_type == 'Admin':
        return render(request,'admin-dashboard/interview_calls_school.html',context)
    else:
        return redirect('/login')
        
@login_required(login_url='/login')
def recent_login_teacher(request):
    path = request.path
    page_title = "Recent Login Teacher | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""
    # users =NewUser.objects.filter(user_type='Teacher', last_login__isnull=False).order_by('-last_login')
    users = NewUser.objects.filter(user_type='Teacher', last_login__gte=timezone.now() - timezone.timedelta(days=5)).order_by('-last_login')
    for user in users:
        teacher = Teacher.objects.filter(user_id=user.id).first()
        user.teacher = teacher
        
    context = {
        'path': path,
        'page_title':page_title,
        'users':users,
    }
    
    if request.user.user_type == 'Admin':
        return render(request,'admin-dashboard/recent_login_teacher.html',context)
    else:
        return redirect('/login')

@login_required(login_url='/login')
def recent_login_school(request):
    path = request.path
    page_title = "Recent Login School | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    users = NewUser.objects.filter(user_type='School',last_login__gte=timezone.now() - timezone.timedelta(days=5)).order_by('-last_login')
   
    for user in users:
        school = School.objects.filter(user_id=user.id).first()
        user.school = school
        
    context = {
        'path': path,
        'page_title':page_title,
        'users':users
    }
    
    if request.user.user_type == 'Admin':
        return render(request,'admin-dashboard/recent_login_school.html',context)
    else:
        return redirect('/login')

@login_required(login_url='/login')
def log_entry(request):
    user_id = request.GET.get('user')
    history = UserLog.objects.all().order_by('-id')[:50]
    response = []
    for hs in history:
        if user_id == hs.user.id:
            temp_dic = {
                'action':hs.action,
                'timestamp':hs.timestamp.strftime("%d-%m-%y, %H:%M:%S")
            }
            response.append(temp_dic)
    return JsonResponse(response,safe=False)

@login_required
def teacher_payment(request):
    """
    View to display teacher payment details with server-side pagination and filtering
    """
    # Initialize filter flags
    filters_applied = False
    name_mobile = request.GET.get('name_mobile', '')
    plan_filter = request.GET.get('plan', '')
    status = request.GET.get('status', '')
    payment_id = request.GET.get('payment_id', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Default queryset
    payments_queryset = TeacherPaymentDetails.objects.all().order_by('-timestamp')
    
    # Apply filters if provided
    if name_mobile or plan_filter or status or payment_id or date_from or date_to:
        filters_applied = True
        
        # Apply filters to queryset
        if name_mobile:
            payments_queryset = payments_queryset.filter(
                Q(user__name__icontains=name_mobile) | 
                Q(user__mobile_no__icontains=name_mobile)
            )
        
        if plan_filter:
            payments_queryset = payments_queryset.filter(plan=plan_filter)
        
        if status:
            payments_queryset = payments_queryset.filter(status=status)
        
        if payment_id:
            payments_queryset = payments_queryset.filter(
                Q(razorpay_payment_id__icontains=payment_id) | 
                Q(razorpay_order_id__icontains=payment_id)
            )
        
        if date_from:
            try:
                date_from_obj = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
                payments_queryset = payments_queryset.filter(timestamp__date__gte=date_from_obj)
            except ValueError:
                pass  # Skip invalid date
        
        if date_to:
            try:
                date_to_obj = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()
                payments_queryset = payments_queryset.filter(timestamp__date__lte=date_to_obj)
            except ValueError:
                pass  # Skip invalid date
    
    # Count total payments
    payments_count = payments_queryset.count()
    
    # Paginate the results
    paginator = Paginator(payments_queryset, 20)  # Show 20 payments per page
    page_number = request.GET.get('page', 1)
    
    try:
        payments = paginator.get_page(page_number)
    except (PageNotAnInteger, EmptyPage):
        payments = paginator.get_page(1)
    
    # Build query parameters for pagination links
    query_params = ''
    if filters_applied:
        params = []
        if name_mobile:
            params.append(f'name_mobile={name_mobile}')
        if plan_filter:
            params.append(f'plan={plan_filter}')
        if status:
            params.append(f'status={status}')
        if payment_id:
            params.append(f'payment_id={payment_id}')
        if date_from:
            params.append(f'date_from={date_from}')
        if date_to:
            params.append(f'date_to={date_to}')
        query_params = '&'.join(params)
    
    # Get all plans and statuses for filter dropdowns
    all_plans = TeacherPaymentDetails.objects.values_list('plan', flat=True).distinct()
    all_statuses = TeacherPaymentDetails.objects.values_list('status', flat=True).distinct()
    
    # Get all subscription plans for filter dropdown
    subscription_plans = TeacherSubscriptionPlan.objects.all()
    
    context = {
        'payments': payments,
        'payments_count': payments_count,
        'filters_applied': filters_applied,
        'subscription_plans': subscription_plans,
        'name_mobile': name_mobile,
        'plan_filter': plan_filter,
        'status': status,
        'all_plans': all_plans,
        'all_statuses': all_statuses,
        'payment_id': payment_id,
        'date_from': date_from,
        'date_to': date_to,
        'query_params': query_params,
        'page_title': 'Teacher Payment Details'
    }
    
    return render(request, 'admin-dashboard/teacher_payment.html', context)


@login_required
def get_payment_details(request):
    """
    AJAX view to get detailed information about a specific payment
    """
    payment_id = request.GET.get('payment_id')
    
    try:
        payment = TeacherPaymentDetails.objects.get(id=payment_id)
        
        # Handle potentially None values safely
        data = {
            'razorpay_payment_id': payment.razorpay_payment_id or "N/A",
            'razorpay_order_id': payment.razorpay_order_id or "N/A",
            'user_name': payment.user.name if payment.user else "N/A",
            'mobile_no': payment.user.mobile_no if payment.user else "N/A",
            'amount': payment.amount,
            'plan': payment.plan or "N/A",
            'subscription_plan': payment.subscription_plan.name if payment.subscription_plan else "N/A",
            'status': payment.status or "N/A",
            'timestamp': payment.timestamp.strftime('%d %b %Y %H:%M:%S') if payment.timestamp else "N/A",
            'data': payment.data or "N/A"
        }
        
        return JsonResponse(data)
    
    except TeacherPaymentDetails.DoesNotExist:
        return JsonResponse({'error': 'Payment not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def export_payments(request):
    """
    View to export payment details to CSV
    """
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="teacher_payments.csv"'
    
    # Create the CSV writer
    writer = csv.writer(response)
    
    # Write header row
    writer.writerow([
        'Payment Date', 
        'Teacher Name', 
        'Mobile No', 
        'Amount', 
        'Plan', 
        'Razorpay Payment ID', 
        'Razorpay Order ID', 
        'Status'
    ])
    
    # Get all payments or filtered payments
    payments = TeacherPaymentDetails.objects.all().order_by('-timestamp')
    
    # Apply filters if provided (use GET parameters to maintain consistency with filtering)
    name_mobile = request.GET.get('name_mobile', '')
    plan_filter = request.GET.get('plan', '')
    status = request.GET.get('status', '')
    payment_id = request.GET.get('payment_id', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if name_mobile:
        payments = payments.filter(
            Q(user__name__icontains=name_mobile) | 
            Q(user__mobile_no__icontains=name_mobile)
        )
    
    if plan_filter:
        payments = payments.filter(plan=plan_filter)
    
    if status:
        payments = payments.filter(status=status)
    
    if payment_id:
        payments = payments.filter(
            Q(razorpay_payment_id__icontains=payment_id) | 
            Q(razorpay_order_id__icontains=payment_id)
        )
    
    if date_from:
        try:
            date_from_obj = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
            payments = payments.filter(timestamp__date__gte=date_from_obj)
        except ValueError:
            pass  # Skip invalid date
    
    if date_to:
        try:
            date_to_obj = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()
            payments = payments.filter(timestamp__date__lte=date_to_obj)
        except ValueError:
            pass  # Skip invalid date
    
    # Write data rows
    for payment in payments:
        writer.writerow([
            payment.timestamp.strftime('%d %b %Y') if payment.timestamp else "N/A",
            payment.user.name if payment.user else "N/A",
            payment.user.mobile_no if payment.user else "N/A",
            payment.amount,
            payment.plan or "N/A",
            payment.razorpay_payment_id or "N/A",
            payment.razorpay_order_id or "N/A",
            payment.status or "N/A"
        ])
    
    return response

def school_payment(request):
    """
    View to display school payment details with server-side pagination and filtering
    """
    # Initialize filter flags
    filters_applied = False
    name_mobile = request.GET.get('name_mobile', '')
    plan_filter = request.GET.get('plan', '')
    status = request.GET.get('status', '')
    payment_id = request.GET.get('payment_id', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Default queryset
    payments_queryset = PaymentDetails.objects.all().order_by('-timestamp')
    
    # Apply filters if provided
    if name_mobile or plan_filter or status or payment_id or date_from or date_to:
        filters_applied = True
        
        # Apply filters to queryset
        if name_mobile:
            payments_queryset = payments_queryset.filter(
                Q(user__name__icontains=name_mobile) | 
                Q(user__mobile_no__icontains=name_mobile)
            )
        
        if plan_filter:
            payments_queryset = payments_queryset.filter(plan=plan_filter)
        
        if status:
            payments_queryset = payments_queryset.filter(status=status)
        
        if payment_id:
            payments_queryset = payments_queryset.filter(
                Q(razorpay_payment_id__icontains=payment_id) | 
                Q(razorpay_order_id__icontains=payment_id)
            )
        
        if date_from:
            try:
                date_from_obj = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
                payments_queryset = payments_queryset.filter(timestamp__date__gte=date_from_obj)
            except ValueError:
                pass  # Skip invalid date
        
        if date_to:
            try:
                date_to_obj = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()
                payments_queryset = payments_queryset.filter(timestamp__date__lte=date_to_obj)
            except ValueError:
                pass  # Skip invalid date
    
    # Count total payments
    payments_count = payments_queryset.count()
    
    # Paginate the results
    paginator = Paginator(payments_queryset, 20)  # Show 20 payments per page
    page_number = request.GET.get('page', 1)
    
    try:
        payments = paginator.get_page(page_number)
    except (PageNotAnInteger, EmptyPage):
        payments = paginator.get_page(1)
    
    # Build query parameters for pagination links
    query_params = ''
    if filters_applied:
        params = []
        if name_mobile:
            params.append(f'name_mobile={name_mobile}')
        if plan_filter:
            params.append(f'plan={plan_filter}')
        if status:
            params.append(f'status={status}')
        if payment_id:
            params.append(f'payment_id={payment_id}')
        if date_from:
            params.append(f'date_from={date_from}')
        if date_to:
            params.append(f'date_to={date_to}')
        query_params = '&'.join(params)
    
    # Get all plans and statuses for filter dropdowns
    all_plans = PaymentDetails.objects.values_list('plan', flat=True).distinct()
    all_statuses = PaymentDetails.objects.values_list('status', flat=True).distinct()
    
    # Get all subscription plans for filter dropdown
    subscription_plans = SchoolSubscriptionPlan.objects.all()
    
    context = {
        'payments': payments,
        'payments_count': payments_count,
        'filters_applied': filters_applied,
        'subscription_plans': subscription_plans,
        'name_mobile': name_mobile,
        'plan_filter': plan_filter,
        'status': status,
        'all_plans': all_plans,
        'all_statuses': all_statuses,
        'payment_id': payment_id,
        'date_from': date_from,
        'date_to': date_to,
        'query_params': query_params,
        'page_title': 'School Payment Details'
    }
    
    return render(request, 'admin-dashboard/school_payment.html', context)


@login_required
def get_school_payment_details(request):
    """
    AJAX view to get detailed information about a specific school payment
    """
    payment_id = request.GET.get('payment_id')
    
    try:
        payment = PaymentDetails.objects.get(id=payment_id)
        
        # Handle potentially None values safely
        data = {
            'razorpay_payment_id': payment.razorpay_payment_id or "N/A",
            'razorpay_order_id': payment.razorpay_order_id or "N/A",
            'user_name': payment.user.name if payment.user else "N/A",
            'mobile_no': payment.user.mobile_no if payment.user else "N/A",
            'amount': payment.amount,
            'plan': payment.plan or "N/A",
            'subscription_plan': payment.subscription_plan.name if payment.subscription_plan else "N/A",
            'status': payment.status or "N/A",
            'timestamp': payment.timestamp.strftime('%d %b %Y %H:%M:%S') if payment.timestamp else "N/A",
            'data': payment.data or "N/A"
        }
        
        return JsonResponse(data)
    
    except PaymentDetails.DoesNotExist:
        return JsonResponse({'error': 'Payment not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def export_school_payments(request):
    """
    View to export school payment details to CSV
    """
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="school_payments.csv"'
    
    # Create the CSV writer
    writer = csv.writer(response)
    
    # Write header row
    writer.writerow([
        'Payment Date', 
        'School Name', 
        'Mobile No', 
        'Amount', 
        'Plan', 
        'Razorpay Payment ID', 
        'Razorpay Order ID', 
        'Status'
    ])
    
    # Get all payments or filtered payments
    payments = PaymentDetails.objects.all().order_by('-timestamp')
    
    # Apply filters if provided (use GET parameters to maintain consistency with filtering)
    name_mobile = request.GET.get('name_mobile', '')
    plan_filter = request.GET.get('plan', '')
    status = request.GET.get('status', '')
    payment_id = request.GET.get('payment_id', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if name_mobile:
        payments = payments.filter(
            Q(user__name__icontains=name_mobile) | 
            Q(user__mobile_no__icontains=name_mobile)
        )
    
    if plan_filter:
        payments = payments.filter(plan=plan_filter)
    
    if status:
        payments = payments.filter(status=status)
    
    if payment_id:
        payments = payments.filter(
            Q(razorpay_payment_id__icontains=payment_id) | 
            Q(razorpay_order_id__icontains=payment_id)
        )
    
    if date_from:
        try:
            date_from_obj = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
            payments = payments.filter(timestamp__date__gte=date_from_obj)
        except ValueError:
            pass  # Skip invalid date
    
    if date_to:
        try:
            date_to_obj = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()
            payments = payments.filter(timestamp__date__lte=date_to_obj)
        except ValueError:
            pass  # Skip invalid date
    
    # Write data rows
    for payment in payments:
        writer.writerow([
            payment.timestamp.strftime('%d %b %Y') if payment.timestamp else "N/A",
            payment.user.name if payment.user else "N/A",
            payment.user.mobile_no if payment.user else "N/A",
            payment.amount,
            payment.plan or "N/A",
            payment.razorpay_payment_id or "N/A",
            payment.razorpay_order_id or "N/A",
            payment.status or "N/A"
        ])
    
    return response

@login_required(login_url='/login')
def verified_teachers(request):
    path = request.path
    page_title = "Verified teachers | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""
    limit_range = 30
    page = request.GET.get('page', 1)

    user_id = request.user.id
    filters_applied = False
    qualification = ''
    name_email_mobile = ''
    category = ''
    payment = ''
    profile = ''
    subject_of_experience = ''
    applied = ''
    status = ''
    years_of_experience = ''
    subject_of_specialization = ''
    current_salary = ''
    expected_salary = ''
    state = ''
    district = ''
    pincode = ''
    experience_type = ''
    experience_in = ''

    teachers = Teacher.objects.filter(status__iexact='Approved').order_by('-id')

    # Existing filtering logic for teachers (unchanged)
    if request.POST.get('name_email_mobile'):
        name_email_mobile = request.POST.get('name_email_mobile')
        teachers = teachers.filter(
            Q(user__name=name_email_mobile) | Q(user__mobile_no=name_email_mobile)
        )
        filters_applied = True

    if request.POST.get('experience_in'):
        category = request.POST.get('experience_in')
        teachers = teachers.filter(
            Q(experience_in__icontains=category) | Q(want_to_teach_for__icontains=category)
        )
        filters_applied = True

    if request.POST.get('payment'):
        payment = request.POST.get('payment')
        teachers = teachers.filter(payment_status__iexact=payment)
        filters_applied = True

    if request.POST.get('profile'):
        profile = request.POST.get('profile')
        if profile == 'Complete':
            teachers = teachers.exclude(
                gender__isnull=True, qualification__isnull=True, 
                subject_of_specialization__isnull=True, experience_type__isnull=True,
                address_state__isnull=True, address_pincode__isnull=True,
                years_of_experience__isnull=True, current_salary__isnull=True, 
                expected_salary__isnull=True, preferred_location_district__isnull=True
            )
        else:
            teachers = teachers.exclude(
                gender__isnull=False, qualification__isnull=False, 
                subject_of_specialization__isnull=False, experience_type__isnull=False,
                address_state__isnull=False, address_pincode__isnull=False,
                years_of_experience__isnull=False, current_salary__isnull=False, 
                expected_salary__isnull=False, preferred_location_district__isnull=False
            )
        filters_applied = True

    if request.POST.get('subject_of_experience'):
        subject_of_experience = request.POST.get('subject_of_experience')
        teachers = teachers.filter(
            Q(subject_of_experience__icontains=subject_of_experience) | 
            Q(subject_i_teach__icontains=subject_of_experience)
        )
        filters_applied = True

    if request.POST.get('status'):
        status = request.POST.get('status')
        teachers = teachers.filter(status__iexact=status)
        filters_applied = True

    if request.POST.get('education'):
        qualification = request.POST.get('education')
        teachers = teachers.filter(qualification__iexact=qualification)
        filters_applied = True

    if request.POST.get('years_of_experience'):
        years_of_experience = request.POST.get('years_of_experience')
        teachers = teachers.filter(years_of_experience__iexact=years_of_experience)
        filters_applied = True

    if request.POST.get('experience_type'):
        experience_type = request.POST.get('experience_type')
        teachers = teachers.filter(experience_type__iexact=experience_type)
        filters_applied = True

    if request.POST.get('subject_specialization'):
        subject_of_specialization = request.POST.get('subject_specialization')
        teachers = teachers.filter(subject_of_specialization__iexact=subject_of_specialization)
        filters_applied = True

    if request.POST.get('current_salary'):
        current_salary = request.POST.get('current_salary')
        teachers = teachers.filter(current_salary__iexact=current_salary)
        filters_applied = True

    if request.POST.get('expected_salary'):
        expected_salary = request.POST.get('expected_salary')
        teachers = teachers.filter(expected_salary__iexact=expected_salary)
        filters_applied = True

    if request.POST.get('state'):
        state = request.POST.get('state')
        teachers = teachers.filter(preferred_location_district__icontains=state)
        filters_applied = True

    if request.POST.get('district'):
        district = request.POST.get('district')
        teachers = teachers.filter(preferred_location_district__icontains=district)
        filters_applied = True

    if request.POST.get('pincode'):
        pincode = request.POST.get('pincode')
        teachers = teachers.filter(address_pincode__iexact=pincode)
        filters_applied = True

    teachers = teachers.order_by('-id')

    # Job filtering for WhatsApp modal - Updated for multiselect
    grades = request.GET.getlist('grade', [])  # This will handle multiple grade selections
    subjects_selected = request.GET.getlist('subject', [])  # This will handle multiple subject selections
    state_filter = request.GET.get('state', '')
    
    # Get job data for WhatsApp functionality
    post = PostJob.objects.values('id','job_code', 'teacher_grade', 'subject', 'district', 'state','user__name').filter(status__iexact='Approved').order_by('-id')
    walkin = WalkinJob.objects.filter(status__iexact='Approved').order_by('-id')
    walkin_processed = []
    
    for job in walkin:
        new_user = NewUser.objects.filter(mobile_no=job.user).first()
        school = School.objects.filter(user_id=new_user).first()
        job_data = {
            'id': job.id,
            'job_code': job.job_code,
            'teacher_grade': job.teacher_grade,
            'subject': job.subject,
            'district': school.district if school else None,
            'state': school.state if school else None,
            'user__name': school.user.name if school else None
        }
        walkin_processed.append(job_data)
    
    post_list = list(post)
    jobs1 = walkin_processed + post_list
    
    # Apply job filters for AJAX requests - Updated for multiselect
    if grades:
        filtered_jobs = []
        for job in jobs1:
            teacher_grade = job.get('teacher_grade', '')
            if teacher_grade:
                # Handle different grade formats
                if isinstance(teacher_grade, str) and teacher_grade.startswith("["):
                    try:
                        teacher_grade_list = eval(teacher_grade)
                        if isinstance(teacher_grade_list, list):
                            teacher_grade = ', '.join(teacher_grade_list)
                    except:
                        pass
                elif isinstance(teacher_grade, list):
                    teacher_grade = ', '.join(teacher_grade)
                
                # Check if any selected grade matches the job's grades
                job_matches = False
                for selected_grade in grades:
                    if selected_grade.lower() in teacher_grade.lower():
                        job_matches = True
                        break
                
                if job_matches:
                    filtered_jobs.append(job)
        jobs1 = filtered_jobs
        
    if subjects_selected:
        filtered_jobs = []
        for job in jobs1:
            job_subject = job.get('subject', '')
            if job_subject:
                # Handle different subject formats
                if isinstance(job_subject, str) and job_subject.startswith("["):
                    try:
                        job_subject_list = eval(job_subject)
                        if isinstance(job_subject_list, list):
                            job_subject = ', '.join(job_subject_list)
                    except:
                        pass
                elif isinstance(job_subject, list):
                    job_subject = ', '.join(job_subject)
                
                # Check if any selected subject matches the job's subjects
                job_matches = False
                for selected_subject in subjects_selected:
                    if selected_subject.lower() in job_subject.lower():
                        job_matches = True
                        break
                
                if job_matches:
                    filtered_jobs.append(job)
        jobs1 = filtered_jobs
        
    if state_filter:
        filtered_jobs = []
        for job in jobs1:
            job_state = job.get('state', '')
            if job_state and job_state.lower() == state_filter.lower():
                filtered_jobs.append(job)
        jobs1 = filtered_jobs

    # Handle AJAX request for job filtering
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'jobs1': jobs1
        })

    # PAGINATION IMPLEMENTATION - filter based
    if not filters_applied:
        paginator = Paginator(teachers, limit_range)
        teachers = paginator.get_page(page)
    else:
        teachers = teachers

    labels = Labels.objects.all().order_by('name')

    qualification_data = TeacherFormData.objects.filter(data_type='Qualification')
    specialization_data = TeacherFormData.objects.filter(data_type='Subject Specialzation')
    experience_type_data = TeacherFormData.objects.filter(data_type='Experience Type')
    expected_salary_data = TeacherFormData.objects.filter(data_type='Expected Salary')
    experience_in_data = TeacherGrade.objects.all()
    experience_subject_data = TeacherFormData.objects.filter(data_type='Subject of Experience')
    experience_year_data = TeacherFormData.objects.filter(data_type='Years of experience')
    current_salary_data = TeacherFormData.objects.filter(data_type='Current Salary')
    experience_in_fresher_data = TeacherGrade.objects.all()

    subject_teach_fresher_data_list = [
        st.name for st in TeacherSubject.objects.all().order_by('name')
    ]
    st_list = sorted(set(subject_teach_fresher_data_list))

    state_data = State.objects.all().order_by('name')
    district_data = District.objects.all().order_by('name')
    label_data = Teacher.objects.values('label').annotate(total=Count('label'))

    jobs = PostJob.objects.values(
        'id', 'job_code', 'teacher_grade', 'subject', 'district', 'state', 'user__name'
    ).filter(status__iexact='Approved').order_by('-id')

    # Get data for WhatsApp modal filters
    grade_categories = Grade.objects.all().order_by('name')
    subjects_form_data = JobFormData.objects.filter(data_type='Subject')
    
    # Build comprehensive subject list for modal
    grade_subject_list = []
    
    # Get subjects from TeacherSubject for each grade
    for gradei in grade_categories:
        dis_data = TeacherSubject.objects.filter(grade__name__iexact=gradei.name).order_by('name')
        for g in dis_data:
            grade_subject_list.append(g.name)
        
        # Get subjects from Subject model for each grade
        dis_data_1 = Subject.objects.filter(grade__name__iexact=gradei.name).order_by('name')
        for gg in dis_data_1:
            grade_subject_list.append(gg.name)

    # Add any additional subjects from form data
    for subject_data in subjects_form_data:
        if subject_data.info:
            grade_subject_list.append(subject_data.info)

    # Include currently selected subjects to maintain state
    if subjects_selected:
        for selected_subject in subjects_selected:
            grade_subject_list.append(selected_subject)

    # Remove duplicates and sort
    grade_subject_list = sorted(list(set(grade_subject_list)))

    context = {
        'path': path,
        'page_title': page_title,
        'teachers': teachers,  # Using paginated queryset
        'labels': labels,
        'district_data': district_data,
        'state_data': state_data,
        'qualification_data': qualification_data,
        'specialization_data': specialization_data,
        'experience_type_data': experience_type_data,
        'expected_salary_data': expected_salary_data,
        'experience_in_data': experience_in_data,
        'experience_subject_data': experience_subject_data,
        'experience_year_data': experience_year_data,
        'current_salary_data': current_salary_data,
        'subject_teach_fresher_data': st_list,
        'experience_in_fresher_data': experience_in_fresher_data,
        'label_data': label_data,
        'teachers_count': teachers.paginator.count if not filters_applied else teachers.count(),
        'qualification': qualification,
        'name_email_mobile': name_email_mobile,
        'category': category,
        'payment': payment,
        'profile': profile,
        'subject_of_experience': subject_of_experience,
        'applied': applied,
        'status': status,
        'years_of_experience': years_of_experience,
        'subject_of_specialization': subject_of_specialization,
        'current_salary': current_salary,
        'expected_salary': expected_salary,
        'state': state,
        'district': district,
        'pincode': pincode,
        'experience_type': experience_type,
        'jobs': jobs,
        'experience_in': category,
        'filters_applied': filters_applied,
        # WhatsApp modal specific context - Updated for multiselect
        'jobs1': jobs1,
        'grade_categories': grade_categories,
        'subjects': grade_subject_list,  # Complete subject list for multiselect
        'grades': grades,  # Selected grades list
        'subject_s': subjects_selected,  # Selected subjects list
        'state_s': state_filter,
        # Additional context for modal state management
        'modal_open': bool(grades or subjects_selected or state_filter),  # Keep modal open if filters applied
    }

    if request.user.user_type == 'Admin':
        return render(request, 'admin-dashboard/verified_teachers.html', context)
    else:
        return redirect('/login')
    
@login_required(login_url='/login')
def expired_teachers_approval(request):
    path = request.path
    page_title = "Expired teachers approval"
    meta_desc = ""
    keyword = ""
    schema = ""

    teachers = Teacher.objects.filter(status__iexact='Expired')

    context = {
        'path': path,
        'teachers':teachers,
        'page_title':page_title
    }
    if request.user.user_type == 'Admin':
        return render(request,'admin-dashboard/expired_teachers_approval.html',context)
    else:
        return redirect('/login')
    
@login_required(login_url='/login')
def unverified_teachers(request):
    path = request.path
    page_title = "Unverified teachers | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""
    limit_range = 20
    page = request.GET.get('page', 1)
    
    # Initialize filter variables
    filters_applied = False
    name_email_mobile = ''
    experience_in = ''
    payment = ''
    profile = ''
    subject_of_experience = ''
    applied = ''
    status = ''
    qualification = ''
    years_of_experience = ''
    experience_type = ''
    subject_specialization = ''
    current_salary = ''
    expected_salary = ''
    state = ''
    district = ''
    pincode = ''

    # Get all 'New' status teachers
    teachers = Teacher.objects.filter(status__iexact='New').order_by('-id')
    
    # Filtering logic - matching verified teachers but only with fields in the template
    if request.POST.get('name_email_mobile'):
        name_email_mobile = request.POST.get('name_email_mobile')
        teachers = teachers.filter(
            Q(user__name__icontains=name_email_mobile) | 
            Q(user__mobile_no__icontains=name_email_mobile) | Q(user__email__icontains=name_email_mobile)
        )
        filters_applied = True

    if request.POST.get('experience_in'):
        experience_in = request.POST.get('experience_in')
        teachers = teachers.filter(experience_in__iexact=experience_in)
        filters_applied = True

    if request.POST.get('payment'):
        payment = request.POST.get('payment')
        if payment == 'Paid':
            teachers = teachers.filter(plan__iexact='Premium')
        elif payment == 'Unpaid':
            teachers = teachers.filter(plan__iexact='Basic')
        filters_applied = True

    if request.POST.get('profile'):
        profile = request.POST.get('profile')
        if profile == 'Complete':
            teachers = teachers.filter(
                ~Q(experience_in__isnull=True),
                ~Q(experience_in=""),
                ~Q(subject_of_experience__isnull=True),
                ~Q(subject_of_experience=""),
                ~Q(preferred_location_district__isnull=True),
                ~Q(preferred_location_district="")
            )
        elif profile == 'Incomplete':
            teachers = teachers.filter(
                Q(experience_in__isnull=True) | 
                Q(experience_in="") |
                Q(subject_of_experience__isnull=True) | 
                Q(subject_of_experience="") |
                Q(preferred_location_district__isnull=True) | 
                Q(preferred_location_district="")
            )
        filters_applied = True

    if request.POST.get('subject_of_experience'):
        subject_of_experience = request.POST.get('subject_of_experience')
        teachers = teachers.filter(subject_of_experience__iexact=subject_of_experience)
        filters_applied = True

    if request.POST.get('applied'):
        applied = request.POST.get('applied')
        if applied == 'Applied':
            teachers = teachers.filter(jobapplication__isnull=False).distinct()
        elif applied == 'Not Applied':
            teachers = teachers.filter(jobapplication__isnull=True)
        filters_applied = True

    if request.POST.get('status'):
        status = request.POST.get('status')
        if status == 'Enable':
            teachers = teachers.filter(user__is_active=True)
        elif status == 'Disable':
            teachers = teachers.filter(user__is_active=False)
        filters_applied = True

    if request.POST.get('education'):
        qualification = request.POST.get('education')
        teachers = teachers.filter(qualification__iexact=qualification)
        filters_applied = True

    if request.POST.get('years_of_experience'):
        years_of_experience = request.POST.get('years_of_experience')
        teachers = teachers.filter(years_of_experience__iexact=years_of_experience)
        filters_applied = True

    if request.POST.get('experience_type'):
        experience_type = request.POST.get('experience_type')
        teachers = teachers.filter(experience_type__iexact=experience_type)
        filters_applied = True

    if request.POST.get('subject_specialization'):
        subject_specialization = request.POST.get('subject_specialization')
        teachers = teachers.filter(subject_of_specialization__iexact=subject_specialization)
        filters_applied = True

    if request.POST.get('current_salary'):
        current_salary = request.POST.get('current_salary')
        teachers = teachers.filter(current_salary__iexact=current_salary)
        filters_applied = True

    if request.POST.get('expected_salary'):
        expected_salary = request.POST.get('expected_salary')
        teachers = teachers.filter(expected_salary__iexact=expected_salary)
        filters_applied = True

    if request.POST.get('state'):
        state = request.POST.get('state')
        teachers = teachers.filter(address_state__iexact=state)
        filters_applied = True

    if request.POST.get('district'):
        district = request.POST.get('district')
        teachers = teachers.filter(address_district__iexact=district)
        filters_applied = True

    if request.POST.get('pincode'):
        pincode = request.POST.get('pincode')
        teachers = teachers.filter(address_pincode__iexact=pincode)
        filters_applied = True
        
    teachers = teachers.order_by('-id')
    filters_applied = False
    # PAGINATION IMPLEMENTATION - filter based
    if not filters_applied:
        paginator = Paginator(teachers, limit_range)
        teachers = paginator.get_page(page)
    else:
        teachers = teachers

    # Get data for filter dropdowns - using the field names in the template
    qualification_data = TeacherFormData.objects.filter(data_type='Qualification')
    specialization_data =  TeacherFormData.objects.filter(data_type='Subject Specialzation')
    expected_salary_data = TeacherFormData.objects.filter(data_type='Expected Salary')
    experience_in_data = TeacherGrade.objects.all()
    experience_year_data = TeacherFormData.objects.filter(data_type='Years of experience')
    current_salary_data = TeacherFormData.objects.filter(data_type='Current Salary')
    
    subject_teach_fresher_data = TeacherFormData.objects.filter(data_type='Subject i can teach')
    state_data = State.objects.all().order_by('name')
    district_data = District.objects.all().order_by('name')

    try:
        welcome_enabled_obj = WelcomeMessageControl.objects.get(id=1)
        welcome_enabled = welcome_enabled_obj.is_welcome_message_enabled
    except Exception:
        welcome_enabled = False

    context = {
        'path': path,
        'teachers':teachers,
        'page_title':page_title,
        'welcome_enabled':welcome_enabled,
        'filters_applied': filters_applied,
        'teachers_count': teachers.paginator.count if not filters_applied else teachers.count(),
        
        # Filter values - matching ones in the template
        'name_email_mobile': name_email_mobile,
        'experience_in': experience_in,
        'payment': payment,
        'profile': profile,
        'subject_of_experience': subject_of_experience,
        'applied': applied,
        'status': status,
        'qualification': qualification,
        'years_of_experience': years_of_experience,
        'experience_type': experience_type,
        'subject_specialization': subject_specialization,
        'current_salary': current_salary,
        'expected_salary': expected_salary,
        'state': state,
        'district': district,
        'pincode': pincode,
        
        # Data for dropdowns - using what's in the template
        'qualification_data': qualification_data,
        'experience_year_data': experience_year_data,
        'current_salary_data': current_salary_data,
        'expected_salary_data': expected_salary_data,
        'state_data': state_data,
        'district_data': district_data,
        'experience_in_data': experience_in_data,
        'subject_teach_fresher_data': subject_teach_fresher_data,
        'specialization_data': specialization_data,
    }
    
    if request.user.user_type == 'Admin':
        return render(request,'admin-dashboard/unverified_teachers.html',context)
    else:
        return redirect('/login')
     
@login_required(login_url='/login')
def rejected_teachers(request):
    path = request.path
    page_title = "Rejected Teachers | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    teachers = Teacher.objects.filter(status__iexact='Disabled').order_by('-id')[:1000]

    context = {
        'path': path,
        'teachers':teachers,
        'page_title':page_title
    }
    if request.user.user_type == 'Admin':
        return render(request,'admin-dashboard/rejected_teachers.html',context)
    else:
        return redirect('/login')
    
@login_required(login_url='/login')
def verified_institutions(request):
    path = request.path
    page_title = "Verified Institutions | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    schools = School.objects.filter(status__iexact='Approved').order_by('-timestamp')
    labels = Labels.objects.all().order_by('name')
    state_data = State.objects.all().order_by('name')
    district_data = District.objects.all().order_by('name')


    if request.POST.get('state') != '' and request.POST.get('state') != None:
        state = request.POST.get('state')
        print("state",state)
        schools = School.objects.filter(status__iexact='Approved').filter(state__iexact=state).order_by('-timestamp')
    if request.POST.get('district') != '' and request.POST.get('state') != None:
        district = request.POST.get('district')
        print("district",district)
        schools = School.objects.filter(status__iexact='Approved').filter(district__iexact=district).order_by('-timestamp')
    if request.POST.get('school_type') != '' and request.POST.get('state') != None:
        school_type = request.POST.get('school_type')
        print("school_type",school_type)
        schools = School.objects.filter(status__iexact='Approved').filter(institute_type__iexact=school_type).order_by('-timestamp')
    if request.POST.get('payment')  != '' and request.POST.get('state') != None:
        payment = request.POST.get('payment')
        print("payment",payment)
        schools = School.objects.filter(status__iexact='Approved').filter(payment_status__iexact=payment).order_by('-timestamp')
   
    context = {
        'path': path,
        'schools':schools,
        'page_title':page_title,
        'labels':labels,
        'state_data':state_data,
        'district_data':district_data,
        }
        
    if request.user.user_type == 'Admin':
        return render(request,'admin-dashboard/verified_institutions.html',context)
    else:
        return redirect('/login')
    

@login_required(login_url='/login')
def rejected_schools(request):
    path = request.path
    page_title = "Rejected Institutions | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""
    
    schools = School.objects.filter(status__iexact='Disabled')

    context = {
        'path': path,
        'schools':schools,
        'page_title':page_title
    }
    if request.user.user_type == 'Admin':
        return render(request,'admin-dashboard/rejected_institutions.html',context)
    else:
        return redirect('/login')

@login_required(login_url='/login')
def unverified_institutions(request):
    path = request.path
    page_title = "Unverified Institutions | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""
    
    schools = School.objects.filter(status__iexact='New')
    try:
        welcome_enabled_obj=WelcomeMessageControl.objects.get(id=1)
        welcome_enabled=welcome_enabled_obj.is_welcome_message_enabled
    except Exception:
        welcome_enabled=False

    context = {
        'path': path,
        'schools':schools,
        'page_title':page_title,
        'welcome_enabled':welcome_enabled
    }
    if request.user.user_type == 'Admin':
        return render(request,'admin-dashboard/unverified_institutions.html',context)
    else:
        return redirect('/login')
    
from django.views.decorators.http import require_GET
from django.http import JsonResponse

@require_GET
@login_required(login_url='/login')
def admin_job_alert(request):
    path = request.path
    page_title = "Admin Job Alert | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    jobs = JobAlert.objects.all().order_by("-id")
    
    # Handle multiple grade and subject selections
    grades = request.GET.getlist('grade', [])  
    subject = request.GET.getlist('subject', []) 
    state = request.GET.get('state', '')
    
    grade_categories = Grade.objects.all().order_by('name')
    subjects = JobFormData.objects.filter(data_type='Subject')
    state_data = State.objects.all()
    
    post = PostJob.objects.values('id','job_code', 'teacher_grade', 'subject', 'district', 'state','user__name').filter(status__iexact='Approved').order_by('-id')
    walkin = WalkinJob.objects.filter(status__iexact='Approved').order_by('-id')
    walkin_processed = []
    
    for job in walkin:
        new_user = NewUser.objects.filter(mobile_no=job.user).first()
        school = School.objects.filter(user_id=new_user).first()
        job_data = {
            'id': job.id,
            'job_code': job.job_code,
            'teacher_grade': job.teacher_grade,
            'subject': job.subject,
            'district': school.district if school else None,
            'state': school.state if school else None,
            'user__name': school.user.name if school else None  # Use user__name to match post structure
        }
        walkin_processed.append(job_data)
    
    post_list = list(post)
    jobs1 = walkin_processed + post_list
    
    # Filter by multiple grades
    if grades:
        filtered_jobs = []
        for job in jobs1:
            teacher_grade = job.get('teacher_grade', '')
            if teacher_grade:
                # Handle string representation of lists
                if isinstance(teacher_grade, str) and teacher_grade.startswith("["):
                    try:
                        teacher_grade = ', '.join(eval(teacher_grade))
                    except:
                        pass
                elif isinstance(teacher_grade, list):
                    teacher_grade = ', '.join(teacher_grade)
                
                # Check if any selected grade is in the job's teacher_grade
                for grade in grades:
                    if grade.lower() in teacher_grade.lower():
                        filtered_jobs.append(job)
                        break
        jobs1 = filtered_jobs
    
    # Filter by multiple subjects    
    if subject:
        filtered_jobs = []
        for job in jobs1:
            job_subject = job.get('subject', '')
            if job_subject:
                # Handle string representation of lists
                if isinstance(job_subject, str) and job_subject.startswith("["):
                    try:
                        job_subject = ', '.join(eval(job_subject))
                    except:
                        pass
                elif isinstance(job_subject, list):
                    job_subject = ', '.join(job_subject)
                
                # Check if any selected subject is in the job's subject
                for sub in subject:
                    if sub.lower() in job_subject.lower():
                        filtered_jobs.append(job)
                        break
        jobs1 = filtered_jobs
        
    if state:
        filtered_jobs = []
        for job in jobs1:
            job_state = job.get('state', '')
            if job_state and job_state.lower() == state.lower():
                filtered_jobs.append(job)
        jobs1 = filtered_jobs
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return JSON response for AJAX requests
        return JsonResponse({
            'jobs1': jobs1
        })
    
    grade_list = []
    for gradei in grade_categories:
        dis_data = TeacherSubject.objects.filter(grade__name__iexact=gradei.name).order_by('name')
        for g in dis_data:
            grade_list.append(g.name)
        
        dis_data_1 = Subject.objects.filter(grade__name__iexact=gradei.name).order_by('name')
        for gg in dis_data_1:
            grade_list.append(gg.name)

    if subject:
        for selected_subject in subject:
            grade_list.append(selected_subject)

    grade_list = list(set(grade_list))
    
    context = {
        'path': path,
        'jobs': jobs,
        'jobs1': jobs1,
        'page_title': page_title,
        'grade_categories': grade_categories,
        'subjects': sorted(grade_list),
        'state_data': state_data,
        'grades': grades,
        'subject_s': subject,
        'state_s': state,
    }
    if request.user.user_type == 'Admin':
        return render(request,'admin-dashboard/admin_job_alert.html',context)
    else:
        return redirect('/login')
        
def admin_my_jobs(request):
    path = request.path
    page_title = "My Jobs | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""
    
    jobs = PostJob.objects.filter(user__user_type='Admin')
    
    for job in jobs:
        job_app_count = JobApplicant.objects.filter(job__id=job.id).count()
        job.job_app_count=job_app_count
    
    context = {
        'path': path,
        'jobs':jobs,
        'page_title':page_title
    }

    return render(request,'admin-dashboard/admin_my_jobs.html', context)

@login_required(login_url='/login')
def active_jobs(request):
    path = request.path
    page_title = "Active Jobs | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""
    
    # Set pagination parameters
    page = request.GET.get('page', 1)
    items_per_page = 50
    
    try:
        if request.GET.get('school'):
            school = request.GET.get('school')
            school_first = School.objects.filter(user__name=school).first()
            post_job = PostJob.objects.filter(user_id=school_first.user.id).filter(status__iexact='Approved')
            walkin_job = WalkinJob.objects.filter(user=school_first.user).filter(status__iexact='Approved')
            jobs_list = list(post_job) + list(walkin_job)
        else:
            post_job = PostJob.objects.filter(status__iexact='Approved').order_by('-id')
            walkin_job = WalkinJob.objects.filter(status__iexact='Approved').order_by('-id')
            jobs_list = list(post_job) + list(walkin_job)
    except:
        post_job = PostJob.objects.filter(status__iexact='Approved').order_by('-id')
        walkin_job = WalkinJob.objects.filter(status__iexact='Approved').order_by('-id')
        jobs_list = list(post_job) + list(walkin_job)
    
    # Create a Django Paginator instance
    paginator = Paginator(jobs_list, items_per_page)
    
    try:
        # Get the specified page
        jobs = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        jobs = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page
        jobs = paginator.page(paginator.num_pages)
    
    # Add job application count to each job
    for job in jobs:
        if JobApplicant.objects.filter(job__id=job.id).exists():
            job_app_count = JobApplicant.objects.filter(job__id=job.id).count()
        else:
            job_app_count = JobApplicant.objects.filter(walkin_job__id=job.id).count()
        job.job_app_count = job_app_count
    
    context = {
        'path': path,
        'jobs': jobs,
        'page_title': page_title,
        'paginator': paginator,
    }
    
    if request.user.user_type == 'Admin':
        return render(request, 'admin-dashboard/active_jobs.html', context)
    else:
        return redirect('/login')

@login_required(login_url='/login')
def job_application(request):
    path = request.path
    page_title = "Jobs & Applications | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""
    school_id = request.GET.get('school')
    if school_id:
        school = School.objects.get(id=school_id)
    else:
        school_name = request.GET.get('school_name')
        school = School.objects.get(user__name__iexact=school_name)

    # school = School.objects.get(id=school_id)
    user_id = school.user.id
    jobs = PostJob.objects.filter(user_id=user_id)
    for job in jobs:
        job_app_count = JobApplicant.objects.filter(job__id=job.id).count()
        job.job_app_count=job_app_count
    context = {
        'path': path,
        'jobs':jobs,
        'page_title':page_title,
        'school':school
    }
    if request.user.user_type == 'Admin':
        return render(request,'admin-dashboard/job_application.html',context)
    else:
        return redirect('/login')


@login_required(login_url='/login')
def admin_expired_jobs(request):
    path = request.path
    page_title = "Expired Jobs"

    # Filter jobs that are expired, disabled, or past expiry date
    jobs_queryset = PostJob.objects.filter(
        Q(status__iexact='Expired') | 
        Q(status__iexact='Disabled') | 
        Q(expiry_date__lte=datetime.now())
    ).order_by('-timestamp')

    # Total number of jobs before pagination
    total_jobs = jobs_queryset.count()

    # Pagination
    paginator = Paginator(jobs_queryset, 100)  # 100 jobs per page
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Add job application count for jobs on this page
    for job in page_obj:
        job.job_app_count = JobApplicant.objects.filter(job__id=job.id).count()

    # Calculate start and end indices
    start_index = (page_obj.number - 1) * 100 + 1
    end_index = min(start_index + len(page_obj) - 1, total_jobs)

    context = {
        'path': path,
        'jobs': page_obj,  # Paginated jobs for current page
        'page_obj': page_obj,  # Pagination object
        'page_title': page_title,
        'total_jobs': total_jobs,  # Total number of jobs
        'start_index': start_index,
        'end_index': end_index
    }

    if request.user.user_type == 'Admin':
        return render(request, 'admin-dashboard/admin_expired_jobs.html', context)
    else:
        return redirect('/login')
    
@login_required(login_url='/login')
def rejected_jobs(request):
    path = request.path
    page_title = "Rejected Jobs"

    try:
        if request.GET.get('school'):
            school = request.GET.get('school')
            school_first = School.objects.filter(user__name=school).first()
            jobs = PostJob.objects.filter(user_id=school_first.user.id, status__iexact='Disabled').order_by('-id')
            walkin_job = WalkinJob.objects.filter(user=school_first.user, status__iexact='Disabled').order_by('-id')
        else:
            jobs = PostJob.objects.filter(status__iexact='Disabled').order_by('-id')
            walkin_job = WalkinJob.objects.filter(status__iexact='Disabled').order_by('-id')
    except:
        jobs = PostJob.objects.filter(status__iexact='Disabled').order_by('-id')
        walkin_job = WalkinJob.objects.filter(status__iexact='Disabled').order_by('-id')

    all_jobs = list(jobs) + list(walkin_job)
    
    for job in all_jobs:
        job.job_app_count = JobApplicant.objects.filter(job__id=job.id).count()

    # Pagination logic
    page = request.GET.get('page', 1)  # Get the current page number from request
    paginator = Paginator(all_jobs, 10)  # Show 10 jobs per page
    paginated_jobs = paginator.get_page(page)
    page_number = request.GET.get('page')
    all_jobs = paginator.get_page(page_number)

    start_index = (all_jobs.number - 1) * paginator.per_page + 1
    end_index = start_index + len(all_jobs) - 1
    total_jobs = paginator.count
    context = {
        'path': path,
        'jobs': paginated_jobs,  # Use paginated queryset
        'page_title': page_title,
        'start_index': start_index,
        'end_index': end_index,
        'total_jobs': total_jobs
    }

    if request.user.user_type == 'Admin':
        return render(request, 'admin-dashboard/rejected_jobs.html', context)
    else:
        return redirect('/login')
    
@login_required(login_url='/login')
def pending_approval(request):
    path = request.path
    page_title = "Pending Approval"
    meta_desc = ""
    keyword = ""
    schema = ""
    try:
        if request.GET.get('school'):
            school = request.GET.get('school')
            school_first = School.objects.filter(user__name=school).first()
            print(school_first.user,'\n')
            jobs = PostJob.objects.filter(user_id=school_first.user.id).filter(status__iexact='New').order_by('-id')
            walkin_job= WalkinJob.objects.filter(user=school_first.user).filter(status__iexact='New').order_by('-id')
        else:
            jobs = PostJob.objects.filter(status__iexact='New').order_by('-id')
            walkin_job= WalkinJob.objects.filter(status__iexact='New').order_by('-id')
    except:
        jobs = PostJob.objects.filter(status__iexact='New').order_by('-id')
        walkin_job= WalkinJob.objects.filter(status__iexact='New').order_by('-id')

    all_jobs = list(jobs) + list(walkin_job)
    for job in all_jobs:
        if not JobApplicant.objects.filter(walkin_job__id=job.id).exists():
            job_app_count = JobApplicant.objects.filter(job__id=job.id).count()
        job_app_count = JobApplicant.objects.filter(walkin_job__id=job.id).count()
        job.job_app_count=job_app_count
    context = {
        'path': path,
        'jobs':all_jobs,
        'page_title':page_title
    }
    if request.user.user_type == 'Admin':
        return render(request,'admin-dashboard/pending_approval.html',context)
    else:
        return redirect('/login')
    
@login_required(login_url='/login')
def employer_details(request):

    user_id = request.GET.get('user')
    school = School.objects.filter(user__id=user_id).first()

    context = {
        'school_name':school.user.name,
        'email':school.school_email,
        'mobile_no':school.user.mobile_no,
        'alt_mobile_no':school.user.alt_mobile_no,
        'website':school.website,
    }

    return JsonResponse(context, safe=False)
    
@login_required(login_url='/login')
def job_details(request):

    job_id = request.GET.get('job_id')
    context = {}
    
    if not WalkinJob.objects.filter(id=job_id).exists():
        job = PostJob.objects.filter(id=job_id).first()
        school = School.objects.filter(user_id=job.user).first()
        context = {
            'school_name':str(job.user.name),
            'school_mobile':int(job.user.mobile_no),
            'job_code':job.job_code,
            'teacher_grade':job.teacher_grade,
            'subject':job.subject,
            'highest_qualification':job.highest_qualification,
            'experienced_required':job.experienced_required,
            'salary_offered':job.salary_offered,
            'expiry_date':job.expiry_date,
            'benifits_compensation':job.benifits_compensation,
            'pincode':job.pincode,
            'state':job.state,
            'district':job.district,
            'address':job.address,
            'timestamp':job.timestamp,
            'promo_applied':job.promo_applied,
        }
    else:
        job = WalkinJob.objects.filter(id=job_id).first()
        school = School.objects.filter(user_id=job.user).first()
        context = {
            'school_name':job.contact_name,
            'school_mobile':job.contact_mobile,
            'job_code':job.job_code,
            'teacher_grade':job.teacher_grade,
            'subject':job.subject,
            'highest_qualification':'',
            'experienced_required':'',
            'salary_offered':job.salary_range,
            'expiry_date':job.walkin_date,
            'benifits_compensation':'',
            'pincode':'',
            'state':'',
            'district':'',
            'address':'',
            'timestamp':job.timestamp,
        }

    return JsonResponse(context, safe=False)

def admin_post_job(request):
    path = request.path
    page_title = "Post A Job | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""
    context = {
        'path': path,
    }
    return render(request,'admin-dashboard/admin_post_job.html', context)

def admin_walkin_job(request):
    path = request.path
    page_title = "Post A Walk-in Job | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""
   
    # Get all grades and subjects
    grade_data = Grade.objects.all()
    subject_data = JobFormData.objects.filter(data_type='Subject')
    salary_data = JobFormData.objects.filter(data_type='Salary offered')
    
    # Get default payment price
    default_payment_price = 0
    payment_settings = PaymentDetails.objects.first()
    if payment_settings and hasattr(payment_settings, 'walkin_job_price'):
        default_payment_price = payment_settings.walkin_job_price
   
    # Check if free to apply is enabled
    is_free_to_apply = False
    faculty_me_permission = FacultyMe_Permission.objects.first()
    if faculty_me_permission and hasattr(faculty_me_permission, 'free_to_apply_walkin_job'):
        is_free_to_apply = faculty_me_permission.free_to_apply_walkin_job
    
    if request.method == 'POST':
        # try:
        #     selected_school_id = request.POST.get('school_user')
        #     print("selected_school_id",selected_school_id)
        #     school = School.objects.get(user=selected_school_id)
        #     print("school",school.user)
        #     if not school:
        #         messages.error(request, "School with the provided ID not found.")
        #         return redirect('admin_walkin_job')
            
            # Check if school has an active subscription
            # try:
            #     subscription = SchoolWalkinSubscription.objects.get(school_id=school.user.id)
            #     if subscription.job_post_remaining <= 0:
            #         messages.error(request, "The selected school has no job postings left in their current plan.")
            #         return redirect('admin_walkin_job')
            # except SchoolWalkinSubscription.DoesNotExist:
            #     messages.error(request, "The selected school has no active subscription.")
            #     return redirect('admin_walkin_job')
            
            # Process grade and subject data
            grade_ids = request.POST.getlist('teacher_grade[]')
            grade_queryset = Grade.objects.filter(id__in=grade_ids)
            grade_names = [grade.name for grade in grade_queryset]
            grade_string = str(grade_names)
            
            user= request.POST.get('school_user')
            # Generate unique job code
            code = ''.join(random.choice(string.digits) for _ in range(3))
            school= School.objects.filter(user=user).first()
            if not school:
                school=user[:5]
            # Create a new WalkinJob instance
            new_job = WalkinJob(
                user=user,
                description=request.POST.get('description'),
                teacher_grade=grade_string,
                subject=request.POST.getlist('subject[]'),
                walkin_date=datetime.strptime(request.POST.get('walkin_date'), "%Y-%m-%d").date(),
                contact_name=request.POST.get('contact_name', ''),
                contact_designation=request.POST.get('contact_designation', ''),
                contact_mobile=request.POST.get('contact_mobile', ''),
                alternative_mobile=request.POST.get('alternative_mobile', ''),
                salary_range=request.POST.get('salary_range'),
                job_code=school+'W'+code,
                free_to_apply=request.POST.get('free_to_apply') == 'on',
                payment_pricing=request.POST.get('payment_price'),
                status='Approved',
            )
            new_job.save()
            
            # Update the subscription job count
            # subscription.job_post_remaining -= 1
            # subscription.save()
            
            messages.success(request, "Walk-in job posted successfully for " + request.POST.get('school_user'))
            return redirect('admin_walkin_job')
            
        # except Exception as e:
        #     messages.error(request, f"Error posting job: {str(e)}")
        #     return redirect('admin_walkin_job')
   
    # Get existing walkin job if editing
    existing_job = None
    if request.method == 'GET' and 'job_id' in request.GET:
        job_id = request.GET.get('job_id')
        try:
            existing_job = WalkinJob.objects.get(id=job_id)
        except WalkinJob.DoesNotExist:
            existing_job = None
            
    context = {
        'path': path,
        'page_title': page_title,
        'meta_desc': meta_desc,
        'keyword': keyword,
        'schema': schema,
        'grade_data': grade_data,
        'subject_data': subject_data,
        'salary_data': salary_data,
        'default_payment_price': default_payment_price,
        'is_free_to_apply': is_free_to_apply,
        'school': '',
        'school_info': '',
        'existing_job': existing_job,
        'min_walkin_date': (datetime.now().date() + timedelta(days=6)).strftime('%Y-%m-%d'),
    }
   
    return render(request, 'admin-dashboard/admin_walkin_job.html', context)

def admin_settings(request):
    path = request.path
    page_title = "Admin Settings | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""
    context = {
        'path': path,
    }
    return render(request,'admin-dashboard/admin_settings.html', context)

def application_detail(request):
    page_title = "Application Details | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""
    return render(request,'admin-dashboard/application_detail.html')

def test_auth(request):
    page_title = "Application Details | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""
    return render(request,'authentication/test_auth.html')


@login_required(login_url='/login')
@csrf_exempt
def toggle_welcome_message_controler(request):
    if request.method == 'POST':
        if request.user.user_type == 'Admin':
            if not WelcomeMessageControl.objects.all().exists():
                welcome_enabled_obj= WelcomeMessageControl.objects.create(is_welcome_message_enabled=True)
                welcome_enabled=welcome_enabled_obj.is_welcome_message_enabled
                return JsonResponse({'status': 'success', 'welcome_enabled': welcome_enabled})
            elif WelcomeMessageControl.objects.filter(is_welcome_message_enabled=True).exists():
                welcome_enabled_obj= WelcomeMessageControl.objects.filter(is_welcome_message_enabled=True).update(is_welcome_message_enabled=False)
                welcome_enabled_obj=WelcomeMessageControl.objects.get(id=1)
                welcome_enabled=welcome_enabled_obj.is_welcome_message_enabled
                return JsonResponse({'status': 'success', 'welcome_enabled': welcome_enabled})
            else:
                welcome_enabled_obj= WelcomeMessageControl.objects.filter(is_welcome_message_enabled=False).update(is_welcome_message_enabled=True)
                welcome_enabled_obj=WelcomeMessageControl.objects.get(id=1)
                welcome_enabled=welcome_enabled_obj.is_welcome_message_enabled
                return JsonResponse({'status': 'success', 'welcome_enabled': welcome_enabled})
        else:
            return redirect('/login')
    else:
         return HttpResponse(status=400)

@login_required(login_url='/login')
def review_shortlisted(request):
    shortlist = request.GET.get('shortlist')

    shortlist_array = shortlist.split(",")

    for shortlist in shortlist_array:
        ShortlistedTeachers.objects.filter(id=shortlist).update(is_review=True)
        
    return JsonResponse(True, safe=False)

@login_required(login_url='/login')
@csrf_exempt
def selected_job_alert_delete(request):
    if request.method == 'POST':
        job_alert=request.POST.get('job_alert')
        print(job_alert, "dkdkdkdkdk")
        job_alert_array=job_alert.split(",")
        for jobalert in job_alert_array:
            data=JobAlert.objects.get(id=jobalert)
            data.delete()
        return JsonResponse(True, safe=False)



def admin_add_job(request):
        
    page_title = "Add Job | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    if request.method == 'POST':
                        
        user_id = request.user.id
        UserLog.objects.create(user=request.user,action='New Job Added')
        school_phone = request.POST.get('school_name')
        teacher_grade = request.POST.get('teacher_grade')
        subject = request.POST.get('subject')
        highest_qualification = request.POST.get('highest_qualification')
        experienced_required = request.POST.get('experienced_required')
        salary_offered = request.POST.get('salary_offered')
        joining_date = request.POST.get('joining_date')
        expiry_date=request.POST.get('expiry_date')
        description=request.POST.get('description')
        if NewUser.objects.filter(mobile_no=school_phone).exists():
            school_obj=NewUser.objects.get(mobile_no=school_phone)
           
        else:
            messages.error(request, 'School dose not exist')
            return redirect(request.META['HTTP_REFERER'])

        try:
            joining_date = datetime.strptime(joining_date, '%d-%m-%Y')
        except:
            joining_date = datetime.strptime(joining_date, '%d/%m/%Y')
       
        if expiry_date:
            try:
                expiry_date = datetime.strptime(expiry_date, '%d-%m-%Y')
            except:
                expiry_date = datetime.strptime(expiry_date, '%d/%m/%Y')
            expiry_date = expiry_date.strftime("%Y-%m-%d")
        else:
            # Get the current date
            current_date = datetime.now()
            # Calculate the expiration date by adding 45 days
            expiration_date = current_date + timedelta(days=45)
            # Format the expiration date as a string
            expiry_date = expiration_date.strftime('%Y-%m-%d')

        joining_date = joining_date.strftime("%Y-%m-%d")
        benifits_compensation = request.POST.get('benifits_compensation')
        # benifits_compensation = ','.join(benifits_compensation)
        pincode = request.POST.get('pincode')
        state = request.POST.get('state')
        district = request.POST.get('district')
        address = request.POST.get('address')
      
        job_code = ''.join(random.choice(string.digits) for _ in range(3))
        job_code = str(user_id)+'J'+job_code
        PostJob.objects.create(
            user_id=school_obj.id,
            teacher_grade=teacher_grade,
            subject=subject,
            highest_qualification=highest_qualification,
            experienced_required=experienced_required,
            salary_offered=salary_offered,
            joining_date=joining_date,
            expiry_date=expiry_date,
            benifits_compensation=benifits_compensation,
            pincode=pincode,
            state=state,
            district=district,
            address=address,
            job_code = job_code,
            description=description,
        )
        messages.success(request, 'Job is posted successfully')

    return redirect(request.META['HTTP_REFERER'])


def admin_post_job(request):
    page_title = "Post a job | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    if not request.user.is_authenticated:

        return redirect('/login')

    grade_data = Grade.objects.all()
    # subject_data = JobFormData.objects.filter(data_type='Subject')
    subject_data = JobFormData.objects.filter(data_type='Subject')
    print(subject_data.count(), "coutnts")
    qualification_data = JobFormData.objects.filter(data_type='Highest Qualification')
    experience_data = JobFormData.objects.filter(data_type='Experience Required')
    salary_data = JobFormData.objects.filter(data_type='Salary offered')
    benifits_data = JobFormData.objects.filter(data_type='Benefits & compensation')
    school_data=NewUser.objects.filter(user_type='School')
    context = {
        'page_title':page_title,
        'meta_desc':meta_desc,
        'keyword':keyword,
        'schema':schema,
        'grade_data':grade_data,
        'subject_data':subject_data,
        'qualification_data':qualification_data,
        'experience_data':experience_data,
        'salary_data':salary_data,
        'benifits_data':benifits_data,
        'school_data':school_data,
    }

    return render(request,'admin-dashboard/admin_post_job.html',context)
    


from django.contrib.auth import authenticate, login

def change_pin(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        user_obj = NewUser.objects.get(id=request.user.id)
        
        # Check if the old password is correct
        if not user_obj.check_password(old_password):
            messages.error(request, 'Incorrect old PIN.')
            return redirect('change_pin')

        # Check if the new passwords match
        if new_password1 != new_password2:
            messages.error(request, 'New PINs do not match.')
            return redirect('change_pin')
        
        # Validate PIN format (4 digits)
        if len(new_password1) != 4 or not new_password1.isdigit():
            messages.error(request, 'PIN must be exactly 4 digits.')
            return redirect('change_pin')

        # Set the new password and save the user object
        user_obj.set_password(new_password1)
        user_obj.save()
        
        # Log the user back in with the new password to maintain session
        # Use mobile_no instead of username (NewUser uses mobile_no as USERNAME_FIELD)
        user = authenticate(request, mobile_no=user_obj.mobile_no, password=new_password1)
        if user is not None:
            login(request, user)
            UserLog.objects.create(user=user, action='PIN Changed')
            messages.success(request, 'PIN changed successfully.')
        else:
            messages.warning(request, 'PIN changed but please login again.')
            return redirect('/login')
        
        # Redirect based on user type
        if request.user.user_type == 'Teacher':
            return redirect('/teacher-account')
        elif request.user.user_type == 'School':
            return redirect('/school-account')
        else:
            return redirect('change_pin')
    else:
        return render(request, 'authentication/change_password.html')

@csrf_exempt
def save_lead(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    data = json.loads(request.body)

    Lead.objects.create(
        name=data.get("name"),
        whatsapp=data.get("whatsapp"),
        grades=data.get("grades"),
        subjects=data.get("subjects"),
        location=data.get("location")
    )

    return JsonResponse({"message": "Lead saved successfully"})

@login_required(login_url='/login')
def interview_calls_school_none(request):
    path = request.path
    page_title = "Interview Calls | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""
    school_list=[]

    schools = School.objects.all()
    for school in schools:
        temp_dic = {} 
        # try:
        job_applications = JobApplicant.objects.filter(job__user=school.user)
        if not job_applications:
            new_job_applicant_count =0
            approved_job_applicant_count =0

            new_interview_count = 0
            approved_interview_count = 0

            new_job_count = 0
            approved_job_count = 0
            context={
                'new_job_count':new_job_count,
                'approved_job_count':approved_job_count,
                'new_interview_count':new_interview_count,
                'approved_interview_count':approved_interview_count,
                'new_job_applicant_count':new_job_applicant_count,
                'approved_job_applicant_count':approved_job_applicant_count,
                'page_title':page_title,
                'path':path 
            }
            try:
                temp_dic[school.user.name] = context
            except:
                pass
            school_list.append(temp_dic)
        # except:
        #     pass
    
    context = {
        'path': path,
        'job_applications':job_applications,
        'page_title':page_title,
        'school_list':school_list
    }

    if request.user.user_type == 'Admin':
        return render(request,'admin-dashboard/interview_calls_school_none.html',context)
    else:
        return redirect('/login')


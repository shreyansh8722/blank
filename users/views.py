from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.urls import reverse
import os
from django.contrib.auth import authenticate, logout, login as auth_login
from django.contrib import messages
from .forms import CreateUserForm
from .models import *
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.http import JsonResponse
import random,string
from cog_static_app.models import *
import requests
from django.views.decorators.csrf import csrf_exempt
from cog_static_app.views import *
import threading
import json

# Import MSG91 helper from centralized module
from msg91 import send_sms_via_msg91, REG_TEMPLATE_ID

@csrf_exempt
def login(request): 
    page_title = "Login"
    meta_desc = ""
    keyword = ""
    schema = ""
    if request.user.is_authenticated:
        if request.user.user_type == 'Teacher':
            return redirect('/teacher-account')

        if request.user.user_type == 'School':
            return redirect('/school-account')
        
        if request.user.user_type == 'Admin':
            return redirect('/admin-dashboard')
    else:
        if request.method == 'POST':
            mobile_no = request.POST.get('mobile_no')
            password = request.POST.get('password')

            user = authenticate(request, mobile_no=mobile_no, password=password)
            if user is not None:
                # If login was initiated with a next/plan param, prefer redirecting there after successful auth
                next_url = request.POST.get('next') or request.GET.get('next')
                plan_param = request.POST.get('plan') or request.GET.get('plan')

                if user.is_mobile_no_verified:
                    auth_login(request, user)
                    UserLog.objects.create(user=user,action='Login')
                    # If a next_url was provided and is safe, redirect to it (append plan if present)
                    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                        redirect_to = next_url
                        if plan_param:
                            sep = '&' if '?' in redirect_to else '?'
                            redirect_to = f"{redirect_to}{sep}plan={plan_param}"
                        return redirect(redirect_to)
                    if request.user.user_type == 'Teacher':
                        job_id = request.GET.get('job')
                        job_code = request.GET.get('jobcode')
                        if request.GET.get('job') and job_code != '' and job_code != 'None' :
                            return redirect ('/current-vacancies?jobcode='+job_code)
                            # return redirect ('/apply-for-job?job='+job_id)
                        else:                            
                            user_t = NewUser.objects.get(id=request.user.id)
                            try:
                                t = Teacher.objects.get(user=user_t)
                                
                                # Check if profile is complete
                                if t.gender and t.qualification and t.subject_of_specialization and t.experience_type and t.address_pincode and t.address_state and t.expected_salary:
                                    return redirect('/teacher-account')
                                else:
                                    return redirect('/teacher-profile')
                            except Teacher.DoesNotExist:
                                # Teacher object doesn't exist, create it and redirect to profile
                                Teacher.objects.create(user=user_t)
                                return redirect('/teacher-profile')

                    if request.user.user_type == 'School':
                        s = School.objects.filter(user=user).first()
                        if s:
                            # Check if profile is complete
                            if s.institute_type and s.contact_person_name and s.pincode and s.address and s.primary_mobile and s.district and s.state:
                                return redirect('/school-account')
                            else:
                                return redirect('/school-profile')
                        else:
                            # School object doesn't exist, create it and redirect to profile
                            School.objects.create(user=user)
                            return redirect('/school-profile')
                else:
                    messages.info(request, 'Mobile No. not verified')
                    messages.warning(request, 'OTP sent successfully to your mobile no.')

                    otp_code = ''.join(random.choice(string.digits) for _ in range(4))
                    otp_history, created = OtpHistory.objects.get_or_create(user_id=user.id)
                    OtpHistory.objects.filter(pk=otp_history.id).update(otp=otp_code,otp_session=1)

                    otp_info = OtpHistory.objects.get(id=otp_history.id)

                    
                    # Use MSG91 OTP template
                    try:
                        status, response_text = send_sms_via_msg91(user.mobile_no, template_id=REG_TEMPLATE_ID, template_vars={'OTP': otp_info.otp})
                        print(f'MSG91 send (login) response: status={status}, body={response_text}')
                        messages.warning(request, 'OTP sent successfully to your mobile no.')
                    except Exception as e:
                        print('SMS send failed (login flow):', e)
                        messages.error(request, 'Unable to send OTP right now. Please try Resend OTP or try again later.')

                    if user.user_type == 'Teacher':
                        return redirect('/registration?mobile_no='+mobile_no)
                    elif user.user_type == 'School':
                        return redirect('/registration?mobile_no='+mobile_no)
                    else:
                        pass
            else:
                mobile_no = request.POST.get('mobile_no')
                try:
                    res = NewUser.objects.get(mobile_no__iexact=mobile_no)
                    messages.info(request, 'PIN wrong please retry!')
                except:
                    messages.info(request, 'Mobile No. not registered')
    job_code = request.GET.get('jobcode', None)  # Returns None if 'job_code' is not present
    job      = request.GET.get('job', None)  # Returns None if 'job_code' is not present

    context = {'job_code': job_code, 'job' : job}
    return render(request,'authentication/login.html',context)    

def logoutUser(request):
    UserLog.objects.create(user=request.user,action='Logout')    
    logout(request)
    return redirect('/login')

from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

@csrf_protect
@require_http_methods(["GET", "POST"])
def registration(request):
    page_title = "Registration | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""
    user_type = request.GET.get('type', 'Teacher')
    job_code  = request.GET.get('job_code', None)  # Returns None if 'job_code' is not present
    job       = request.GET.get('job', None)  # Returns None if 'job_code' is not present
    otp_history = None
    customer_info = None
    if request.method == 'POST':
        clicked = request.POST.get('click')
    else:
        clicked = request.GET.get('click')
        
    # if clicked == '1' and user_type == 'SCHOOLEXCLUSIVE':
    #     user_type = 'School'
    #     request.user.user_type = 'School'
    # print("click:", clicked)
    # print("User Type from GET:", user_type)
    # print("User Type:", user_type)
    
    form = CreateUserForm()
    if request.user.is_authenticated:
        if request.user.user_type == 'Teacher' or user_type == 'Teacher':
            return redirect('/teacher-account')
        else:
            return redirect('/school-account')
    else:
        # print('form - ', user_type)
        form = CreateUserForm()
        if request.method == 'POST':
            post_data = request.POST.copy()
            
            if user_type == 'SCHOOLEXCLUSIVE':
                post_data['user_type'] = 'School'

            form = CreateUserForm(post_data)

            # If the mobile exists but is not verified yet, allow re-registration flow here
            # This ensures users who started registration but skipped OTP can re-request OTP
            if request.POST.get('mobile_no') and not request.POST.get('otp'):
                mobile_no_tmp = request.POST.get('mobile_no')
                existing_tmp = NewUser.objects.filter(mobile_no=mobile_no_tmp).first()
                if existing_tmp and not existing_tmp.is_mobile_no_verified:
                    # Update existing (unverified) user and resend OTP
                    NewUser.objects.filter(id=existing_tmp.id).update(
                        name=request.POST.get('name') or existing_tmp.name,
                        temp_data=request.POST.get('password1') or existing_tmp.temp_data,
                        alt_mobile_no=request.POST.get('alt_mobile_no') or existing_tmp.alt_mobile_no,
                        is_active=False,
                        is_mobile_no_verified=False,
                    )
                    user_info = NewUser.objects.get(id=existing_tmp.id)
                    otp_code = ''.join(random.choice(string.digits) for _ in range(4))
                    otp_history, created = OtpHistory.objects.get_or_create(user_id=user_info.id)
                    OtpHistory.objects.filter(pk=otp_history.id).update(otp=otp_code, otp_session=1)
                    otp_info = OtpHistory.objects.get(id=otp_history.id)

                    # Use MSG91 OTP template
                    try:
                        status, response_text = send_sms_via_msg91(user_info.mobile_no, template_id=REG_TEMPLATE_ID, template_vars={'OTP': otp_info.otp})
                        print(f'MSG91 send (re-registration) response: status={status}, body={response_text}')
                        messages.warning(request, 'OTP sent successfully to your mobile no.')
                    except Exception as e:
                        print('SMS send failed (re-registration flow):', e)
                        messages.error(request, 'Unable to send OTP right now. Please try Resend OTP or try again later.')

                    # Redirect to registration GET with mobile to show OTP modal
                    if request.POST.get('user_type') == 'School' or request.GET.get('type') == 'SCHOOLEXCLUSIVE':
                        return redirect('/registration?type=School&mobile_no=' + user_info.mobile_no)
                    else:
                        return redirect('/registration?type=Teacher&mobile_no=' + user_info.mobile_no)
            
            # print("Form Data:", form.data)
            if request.POST.get('otp'):
                # print('OTP:', user_type)
                # Handle OTP verification
                mobile_no_verify = request.POST.get('mobile_no')
                otp_entered = request.POST.get('otp')
                
                # Get the OTP record from OtpHistory for this mobile number
                otp_record = OtpHistory.objects.filter(
                    user__mobile_no=mobile_no_verify,
                    otp=otp_entered,
                    otp_session=1  # Only valid OTPs (session 1 means active)
                ).first()
                
                if otp_record:
                    if user_type == 'SCHOOLEXCLUSIVE':
                        user_type = 'School'
                        request.user.user_type = 'School'
                    
                    # Mark mobile verified and activate the account now that OTP is confirmed
                    NewUser.objects.filter(mobile_no=mobile_no_verify).update(
                        is_mobile_no_verified=True, 
                        is_active=True
                    )
                    new_user_info = NewUser.objects.filter(mobile_no=mobile_no_verify).first()
                    
                    # Invalidate the OTP after successful verification (set session to 2 = used)
                    OtpHistory.objects.filter(id=otp_record.id).update(otp_session=2)
                        
                    user = authenticate(request, mobile_no=new_user_info.mobile_no,password=new_user_info.temp_data)
                    welcome_enabled=WelcomeMessageControl.objects.get(id=1)
                    if user is not None:
                        auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                        NewUser.objects.filter(id=new_user_info.id).update(temp_data=None)
                        
                        # Process draft jobs for schools using stored session data
                        if user_type != 'Teacher' and request.user.user_type != 'Teacher':
                           # Get draft jobs from session data
                            draft_jobs_data = get_draft_jobs_from_storage(new_user_info.mobile_no)
                            
                            for draft_job_data in draft_jobs_data:
                                job_code = ''.join(random.choice(string.digits) for _ in range(3))
                                job_code = str(user.id) + 'J' + job_code
                                expiry_date = datetime.now() + timedelta(days=45)
                                
                                PostJob.objects.create(
                                    user_id=user.id,
                                    teacher_grade=draft_job_data.get('teacher_grade', ''),
                                    subject=draft_job_data.get('subject', ''),
                                    highest_qualification=draft_job_data.get('highest_qualification', ''),
                                    experienced_required=draft_job_data.get('experienced_required', ''),
                                    salary_offered=draft_job_data.get('salary_offered', ''),
                                    joining=draft_job_data.get('joining', ''),
                                    expiry_date=expiry_date,
                                    benifits_compensation=draft_job_data.get('benifits_compensation', ''),
                                    pincode=draft_job_data.get('pincode', ''),
                                    state=draft_job_data.get('state', ''),
                                    district=draft_job_data.get('district', ''),
                                    address=draft_job_data.get('address', ''),
                                    job_code=job_code,
                                    description=draft_job_data.get('description', ''),
                                )
                            
                            # Clear draft jobs after converting to actual jobs
                            clear_draft_jobs_from_storage(new_user_info.mobile_no)
                        
                        if request.user.user_type == 'Teacher':
                            # Get or create Teacher object (in case of re-registration)
                            teacher_info, created = Teacher.objects.get_or_create(user=user)
                            
                            if teacher_info:
                               
                                if welcome_enabled.is_welcome_message_enabled and created:
                                    # Only send welcome message for new teachers
                                    thread_1 = threading.Thread(target=lambda:send_whatsapp_teacher_welcome(request,teacher_info.user.mobile_no,teacher_info.user.name))
                                    thread_1.start()
                                
                                # Get job_code from GET or POST parameters
                                job_code_param = request.GET.get('job_code') or request.POST.get('job_code') or request.GET.get('jobcode') or request.POST.get('jobcode')
                                
                                # Check if profile is complete
                                if not teacher_info.qualification:
                                    if job_code_param and job_code_param != 'None':
                                        return redirect(f'/teacher-profile?jobcode={job_code_param}')
                                    return redirect('/teacher-profile')
                                
                                if job_code_param and job_code_param != 'None': 
                                    return redirect(f'/current-vacancies?jobcode={job_code_param}')
                                
                                return redirect('/teacher-profile')
                            else:
                                return redirect('/teacher-profile')
                        else:
                            # Get or create School object (in case of re-registration)
                            school_info, created = School.objects.get_or_create(user=user)
                            if school_info:
                                if welcome_enabled.is_welcome_message_enabled and created:
                                    # Only send welcome message for new schools
                                    thread_1 = threading.Thread(target=lambda:send_whatsapp_school_welcome(request,school_info.user.mobile_no,school_info.user.name))
                                    thread_1.start()                                   
                                return redirect('/school-profile')
                            else:
                                return redirect('/school-profile')
                else:
                    # OTP verification failed - either wrong OTP or OTP already used/expired
                    messages.error(request, 'Invalid or expired OTP. Please check and try again or click Resend OTP.')
                    # Redirect back to registration page with mobile number to show OTP modal again
                    if user_type == 'School' or user_type == 'SCHOOLEXCLUSIVE':
                        return redirect(f'/registration?type=School&mobile_no={mobile_no_verify}')
                    else:
                        return redirect(f'/registration?type=Teacher&mobile_no={mobile_no_verify}')
            
            elif not request.GET.get('mobile_no'):
                # Handle initial 
                # print("Form Data:", user_type)
                if form.is_valid():
                    if user_type == 'SCHOOLEXCLUSIVE':
                        user_type = 'School'
                        request.user.user_type = 'School'
                    # print("User Type after form validation:", user_type)
                    # Additional validation for password match
                    password1 = request.POST.get('password1')
                    password2 = request.POST.get('password2')
                    # print("Password 1:", user_type)
                    
                    if password1 != password2:
                        messages.error(request, 'Passwords do not match!')
                        context = {
                            'page_title': page_title,
                            'meta_desc': meta_desc,
                            'keyword': keyword,
                            'schema': schema,
                            'otp_history': otp_history,
                            'customer_info': customer_info,
                            'user_type': user_type,
                            'jobcode': job_code,
                            'job': job,
                            'grade_data': Grade.objects.all() if user_type == 'School' else None,
                            'subject_data': JobFormData.objects.filter(data_type='Subject') if user_type == 'School' else None,
                            'qualification_data': JobFormData.objects.filter(data_type='Highest Qualification') if user_type == 'School' else None,
                            'experience_data': JobFormData.objects.filter(data_type='Experience Required') if user_type == 'School' else None,
                            'salary_data': JobFormData.objects.filter(data_type='Salary offered') if user_type == 'School' else None,
                            'benifits_data': JobFormData.objects.filter(data_type='Benefits & compensation') if user_type == 'School' else None,
                        }
                        return render(request, 'authentication/teacher_registration.html', context)
                    
                    # Handle registration where mobile may already exist but is not active
                    if user_type == 'SCHOOLEXCLUSIVE':
                        user_type = 'School'
                        request.user.user_type = 'School'
                    name = request.POST.get('name')
                    mobile_no = request.POST.get('mobile_no')

                    if request.POST.get('alt_mobile_no'):
                        alt_mobile_no = request.POST.get('alt_mobile_no')
                    else:
                        alt_mobile_no = None

                    existing_user = NewUser.objects.filter(mobile_no=mobile_no).first()
                    if existing_user:
                        # If the user exists but is not active, treat this as re-registration: update fields and keep inactive until OTP
                        NewUser.objects.filter(id=existing_user.id).update(
                            name=name,
                            temp_data=request.POST.get('password1'),
                            alt_mobile_no=alt_mobile_no,
                            is_active=False,
                            is_mobile_no_verified=False,
                            user_type=(user_type if user_type in ['Teacher','School'] else existing_user.user_type)
                        )
                        user_info = NewUser.objects.get(id=existing_user.id)
                    else:
                        # Create a new user but keep inactive until OTP verification
                        try:
                            new_user = form.save(commit=False)
                            new_user.temp_data = request.POST.get('password1')
                            new_user.is_active = False
                            new_user.is_mobile_no_verified = False
                            new_user.save()
                            user_info = new_user
                        except Exception as e:
                            print('registration: form.save() error:', e)
                            user_info = NewUser.objects.get(mobile_no=mobile_no)
                    
                    # Generate OTP and save to OtpHistory (MSG91 will be used to send SMS)
                    otp_code = ''.join(random.choice(string.digits) for _ in range(4))
                    otp_history, created = OtpHistory.objects.get_or_create(user_id=user_info.id)
                    # Use update for atomic write
                    OtpHistory.objects.filter(pk=otp_history.id).update(otp=otp_code, otp_session=1)
                    otp_info = OtpHistory.objects.get(id=otp_history.id)

                    # Use MSG91 OTP template
                    try:
                        status, response_text = send_sms_via_msg91(user_info.mobile_no, template_id=REG_TEMPLATE_ID, template_vars={'OTP': otp_info.otp})
                        print(f'MSG91 send (registration) response: status={status}, body={response_text}')
                        messages.warning(request, 'OTP sent successfully to your mobile no.')
                    except Exception as e:
                        print('SMS send failed (registration flow):', e)
                        messages.error(request, 'Unable to send OTP right now. Please try Resend OTP or try again later.')

                    # Redirect to registration GET so the OTP modal is shown (preserves type/job if present)
                    if user_type == 'Teacher':
                        redirect_url = f'/registration?type=Teacher&mobile_no={mobile_no}'
                    else:
                        redirect_url = f'/registration?type=School&mobile_no={mobile_no}'

                    job_code_post = request.POST.get('jobcode') or ''
                    job_post = request.POST.get('job') or ''
                    if job_code_post:
                        redirect_url += f'&job_code={job_code_post}'
                    if job_post:
                        redirect_url += f'&job={job_post}'

                    return redirect(redirect_url)

                    # Note: previously the flow auto-activated Teacher accounts (skipping OTP).
                    # We now send OTP and redirect for verification. The old auto-activation path
                    # is preserved further down if needed, but won't be executed because of the return above.
                    try:
                        # Mark the account as verified/active
                        NewUser.objects.filter(mobile_no=mobile_no).update(is_mobile_no_verified=True, is_active=True)
                        new_user_info = NewUser.objects.filter(mobile_no=mobile_no).first()

                        # Authenticate and log the user in using the temp_data (keeps existing flow)
                        user = authenticate(request, mobile_no=new_user_info.mobile_no, password=new_user_info.temp_data)
                        welcome_enabled = WelcomeMessageControl.objects.get(id=1) if WelcomeMessageControl.objects.exists() else SimpleNamespace(is_welcome_message_enabled=False)
                        if user is not None:
                            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                            # clear temp_data as done in the OTP-confirmation path
                            NewUser.objects.filter(id=new_user_info.id).update(temp_data=None)

                            if user_type == 'Teacher':
                                # create teacher record and send welcome if configured
                                Teacher.objects.create(user=user)
                                teacher_info = Teacher.objects.filter(user_id=new_user_info.id).first()
                                if teacher_info and welcome_enabled.is_welcome_message_enabled:
                                    thread_1 = threading.Thread(target=lambda: send_whatsapp_teacher_welcome(request, teacher_info.user.mobile_no, teacher_info.user.name))
                                    thread_1.start()

                                # Redirect to profile (same behavior as OTP-confirmation branch)
                                job_code_param = request.GET.get('job_code') or request.POST.get('job_code') or request.GET.get('jobcode') or request.POST.get('jobcode')
                                if not teacher_info.qualification:
                                    if job_code_param:
                                        return redirect(f'/teacher-profile?jobcode={job_code_param}')
                                    return redirect('/teacher-profile')

                                if job_code_param and job_code_param != 'None':
                                    return redirect(f'/current-vacancies?jobcode={job_code_param}')

                                return redirect('/teacher-profile')
                            else:
                                # For non-teacher types fall back to existing behavior (activate and redirect to school-profile)
                                School.objects.create(user=user)
                                school_info = School.objects.filter(user_id=new_user_info.id).first()
                                if school_info and welcome_enabled.is_welcome_message_enabled:
                                    thread_1 = threading.Thread(target=lambda: send_whatsapp_school_welcome(request, school_info.user.mobile_no, school_info.user.name))
                                    thread_1.start()
                                return redirect('/school-profile')
                    except Exception as e:
                        print('Auto-activation/login (skip OTP) failed:', e)
                        # If something goes wrong, fall back to showing registration page (OTP path still present)
                        return redirect(f'/registration?type=Teacher&mobile_no={mobile_no}')
                        
        if request.GET.get('mobile_no'):
            customer_info = NewUser.objects.get(mobile_no=request.GET.get('mobile_no'))
            otp_history = OtpHistory.objects.filter(user__mobile_no=request.GET.get('mobile_no')).first()

    # Get job form data for school registration
    if user_type == 'School' or user_type == 'SCHOOLEXCLUSIVE':
        grade_data = Grade.objects.all()
        subject_data = JobFormData.objects.filter(data_type='Subject')
        qualification_data = JobFormData.objects.filter(data_type='Highest Qualification')
        experience_data = JobFormData.objects.filter(data_type='Experience Required')
        salary_data = JobFormData.objects.filter(data_type='Salary offered')
        benifits_data = JobFormData.objects.filter(data_type='Benefits & compensation')
    else:
        grade_data = None
        subject_data = None
        qualification_data = None
        experience_data = None
        salary_data = None
        benifits_data = None

    context = {
        'page_title':page_title,
        'meta_desc':meta_desc,
        'keyword':keyword,
        'schema':schema,
        'otp_history':otp_history,
        'customer_info':customer_info,
        'user_type':user_type,
        'jobcode':job_code,
        'job':job,
        'grade_data': grade_data,
        'subject_data': subject_data,
        'qualification_data': qualification_data,
        'experience_data': experience_data,
        'salary_data': salary_data,
        'benifits_data': benifits_data,
        'form': form,  # Add form to context for error display
    }
    
    return render(request,'authentication/teacher_registration.html', context)

@csrf_protect
@require_http_methods(["POST"])
def save_draft_job(request):
    """Save draft job data using dictionary-based storage"""
    if request.method == 'POST':
        import json
        
        mobile_no = request.POST.get('mobile_no')
        job_location = json.loads(request.POST.get('job_location', '{}'))
        job_data = json.loads(request.POST.get('job_data', '{}'))
        
        # Create draft job dictionary
        draft_job_data = {
            'mobile_no': mobile_no,
            'teacher_grade': job_data.get('teacher_grade', ''),
            'subject': job_data.get('subject', ''),
            'highest_qualification': job_data.get('highest_qualification', ''),
            'experienced_required': job_data.get('experienced_required', ''),
            'salary_offered': job_data.get('salary_offered', ''),
            'joining': job_data.get('joining', ''),
            'benifits_compensation': job_data.get('benifits_compensation', ''),
            'pincode': job_location.get('pincode', ''),
            'state': job_location.get('state', ''),
            'district': job_location.get('district', ''),
            'address': job_location.get('address', ''),
            'description': job_data.get('description', ''),
            'created_at': datetime.now().isoformat(),
        }
        
        save_draft_job_to_cache(mobile_no, draft_job_data)
        
        return JsonResponse({'success': True, 'message': 'Draft job saved successfully'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


# Dictionary-based storage for draft jobs using Django's cache framework
from django.core.cache import cache

def save_draft_job_to_cache(mobile_no, draft_job_data):
    """Save draft job data to dictionary-based storage (cache)"""
    cache_key = f"draft_jobs_{mobile_no}"
    existing_jobs = cache.get(cache_key, [])
    
    # Add new job to the list
    existing_jobs.append(draft_job_data)

    cache.set(cache_key, existing_jobs, timeout=86400)

def get_draft_jobs_from_storage(mobile_no):
    """Get draft jobs from dictionary-based storage (cache)"""
    cache_key = f"draft_jobs_{mobile_no}"
    return cache.get(cache_key, [])

def clear_draft_jobs_from_storage(mobile_no):
    """Clear draft jobs from dictionary-based storage (cache)"""
    cache_key = f"draft_jobs_{mobile_no}"
    cache.delete(cache_key)
      
def forgot_password(request):
    page_title = "Forgot Password"
    meta_desc = ""
    keyword = ""
    schema = ""


    return render(request,'authentication/forgot_password.html') 

def check_mobile(request, mobile_no):
    try:
        # Consider a mobile "taken" only if it is already verified. Unverified (OTP pending)
        # accounts should NOT block registration and should allow re-send of OTP.
        exists = NewUser.objects.filter(mobile_no=mobile_no, is_mobile_no_verified=True).exists()
        return JsonResponse(bool(exists), safe=False)
    except Exception as e:
        print('check_mobile error:', e)
        # On error, return False so registration can proceed (safer UX)
        return JsonResponse(False, safe=False)

def check_email(request, email):

    if NewUser.objects.filter(email=email).exists():
        return JsonResponse(True,safe=False)
    else:
        return JsonResponse(False,safe=False)


def resend_otp(request):
        
    page_title = "Resend OTP | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    if request.GET.get('otp_mobile_no'):

        user_info = NewUser.objects.get(mobile_no=request.GET.get('otp_mobile_no'))
        UserLog.objects.create(user=user_info,action='Resend OTP')
                    
        otp_code = ''.join(random.choice(string.digits) for _ in range(4))
        otp_history, created = OtpHistory.objects.get_or_create(user_id=user_info.id)
        # Reset otp_session to 1 (active) when resending - previous OTP is invalidated
        OtpHistory.objects.filter(pk=otp_history.id).update(otp=otp_code, otp_session=1)

        otp_info = OtpHistory.objects.get(id=otp_history.id)

                    
        # Use MSG91 OTP template
        try:
            status, response_text = send_sms_via_msg91(user_info.mobile_no, template_id=REG_TEMPLATE_ID, template_vars={'OTP': otp_info.otp})
            print(f'MSG91 send (resend_otp) response: status={status}, body={response_text}')
            messages.warning(request, 'OTP Resent successfully to your mobile no.')
        except Exception as e:
            print('SMS resend failed (resend_otp):', e)
            messages.error(request, 'Unable to resend OTP right now. Please try again later.')

        return redirect('/registration?mobile_no='+user_info.mobile_no)
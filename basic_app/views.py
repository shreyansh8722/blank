from django.shortcuts import redirect, render
import os
from django.contrib import messages
from .models import *
from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Sum
import json
import requests
from django.http import JsonResponse
from cog_static_app.views import disable_expired_jobs,disable_expired_promotions

disable_expired_jobs(repeat=86400) 
disable_expired_promotions(repeat=86400)
def get_authorization_shiprocket(request):
    
    url = "https://apiv2.shiprocket.in/v1/external/auth/login"

    payload = json.dumps({
                    "email": "corenpure@gmail.com",
                    "password": "1qaz2wsx3edc@A"
                })
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, data=payload, timeout=15)
        
        # Log the response for debugging
        print(f'Shiprocket auth status: {response.status_code}')
        
        if response.status_code == 200:
            data_dict = response.json()
            shiprocket_token = data_dict.get('token')
            if shiprocket_token:
                print('Shiprocket auth successful')
                return shiprocket_token
        elif response.status_code == 403:
            print(f'Shiprocket auth 403 Forbidden - credentials may be invalid or IP blocked')
            try:
                error_data = response.json()
                print(f'Shiprocket error response: {error_data}')
            except:
                print(f'Shiprocket response text: {response.text[:200]}')
        elif response.status_code == 401:
            print('Shiprocket auth 401 Unauthorized - invalid credentials')
        else:
            print(f'Shiprocket auth failed with status {response.status_code}: {response.text[:200]}')
        
        return None
    except requests.exceptions.Timeout:
        print('Shiprocket auth timeout')
        return None
    except Exception as e:
        print(f'Shiprocket auth exception: {str(e)[:200]}')
        return None
# def getpincodedetails(request,pincode):
#     data = {'city': '', 'address': '', 'state': '', 'is_exists': False}

#     # API definitions in order
#     api_chain = [
#         # {
#         #     "name": "Zippopotam",
#         #     "url": f"http://api.zippopotam.us/IN/{pincode}",
#         #     "handler": lambda r: {
#         #         'city': r['places'][0].get('place name', ''),
#         #         'address': r['places'][0].get('place name', ''),
#         #         'state': r['places'][0].get('state', ''),
#         #         'is_exists': True
#         #     } if 'places' in r and r['places'] else None
#         # },
#         {
#             "name": "IndiaPost",
#             "url": f"https://api.postalpincode.in/pincode/{pincode}",
#             "handler": lambda r: parse_india_post_api(r)
#         },
#         {
#             "name": "PincodeNet",
#             "url": f"https://pincode.net.in/api/pincode/{pincode}",
#             "headers": {'User-Agent': 'Mozilla/5.0'},
#             "handler": lambda r: (
#                 {
#                     'city': rec.get('district') or rec.get('division', ''),
#                     'state': rec.get('state', ''),
#                     'address': rec.get('office') or rec.get('district', ''),
#                     'is_exists': True
#                 } if isinstance(r, dict)
#                   and r.get('status') == 'success'
#                   and (records := r.get('data'))
#                   and (rec := records[0])
#                 else None
#             )
#         },
#         {
#             "name": "PostalAlt",
#             "url": f"https://www.postalpincode.in/api/pincode/{pincode}",
#             "handler": lambda r: parse_postal_api(r)
#         }
#     ]

#     for api in api_chain:
#         try:
#             response = requests.get(api["url"], timeout=10, headers=api.get("headers", {}))
#             if response.status_code != 200:
#                 continue
    
#             # Parse JSON safely
#             try:
#                 json_data = response.json()
#             except ValueError:
#                 # Invalid JSON → skip to next API
#                 continue
    
#             # Skip blank or empty JSON
#             if not json_data or json_data == {}:
#                 continue
    
#             parsed = api["handler"](json_data)
    
#             # Parsed must exist AND is_exists must be True
#             if parsed and parsed.get('is_exists'):
#                 print(f"Pincode {pincode} found via {api['name']}: {parsed}")
#                 return JsonResponse(parsed)
    
#         except Exception as e:
#             print(f"{api['name']} API error for {pincode}: {str(e)[:100]}")
    
#     print(f"Pincode {pincode} not found in any API")
#     return JsonResponse(data)


def getpincodedetails(request, pincode):
    data = {'city': '', 'address': '', 'state': '', 'is_exists': False}
    
    # Try Zippopotam.us API (reliable, no auth, works globally)
    # try:
    #     url = f"http://api.zippopotam.us/IN/{pincode}"
    #     response = requests.get(url, timeout=10)
        
    #     if response.status_code == 200:
    #         zip_data = response.json()
    #         if 'places' in zip_data and len(zip_data['places']) > 0:
    #             place = zip_data['places'][0]
    #             data['city'] = place.get('place name', '')
    #             data['state'] = place.get('state', '')
    #             data['address'] = place.get('place name', '')
    #             data['is_exists'] = True
    #             print(f"Pincode {pincode} found via Zippopotam: {data}")
    #             return JsonResponse(data)
    # except Exception as e:
    #     print(f"Zippopotam API error for {pincode}: {str(e)[:100]}")
    
    # Try India Post API (free, no auth required)
    try:
        url = f"https://api.postalpincode.in/pincode/{pincode}"
        response = requests.get(url, timeout=10,headers={'User-Agent': 'Mozilla/5.0'})
        
        if response.status_code == 200:
            parsed_data = parse_india_post_api(response.json())
            if parsed_data and parsed_data.get('is_exists'):
                print(f"Pincode {pincode} found via India Post API: {parsed_data}")
                return JsonResponse(parsed_data)
    except Exception as e:
        print(f"India Post API error for {pincode}: {str(e)[:100]}")
    
    # Try Pincode.net.in API
    try:
        url = f"https://pincode.net.in/api/pincode/{pincode}"
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        
        if response.status_code == 200:
            pin_data = response.json()
            if isinstance(pin_data, dict) and pin_data.get('status') == 'success':
                records = pin_data.get('data', [])
                if records and len(records) > 0:
                    record = records[0]
                    data['city'] = record.get('district', '') or record.get('division', '')
                    data['state'] = record.get('state', '')
                    data['address'] = record.get('office', '') or record.get('district', '')
                    data['is_exists'] = True
                    print(f"Pincode {pincode} found via Pincode.net.in: {data}")
                    return JsonResponse(data)
    except Exception as e:
        print(f"Pincode.net.in API error for {pincode}: {str(e)[:100]}")
    
    # Try alternative Postal API
    try:
        url = f"https://www.postalpincode.in/api/pincode/{pincode}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            parsed_data = parse_postal_api(response.json())
            if parsed_data and parsed_data.get('is_exists'):
                print(f"Pincode {pincode} found via Postal API: {parsed_data}")
                return JsonResponse(parsed_data)
    except Exception as e:
        print(f"Postal API error for {pincode}: {str(e)[:100]}")

    print(f'Pincode {pincode} not found in any API')
    return JsonResponse(data)

def parse_india_post_api(response_data):
    """Parse India Post API response"""
    data = {'city': '', 'address': '', 'state': '', 'is_exists': False}

    try:
        if response_data and isinstance(response_data, list):
            root = response_data[0]

            if root.get("Status") == "Success":
                offices = root.get("PostOffice") or []
                if offices:
                    office = offices[0]

                    data['city'] = office.get('District') or office.get('Block') or ''
                    data['address'] = office.get('Name') or ''
                    data['state'] = office.get('State') or ''

                    # IMPORTANT: India Post Success → treat as valid
                    data['is_exists'] = True

    except Exception as e:
        print("Error parsing India Post API:", e)

    return data


def parse_postal_api(response_data):
    """Parse alternative Postal API response"""
    data = {'city': '', 'address': '', 'state': '', 'is_exists': False}
    try:
        if isinstance(response_data, dict):
            if response_data.get('Status') == 'Success':
                records = response_data.get('PostOffice', [])
                if records and len(records) > 0:
                    record = records[0]
                    data['city'] = record.get('District', '') or record.get('Block', '')
                    data['address'] = record.get('Name', '')
                    data['state'] = record.get('State', '')
                    data['is_exists'] = True
    except Exception as e:
        print(f'Error parsing Postal API: {e}')
    return data

def basic(request):
    page_title = "Basic | title"
    meta_desc = ""
    keyword = ""
    schema = ""

    context = {
        'page_title':page_title,
        'meta_desc':meta_desc,
        'keyword':keyword,
        'schema':schema,
    }

    return render(request,'basic.html', context)  

def newsletter(request):
    page_title = "Add Newsletter | title"
    meta_desc = ""
    keyword = ""
    schema = ""

    if request.method == 'POST':

        email = request.POST.get('email')
        nl=Newsletter.objects.create(email=email)

        if nl:
            return JsonResponse(True,safe=False)
        else:
            return JsonResponse(False,safe=False)


def add_inquiry(request):
    page_title = "Add Inquiry | title"
    meta_desc = ""
    keyword = ""
    schema = ""

    if request.method == 'POST':

        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        inquiry=Inquiry.objects.create(name=name, email=email,message=message)
        
        # Mail to Admin

        context = {
            'name': inquiry.name,
            'email': inquiry.email,
            'message': inquiry.message,
        }

        html_message = render_to_string('mails/mail_inquiry.html',context)
        from_email = 'Faculty Me <'+settings.EMAIL_HOST_USER+'>'
        subject = "Faculty Me - New Inquiry"
        message = EmailMultiAlternatives(
            subject=subject,
            body="",
            from_email=from_email,
            to=['support@facultyme.com']
            )
        message.attach_alternative(html_message, "text/html")
        message.send(fail_silently=True)

        if inquiry:
            return JsonResponse(True,safe=False)
        else:
            return JsonResponse(False,safe=False) 

def add_review(request):
    page_title = "Add Review | title"
    meta_desc = ""
    keyword = ""
    schema = ""
    if request.method == 'POST':

        # product_id = request.POST.get('product_id')
        name = request.POST.get('name')
        email = request.POST.get('email')
        image = request.FILES.get('image')
        review = request.POST.get('review')
        rating = request.POST.get('rating')

        review=Review.objects.create(
            # product_id=product_id,
            name=name,
            email=email,
            image=image,
            review=review,
            rating=rating)

        # rating_count=Review.objects.filter(product_id=product_id).count()
        # total_rating_sum=Review.objects.filter(product_id=product_id).aggregate(Sum('rating')) 

        # Product.objects.filter(pk=product_id).update(avg_rating=round((float(total_rating_sum['rating__sum'])/float(rating_count)),2))

        
        if review:
            return JsonResponse(True,safe=False)
        else:
            return JsonResponse(False,safe=False)            


def about(request):
    page_title = "About Us | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    return render(request,'static-pages/about.html', {'page_title':page_title,'meta_desc':meta_desc,'keyword':keyword,'schema':schema })     

def landing_page(request):
    page_title = "FacultyMe - Teacher Job Alerts"
    meta_desc = ""
    keyword = ""
    schema = ""

    return render(request,'static-pages/landing_page.html', {'page_title':page_title,'meta_desc':meta_desc,'keyword':keyword,'schema':schema })     


def team(request):
    """
    Render the team page. The view passes a `team` list to the template. Each member is a dict:
    {name, role, description, image}

    Currently this uses a hard-coded list (easy to replace with DB-backed Team.objects.all()).
    """
    page_title = "Our Team | Faculty Me"
    meta_desc = "Meet the team behind Faculty Me"
    keyword = "team, facultyme, about us"
    schema = ""

    team = [
        {
            'name': 'Amol Choudhary',
            'role': 'Founder & CEO',
            'description': 'To build India’s most trusted and comprehensive platform that supports educators at every stage and strengthens the quality of education nationwide.',
            'image': '/static/facultyme_img/cto.png',
            'info': 'Amol Choudhary is the Founder and CEO of FacultyMe, a rapidly growing platform that connects educators and schools across India. With 10+ years of experience as an educator for competitive exams such as NEET and CET, Amol has guided students toward achieving their goal of securing medical seats. \n Beginning his journey as an educator, he has managed academic programs, mentored students, and contributed to improving learning outcomes across multiple institutes. His deep understanding of the challenges faced by educators led him to build FacultyMe, which today serves 1,000+ schools and 20,000+ teachers across the country. \n Under his leadership, FacultyMe aims to become a one-stop solution for educators—providing recruitment support, professional development, academic tools, and essential resources that empower teachers and educational institutions nationwide.',
            'linkedin': 'https://www.linkedin.com/in/amol-choudhary-facultyme',
            'twitter': '',
            'instagram': ''
        }
    ]

    context = {
        'page_title': page_title,
        'meta_desc': meta_desc,
        'keyword': keyword,
        'schema': schema,
        'team': team,
    }

    return render(request, 'team.html', context)

def contact(request):
    page_title = "COntact | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    return render(request,'static-pages/contact.html', {'page_title':page_title,'meta_desc':meta_desc,'keyword':keyword,'schema':schema })     

def institute_faq(request):
    page_title = "School FAQs | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    faqs = Faq.objects.filter(type__iexact='School')


    context = {
        'page_title':page_title,
        'meta_desc':meta_desc,
        'keyword':keyword,
        'schema':schema,
        'faqs':faqs,
    }

    return render(request,'static-pages/institute_faq.html', context)     

def teacher_faq(request):
    page_title = "Teacher FAQs | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    faqs = Faq.objects.filter(type__iexact='School')


    context = {
        'page_title':page_title,
        'meta_desc':meta_desc,
        'keyword':keyword,
        'schema':schema,
        'faqs':faqs,
    }

    return render(request,'static-pages/teacher_faq.html', context)     

def error(request):
    page_title = "Error | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    return render(request,'static-pages/error.html', {'page_title':page_title,'meta_desc':meta_desc,'keyword':keyword,'schema':schema })     

def thankyou(request):
    page_title = "Thankyou | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    return render(request,'static-pages/thankyou.html', {'page_title':page_title,'meta_desc':meta_desc,'keyword':keyword,'schema':schema })     

def privacy(request):
    page_title = "Privacy Policy | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""
    
    policy = PrivacyPolicy.objects.first()

    context = {
        'page_title':page_title,
        'meta_desc':meta_desc,
        'keyword':keyword,
        'schema':schema,
        'policy':policy,
    }

    return render(request,'static-pages/privacy_policy.html', context)     

def terms_condition(request):
    page_title = "Terms | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    terms = TermsAndConditions.objects.first()
    
    context = {
        'page_title':page_title,
        'meta_desc':meta_desc,
        'keyword':keyword,
        'schema':schema,
        'terms':terms,
    }

    return render(request,'static-pages/terms_condition.html', context)     

def refund_cancellation_policy(request):
    page_title = "Refund/ Cancellation Policy | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""
    
    policy = RefundCancellationPolicy.objects.first()
    
    context = {
        'page_title':page_title,
        'meta_desc':meta_desc,
        'keyword':keyword,
        'schema':schema,
        'policy':policy,
    }

    return render(request,'static-pages/refund_cancellation.html', context)     

def blogs(request):
    page_title = "Blogs | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    return render(request,'blogs.html', {'page_title':page_title,'meta_desc':meta_desc,'keyword':keyword,'schema':schema })         

def blog_detail(request):
    page_title = "Blog Detail | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    return render(request,'static-pages/blog_detail.html', {'page_title':page_title,'meta_desc':meta_desc,'keyword':keyword,'schema':schema })     

def checkout(request):
    page_title = "Checkout | Faculty Me"
    meta_desc = ""
    keyword = ""
    schema = ""

    return render(request,'static-pages/checkout.html', {'page_title':page_title,'meta_desc':meta_desc,'keyword':keyword,'schema':schema })     

from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from . models import Person,PersonData,Director,Specialist,Certificate
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import IntegrityError , transaction
from django.core.mail import send_mail
from directors.models import SpecialistRequest
import random
from django.conf import settings
  
verification_codes= {}
def generate_verification_code():
    return str(random.randint(100000, 999999))
def send_verification_code_email(user_email,code):
    subject = 'Your Email Verification Code'
    message = f"Your verification code is: {code}"
    send_mail(subject, message , settings.EMAIL_HOST_USER,[user_email])

def user_register_view(request: HttpRequest):
    if request.method == 'POST':
        if request.POST['password'] == request.POST['repeat-password']:
            try:
                with transaction.atomic():
                    email = request.POST['email']
                    username = request.POST['username']
                    # Check if username already exists
                    # if User.objects.filter(username=username).exists():
                    #     messages.error(request, "Username already taken. Please choose another.", "alert-danger")
                    #     return render(request, "accounts/register.html")
                    
                    # Check if email already exists
                    # if User.objects.filter(email=email).exists():
                    #     messages.error(request, "Email already registered. Please use another email.", "alert-danger")
                    #     return render(request, "accounts/register.html")
                    
                    new_user = User.objects.create_user(
                        username=username,
                        email=email,
                        first_name=request.POST['first_name'],
                        last_name=request.POST['last_name'],
                        password=request.POST['password']
                    )
                    new_user.is_active = False
                    new_user.save()
                   
                    birth_date = request.POST.get('birth_date')
                    gender = request.POST.get('gender')
                    
                    person = Person.objects.create(
                        user=new_user,
                        birth_date=birth_date,
                        gender=gender
                    )
                    height = request.POST.get('height')
                    weight = request.POST.get('weight')
                    goal = request.POST.get('goal', '')
                    chronic_diseases = request.POST.get('chronic_diseases', '')
                    
                    
                    person_data = PersonData.objects.create(
                        person=person,
                        height=float(height),
                        weight=float(weight),
                        goal=goal,
                        chronic_diseases=chronic_diseases
                    )                
                
                code = generate_verification_code()
                verification_codes[email] = code
                send_verification_code_email(email, code)
                return render(request, "accounts/vertify.html", {"email": email})
            
            except IntegrityError as e:
                print(f"IntegrityError: {e}")
                if "username" in str(e).lower():
                    messages.error(request, "Username already exists. Please choose another.", "alert-danger")
                elif "email" in str(e).lower():
                    messages.error(request, "Email already registered. Please use another email.", "alert-danger")
                else:
                    messages.error(request, f"Database error: {str(e)}", "alert-danger")
            
            except ValueError as e:
                messages.error(request, str(e), "alert-danger")
            
            except Exception as e:
                print(f"Exception: {e}")
                messages.error(request, f"Unexpected error during signup: {str(e)}", "alert-danger")
        else:
            messages.error(request, "Passwords must be the same", "alert-danger")
    
    return render(request, "accounts/register.html", {
        'specialty_choices': Specialist.SpecialtyChoices.choices,
        'gender_choices': Person.GenderChoices.choices
    })

def specialist_register_view(request: HttpRequest):
    if request.method == 'POST':
        if request.POST['password'] == request.POST['repeat-password']:
            try:
                with transaction.atomic():
                    email = request.POST['email']
                    username = request.POST['username']
                    
                    new_user = User.objects.create_user(
                        username=username,
                        email=email,
                        first_name=request.POST['first_name'],
                        last_name=request.POST['last_name'],
                        password=request.POST['password']
                    )
                    new_user.is_active = False
                    new_user.save()
                    
                    birth_date = request.POST.get('birth_date')
                    gender = request.POST.get('gender')
                    specialty = request.POST.get('specialty')
                    
                    specialist = Specialist.objects.create(
                        user=new_user,
                        birth_date=birth_date,
                        gender=gender,
                        specialty=specialty,
                        specialization_certificate=request.FILES.get('specialization_certificate'),
                        image = request.FILES.get('image')
                    )
                    specialisr_request = SpecialistRequest.objects.create(
                        specialist = specialist
                    )
                    
                    for key in request.POST:
                        if key.startswith('certificates-name-'):
                            certificate_number = key.split('-')[-1]
                            certificate_name = request.POST[key]
                            
                            file_key = f'certificates-file-{certificate_number}'
                            if file_key in request.FILES:
                                certificate_file = request.FILES[file_key]
                                
                                Certificate.objects.create(
                                    specialist=specialist,
                                    name=certificate_name,
                                    image=certificate_file
                                )
                code = generate_verification_code()
                verification_codes[email] = code
                send_verification_code_email(email, code)
                messages.info(request, "Your specialist account has been created and will be reviewed by a director after verification.", "alert-info")
                return render(request, "accounts/vertify.html", {"email": email})
            
            except IntegrityError as e:
                print(f"IntegrityError: {e}")
                if "username" in str(e).lower():
                    messages.error(request, "Username already exists. Please choose another.", "alert-danger")
                elif "email" in str(e).lower():
                    messages.error(request, "Email already registered. Please use another email.", "alert-danger")
                else:
                    messages.error(request, f"Database error: {str(e)}", "alert-danger")
            except ValueError as e:
                messages.error(request, str(e), "alert-danger")
            except Exception as e:
                print(f"Exception: {e}")
                messages.error(request, f"Unexpected error during register: {str(e)}", "alert-danger")
        else:
            messages.error(request, "Passwords must be the same", "alert-danger")
    return render(request, "accounts/register.html", {
        'specialty_choices': Specialist.SpecialtyChoices.choices
    })

def vertify_view(request:HttpRequest):
    if request.method == 'POST':
        code = request.POST.get('code')
        email = request.POST.get('email')
        expected_code = verification_codes.get(email)
        
        if expected_code and code == expected_code:
            user = User.objects.filter(email=email).order_by('-id').first()
            if user:
                user.is_active = True
                user.save()
                messages.success(request, "User registered successfully", "alert-success")
                return redirect('accounts:login_view')
            else:
                messages.error(request, "User not found.", "alert-danger")
        else:
            messages.error(request, "Invalid verification code.", "alert-danger")
    return render(request, "accounts/vertify.html", {"email": email})

def login_view(request: HttpRequest):
    if request.user.is_authenticated:
        messages.error(request, "You are Already logged in ", "alert-warning")
        return redirect('core:home_view')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if hasattr(user, 'specialist'):
                try:
                    specialist_request = SpecialistRequest.objects.get(specialist=user.specialist)
                    
                    if specialist_request.status == SpecialistRequest.RequestStatus.PENDING:
                        messages.error(request, "Your specialist request is still pending approval. Please wait until a director accepts you.", "alert-danger")
                        return redirect('accounts:login_view')
                    
                    if specialist_request.status == SpecialistRequest.RequestStatus.REJECTED:
                        messages.error(request, "Your specialist request has been rejected.", "alert-danger")
                        return redirect('accounts:login_view')
                
                except SpecialistRequest.DoesNotExist:
                    print("No SpecialistRequest found for this user")
                    messages.error(request, "Your specialist account is not properly set up. Please contact an administrator.", "alert-danger")
                    return redirect('accounts:login_view')
                except Exception as e:
                    print(f"Exception when checking specialist status: {e}")
                    messages.error(request, "There was a problem verifying your specialist status. Please contact support.", "alert-danger")
                    return redirect('accounts:login_view')

            
            if user.is_active:
                login(request, user)
                messages.success(request, f"Welcome {user.username}, you logged in successfully!", "alert-success")
                
                if hasattr(user, 'specialist'):
                    return redirect('specialists:specialist_dashboard', specialist_id=user.specialist.id)
                elif hasattr(user, 'director'):
                    return redirect('directors:dashboard')
                
                return redirect('core:home_view')
            else:
                messages.error(request, "Your account is not active. Please verify your email.", "alert-danger")
        else:
            messages.error(request, "Invalid username or password. Please try again.", "alert-danger")
    
    return render(request, "accounts/login.html")

def logout_view(request:HttpRequest):
    logout(request)
    messages.success(request,"logged out successfuly ", "alert-warning")
    return redirect('accounts:login_view')

# def profile_view(request: HttpRequest,user_name):
#     try:
#         user = User.objects.get(username=user_name)
#     except Exception as e:
#         print(e)
#         messages.error(request, "user not found . ", "alert-danger")
#         redirect('core:home')
#     return render(request, "accounts/profile.html")


def profile_view(request, user_name):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to view profiles.", "alert-danger")
        return redirect('accounts:login_view')
    try:
        profile_user = User.objects.get(username=user_name)
        if request.user.username != user_name:
            messages.error(request, "You can only view your own profile.", "alert-danger")
            return redirect('core:home_view')
        return render(request, 'accounts/profile.html', {'profile_user': profile_user})

    except User.DoesNotExist:
        messages.error(request, "User not found.", "alert-danger")
        return redirect('core:home_view')

    
def update_profile_view(request,user_name):
    if not request.user.is_authenticated:
        return redirect('accounts:login_view')
    if request.user.username != user_name:
        messages.error(request, "You can update your own profile.", "alert-danger")
        return redirect('core:home_view')
    # Get context data for the template
    context = {}
    
    # Get latest person data if user is a person
    if hasattr(request.user, 'person'):
        person = request.user.person
        person_data = PersonData.objects.filter(person=person).order_by('-created_at').first()
        context['latest_data'] = person_data
    
    # Get certificates if user is a specialist
    if hasattr(request.user, 'specialist'):
        specialist = request.user.specialist
        certificates = Certificate.objects.filter(specialist=specialist)
        context['certificates'] = certificates
        
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name')
        request.user.last_name = request.POST.get('last_name')
        request.user.save()
        
        # Handle certificate deletion
        if 'delete_certificate' in request.POST:
            cert_id = request.POST.get('delete_certificate')
            try:
                certificate = Certificate.objects.get(id=cert_id, specialist=request.user.specialist)
                certificate.delete()
                messages.success(request, "Certificate deleted successfully!", "alert-success")
                return redirect('accounts:update_profile_view',user_name)
            except Certificate.DoesNotExist:
                messages.error(request, "Certificate not found!", "alert-danger")
        
        # if specialist
        if hasattr(request.user, 'specialist'):
            specialist = request.user.specialist
            if 'specialty' in request.POST:
                specialist.specialty = request.POST.get('specialty')
            
            if 'profile_image' in request.FILES:
                specialist.image = request.FILES['profile_image']
            
            for key in request.POST:
                if key.startswith('certificates-name-'):
                    certificate_number = key.split('-')[-1]
                    certificate_name = request.POST[key]
                    
                    file_key = f'certificate_file_{certificate_number}'
                    if file_key in request.FILES:
                        certificate_file = request.FILES[file_key]
                        
                        Certificate.objects.create(
                            specialist=specialist,
                            name=certificate_name,
                            image=certificate_file
                        )
            specialist.save()

        # if person
        if hasattr(request.user, 'person'):
            person = request.user.person
            height = request.POST.get('height')
            weight = request.POST.get('weight')
            if height and weight:
                PersonData.objects.create(
                    person=person,
                    height=float(height),
                    weight=float(weight),
                    goal=request.POST.get('goal', ''),
                    chronic_diseases=request.POST.get('chronic_diseases', '')
                )
        
        messages.success(request, "Profile updated successfully!", "alert-success")
        return redirect('accounts:update_profile_view',user_name)
    
    return render(request, 'accounts/update_profile.html', context)
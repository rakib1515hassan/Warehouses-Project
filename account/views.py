import csv
from datetime import timedelta, datetime

from django.contrib.auth import authenticate, login
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
import random
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlencode, urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.csrf import csrf_exempt

from account.forms import RegistrationForm
from account.models import WarehouseUser, AccountTypeChangeRequest
from django.http import HttpResponse, JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from core.models import Warehouse, Booking, Payment, Rating, Invoice

from .decorators import email_verified_required, EmailVerifiedRequiredMixin


class AccountDetail(LoginRequiredMixin, EmailVerifiedRequiredMixin, TemplateView):
    model = WarehouseUser
    # template_name = "account.html"
    template_name = 'dashboard/index.html'
    context_object_name = "user"

    def get(self, request, *args, **kwargs):
        user = request.user

        if user.account_type == "BUSINESS":
            return redirect("account:bookings")

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.account_type == "WAREHOUSE_OWNER":
            context['warehouses'] = Warehouse.objects.filter(owner=self.request.user)
        elif self.request.user.account_type == "ADMIN":
            context['warehouses'] = Warehouse.objects.all()
        return context


class Bookings(LoginRequiredMixin, EmailVerifiedRequiredMixin, TemplateView):
    model = Booking
    # template_name = "account.html"
    template_name = 'dashboard/booking.html'
    context_object_name = "user"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.account_type == "WAREHOUSE_OWNER":
            bookings = Booking.objects.filter(warehouse__owner=self.request.user)
            context['earning'] = Payment.objects.filter(booking__in=bookings).aggregate(Sum('amount'))['amount__sum']
        elif self.request.user.account_type == "ADMIN":
            bookings = Booking.objects.all()
        elif self.request.user.account_type == "BUSINESS":
            bookings = Booking.objects.filter(business=self.request.user)

        pending_bookings = bookings.filter(status="PENDING")
        pending_ratio = 100 * pending_bookings.count() / bookings.count() if bookings.count() > 0 else 0

        context['bookings'] = bookings
        context['pending_bookings'] = pending_bookings.count()
        context['pending_ratio'] = pending_ratio
        return context


class SpaceRequest(LoginRequiredMixin, EmailVerifiedRequiredMixin, TemplateView):
    model = Booking
    template_name = 'dashboard/space_request.html'
    context_object_name = "user"

    def dispatch(self, request, *args, **kwargs):
        if request.user.account_type == "BUSINESS":
            raise Http404("Permission Denied ")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.account_type == "WAREHOUSE_OWNER" or self.request.user.is_superuser:
            space_request = Booking.objects.filter(business=self.request.user)

        context['space_request'] = space_request

        return context


class Details(LoginRequiredMixin, EmailVerifiedRequiredMixin, TemplateView):
    model = WarehouseUser
    template_name = "dashboard/overview.html"
    context_object_name = "user"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['earning'] = user_earning(self.request.user)
        return context


class Settings(LoginRequiredMixin, EmailVerifiedRequiredMixin, TemplateView):
    model = WarehouseUser
    template_name = "dashboard/settings.html"
    context_object_name = "user"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['earning'] = user_earning(self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        # for update profile
        request.user.first_name = request.POST.get('first_name', None)
        request.user.last_name = request.POST.get('last_name', None)
        request.user.address = request.POST.get('address', None)
        request.user.phone_number = request.POST.get('phone', None)
        request.user.company_name = request.POST.get('company_name', None)
        request.user.email = request.POST.get('email', None)
        if request.POST.get('confirm_password'):
            request.user.set_password(request.POST.get('confirm_password'))
            subject = 'Password Changed'
            message = f'Your password has been changed successfully'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [request.user.email]
            try:
                e_message = EmailMessage(subject, message, from_email, recipient_list)
                e_message.content_subtype = 'html'
                e_message.send()
            except Exception as e:
                print(e)
                pass

        request.user.save()

        return JsonResponse({"message": "success"}, status=200)


def user_login(request):
    if request.user.is_authenticated:
        return render(request, 'index.html')

    if request.method == 'POST':
        email_or_username = request.POST.get('email_or_username')
        password = request.POST.get('password')
        next_param = request.POST.get('next', '')
        redirect_url = f"{reverse('account:login')}?{urlencode({'next': next_param})}"
        user = None

        try:
            # Authenticate using email
            if (WarehouseUser.objects.filter(email=email_or_username).exists()):
                usr = WarehouseUser.objects.get(email=email_or_username)
                user = authenticate(request, username=usr.username, password=password)

            # Authenticate using username
            elif (WarehouseUser.objects.filter(username=email_or_username).exists()):
                usr = WarehouseUser.objects.get(username=email_or_username)
                user = authenticate(request, username=usr.username, password=password)

            if user is not None:
                login(request, user)
                if request.POST.get('next'):
                    return redirect(next_param)
                # if superuser then redirect to dashboard otherwise redirect to home page
                if user.is_superuser:
                    return redirect('account:account')
                else:
                    return redirect('core:index')

            else:
                messages.error(request, 'Invalid email or password.')
                return redirect(redirect_url)

        except ObjectDoesNotExist:
            messages.error(request, 'Invalid email or password.')
            return redirect(redirect_url)
    else:
        return render(request, 'login.html')


# logout view
@login_required
def user_logout(request):
    logout(request)
    return redirect('account:login')


def user_signup(request):
    registerForm = RegistrationForm()
    if request.user.is_authenticated:
        return redirect('core:index')

    if request.method == 'POST':
        registerForm = RegistrationForm(request.POST)
        if registerForm.is_valid():
            user = registerForm.save(commit=False)
            user.verification_code = str(random.randint(100000, 999999))
            password = registerForm.cleaned_data.get('password')
            user.set_password(password)
            user.save()
            # login(request, user)
            subject = 'Verify your email address'
            message = f'Your verification code is: {user.verification_code}'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [user.email]
            try:
                e_message = EmailMessage(subject, message, from_email, recipient_list)
                e_message.content_subtype = 'html'
                e_message.send()
                return redirect("account:verify_email")
            except Exception as e:
                return render(request, 'register.html')

    return render(request, 'register.html', {'form': registerForm})


def validate_field(request):
    if request.GET.get('email'):
        if WarehouseUser.objects.filter(email__icontains=request.GET.get('email')).exists():
            return HttpResponse("<div class='text-danger'>Email exists</div>")
        else:
            return HttpResponse("<div class='text-success'>Email available</div>")
    elif request.GET.get('username'):
        if WarehouseUser.objects.filter(username__icontains=request.GET.get('username')).exists():
            return HttpResponse("<div class='text-danger'>Username exists</div>")
        else:
            return HttpResponse("<div class='text-success'>Username available</div>")


def forget_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if WarehouseUser.email_exists(email):
            messages.info(request, "An email has been send to your mail. Please follow the instruction in email for "
                                   "rest your password")
            user = WarehouseUser.objects.get(email=email)
            current_site = get_current_site(request)
            mail_subject = "Reset password"
            messsage = render_to_string('rest_password_mail.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
                'time': urlsafe_base64_encode(force_bytes(timezone.now() + timedelta(hours=2))),
            })
            print(timezone.now())
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email, ]
            send_mail(mail_subject, messsage, email_from, recipient_list)

        else:
            messages.info(request, "Invalid Email")

    return render(request, 'forget_password.html')


def resetpassword_validate(request, uidb64, token, time64):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = WarehouseUser.objects.get(pk=uid)
        decoded_time = urlsafe_base64_decode(time64).decode('utf-8')
        expiration_time = datetime.fromisoformat(decoded_time)
    except:
        user = None
        expiration_time = None
        uid = None

    if user is not None and default_token_generator.check_token(user,
                                                                token) and expiration_time and expiration_time > timezone.now():
        request.session['cid'] = uid
        messages.success(request, "please reset your password here")
        return redirect('account:reset_password')

    else:
        messages.warning(request, "Link expired!!!")
        return redirect('account:login')


def reset_password(request):
    if request.session.get('cid'):
        if request.method == "POST":
            password = request.POST.get("create_password")
            confirm_password = request.POST.get("confirm_password")
            if password == confirm_password:
                cid = request.session.get('cid')
                user = WarehouseUser.objects.get(pk=cid)
                new_pass = make_password(confirm_password)
                user.password = new_pass
                user.save()
                del request.session['cid']
                messages.success(request, "Reset password successfully!!!")
                return redirect('account:login')
            else:
                messages.error(request, "Password doesn't match!!!")
                return redirect('account:reset_password')
        else:
            return render(request, 'reset_password.html')
    else:
        messages.warning(request, "Link Expired!!!")
        return redirect('account:login')


@login_required
def not_verified(request):
    user = request.user
    user.verification_code = str(random.randint(100000, 999999))
    user.is_email_verified = False
    user.save()
    subject = 'Verify your email address'
    message = f'Your verification code is: {user.verification_code}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    try:
        e_message = EmailMessage(subject, message, from_email, recipient_list)
        e_message.content_subtype = 'html'
        e_message.send()
        return redirect("account:verify_email")
    except Exception as e:
        return render(request, 'register.html')


@login_required
def verify_email(request):
    if request.method == 'POST':
        user = request.user
        verification_code = request.POST.get('verification_code')
        if verification_code == user.verification_code:
            user.is_email_verified = True
            user.save()
            # login(request, user)
            return redirect('/')
        else:
            error_message = 'Incorrect verification code'
    else:
        error_message = ''
    return render(request, 'verify_email.html', {'error_message': error_message})


@login_required
@email_verified_required
def export_view(request):
    if request.user.is_superuser:
        context = {
            "total_warehouse": Warehouse.objects.all().count(),
            "total_user": WarehouseUser.objects.filter(is_superuser=False).count(),
            "total_booking": Booking.objects.all().count()
        }
        return render(request, 'dashboard/export.html', context)
    else:
        return redirect('account:account')


@login_required
@email_verified_required
def export_bookings_csv(request):
    global model, response
    if request.method == "POST":
        model = request.POST.get("model")
    if model == "Booking":
        bookings = Booking.objects.all()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="bookings.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Ware House', 'Owner', 'Business', 'Product', 'Quantity', 'Area',
            'Start Date', 'Duration_Storage', 'Status', 'Time'
        ])

        for booking in bookings:
            writer.writerow([
                booking.id,
                booking.warehouse,
                booking.warehouse.owner,
                booking.business,
                booking.product,
                booking.quantity,
                booking.area,
                booking.start_date,
                booking.Duration_Storage,
                booking.status,
                booking.created_at
            ])
    elif model == "Warehouse":
        warehouses = Warehouse.objects.all()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="warehouses.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Warehouse ID', 'Owner', 'Name', 'Location', 'Coordinates', 'Size', 'Price',
            'Availability', 'Accessibility', 'Warehouse Type', 'Storage Temperature',
            'Workforce', 'Warehouse Classification', 'Storage Space Type', 'Equipment',
            'Security', 'Services Offered', 'Order Taking Time', 'Flexibility Transport Appointments',
            'Flexible Hours', 'Authorization Access People Outside', 'Insurance',
            'Is Available', 'Created At',
        ])

        for warehouse in warehouses:
            writer.writerow([
                warehouse.id,
                warehouse.owner,
                warehouse.name,
                warehouse.location,
                warehouse.coordinates,
                warehouse.size,
                warehouse.price,
                warehouse.availability,
                warehouse.accessibility,
                warehouse.warehouse_type,
                warehouse.storage_temperature,
                warehouse.workforce,
                warehouse.warehouse_classification,
                ', '.join(str(sst) for sst in warehouse.storage_space_type.all()),
                ', '.join(str(equipment) for equipment in warehouse.equipment.all()),
                ', '.join(str(security) for security in warehouse.security.all()),
                ', '.join(str(service) for service in warehouse.services_offered.all()),
                warehouse.order_taking_time,
                warehouse.flexibility_transport_appointments,
                warehouse.flexible_hours,
                warehouse.authorization_access_people_outside,
                warehouse.Insurance,
                warehouse.is_available,
                warehouse.created_at,

            ])
    elif model == "User":
        users = WarehouseUser.objects.all()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Full Name', 'Account Type', 'Email', 'Phone Number',
            'Company Name', 'Address', 'Is Email Verified'
        ])

        for user in users:
            writer.writerow([
                user.id,
                user.get_full_name(),
                user.get_account_type_display(),
                user.email,
                user.phone_number,
                user.company_name,
                user.address,
                user.is_email_verified
            ])
    elif model == "Rating":
        ratings = Rating.objects.all()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="ratings.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Ware House', 'Owner Rating', 'Owner Review', 'Business Rating',
            'Business Review'
        ])

        for rate in ratings:
            writer.writerow([
                rate.id,
                rate.booking.warehouse,
                rate.warehouse_owner_rating,
                rate.warehouse_owner_review,
                rate.business_rating,
                rate.business_review,
            ])

    elif model == "Invoice":
        invoices = Invoice.objects.all()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="invoice.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Ware House', 'Owner', 'Business', 'price'
        ])

        for invoice in invoices:
            writer.writerow([
                invoice.id,
                invoice.booking.warehouse,
                invoice.booking.warehouse.owner,
                invoice.booking.business,
                invoice.price,
            ])

    return response


def complete_profile(request):
    if request.method == "POST":
        request.user.account_type = request.POST.get('account_type')
        request.user.company_name = request.POST.get('company_name')
        request.user.is_email_verified = True
        request.user.save()
        return redirect("core:index")
    return render(request, "complete_profile.html")


def user_earning(user):
    warehouse_bookings = Booking.objects.filter(warehouse__owner=user)
    earning = Payment.objects.filter(booking__in=warehouse_bookings).aggregate(Sum('amount'))['amount__sum']
    my_bookings = Booking.objects.filter(business=user)
    spend = Payment.objects.filter(booking__in=my_bookings).aggregate(Sum('amount'))[
        'amount__sum']
    earning = earning or 0
    spend = spend or 0

    return earning - spend


@login_required
def customer_list(request):
    if not request.user.account_type == "ADMIN":
        raise Http404("Permission Denied ")
    context = {}
    context['user_list'] = WarehouseUser.objects.all().exclude(account_type="ADMIN")
    return render(request, "dashboard/user/list.html", context)


@csrf_exempt
@login_required
def customer_request(request):
    if not request.user.account_type == "ADMIN":
        raise Http404("Permission Denied ")
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        user = WarehouseUser.objects.get(id=user_id)
        change_request = AccountTypeChangeRequest.objects.get(user=user)
        user.account_type = "WAREHOUSE_OWNER"
        user.company_name = change_request.company_name
        subject = 'Account Type Change Request Accepted'
        message = f'Your request for account type change to Warehouse Owner has been accepted. Now you can add your own warehouse. Thank you'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user.email]
        try:
            e_message = EmailMessage(subject, message, from_email, recipient_list)
            e_message.content_subtype = 'html'
            e_message.send()
        except Exception as e:
            return JsonResponse({"result": "bad"}, status=400)
        user.save()
        change_request.delete()
        return JsonResponse({"result": "ok"}, status=200)
    context = {}
    context['request_user_list'] = AccountTypeChangeRequest.objects.all()
    return render(request, "dashboard/user/request.html", context)

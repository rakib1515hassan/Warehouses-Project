import os
import random
from django.contrib.auth import authenticate, login
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404, JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
# from weasyprint import HTML, CSS
# from weasyprint.text.fonts import FontConfiguration

from account.decorators import EmailVerifiedRequiredMixin,email_verified_required

from account.models import WarehouseUser, AccountTypeChangeRequest

from core.forms import WarehouseForm

from core.models import Accessibility, Availability, Duration_Storage, Equipment, Flexible_hours, Insurance, Order_taking_time, Product, Security, Start_Date, Storage_space_type, Warehouse_Classification, Warehouse_type, Workforce, Thread, Message, Rating, Invoice, Warehouse, WarehousePhoto, Booking, Services_Offered, Storage_temperature, Contact



def HomeView(request):
    template_name = "index.html"
    context = {}
    if request.user.is_authenticated and request.user.is_email_verified is False:
        return redirect("account:complete_profile")

    context['services'] = Services_Offered.objects.all()
    context['warehouses'] = Warehouse.objects.all()[:6]

    return render(request, template_name, context)


class HomeView2(TemplateView):
    template_name = "index2.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = Services_Offered.objects.all()
        context['warehouses'] = Warehouse.objects.all()[:6]
        return context


class ContactView(TemplateView):
    template_name = "contact.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = Services_Offered.objects.all()
        return context
    
    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        from_mail = request.POST.get('from_mail')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        contact = Contact.objects.create(name= name, email= from_mail, subject= subject, message= message)
        messages.success(request, "Your message is successfully submitted.")

        return self.render_to_response(self.get_context_data())
    


class WareHouseList(ListView):
    model = Warehouse
    template_name = "filter.html"
    context_object_name = "warehouses"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = Services_Offered.objects.all()
        context['temperatures'] = Storage_temperature.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        print(request.POST)
        location = request.POST.get('location')
        service = request.POST.get('service')
        transport = request.POST.get('transport')
        temperature = request.POST.get('temperature')
        queryset = Warehouse.objects.all()
        if location:
            queryset = queryset.filter(location__icontains=location)
        if service:
            queryset = queryset.filter(services_offered__name__in=[service])

        if transport:
            queryset = queryset.filter(warehouse_type__name__icontains=transport)

        if temperature:
            queryset = queryset.filter(storage_temperature_id=temperature)

        self.object_list = queryset
        context = self.get_context_data()
        return self.render_to_response(context)


class WareHouseDetails(DetailView):
    model = Warehouse
    template_name = "signle-page.html"
    context_object_name = "warehouse"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        context['start_date'] = Start_Date.objects.all()
        context['duration_storage'] = Duration_Storage.objects.all()
        context['reviews'] = Rating.objects.filter(booking__warehouse=self.get_object())
        if self.request.user.is_authenticated:
            if Booking.objects.filter(warehouse=self.get_object(), business=self.request.user, status="APPROVED").exists():
                context['userbooking'] = Booking.objects.filter(warehouse=self.get_object(), business=self.request.user,status="APPROVED", rating_booking__isnull=True)

        return context

    def post(self, request, *args, **kwargs):
        # Get the warehouse object from the primary key in the URL
        warehouse = self.get_object()
        if request.POST.get('message'):
            message_subject= request.POST.get('subject')
            thread = Thread.objects.filter(
                Q(first_person=request.user, second_person=warehouse.owner) |
                Q(first_person=warehouse.owner, second_person=request.user)
            ).first()
            if thread is None:
                thread = Thread.objects.create(first_person=request.user, second_person=warehouse.owner)
            Message.objects.create(thread=thread, user=request.user, message=f"Subject: {message_subject}. "f"{request.POST.get('message')}")
            subject = f'New message {message_subject}'
            message = f"Hi {warehouse.owner.get_full_name}, {request.user.get_full_name} send a message: " \
                      f"{request.POST.get('message')}. Go to your dashboard to check new message"
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [warehouse.owner.email]
            try:
                e_message = EmailMessage(subject, message, from_email, recipient_list)
                e_message.content_subtype = 'html'
                e_message.send()
            except Exception as e:
                print(e)
                pass
        elif request.POST.get('rating'):
            Rating.objects.create(
                booking=Booking.objects.get(id=request.POST.get('booking')),
                business_rating=request.POST.get('rating'),
                business_review=request.POST.get('review')
            )
        else:
            # Process the form data
            product_name = request.POST.get('product_name')
            quantity = request.POST.get('quantity')
            area = request.POST.get('area')
            start_date = request.POST.get('start_date')
            duration_storage = request.POST.get('duration_storage')

            product_instance = Product.objects.get(name=product_name)
            start_date_instance = Start_Date.objects.get(name=start_date)
            duration_storage_instance = Duration_Storage.objects.get(name=duration_storage)

            if warehouse.size < int(area):
                return render(request, self.template_name)

            update_warehouse_size = warehouse.size - int(area)
            Warehouse.objects.filter(pk=warehouse.pk).update(size=update_warehouse_size)

            if request.user.is_authenticated:
                # Update the user's profile if necessary
                if request.user.first_name == '':
                    first_name = request.POST.get('first_name')
                    WarehouseUser.objects.update(first_name=first_name)
                if request.user.last_name == '':
                    last_name = request.POST.get('last_name')
                    WarehouseUser.objects.update(last_name=last_name)
                if request.user.company_name == '':
                    company_name = request.POST.get('company_name')
                    WarehouseUser.objects.update(company_name=company_name)
                if request.user.phone_number == '':
                    phone_number = request.POST.get('phone_number')
                    WarehouseUser.objects.update(phone_number=phone_number)
            else:
                # Create an anonymous user if necessary
                a_first_name = request.POST.get('a_first_name')
                a_last_name = request.POST.get('a_last_name')
                a_email = request.POST.get('a_email')
                a_company_name = request.POST.get('a_company_name')
                a_phone_number = request.POST.get('a_phone_number')
                a_checkbox = request.POST.get('a_checkbox')

                random_password = random.randint(100000, 999999)

                if a_checkbox:
                    user = WarehouseUser.objects.create_user(email=a_email, password=random_password, username=a_email)
                    user.verification_code = str(random.randint(100000, 999999))
                    user.save()
                    login(request, user)
                    subject = 'Verify your email address and Login Password'
                    message = f'Your verification code is: {user.verification_code}. Your password is {random_password}'
                    from_email = settings.EMAIL_HOST_USER
                    recipient_list = [a_email]
                    try:
                        e_message = EmailMessage(subject, message, from_email, recipient_list)
                        e_message.content_subtype = 'html'
                        e_message.send()
                        return redirect("account:verify_email")
                    except Exception as e:
                        print(e)
                        pass

            total_price = warehouse.price * int(area)

            try:
                if request.user.is_authenticated:
                    booking = Booking.objects.create(warehouse=warehouse, business=request.user, quantity=quantity, area=area, start_date=start_date_instance,Duration_Storage=duration_storage_instance,product=product_instance)
                    invoice = Invoice.objects.create(user=request.user, booking=booking, price=total_price)
                    return redirect('core:download-invoice', id=invoice.id, mode='view')

            except Exception as e:
                messages.error(request, f'Error creating booking: {str(e)}')
                print(e)

            return redirect("core:warehouse_details", warehouse.pk)

        return redirect("core:warehouse_details", warehouse.pk)


class MyWareHouseList(LoginRequiredMixin,EmailVerifiedRequiredMixin, ListView):
    model = Warehouse
    template_name = "mywarehouses.html"
    context_object_name = "mywarehouses"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(owner=self.request.user)
        return queryset


class WarehouseCreateView(LoginRequiredMixin, EmailVerifiedRequiredMixin, CreateView):
    model = Warehouse
    form_class = WarehouseForm
    template_name = 'create_warehouse.html'
    success_url = reverse_lazy('account:account')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['equipments'] = Equipment.objects.all()
        context['security'] = Security.objects.all()
        context['storage_space_type'] = Storage_space_type.objects.all()
        context['availability'] = Availability.objects.all()
        context['accessibility'] = Accessibility.objects.all()
        context['warehouse_type'] = Warehouse_type.objects.all()
        context['storage_temperature'] = Storage_temperature.objects.all()
        context['workforce'] = Workforce.objects.all()
        context['warehouse_Classification'] = Warehouse_Classification.objects.all()
        context['services_Offered'] = Services_Offered.objects.all()
        context['order_taking_time'] = Order_taking_time.objects.all()
        context['flexible_hours'] = Flexible_hours.objects.all()
        context['insurance'] = Insurance.objects.all()
        return context

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            self.object = form.save(commit=False)
            self.object.owner = request.user
            location_coordinates = form.cleaned_data['location_coordinates']
            self.object.location = request.POST.get("location")
            self.object.coordinates = location_coordinates
            self.object.save()
            form.save_m2m()
            for photo in request.FILES.getlist('photos'):
                WarehousePhoto.objects.create(warehouse=self.object, photo=photo)
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


class WarehouseUpdateView(LoginRequiredMixin, EmailVerifiedRequiredMixin, UpdateView):
    model = Warehouse
    form_class = WarehouseForm
    template_name = 'update_warehouse.html'
    success_url = reverse_lazy('account:account')

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.owner != request.user:
            raise Http404("You are not the owner of this warehouse.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['photos'] = self.object.photos.all()
        return context

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        warehouse = self.get_object()
        # Create a form instance with the warehouse object as the instance parameter
        form = self.form_class(request.POST, request.FILES, instance=warehouse)
        if form.is_valid():
            self.object = form.save(commit=True)
            if form.cleaned_data['location_coordinates']:
                location_coordinates = form.cleaned_data['location_coordinates']
                self.object.location = request.POST.get("location")
                self.object.coordinates = location_coordinates
            self.object.save()
            for photo in request.FILES.getlist('photos'):
                WarehousePhoto.objects.create(warehouse=self.object, photo=photo)
            for photo_id in request.POST.getlist('delete_photos'):
                WarehousePhoto.objects.filter(id=photo_id).delete()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


@login_required
@email_verified_required
def WarehouseDeleteView(request, w_id):
    try:
        ware_house = Warehouse.objects.get(id=w_id, owner=request.user)
        ware_house.delete()
        return JsonResponse(data={"response": "ok"}, status=200)
    except ObjectDoesNotExist:
        return JsonResponse(data={"response": "bad"}, status=400)

@login_required
@email_verified_required
def create_booking(request, id):
    try:
        warehouse = Warehouse.objects.filter(pk=id).filter(is_available=True)
    except ObjectDoesNotExist:
        messages.error(request, 'Warehouse does not exist')
        return redirect('core:warehouse')

    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        quantity = request.POST.get('quantity')
        area = request.POST.get('area')
        start_date = request.POST.get('start_date')
        duration_Storage = request.POST.get('duration_storage')

        if request.user.is_authenticated:
            if request.user.first_name == '':
                first_name = request.POST.get('first_name')
                WarehouseUser.objects.update(first_name=first_name)
            if request.user.last_name == '':
                last_name = request.POST.get('last_name')
                WarehouseUser.objects.update(last_name=last_name)
            if request.user.company_name == '':
                company_name = request.POST.get('company_name')
                WarehouseUser.objects.update(company_name=company_name)
            if request.user.phone_number == '':
                phone_number = request.POST.get('phone_number')
                WarehouseUser.objects.update(phone_number=phone_number)
      
            a_first_name = request.POST.get('a_first_name')
            a_last_name = request.POST.get('a_last_name')
            a_email = request.POST.get('a_email')
            a_company_name = request.POST.get('a_company_name')
            a_phone_number = request.POST.get('a_phone_number')
            a_checkbox = request.POST.get('a_checkbox')

            random_password = random.randint(100000, 999999)

            if a_checkbox:
                user = WarehouseUser.objects.create_user(email=a_email, password=random_password, username=a_email)
                user.verification_code = str(random.randint(100000, 999999))
                user.save()
                login(request, user)
                subject = 'Verify your email address and Login Password'
                message = f'Your verification code is: {user.verification_code}. Your password is {random_password}'
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [a_email]
                try:
                    e_message = EmailMessage(subject, message, from_email, recipient_list)
                    e_message.content_subtype = 'html'
                    e_message.send()
                    return redirect("account:verify_email")
                except Exception as e:
                    print(e)
                    pass

        total_price = warehouse.price * int(area)

        try:
            if request.user.is_authenticated:
                booking = Booking.objects.create(warehouse=warehouse, business=request.user, quantity=quantity, area=area, start_date=start_date, duration_Storage=duration_Storage, product=product_name)

                Invoice.objects.create(user=request.user, booking=booking, price=total_price)

            return redirect('booking-list')
        except Exception as e:
            messages.error(request, f'Error creating booking: {str(e)}')
            return redirect('warehouse-detail', id=id)

    return render(request, 'create_booking.html', {'warehouse': warehouse})


class MyBooking(LoginRequiredMixin,EmailVerifiedRequiredMixin, ListView):
    model = Booking
    template_name = "test.html"
    context_object_name = "booking_lists"

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset().filter(business=user)
        return queryset


class BookingDetail(LoginRequiredMixin,EmailVerifiedRequiredMixin,DetailView):
    model = Booking
    template_name = "booking_detail.html"
    context_object_name = "booking"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(business=self.request.user)
        return queryset


@csrf_exempt
@login_required
@email_verified_required
def BookingStatusChange(request):
    booking_id = request.POST.get("booking_id")
    status = request.POST.get("status")
    booking = Booking.objects.get(id=booking_id)
    if booking.warehouse.owner != request.user:
        return Http404("You are not the owner of this warehouse.")
    
    if status == "DECLINE":
        booking.status = "DECLINE"
        booking.save()
    else:
        booking.status = "APPROVED"
        booking.save()
        subject = 'Booking Approved'
        message = f'Your booking for warehouse: {booking.warehouse.name} for {booking.Duration_Storage} has been changed Approved.' \
                f' Please go to your dashboard for more information'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [booking.business.email]
        try:
            e_message = EmailMessage(subject, message, from_email, recipient_list)
            e_message.content_subtype = 'html'
            e_message.send()
        except Exception as e:
            print(e)
            pass
    return JsonResponse({"response": "Success"}, status=200)


@login_required
@email_verified_required
def BookingOwnerRating(request):
    booking = Booking.objects.get(id=request.POST.get("booking_id"))
    try:
        rating = Rating.objects.get(booking=booking)
    except ObjectDoesNotExist:
        rating = Rating.objects.create(booking=booking)
    rating.warehouse_owner_rating = request.POST.get("brating")
    rating.warehouse_owner_review = request.POST.get("review")
    rating.save()
    messages.success(request, f'Review submit successfully')
    return redirect('account:bookings')

@login_required
@email_verified_required
def download_invoice(request, id, mode):
    invoice = get_object_or_404(Invoice, id=id)

    if mode == 'view':
        return render(request, 'invoice_template.html', {'invoice': invoice})

    # elif mode == 'download':
    #     font_config = FontConfiguration()
    #     html_string = render_to_string('invoice_template.html', {'invoice': invoice})

    #     pdf_file = HTML(string=html_string).write_pdf(
    #         stylesheets=[os.path.join(settings.BASE_DIR, 'static/css/bootstrap.min.css'),os.path.join(settings.BASE_DIR, 'static/css/invoice.css') ], font_config=font_config)
    #     response = HttpResponse(pdf_file, content_type='application/pdf')
    #     response['Content-Disposition'] = f'attachment; filename=invoice_{id}.pdf'
    #     return response
    else:
        return HttpResponse(status=400)


@login_required
@email_verified_required
def account_request(request):
    if request.user.account_type == "BUSINESS":
        if AccountTypeChangeRequest.objects.filter(user=request.user).exists():
            return redirect('core:index2')
        company_name = request.POST.get("company_name")
        AccountTypeChangeRequest.objects.create(user=request.user,company_name=company_name)
        subject = 'Account Type Change Request'
        message = f'Your request for account type change to Warehouse Owner has been placed. We will send another mail about the confirmation. Thank you'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [request.user.email]
        try:
            e_message = EmailMessage(subject, message, from_email, recipient_list)
            e_message.content_subtype = 'html'
            e_message.send()
        except Exception as e:
            pass

        return redirect('core:index2')
    else:
        return redirect('core:index')
from django.db import models

from django.db.models import Q, Avg, Count

from account.models import WarehouseUser


class Equipment(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Security(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Storage_space_type(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Availability(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Accessibility(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Warehouse_type(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Storage_temperature(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Workforce(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Warehouse_Classification(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Services_Offered(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Order_taking_time(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Flexible_hours(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Insurance(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Warehouse(models.Model):
    owner = models.ForeignKey(WarehouseUser, on_delete=models.CASCADE, related_name="warehouse_owner")
    name = models.CharField(max_length=250)
    location = models.CharField(max_length=255)
    coordinates = models.CharField(max_length=250, blank=True)
    size = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    availability = models.ForeignKey(Availability, on_delete=models.CASCADE)
    accessibility = models.ForeignKey(Accessibility, on_delete=models.CASCADE)
    warehouse_type = models.ForeignKey(Warehouse_type, on_delete=models.CASCADE)
    storage_temperature = models.ForeignKey(Storage_temperature, on_delete=models.CASCADE)
    workforce = models.ForeignKey(Workforce, on_delete=models.CASCADE)
    warehouse_classification = models.ForeignKey(Warehouse_Classification, on_delete=models.CASCADE)
    storage_space_type = models.ManyToManyField(Storage_space_type, blank=True)
    equipment = models.ManyToManyField(Equipment, blank=True)
    security = models.ManyToManyField(Security, blank=True)
    services_offered = models.ManyToManyField(Services_Offered, blank=True)
    order_taking_time = models.ForeignKey(Order_taking_time, on_delete=models.CASCADE)
    flexibility_transport_appointments = models.CharField(max_length=50)
    flexible_hours = models.ForeignKey(Flexible_hours, on_delete=models.CASCADE)
    authorization_access_people_outside = models.CharField(max_length=50)
    Insurance = models.ForeignKey(Insurance, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

    def get_photo(self):
        return self.photos.all().first()

    def averageReview(self):
        reviews = Rating.objects.filter(booking__warehouse=self).aggregate(average=Avg('business_rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg

    def countReview(self):
        reviews = Rating.objects.filter(booking__warehouse=self).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count

    @property
    def booked(self):
        return self.booking_set.all()

    class Meta:
        ordering = ['-created_at']


class ThreadManager(models.Manager):
    def by_user(self, **kwargs):
        user = kwargs.get('user')
        lookup = Q(first_person=user) | Q(second_person=user)
        qs = self.get_queryset().filter(lookup).distinct()
        return qs


class Thread(models.Model):
    first_person = models.ForeignKey(WarehouseUser, on_delete=models.CASCADE, related_name="thread_first_person")
    second_person = models.ForeignKey(WarehouseUser, on_delete=models.CASCADE, related_name="thread_second_person")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ThreadManager()

    def __str__(self):
        return f"Thread of {self.first_person.username} and {self.second_person.username}"


class Message(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="message_thread")
    user = models.ForeignKey(WarehouseUser, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message of {self.thread} by {self.user.username}"


class WarehousePhoto(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to='warehouse_photos/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pk}"

    class Meta:
        ordering = ['-created_at']


class Start_Date(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Duration_Storage(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


Booking_status = (
    ("PENDING", "Pending"),
    ("APPROVED", "Approve"),
    ("DECLINE", "Decline")
)


class Booking(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    business = models.ForeignKey(WarehouseUser, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    area = models.PositiveIntegerField()
    start_date = models.ForeignKey(Start_Date, on_delete=models.CASCADE)
    Duration_Storage = models.ForeignKey(Duration_Storage, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Booking_status, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Book {self.area}m^2 area from {self.start_date} for {self.Duration_Storage.name}"

    def get_invoice(self):
        return Invoice.objects.get(booking=self)

    def is_owner_not_reviewed(self):
        try:
            Rating.objects.get(booking=self)
        except:
            return True
        if self.rating_booking.get().warehouse_owner_rating is None:
            return True
        else:
            return False

    class Meta:
        ordering = ['-created_at']


class Invoice(models.Model):
    user = models.ForeignKey(WarehouseUser, on_delete=models.CASCADE, null=True, blank=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="booking_invoice")
    price = models.DecimalField(max_digits=20, decimal_places=2)


class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    method = models.CharField(max_length=255)
    amount = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for {self.booking}'s Warehouse"

    class Meta:
        ordering = ['-created_at']


class Rating(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="rating_booking", null=True, blank=True)
    warehouse_owner_rating = models.FloatField(blank=True, null=True)
    warehouse_owner_review = models.TextField(blank=True, null=True)
    business_rating = models.FloatField(blank=True, null=True)
    business_review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ratings for {self.booking}"

    class Meta:
        ordering = ['-created_at']


class Contact(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    subject = models.CharField(max_length=100, null=True, blank=True)
    message = models.TextField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.name

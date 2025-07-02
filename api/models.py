from django.db import models
from django.utils.translation import gettext_lazy as _

class Table(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Table Name/Number"))
    capacity = models.IntegerField(verbose_name=_("Capacity"))
    location = models.CharField(max_length=100, blank=True, verbose_name=_("Location (e.g., Terrace, Indoors)"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    def __str__(self):
        return f"{self.name} ({self.capacity} seats)"

    class Meta:
        verbose_name = _("Table")
        verbose_name_plural = _("Tables")

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Category Name"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    order = models.IntegerField(default=0, help_text=_("Order of display for categories"), verbose_name=_("Display Order"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Menu Category")
        verbose_name_plural = _("Menu Categories")
        ordering = ['order', 'name']

class Dish(models.Model):
    name = models.CharField(max_length=200, verbose_name=_("Dish Name"))
    description = models.TextField(verbose_name=_("Description"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price"))
    image = models.ImageField(upload_to='dishes/', blank=True, null=True, verbose_name=_("Image"))
    category = models.ForeignKey(Category, related_name='dishes', on_delete=models.CASCADE, verbose_name=_("Category"))
    is_available = models.BooleanField(default=True, verbose_name=_("Is Available"))
    is_featured = models.BooleanField(default=False, help_text=_("Feature this dish on the homepage?"), verbose_name=_("Is Featured"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Dish")
        verbose_name_plural = _("Dishes")
        ordering = ['category', 'name']

class Event(models.Model):
    title = models.CharField(max_length=200, verbose_name=_("Event Title"))
    description = models.TextField(verbose_name=_("Description"))
    event_date = models.DateField(verbose_name=_("Event Date"))
    event_time = models.TimeField(verbose_name=_("Event Time"))
    image = models.ImageField(upload_to='events/', blank=True, null=True, verbose_name=_("Image"))
    capacity = models.IntegerField(blank=True, null=True, verbose_name=_("Capacity"))
    is_published = models.BooleanField(default=False, verbose_name=_("Is Published"))
    booking_required = models.BooleanField(default=False, verbose_name=_("Booking Required"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")
        ordering = ['-event_date', '-event_time']

class Reservation(models.Model):
    class ReservationStatus(models.TextChoices):
        PENDING = 'pending', _('Pending')
        CONFIRMED = 'confirmed', _('Confirmed')
        CANCELLED = 'cancelled', _('Cancelled')
        COMPLETED = 'completed', _('Completed')
        NO_SHOW = 'no-show', _('No-Show')

    customer_name = models.CharField(max_length=200, verbose_name=_("Customer Name"))
    customer_email = models.EmailField(verbose_name=_("Customer Email"))
    customer_phone = models.CharField(max_length=20, verbose_name=_("Customer Phone"))
    reservation_date = models.DateField(verbose_name=_("Reservation Date"))
    reservation_time = models.TimeField(verbose_name=_("Reservation Time"))
    number_of_guests = models.IntegerField(verbose_name=_("Number of Guests"))
    special_requests = models.TextField(blank=True, null=True, verbose_name=_("Special Requests"))
    status = models.CharField(
        max_length=10,
        choices=ReservationStatus.choices,
        default=ReservationStatus.PENDING,
        verbose_name=_("Status")
    )
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Assigned Table"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Reservation for {self.customer_name} on {self.reservation_date} at {self.reservation_time}"

    class Meta:
        verbose_name = _("Reservation")
        verbose_name_plural = _("Reservations")
        ordering = ['-reservation_date', '-reservation_time']

class ContactMessage(models.Model):
    name = models.CharField(max_length=200, verbose_name=_("Name"))
    email = models.EmailField(verbose_name=_("Email"))
    subject = models.CharField(max_length=200, verbose_name=_("Subject"))
    message = models.TextField(verbose_name=_("Message"))
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False, verbose_name=_("Mark as Read"))


    def __str__(self):
        return f"Message from {self.name} - {self.subject}"

    class Meta:
        verbose_name = _("Contact Message")
        verbose_name_plural = _("Contact Messages")
        ordering = ['-created_at']

# Make sure to add 'api' to INSTALLED_APPS in settings.py
# Also, Pillow will be needed for ImageField: pip install Pillow
# Then run:
# python manage.py makemigrations api
# python manage.py migrate

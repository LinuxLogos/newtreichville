from django.contrib import admin
from .models import Table, Category, Dish, Event, Reservation, ContactMessage

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'location', 'is_active')
    list_filter = ('is_active', 'location')
    search_fields = ('name', 'location')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'description')
    list_editable = ('order',)
    search_fields = ('name',)

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available', 'is_featured', 'updated_at')
    list_filter = ('category', 'is_available', 'is_featured')
    search_fields = ('name', 'description')
    list_editable = ('price', 'is_available', 'is_featured')
    autocomplete_fields = ['category'] # Assuming CategoryAdmin has search_fields defined

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'event_time', 'is_published', 'booking_required', 'capacity')
    list_filter = ('is_published', 'booking_required', 'event_date')
    search_fields = ('title', 'description')
    list_editable = ('is_published', 'booking_required')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'reservation_date', 'reservation_time', 'number_of_guests', 'status', 'table', 'updated_at')
    list_filter = ('status', 'reservation_date', 'table')
    search_fields = ('customer_name', 'customer_email', 'customer_phone')
    list_editable = ('status',)
    autocomplete_fields = ['table'] # Assuming TableAdmin has search_fields defined
    date_hierarchy = 'reservation_date'

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'name', 'email', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    list_editable = ('is_read',)
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')

    def has_add_permission(self, request):
        # Prevent adding contact messages from the admin
        return False

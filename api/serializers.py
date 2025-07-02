from rest_framework import serializers
from .models import Table, Category, Dish, Event, Reservation, ContactMessage

class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ['id', 'name', 'capacity', 'location', 'is_active']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'order']

class DishSerializer(serializers.ModelSerializer):
    # category = CategorySerializer(read_only=True) # Pour afficher les détails de la catégorie en lecture
    # category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True) # Pour l'écriture

    class Meta:
        model = Dish
        fields = ['id', 'name', 'description', 'price', 'image', 'category', 'is_available', 'is_featured', 'created_at', 'updated_at']
        # depth = 1 # Alternative simple pour afficher les détails des relations en lecture

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'event_date', 'event_time', 'image', 'capacity', 'is_published', 'booking_required', 'created_at', 'updated_at']

class ReservationSerializer(serializers.ModelSerializer):
    # table = TableSerializer(read_only=True)
    # table_id = serializers.PrimaryKeyRelatedField(queryset=Table.objects.all(), source='table', write_only=True, allow_null=True)

    class Meta:
        model = Reservation
        fields = [
            'id', 'customer_name', 'customer_email', 'customer_phone',
            'reservation_date', 'reservation_time', 'number_of_guests',
            'special_requests', 'status', 'table', 'created_at', 'updated_at'
        ]
        read_only_fields = ['status', 'created_at', 'updated_at'] # Status sera géré par la logique métier

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['id', 'name', 'email', 'subject', 'message', 'created_at']
        read_only_fields = ['created_at']

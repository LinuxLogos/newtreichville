from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TableViewSet,
    CategoryViewSet,
    DishViewSet,
    EventViewSet,
    ReservationViewSet,
    ContactMessageViewSet
)

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'tables', TableViewSet, basename='table')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'dishes', DishViewSet, basename='dish')
router.register(r'events', EventViewSet, basename='event')
router.register(r'reservations', ReservationViewSet, basename='reservation')
router.register(r'contact-messages', ContactMessageViewSet, basename='contactmessage')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]

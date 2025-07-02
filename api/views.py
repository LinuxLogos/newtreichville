from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser # AllowAny pour tests, à ajuster pour prod
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string # Pour des emails HTML plus tard
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Table, Category, Dish, Event, Reservation, ContactMessage
from .serializers import (
    TableSerializer, CategorySerializer, DishSerializer, EventSerializer,
    ReservationSerializer, ContactMessageSerializer
)

class TableViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows tables to be viewed or edited.
    """
    queryset = Table.objects.filter(is_active=True)
    serializer_class = TableSerializer
    permission_classes = [IsAdminUser] # Seuls les admins peuvent gérer les tables

    @action(detail=False, methods=['get'], url_path='availability', permission_classes=[AllowAny]) # Disponibilité est publique
    def availability(self, request):
        # Params attendus: date (YYYY-MM-DD), time (HH:MM), number_of_guests
        date_str = request.query_params.get('date')
        time_str = request.query_params.get('time')
        guests_str = request.query_params.get('guests')

        if not (date_str and time_str and guests_str):
            return Response(
                {"error": "Date, time, and number of guests are required parameters."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            reservation_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            reservation_time = datetime.strptime(time_str, "%H:%M").time()
            num_guests = int(guests_str)
        except ValueError as e:
            return Response(
                {"error": f"Invalid parameter format: {e}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Définir la durée d'une réservation (par exemple, 2 heures)
        reservation_duration = timedelta(hours=2)

        # Combiner date et heure pour obtenir un datetime object pour le début de la réservation souhaitée
        requested_datetime_start = timezone.make_aware(datetime.combine(reservation_date, reservation_time))
        requested_datetime_end = requested_datetime_start + reservation_duration

        # 1. Trouver les tables qui ont la capacité requise et sont actives
        potential_tables = Table.objects.filter(is_active=True, capacity__gte=num_guests)

        # 2. Exclure les tables qui ont des réservations confirmées qui chevauchent le créneau demandé
        # Une réservation chevauche si :
        # (res_start < req_end) ET (res_end > req_start)
        # Nous ne considérons que les réservations 'confirmed' ou 'pending' comme bloquantes
        # (on pourrait être plus strict et ne prendre que 'confirmed')
        conflicting_statuses = [Reservation.ReservationStatus.CONFIRMED, Reservation.ReservationStatus.PENDING]

        unavailable_table_ids = set()
        for table in potential_tables:
            # Récupérer les réservations pour cette table à cette date
            reservations_for_table_on_date = Reservation.objects.filter(
                table=table,
                reservation_date=reservation_date,
                status__in=conflicting_statuses
            )

            for res in reservations_for_table_on_date:
                existing_res_start = timezone.make_aware(datetime.combine(res.reservation_date, res.reservation_time))
                existing_res_end = existing_res_start + reservation_duration # Supposons la même durée pour toutes

                # Vérifier le chevauchement
                if (existing_res_start < requested_datetime_end and
                    existing_res_end > requested_datetime_start):
                    unavailable_table_ids.add(table.id)
                    break # Cette table n'est pas dispo, passer à la suivante

        available_tables = potential_tables.exclude(id__in=unavailable_table_ids)

        serializer = self.get_serializer(available_tables, many=True)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet): # ReadOnly car géré par admin principalement
    """
    API endpoint that allows menu categories to be viewed.
    """
    queryset = Category.objects.all().order_by('order')
    serializer_class = CategorySerializer
    permission_classes = [AllowAny] # Publicly readable

class DishViewSet(viewsets.ReadOnlyModelViewSet): # ReadOnly pour les clients, écriture via admin
    """
    API endpoint that allows dishes to be viewed.
    """
    queryset = Dish.objects.filter(is_available=True)
    serializer_class = DishSerializer
    permission_classes = [AllowAny] # Publicly readable

    def get_queryset(self):
        queryset = Dish.objects.filter(is_available=True)
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset

    @action(detail=False, methods=['get'], url_path='featured')
    def featured(self, request):
        """
        Returns a list of featured dishes.
        """
        featured_dishes = Dish.objects.filter(is_available=True, is_featured=True)
        serializer = self.get_serializer(featured_dishes, many=True)
        return Response(serializer.data)

class EventViewSet(viewsets.ReadOnlyModelViewSet): # ReadOnly pour les clients
    """
    API endpoint that allows events to be viewed.
    """
    queryset = Event.objects.filter(is_published=True).order_by('event_date', 'event_time')
    serializer_class = EventSerializer
    permission_classes = [AllowAny] # Publicly readable

class ReservationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for creating and managing reservations.
    Clients can create (POST). Admins can manage.
    """
    queryset = Reservation.objects.all().order_by('-reservation_date', '-reservation_time')
    serializer_class = ReservationSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            self.permission_classes = [AllowAny] # Ou IsAuthenticated pour utilisateurs loggés
        else:
            # Pour list, retrieve, update, delete : admin seulement
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def perform_create(self, serializer):
        # Logique supplémentaire lors de la création d'une réservation
        # Par exemple, vérifier la disponibilité, assigner une table, envoyer email de confirmation
        # Pour l'instant, on sauve juste la réservation.
        # Le statut par défaut est 'pending'
        reservation = serializer.save() # Sauvegarder d'abord pour avoir l'objet reservation

        # Envoyer un email de confirmation au client
        subject_customer = f"Confirmation de votre réservation chez New Treichville (ID: {reservation.id})"
        message_customer = (
            f"Bonjour {reservation.customer_name},\n\n"
            f"Votre demande de réservation pour le {reservation.reservation_date.strftime('%d/%m/%Y')} "
            f"à {reservation.reservation_time.strftime('%H:%M')} pour {reservation.number_of_guests} personne(s) "
            f"a bien été reçue et est en attente de confirmation.\n\n"
            f"Détails de la demande :\n"
            f"Nom: {reservation.customer_name}\n"
            f"Email: {reservation.customer_email}\n"
            f"Téléphone: {reservation.customer_phone}\n"
            f"Demandes spéciales: {reservation.special_requests or 'Aucune'}\n\n"
            f"Nous vous contacterons bientôt pour confirmer définitivement votre table.\n\n"
            f"Cordialement,\nL'équipe New Treichville"
        )
        try:
            send_mail(
                subject_customer,
                message_customer,
                settings.DEFAULT_FROM_EMAIL,
                [reservation.customer_email],
                fail_silently=False,
            )
        except Exception as e:
            # Log l'erreur, mais ne pas bloquer la réponse à l'utilisateur pour ça
            print(f"Erreur lors de l'envoi de l'email de confirmation client: {e}")

        # Envoyer une notification à l'administrateur (optionnel, mais utile)
        subject_admin = f"Nouvelle demande de réservation (ID: {reservation.id})"
        message_admin = (
            f"Une nouvelle demande de réservation a été effectuée :\n\n"
            f"Client: {reservation.customer_name} ({reservation.customer_email}, {reservation.customer_phone})\n"
            f"Date: {reservation.reservation_date.strftime('%d/%m/%Y')} à {reservation.reservation_time.strftime('%H:%M')}\n"
            f"Nombre de convives: {reservation.number_of_guests}\n"
            f"Table demandée/assignée: {reservation.table or 'Non assignée'}\n"
            f"Demandes spéciales: {reservation.special_requests or 'Aucune'}\n\n"
            f"Statut actuel: {reservation.get_status_display()}\n\n"
            f"Veuillez la vérifier dans l'interface d'administration."
        )
        try:
            send_mail(
                subject_admin,
                message_admin,
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL], # Assurez-vous que ADMIN_EMAIL est défini dans settings.py
                fail_silently=False,
            )
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email de notification admin: {e}")

        # TODO: Ajouter la logique d'assignation de table si applicable


class ContactMessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint for submitting contact messages.
    Clients can create (POST). Admins can view.
    """
    queryset = ContactMessage.objects.all().order_by('-created_at')
    serializer_class = ContactMessageSerializer

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [AllowAny]
        else:
            # list, retrieve, update, delete : admin seulement
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def perform_create(self, serializer):
        contact_message = serializer.save()

        # Envoyer une notification email à l'admin
        subject_admin = f"Nouveau message de contact de {contact_message.name} (Sujet: {contact_message.subject})"
        message_admin = (
            f"Un nouveau message de contact a été reçu :\n\n"
            f"De: {contact_message.name} ({contact_message.email})\n"
            f"Sujet: {contact_message.subject}\n"
            f"Message:\n{contact_message.message}\n\n"
            f"Veuillez le vérifier dans l'interface d'administration ou répondre directement."
        )
        try:
            send_mail(
                subject_admin,
                message_admin,
                settings.DEFAULT_FROM_EMAIL, # Ou contact_message.email si vous voulez pouvoir répondre directement
                [settings.ADMIN_EMAIL],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email de notification de contact: {e}")

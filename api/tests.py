from django.test import TestCase
from django.utils import timezone
from .models import Table, Category, Dish, Event, Reservation, ContactMessage

class ModelCreationTests(TestCase):

    def test_create_table(self):
        table = Table.objects.create(name="Table 1", capacity=4, location="Terrasse")
        self.assertEqual(table.name, "Table 1")
        self.assertEqual(table.capacity, 4)
        self.assertTrue(table.is_active)
        self.assertEqual(str(table), "Table 1 (4 seats)")

    def test_create_category(self):
        category = Category.objects.create(name="Entrées", order=1)
        self.assertEqual(category.name, "Entrées")
        self.assertEqual(str(category), "Entrées")

    def test_create_dish(self):
        category = Category.objects.create(name="Plats Principaux", order=2)
        dish = Dish.objects.create(
            name="Poulet Yassa",
            description="Délicieux poulet mariné au citron et aux oignons.",
            price="15.00",
            category=category,
            is_featured=True
        )
        self.assertEqual(dish.name, "Poulet Yassa")
        self.assertEqual(dish.category.name, "Plats Principaux")
        self.assertTrue(dish.is_available)
        self.assertTrue(dish.is_featured)
        self.assertEqual(str(dish), "Poulet Yassa")

    def test_create_event(self):
        event = Event.objects.create(
            title="Soirée Jazz",
            description="Concert de jazz live.",
            event_date=timezone.now().date(),
            event_time=timezone.now().time(),
            is_published=True
        )
        self.assertEqual(event.title, "Soirée Jazz")
        self.assertTrue(event.is_published)
        self.assertEqual(str(event), "Soirée Jazz")

    def test_create_reservation(self):
        table = Table.objects.create(name="Table VIP", capacity=2)
        reservation = Reservation.objects.create(
            customer_name="John Doe",
            customer_email="john.doe@example.com",
            customer_phone="1234567890",
            reservation_date=timezone.now().date(),
            reservation_time=timezone.now().time(),
            number_of_guests=2,
            table=table,
            status=Reservation.ReservationStatus.CONFIRMED
        )
        self.assertEqual(reservation.customer_name, "John Doe")
        self.assertEqual(reservation.status, Reservation.ReservationStatus.CONFIRMED)
        self.assertEqual(str(reservation), f"Reservation for John Doe on {reservation.reservation_date} at {reservation.reservation_time}")

    def test_create_contact_message(self):
        message = ContactMessage.objects.create(
            name="Jane Doe",
            email="jane.doe@example.com",
            subject="Question",
            message="Bonjour, j'ai une question."
        )
        self.assertEqual(message.name, "Jane Doe")
        self.assertEqual(message.subject, "Question")
        self.assertFalse(message.is_read)
        self.assertEqual(str(message), "Message from Jane Doe - Question")

class BasicAppSetupTests(TestCase):
    def test_api_app_is_installed(self):
        """Test if the 'api' app is in INSTALLED_APPS."""
        from django.conf import settings
        self.assertIn('api', settings.INSTALLED_APPS)

    def test_admin_interface_loads(self):
        """Test if the admin interface loads (requires a superuser and login, or specific admin client)."""
        # This is a more complex test, for now, we'll just check if admin is in INSTALLED_APPS
        from django.conf import settings
        self.assertIn('django.contrib.admin', settings.INSTALLED_APPS)


from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail # Import mail
from django.conf import settings # Import settings

User = get_user_model()

class BasicAPITests(APITestCase):
    def setUp(self):
        # Create a non-admin user
        self.user = User.objects.create_user(username='testuser', password='password123')

        # Create an admin user
        self.admin_user = User.objects.create_superuser(username='testadmin', email='admin@example.com', password='password123')

        # Pre-populate data for GET requests
        self.category = Category.objects.create(name="Boissons", order=3)
        self.dish = Dish.objects.create(
            name="Jus de Bissap",
            description="Jus d'hibiscus rafraîchissant.",
            price="3.00",
            category=self.category
        )
        self.table = Table.objects.create(name="Table Jardin 1", capacity=4, location="Jardin")

    def test_list_categories(self):
        """Ensure we can list categories."""
        url = reverse('category-list') # 'category-list' is DRF default name
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0) # We created one category in setUp

    def test_list_dishes(self):
        """Ensure we can list dishes."""
        url = reverse('dish-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_list_tables(self):
        """Ensure only admin can list tables."""
        url = reverse('table-list')

        # Try as anonymous user
        response_anon = self.client.get(url, format='json')
        self.assertEqual(response_anon.status_code, status.HTTP_403_FORBIDDEN) # IsAdminUser permission check runs

        # Try as non-admin authenticated user
        self.client.force_authenticate(user=self.user)
        response_user = self.client.get(url, format='json')
        self.assertEqual(response_user.status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=None) # Unauthenticate

        # Try as admin user
        self.client.force_authenticate(user=self.admin_user)
        response_admin = self.client.get(url, format='json')
        self.assertEqual(response_admin.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response_admin.data), 0)
        self.client.force_authenticate(user=None) # Unauthenticate

    def test_create_contact_message_api(self):
        """Ensure we can create a new contact message via API."""
        url = reverse('contactmessage-list')
        data = {
            'name': 'Test API User',
            'email': 'testapi@example.com',
            'subject': 'API Test Subject',
            'message': 'This is a test message from the API.'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ContactMessage.objects.count(), 1) # Should be 1 as test classes have separate DB transactions
        self.assertEqual(ContactMessage.objects.latest('created_at').name, 'Test API User')

        # Test that one email was sent (to admin)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, f"Nouveau message de contact de {data['name']} (Sujet: {data['subject']})")
        self.assertIn(settings.ADMIN_EMAIL, mail.outbox[0].to)

    def test_create_reservation_api(self):
        """Ensure we can create a new reservation via API."""
        url = reverse('reservation-list')
        # Ensure a table exists or create one for the reservation
        if not Table.objects.exists():
            Table.objects.create(name="Default Table", capacity=2)

        a_table = Table.objects.first()

        data = {
            'customer_name': 'API Booker',
            'customer_email': 'apibooker@example.com',
            'customer_phone': '0987654321',
            'reservation_date': timezone.now().date().isoformat(),
            'reservation_time': timezone.now().time().strftime('%H:%M:%S'),
            'number_of_guests': 2,
            'table': a_table.id, # Send table ID
            'special_requests': 'Test reservation via API'
        }
        response = self.client.post(url, data, format='json')
        # print(response.data) # For debugging if it fails
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reservation.objects.count(), 1) # Should be 1 as test classes have separate DB transactions
        self.assertEqual(Reservation.objects.latest('created_at').customer_name, 'API Booker')

        # Test that two emails were sent (customer + admin)
        self.assertEqual(len(mail.outbox), 2)
        # Check customer email
        customer_email_sent = any(data['customer_email'] in email.to for email in mail.outbox)
        self.assertTrue(customer_email_sent)
        # Check admin email
        admin_email_sent = any(settings.ADMIN_EMAIL in email.to for email in mail.outbox)
        self.assertTrue(admin_email_sent)


    def test_featured_dishes_api(self):
        """Ensure the featured dishes endpoint works."""
        # Make one dish featured
        self.dish.is_featured = True
        self.dish.save()

        Dish.objects.create(
            name="Thieboudienne",
            description="Riz au poisson sénégalais.",
            price="20.00",
            category=self.category,
            is_featured=True
        )
        Dish.objects.create(
            name="Eau Minérale",
            description="Bouteille d'eau.",
            price="1.00",
            category=self.category,
            is_featured=False # Not featured
        )

        url = reverse('dish-featured') # Uses the custom action name
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2) # Two dishes are featured
        for dish_data in response.data:
            self.assertTrue(dish_data['is_featured'])

    def test_table_availability_api(self):
        """Test the table availability endpoint."""
        url = reverse('table-availability') # Custom action
        # Create some tables with different capacities
        Table.objects.create(name="Table Small", capacity=2, is_active=True)
        Table.objects.create(name="Table Medium", capacity=4, is_active=True)
        Table.objects.create(name="Table Large", capacity=8, is_active=True)
        Table.objects.create(name="Table Inactive", capacity=4, is_active=False)


        # Test for 3 guests
        response = self.client.get(f"{url}?date=2024-01-01&time=19:00&guests=3", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return 'Table Medium', 'Table Large', and self.table (Jardin 1, capacity 4)
        # (Total of 3 tables if self.table was created with capacity >=3)
        # self.table was created with capacity 4. So 3 tables.
        self.assertEqual(len(response.data), 3)
        for table_data in response.data:
            self.assertGreaterEqual(table_data['capacity'], 3)
            self.assertTrue(table_data['is_active'])

        # Test for 5 guests
        response = self.client.get(f"{url}?date=2024-01-01&time=19:00&guests=5", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return 'Table Large' (capacity 8)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Table Large')

        # Test with missing params
        response = self.client.get(f"{url}?date=2024-01-01&time=19:00", format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_table_availability_with_existing_reservations(self):
        """Test availability when tables are partially booked."""
        url = reverse('table-availability')

        table_A = Table.objects.create(name="Table A", capacity=2, is_active=True)
        table_B = Table.objects.create(name="Table B", capacity=4, is_active=True)
        table_C = Table.objects.create(name="Table C", capacity=4, is_active=True) # This one will remain available

        # Date and time for testing
        test_date_str = "2024-07-15"
        test_time_str = "19:00" # 7 PM
        test_datetime = timezone.datetime.strptime(f"{test_date_str}T{test_time_str}", "%Y-%m-%dT%H:%M")

        # Reservation for Table A at 19:00 on test_date_str
        Reservation.objects.create(
            table=table_A, customer_name="Res A", customer_email="a@example.com", customer_phone="1",
            reservation_date=test_datetime.date(), reservation_time=test_datetime.time(),
            number_of_guests=2, status=Reservation.ReservationStatus.CONFIRMED
        )
        # Reservation for Table B at 20:00 on test_date_str (overlaps with a 19:00 request due to 2h duration)
        # 20:00 to 22:00. A request for 19:00 (until 21:00) will overlap.
        Reservation.objects.create(
            table=table_B, customer_name="Res B", customer_email="b@example.com", customer_phone="2",
            reservation_date=test_datetime.date(), reservation_time=(test_datetime + timezone.timedelta(hours=1)).time(),
            number_of_guests=4, status=Reservation.ReservationStatus.PENDING
        )

        # Request for 2 guests at 19:00 on test_date_str
        # Expected: Table C (capacity 4), self.table (Jardin 1, capacity 4)
        # Table A is booked at 19:00. Table B is booked at 20:00, which overlaps.
        response = self.client.get(f"{url}?date={test_date_str}&time={test_time_str}&guests=2", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        available_table_names = sorted([t['name'] for t in response.data])
        expected_tables = sorted([table_C.name, self.table.name]) # self.table was created in setUp

        self.assertEqual(len(response.data), 2, f"Expected 2 tables, got {len(response.data)}: {response.data}")
        self.assertEqual(available_table_names, expected_tables)

        # Request for 2 guests at 21:00 on test_date_str
        # Expected: Table A (booked 19-21), Table B (booked 20-22), Table C, self.table
        # Request for 21:00 (until 23:00).
        # Table A (19-21) is free. Table B (20-22) is NOT free.
        response = self.client.get(f"{url}?date={test_date_str}&time=21:00&guests=2", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        available_table_names = sorted([t['name'] for t in response.data])
        # Table A is free from 21:00. Table B is booked until 22:00.
        # Table C is free. self.table is free.
        expected_tables_21_00 = sorted([table_A.name, table_C.name, self.table.name])
        self.assertEqual(len(response.data), 3, f"Expected 3 tables, got {len(response.data)}: {response.data}")
        self.assertEqual(available_table_names, expected_tables_21_00)

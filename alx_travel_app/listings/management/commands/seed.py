import random
import uuid
from django.core.management.base import BaseCommand
from faker import Faker
from listings.models import User, Property, Booking, Payment, Review, Message
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP


fake = Faker()

class Command(BaseCommand):
    help = "Seed the database with fake data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding database...")

        # Clear existing data
        Message.objects.all().delete()
        Review.objects.all().delete()
        Payment.objects.all().delete()
        Booking.objects.all().delete()
        Property.objects.all().delete()
        User.objects.all().delete()

        # Create users
        users = []
        for _ in range(10):
            user = User.objects.create_user(
                user_id=uuid.uuid4(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.unique.email(),
                password="password123",  # default password
                phone_number=fake.msisdn()[:10],
                role=random.choice(["guest", "host", "admin"]),
            )
            users.append(user)

        # Create properties (assign to hosts only)
        properties = []
        hosts = [u for u in users if u.role == "host"]
        for _ in range(15):
            prop = Property.objects.create(
                property_id=uuid.uuid4(),
                host=random.choice(hosts),
                name=fake.company(),
                description=fake.text(),
                location=fake.city(),
                pricepernight=round(random.uniform(50, 500), 2),
            )
            properties.append(prop)

        # Create bookings
        bookings = []
        for _ in range(20):
            user = random.choice(users)
            prop = random.choice(properties)
            start_date = fake.date_time_between(start_date="-30d", end_date="+30d")
            end_date = start_date + timezone.timedelta(days=random.randint(1, 7))
            total_price = float(prop.pricepernight) * (end_date - start_date).days
            if total_price > Decimal("999.99"):
                total_price = Decimal("999.99")
            booking = Booking.objects.create(
                booking_id=uuid.uuid4(),
                property=prop,
                user=user,
                start_date=start_date,
                end_date=end_date,
                total_price=total_price,
                status=random.choice(["pending", "confirmed", "cancelled"]),
            )
            bookings.append(booking)

        # Create payments
        for booking in bookings:
            Payment.objects.create(
                payment_id=uuid.uuid4(),
                booking=booking,
                amount=Decimal(str(booking.total_price)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                payment_date=fake.date_time_between(start_date=booking.start_date, end_date="now"),
                transaction_id=str(uuid.uuid4()),
                status=random.choice(["pending", "completed", "failed"]),
                payment_method=random.choice(["card", "paypal", "bank"]),
            )

        # Create reviews
        for _ in range(30):
            Review.objects.create(
                review_id=uuid.uuid4(),
                property=random.choice(properties),
                user=random.choice(users),
                rating=random.randint(1, 5),
                comment=fake.text(),
            )

        # Create messages
        for _ in range(30):
            sender, receiver = random.sample(users, 2)
            Message.objects.create(
                message_id=uuid.uuid4(),
                sender=sender,
                receiver=receiver,
                content=fake.text(),
            )

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))

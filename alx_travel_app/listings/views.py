from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import User, Property, Booking, Payment, Review, Message
from .serializers import UserSerializer, PropertySerializer, BookingSerializer, PaymentSerializer, ReviewSerializer, MessageSerializer
from .permissions import IsHostOrAdmin, IsGuestOrAdmin, IsOwnerOrAdmin, IsAdminOrReadOnly
import requests, uuid, os
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .tasks import send_booking_confirmation_email

CHAPA_URL = f"{settings.CHAPA_BASE_URL}/transaction"
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrReadOnly]


class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated, IsHostOrAdmin]

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsGuestOrAdmin]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def perform_create(self, serializer):
        booking = serializer.save()
        # Trigger async task
        send_booking_confirmation_email.delay(
            booking.user.email,
            booking.property.name,
            booking.start_date.strftime("%Y-%m-%d"),
            booking.end_date.strftime("%Y-%m-%d"),
            str(booking.total_price),
        )

@api_view(["POST"])
def initiate_payment(request, booking_id):
    try:
        booking = Booking.objects.get(pk=booking_id)
        tx_ref = str(uuid.uuid4())

        payload = {
            "amount": str(booking.total_price),
            "currency": "ETB",
            "email": booking.user.email,
            "first_name": booking.user.first_name,
            "last_name": booking.user.last_name,
            "tx_ref": tx_ref,
            "callback_url": "http://localhost:8000/api/payments/verify/",
        }

        headers = {"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"}
        response = requests.post(f"{CHAPA_URL}/initialize", json=payload, headers=headers)
        data = response.json()

        if data.get("status") == "success":
            Payment.objects.create(
                booking=booking,
                amount=booking.total_price,
                transaction_id=tx_ref,
                status="pending"
            )
            return Response({"checkout_url": data["data"]["checkout_url"]})

        return Response({"error": data}, status=400)

    except Booking.DoesNotExist:
        return Response({"error": "Booking not found"}, status=404)


@api_view(["GET"])
def verify_payment(request, tx_ref):
    headers = {"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"}
    response = requests.get(f"{CHAPA_URL}/verify/{tx_ref}", headers=headers)
    data = response.json()

    try:
        payment = Payment.objects.get(transaction_id=tx_ref)
        if data.get("status") == "success" and data["data"]["status"] == "success":
            payment.status = "completed"
        else:
            payment.status = "failed"
        payment.save()
    except Payment.DoesNotExist:
        return Response({"error": "Payment not found"}, status=404)

    return Response({"payment_status": payment.status})


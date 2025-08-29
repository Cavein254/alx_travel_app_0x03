from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, PropertyViewSet, BookingViewSet, PaymentViewSet, ReviewViewSet, MessageViewSet, initiate_payment, verify_payment

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('properties', PropertyViewSet)
router.register('bookings', BookingViewSet)
router.register('payments', PaymentViewSet)
router.register('reviews', ReviewViewSet)
router.register('messages', MessageViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path("payments/initiate/<uuid:booking_id>/", initiate_payment, name="initiate_payment"),
    path("payments/verify/<str:tx_ref>/", verify_payment, name="verify_payment"),
]

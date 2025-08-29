from django.contrib import admin
from .models import User, Property, Booking, Payment, Review, Message

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'first_name', 'last_name', 'email', 'role', 'created_at')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('role', 'created_at')
    ordering = ('-created_at',)


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('property_id', 'name', 'host', 'location', 'pricepernight', 'created_at')
    search_fields = ('name', 'location', 'host__first_name', 'host__last_name')
    list_filter = ('location', 'created_at')
    ordering = ('-created_at',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'property', 'user', 'start_date', 'end_date', 'status', 'total_price')
    search_fields = ('property__name', 'user__first_name', 'user__last_name')
    list_filter = ('status', 'start_date', 'end_date')
    ordering = ('-start_date',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'booking', 'amount', 'payment_date', 'payment_method')
    search_fields = ('booking__user__first_name', 'booking__user__last_name')
    list_filter = ('payment_method', 'payment_date')
    ordering = ('-payment_date',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('review_id', 'property', 'user', 'rating', 'created_at')
    search_fields = ('property__name', 'user__first_name', 'user__last_name')
    list_filter = ('rating', 'created_at')
    ordering = ('-created_at',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('message_id', 'sender', 'receiver', 'timestamp')
    search_fields = ('sender__first_name', 'sender__last_name', 'receiver__first_name', 'receiver__last_name')
    list_filter = ('timestamp',)
    ordering = ('-timestamp',)

from django.contrib import admin
from .models import Customer, Order, Ticket

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    search_fields = ('name', 'email')
    ordering = ('-created_at',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__name', 'id')
    ordering = ('-created_at',)

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'customer', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('subject', 'customer__name')
    ordering = ('-created_at',)

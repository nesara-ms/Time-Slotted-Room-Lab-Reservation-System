from django.contrib import admin

# Register your models here.

from django.contrib import admin

from .models import Booking, Profile, Resource


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'department')
    list_filter = ('role',)
    search_fields = ('user__username', 'department')


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'resource_type', 'location', 'capacity', 'manager', 'is_active')
    list_filter = ('resource_type', 'is_active')
    search_fields = ('name', 'location')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('resource', 'user', 'date', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'resource__resource_type', 'date')
    search_fields = ('purpose', 'user__username', 'resource__name')
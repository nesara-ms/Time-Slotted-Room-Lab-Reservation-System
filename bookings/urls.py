from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),

    path('resources/', views.resource_list, name='resource_list'),
    path('resources/add/', views.resource_create, name='resource_create'),
    path('resources/<int:pk>/edit/', views.resource_update, name='resource_update'),
    path('resources/<int:pk>/delete/', views.resource_delete, name='resource_delete'),

    path('calendar/', views.calendar_view, name='calendar'),
    path('api/availability/', views.availability_api, name='availability_api'),

    path('book/', views.booking_create, name='booking_create'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('my-bookings/<int:pk>/cancel/', views.booking_cancel, name='booking_cancel'),

    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('manager/review/<int:pk>/', views.review_booking, name='review_booking'),
]
from django.db import models

# Create your models here.

from datetime import time

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Profile(models.Model):
    ROLE_CHOICES = [
        ('user', 'Regular User'),
        ('manager', 'Room Manager'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    department = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f'{self.user.username} ({self.get_role_display()})'


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)


def is_manager(user):
    """Superusers and users with the 'manager' role can moderate bookings."""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile.role == 'manager'


class Resource(models.Model):
    ROOM = 'ROOM'
    LAB = 'LAB'
    EQUIPMENT = 'EQUIPMENT'
    TYPE_CHOICES = [
        (ROOM, 'Meeting Room'),
        (LAB, 'Laboratory'),
        (EQUIPMENT, 'Equipment'),
    ]
    ICONS = {ROOM: '🏢', LAB: '🔬', EQUIPMENT: '🛠️'}

    name = models.CharField(max_length=100, unique=True)
    resource_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=ROOM)
    location = models.CharField(max_length=150, blank=True)
    capacity = models.PositiveIntegerField(default=1, help_text='Number of people / units')
    description = models.TextField(blank=True)
    manager = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='managed_resources',
        limit_choices_to=Q(profile__role='manager') | Q(is_superuser=True),
        help_text='Leave empty to let any manager approve requests.',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['resource_type', 'name']

    def __str__(self):
        return self.name

    @property
    def icon(self):
        return self.ICONS.get(self.resource_type, '📦')


class Booking(models.Model):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
        (CANCELLED, 'Cancelled'),
    ]

    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    purpose = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    manager_note = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_bookings'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-start_time']

    def __str__(self):
        return f'{self.resource} | {self.date} {self.start_time:%H:%M}-{self.end_time:%H:%M}'

    def overlapping(self, statuses=None):
        """Bookings for the same resource/date whose time range overlaps this one."""
        statuses = statuses or [self.PENDING, self.APPROVED]
        return Booking.objects.filter(
            resource_id=self.resource_id,
            date=self.date,
            status__in=statuses,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        ).exclude(pk=self.pk)

    def clean(self):
        super().clean()
        if not (self.resource_id and self.date and self.start_time and self.end_time):
            return  # field-level errors already reported

        if self.end_time <= self.start_time:
            raise ValidationError({'end_time': 'End time must be later than the start time.'})

        open_t = time(settings.OPEN_HOUR, 0)
        close_t = time(settings.CLOSE_HOUR, 0)
        if self.start_time < open_t or self.end_time > close_t:
            raise ValidationError(
                f'Bookings are only allowed between {open_t:%H:%M} and {close_t:%H:%M}.'
            )

        if self._state.adding:
            now = timezone.localtime()
            if self.date < now.date():
                raise ValidationError({'date': 'You cannot book a date in the past.'})
            if self.date == now.date() and self.start_time < now.time().replace(second=0, microsecond=0):
                raise ValidationError({'start_time': 'This start time has already passed today.'})

        if not self.resource.is_active:
            raise ValidationError('This resource is currently not available for booking.')

        conflict = self.overlapping().first()
        if conflict:
            raise ValidationError(
                f'Conflict: {self.resource.name} is already booked from '
                f'{conflict.start_time:%H:%M} to {conflict.end_time:%H:%M} on '
                f'{self.date:%d %b %Y} ({conflict.get_status_display().lower()}). '
                f'Please choose a different time.'
            )

    @property
    def can_cancel(self):
        return self.status in (self.PENDING, self.APPROVED) and self.date >= timezone.localdate()
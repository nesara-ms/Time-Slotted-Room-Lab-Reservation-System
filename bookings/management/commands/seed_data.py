from datetime import time, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from bookings.models import Booking, Resource


class Command(BaseCommand):
    help = 'Load sample resources, users and bookings'

    def handle(self, *args, **options):
        manager, created = User.objects.get_or_create(username='manager', defaults={'email': 'manager@example.com'})
        if created:
            manager.set_password('manager123')
            manager.save()
        manager.profile.role = 'manager'
        manager.profile.department = 'Facilities'
        manager.profile.save()

        student, created = User.objects.get_or_create(username='student', defaults={'email': 'student@example.com'})
        if created:
            student.set_password('student123')
            student.save()
        student.profile.department = 'Computer Science'
        student.profile.save()

        sample = [
            ('Meeting Room A', Resource.ROOM, 'Block A, Floor 1', 10, 'Projector and whiteboard.'),
            ('Meeting Room B', Resource.ROOM, 'Block A, Floor 2', 6, 'Small discussion room.'),
            ('Conference Hall', Resource.ROOM, 'Main Building', 40, 'Large hall with AV system.'),
            ('Chemistry Lab 1', Resource.LAB, 'Science Block', 20, 'Fume hoods and safety equipment.'),
            ('Computer Lab', Resource.LAB, 'Block C', 30, '30 workstations.'),
            ('3D Printer', Resource.EQUIPMENT, 'Maker Space', 1, 'FDM printer, PLA/ABS.'),
            ('Oscilloscope', Resource.EQUIPMENT, 'Electronics Lab', 1, '4-channel digital oscilloscope.'),
            ('Projector Kit', Resource.EQUIPMENT, 'Store Room', 1, 'Portable projector with screen.'),
        ]
        objs = {}
        for name, rtype, loc, cap, desc in sample:
            obj, _ = Resource.objects.get_or_create(
                name=name,
                defaults={'resource_type': rtype, 'location': loc, 'capacity': cap,
                          'description': desc, 'manager': manager},
            )
            objs[name] = obj

        today = timezone.localdate()
        tomorrow = today + timedelta(days=1)
        demo = [
            ('Meeting Room A', today, time(10, 0), time(12, 0), 'Thesis review meeting', Booking.APPROVED),
            ('Meeting Room A', today, time(14, 0), time(15, 0), 'Group stand-up', Booking.PENDING),
            ('Chemistry Lab 1', tomorrow, time(9, 0), time(12, 0), 'Titration experiment', Booking.PENDING),
            ('3D Printer', tomorrow, time(13, 0), time(17, 0), 'Prototype printing', Booking.APPROVED),
            ('Computer Lab', today, time(11, 0), time(13, 0), 'Programming workshop', Booking.APPROVED),
        ]
        for name, day, start, end, purpose, status in demo:
            Booking.objects.get_or_create(
                resource=objs[name], date=day, start_time=start, end_time=end,
                defaults={'user': student, 'purpose': purpose, 'status': status,
                          'reviewed_by': manager if status != Booking.PENDING else None},
            )

        self.stdout.write(self.style.SUCCESS(
            'Sample data loaded. Logins: manager/manager123 and student/student123'))
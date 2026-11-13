from .models import Booking, is_manager


def roles(request):
    manager = is_manager(request.user)
    pending = 0
    if manager:
        qs = Booking.objects.filter(status=Booking.PENDING)
        if not request.user.is_superuser:
            qs = qs.filter(resource__manager__in=[request.user, None]) | qs.filter(resource__manager__isnull=True)
        pending = qs.distinct().count()
    return {'is_manager': manager, 'nav_pending_count': pending}
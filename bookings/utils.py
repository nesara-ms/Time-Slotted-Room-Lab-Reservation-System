from collections import defaultdict
from datetime import time

from django.conf import settings
from django.utils import timezone

from .models import Booking


def build_day_grid(resources, day):
    """
    Build hourly availability for each resource on a given date.
    Cell status: free | pending | approved | past
    """
    now = timezone.localtime()
    resources = list(resources)
    hours = range(settings.OPEN_HOUR, settings.CLOSE_HOUR)

    bookings = Booking.objects.filter(
        resource__in=resources, date=day,
        status__in=[Booking.PENDING, Booking.APPROVED],
    ).select_related('user')

    by_resource = defaultdict(list)
    for b in bookings:
        by_resource[b.resource_id].append(b)

    rows = []
    for resource in resources:
        cells, free, next_free = [], 0, None
        for h in hours:
            slot_start = time(h, 0)
            slot_end = time(h + 1, 0) if h + 1 < 24 else time.max

            match = None
            for b in by_resource[resource.id]:
                if b.start_time < slot_end and b.end_time > slot_start:
                    if match is None or b.status == Booking.APPROVED:
                        match = b

            is_past = day < now.date() or (day == now.date() and h < now.hour)
            info = ''
            if match:
                status = match.status
                who = match.user.get_full_name() or match.user.username
                info = (f'{match.start_time:%H:%M}-{match.end_time:%H:%M} | {who} | '
                        f'{match.purpose} ({match.get_status_display()})')
            elif is_past:
                status = 'past'
            else:
                status = 'free'
                free += 1
                if next_free is None:
                    next_free = f'{h:02d}:00'

            cells.append({
                'hour': h,
                'status': status,
                'info': info,
                'start': slot_start.strftime('%H:%M'),
                'end': slot_end.strftime('%H:%M'),
            })

        total = len(cells)
        rows.append({
            'resource': resource,
            'cells': cells,
            'free': free,
            'total': total,
            'next_free': next_free,
            'percent': int(free * 100 / total) if total else 0,
        })
    return rows
from datetime import datetime, timedelta
from functools import wraps

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import BookingForm, RegisterForm, ResourceForm
from .models import Booking, Resource, is_manager
from .utils import build_day_grid


# ---------------------------------------------------------------- helpers
def manager_required(view):
    @login_required
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not is_manager(request.user):
            messages.error(request, 'Only room managers can access that page.')
            return redirect('dashboard')
        return view(request, *args, **kwargs)
    return wrapper


def parse_date(value):
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return timezone.localdate()


def moderatable(user):
    """Bookings a manager is allowed to review."""
    qs = Booking.objects.select_related('resource', 'user', 'reviewed_by')
    if user.is_superuser:
        return qs
    return qs.filter(Q(resource__manager=user) | Q(resource__manager__isnull=True))


def get_greeting(now):
    """Return (greeting text, emoji) for the given local datetime."""
    hour = now.hour
    if 5 <= hour < 12:
        return 'Good Morning', '🌅'
    if 12 <= hour < 17:
        return 'Good Afternoon', '☀️'
    if 17 <= hour < 21:
        return 'Good Evening', '🌇'
    return 'Good Night', '🌙'


# ---------------------------------------------------------------- auth
def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Welcome! Your account has been created.')
        return redirect('dashboard')
    return render(request, 'registration/register.html', {'form': form})

# ---------------------------------------------------------------- dashboard
@login_required
def dashboard(request):
    now = timezone.localtime()
    today = now.date()
    user = request.user
    manager = is_manager(user)

    # Resource counts and free slots (shared, system-wide availability)
    resources = Resource.objects.filter(is_active=True)
    rows = build_day_grid(resources, today)
    glance = {
        'rooms': resources.filter(resource_type=Resource.ROOM).count(),
        'labs': resources.filter(resource_type=Resource.LAB).count(),
        'equipment': resources.filter(resource_type=Resource.EQUIPMENT).count(),
        'free_slots': sum(r['free'] for r in rows),
        'total_slots': sum(r['total'] for r in rows),
    }

    greeting, greeting_icon = get_greeting(now)
    context = {
        'today': today,
        'greeting': greeting,
        'greeting_icon': greeting_icon,
        'display_name': user.first_name.strip() or user.get_username(),
        'glance': glance,
        'manager_mode': manager,
    }

    if manager:
        # Manager view: only bookings for resources this manager may moderate.
        qs = moderatable(user)
        pending_qs = qs.filter(status=Booking.PENDING)
        context['manager_stats'] = {
            'total': qs.count(),
            'pending': pending_qs.count(),
            'approved': qs.filter(status=Booking.APPROVED).count(),
            'rejected': qs.filter(status=Booking.REJECTED).count(),
            'approved_today': qs.filter(status=Booking.APPROVED, date=today).count(),
        }
        context['pending_preview'] = pending_qs.order_by('date', 'start_time')[:5]
        context['upcoming'] = qs.filter(
            status=Booking.APPROVED, date__gte=today,
        ).order_by('date', 'start_time')[:5]
    else:
        # Normal user view: only the user's own bookings (no pending figure).
        mine = Booking.objects.filter(user=user)
        context['my_stats'] = {
            'total': mine.count(),
            'approved': mine.filter(status=Booking.APPROVED).count(),
            'rejected': mine.filter(status=Booking.REJECTED).count(),
            'approved_today': mine.filter(date=today, status=Booking.APPROVED).count(),
        }
        context['upcoming'] = mine.filter(
            date__gte=today,
            status__in=[Booking.PENDING, Booking.APPROVED],
        ).select_related('resource').order_by('date', 'start_time')[:5]

    return render(request, 'bookings/dashboard.html', context)


# ---------------------------------------------------------------- resources
@login_required
def resource_list(request):
    rtype = request.GET.get('type', '')
    resources = Resource.objects.select_related('manager')
    if rtype in dict(Resource.TYPE_CHOICES):
        resources = resources.filter(resource_type=rtype)
    return render(request, 'bookings/resource_list.html', {
        'resources': resources, 'rtype': rtype, 'types': Resource.TYPE_CHOICES,
    })


@manager_required
def resource_create(request):
    form = ResourceForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Resource created successfully.')
        return redirect('resource_list')
    return render(request, 'bookings/resource_form.html', {'form': form, 'title': 'Add Resource'})


@manager_required
def resource_update(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    form = ResourceForm(request.POST or None, instance=resource)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Resource updated successfully.')
        return redirect('resource_list')
    return render(request, 'bookings/resource_form.html', {'form': form, 'title': f'Edit {resource.name}'})


@manager_required
def resource_delete(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    if request.method == 'POST':
        resource.delete()
        messages.success(request, 'Resource deleted.')
        return redirect('resource_list')
    return render(request, 'bookings/resource_confirm_delete.html', {'resource': resource})


# ---------------------------------------------------------------- calendar
@login_required
def calendar_view(request):
    day = parse_date(request.GET.get('date'))
    rtype = request.GET.get('type', '')
    resources = Resource.objects.filter(is_active=True)
    if rtype in dict(Resource.TYPE_CHOICES):
        resources = resources.filter(resource_type=rtype)
    rows = build_day_grid(resources, day)
    hours = [f'{c["hour"]:02d}:00' for c in rows[0]['cells']] if rows else []
    return render(request, 'bookings/calendar.html', {
        'day': day, 'prev_day': day - timedelta(days=1), 'next_day': day + timedelta(days=1),
        'is_today': day == timezone.localdate(),
        'rows': rows, 'hours': hours, 'rtype': rtype, 'types': Resource.TYPE_CHOICES,
    })


@login_required
def availability_api(request):
    """JSON list of occupied time ranges - used by the booking form for live conflict hints."""
    rid = request.GET.get('resource', '')
    day = parse_date(request.GET.get('date'))
    if not rid.isdigit():
        return JsonResponse({'bookings': []})
    qs = Booking.objects.filter(
        resource_id=rid, date=day, status__in=[Booking.PENDING, Booking.APPROVED]
    ).order_by('start_time')
    data = [{
        'start': b.start_time.strftime('%H:%M'),
        'end': b.end_time.strftime('%H:%M'),
        'status': b.status,
    } for b in qs]
    return JsonResponse({'bookings': data})


# ---------------------------------------------------------------- bookings
@login_required
def booking_create(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.status = Booking.PENDING
            booking.save()
            messages.success(request, 'Reservation submitted. It is now waiting for manager approval.')
            return redirect('my_bookings')
    else:
        initial = {'date': timezone.localdate()}
        for key, field in (('resource', 'resource'), ('date', 'date'),
                           ('start', 'start_time'), ('end', 'end_time')):
            if request.GET.get(key):
                initial[field] = request.GET[key]
        form = BookingForm(initial=initial)
    return render(request, 'bookings/booking_form.html', {'form': form})


@login_required
def my_bookings(request):
    status = request.GET.get('status', '')
    all_mine = Booking.objects.filter(user=request.user).select_related('resource', 'reviewed_by')
    counts = {
        'all': all_mine.count(),
        'pending': all_mine.filter(status=Booking.PENDING).count(),
        'approved': all_mine.filter(status=Booking.APPROVED).count(),
        'rejected': all_mine.filter(status=Booking.REJECTED).count(),
        'cancelled': all_mine.filter(status=Booking.CANCELLED).count(),
    }
    bookings = all_mine
    if status in dict(Booking.STATUS_CHOICES):
        bookings = bookings.filter(status=status)
    return render(request, 'bookings/my_bookings.html', {
        'bookings': bookings, 'status': status, 'counts': counts,
    })


@login_required
@require_POST
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if booking.can_cancel:
        booking.status = Booking.CANCELLED
        booking.save(update_fields=['status'])
        messages.success(request, 'Reservation cancelled. The slot is free again.')
    else:
        messages.error(request, 'This reservation can no longer be cancelled.')
    return redirect('my_bookings')


# ---------------------------------------------------------------- approval hierarchy
@manager_required
def manager_dashboard(request):
    qs = moderatable(request.user)
    pending = qs.filter(status=Booking.PENDING).order_by('date', 'start_time')
    reviewed = qs.exclude(status=Booking.PENDING).order_by('-created_at')[:15]
    today = timezone.localdate()
    stats = {
        'pending': pending.count(),
        'approved_today': qs.filter(status=Booking.APPROVED, date=today).count(),
        'approved_total': qs.filter(status=Booking.APPROVED).count(),
        'rejected_total': qs.filter(status=Booking.REJECTED).count(),
    }
    return render(request, 'bookings/manager_dashboard.html', {
        'pending': pending, 'reviewed': reviewed, 'stats': stats,
    })


@manager_required
@require_POST
def review_booking(request, pk):
    booking = get_object_or_404(moderatable(request.user), pk=pk)
    action = request.POST.get('action')
    note = request.POST.get('note', '').strip()

    if booking.status != Booking.PENDING:
        messages.warning(request, 'This request has already been reviewed.')
        return redirect('manager_dashboard')

    if action == 'approve':
        if booking.overlapping([Booking.APPROVED]).exists():
            messages.error(request, 'Cannot approve: another approved booking overlaps this slot.')
            return redirect('manager_dashboard')
        booking.status = Booking.APPROVED
    elif action == 'reject':
        booking.status = Booking.REJECTED
    else:
        messages.error(request, 'Invalid action.')
        return redirect('manager_dashboard')

    booking.manager_note = note
    booking.reviewed_by = request.user
    booking.reviewed_at = timezone.now()
    booking.save()
    messages.success(request, f'Request {booking.get_status_display().lower()}: '
                              f'{booking.resource.name} on {booking.date:%d %b} '
                              f'({booking.start_time:%H:%M}-{booking.end_time:%H:%M}).')
    return redirect('manager_dashboard')
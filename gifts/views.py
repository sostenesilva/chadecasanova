import json
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Gift, SiteConfig


def index(request):
    gifts = Gift.objects.all()
    config = SiteConfig.get_config()
    context = {
        'gifts': gifts,
        'config': config,
        'available_count': gifts.filter(status=Gift.STATUS_AVAILABLE).count(),
        'reserved_count':  gifts.filter(status=Gift.STATUS_RESERVED).count(),
        'purchased_count': gifts.filter(status=Gift.STATUS_PURCHASED).count(),
    }
    return render(request, 'gifts/index.html', context)


@require_POST
def reserve_gift(request, pk):
    gift = get_object_or_404(Gift, pk=pk)
    name = request.POST.get('name', '').strip()

    if gift.status != Gift.STATUS_AVAILABLE:
        label = 'reservado' if gift.status == Gift.STATUS_RESERVED else 'comprado'
        response = render(request, 'gifts/partials/step1.html', {
            'error': f'Este presente já foi {label}.', 'name': name, 'pk': pk,
        })
        response['HX-Retarget'] = '#sp-1'
        response['HX-Reswap'] = 'innerHTML'
        return response

    if not name:
        response = render(request, 'gifts/partials/step1.html', {
            'error': 'Informe seu nome.', 'name': '', 'pk': pk,
        })
        response['HX-Retarget'] = '#sp-1'
        response['HX-Reswap'] = 'innerHTML'
        return response

    gift.status = Gift.STATUS_RESERVED
    gift.reserved_by = name
    gift.reserved_at = timezone.now()
    gift.save()

    gifts_qs = Gift.objects.all()
    response = render(request, 'gifts/partials/step2.html', {
        'gift': gift,
        'config': SiteConfig.get_config(),
        'available_count': gifts_qs.filter(status=Gift.STATUS_AVAILABLE).count(),
        'reserved_count':  gifts_qs.filter(status=Gift.STATUS_RESERVED).count(),
    })
    response['HX-Trigger'] = 'goStep2'
    return response


@require_POST
def cancel_gift(request, pk):
    gift = get_object_or_404(Gift, pk=pk)

    if gift.status == Gift.STATUS_PURCHASED:
        response = HttpResponse('')
        response['HX-Trigger'] = json.dumps({'showError': 'Presente já confirmado como comprado.'})
        return response

    gift.status = Gift.STATUS_AVAILABLE
    gift.reserved_by = ''
    gift.reserved_at = None
    gift.save()

    gifts_qs = Gift.objects.all()
    response = render(request, 'gifts/partials/cancel_success.html', {
        'gift': gift,
        'available_count': gifts_qs.filter(status=Gift.STATUS_AVAILABLE).count(),
        'reserved_count':  gifts_qs.filter(status=Gift.STATUS_RESERVED).count(),
    })
    response['HX-Trigger'] = 'cancelSuccess'
    return response


@require_POST
def confirm_gift(request, pk):
    from django.http import JsonResponse
    gift = get_object_or_404(Gift, pk=pk)

    if gift.status == Gift.STATUS_PURCHASED:
        return JsonResponse({'success': False, 'error': 'Presente já confirmado.'}, status=400)
    if gift.status == Gift.STATUS_AVAILABLE:
        return JsonResponse({'success': False, 'error': 'Reserve o presente antes de confirmar.'}, status=400)

    gift.status = Gift.STATUS_PURCHASED
    gift.purchased_by = gift.reserved_by
    gift.purchased_at = timezone.now()
    gift.save()

    return JsonResponse({'success': True, 'purchased_by': gift.purchased_by})

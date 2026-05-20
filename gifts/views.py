import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
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

    if gift.status != Gift.STATUS_AVAILABLE:
        label = 'reservado' if gift.status == Gift.STATUS_RESERVED else 'comprado'
        return JsonResponse({'success': False, 'error': f'Este presente já foi {label}.'}, status=400)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Dados inválidos.'}, status=400)

    name = data.get('name', '').strip()
    if not name:
        return JsonResponse({'success': False, 'error': 'Informe seu nome.'}, status=400)

    gift.status = Gift.STATUS_RESERVED
    gift.reserved_by = name
    gift.reserved_at = timezone.now()
    gift.save()

    config = SiteConfig.get_config()
    store = gift.store
    return JsonResponse({
        'success': True,
        'reserved_by': name,
        'pix_key': config.pix_key,
        'has_pix_qr': bool(config.pix_qr_code),
        'pix_qr_url': config.pix_qr_code.url if config.pix_qr_code else None,
        'delivery_lines': config.get_full_address(),
        'purchase_link': gift.purchase_link,
        'gift_name': gift.name,
        'store_name': store.name if store else None,
        'store_logo_url': store.logo.url if store and store.logo else None,
    })


@require_POST
def confirm_gift(request, pk):
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


@require_POST
def cancel_gift(request, pk):
    gift = get_object_or_404(Gift, pk=pk)

    if gift.status == Gift.STATUS_PURCHASED:
        return JsonResponse({'success': False, 'error': 'Presente já confirmado como comprado.'}, status=400)

    gift.status = Gift.STATUS_AVAILABLE
    gift.reserved_by = ''
    gift.reserved_at = None
    gift.save()

    return JsonResponse({'success': True})

from django.contrib import admin
from django.utils.html import format_html
from .models import Gift, Store, SiteConfig


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display  = ('name', 'logo_preview', 'website')
    search_fields = ('name',)
    readonly_fields = ('logo_preview',)

    fieldsets = (
        (None, {
            'fields': ('name', 'website'),
        }),
        ('Logomarca', {
            'fields': ('logo', 'logo_preview'),
            'description': 'PNG com fundo transparente garante melhor aparência no site.',
        }),
    )

    def logo_preview(self, obj):
        if obj and obj.logo:
            return format_html(
                '<img src="{}" style="max-height:48px;max-width:160px;object-fit:contain;'
                'background:#111;padding:6px;border-radius:8px;">',
                obj.logo.url,
            )
        return '—'
    logo_preview.short_description = 'Preview'


@admin.register(Gift)
class GiftAdmin(admin.ModelAdmin):
    list_display   = ('order', 'name', 'store', 'price_range', 'status_badge', 'reserved_by', 'purchased_by')
    list_display_links = ('name',)
    list_editable  = ('order',)
    list_filter    = ('status', 'store')
    search_fields  = ('name', 'reserved_by', 'purchased_by')
    ordering       = ('order', 'name')
    readonly_fields = ('reserved_at', 'purchased_at', 'preview_image')
    autocomplete_fields = ('store',)

    fieldsets = (
        ('Presente', {
            'fields': ('name', 'description', 'price_range', 'order'),
        }),
        ('Mídia & Links', {
            'fields': ('image_url', 'preview_image', 'purchase_link', 'store'),
        }),
        ('Status', {
            'fields': ('status', 'reserved_by', 'reserved_at', 'purchased_by', 'purchased_at'),
        }),
    )

    def status_badge(self, obj):
        colors = {
            'available': ('#6ee7b7', 'Disponível'),
            'reserved':  ('#fcd34d', 'Reservado'),
            'purchased': ('#f59e0b', '✓ Comprado'),
        }
        color, label = colors.get(obj.status, ('#aaa', obj.status))
        return format_html('<span style="color:{};font-weight:bold;">{}</span>', color, label)
    status_badge.short_description = 'Status'

    def preview_image(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" style="width:120px;height:120px;object-fit:cover;border-radius:8px;">',
                obj.image_url,
            )
        return '—'
    preview_image.short_description = 'Preview'


@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Evento', {
            'fields': ('event_date', 'event_venue', 'event_address'),
        }),
        ('Destinatário', {
            'fields': ('recipient_name',),
        }),
        ('Endereço de Entrega', {
            'description': 'Exibido no modal quando o convidado escolhe comprar na loja.',
            'fields': (
                'address_street', 'address_complement',
                'address_neighborhood', 'address_city',
                'address_state', 'address_zip',
            ),
        }),
        ('PIX', {
            'description': 'Configure a chave PIX e o QR Code para pagamentos.',
            'fields': ('pix_key', 'pix_qr_code', 'preview_pix_qr'),
        }),
    )
    readonly_fields = ('preview_pix_qr',)

    def preview_pix_qr(self, obj):
        if obj and obj.pix_qr_code:
            return format_html(
                '<img src="{}" style="max-width:200px;border-radius:12px;background:#fff;padding:4px;">',
                obj.pix_qr_code.url,
            )
        return '—'
    preview_pix_qr.short_description = 'Preview do QR Code'

    def has_add_permission(self, request):
        return not SiteConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

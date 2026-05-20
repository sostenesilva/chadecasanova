from django.db import models


class Store(models.Model):
    name    = models.CharField('Nome da Loja', max_length=100)
    logo    = models.ImageField('Logomarca', upload_to='stores/', blank=True, null=True,
                                help_text='Upload da logomarca da loja (PNG transparente recomendado)')
    website = models.URLField('Site da loja', max_length=300, blank=True)

    class Meta:
        verbose_name = 'Loja'
        verbose_name_plural = 'Lojas'
        ordering = ['name']

    def __str__(self):
        return self.name


class Gift(models.Model):
    STATUS_AVAILABLE = 'available'
    STATUS_RESERVED  = 'reserved'
    STATUS_PURCHASED = 'purchased'
    STATUS_CHOICES = [
        (STATUS_AVAILABLE, 'Disponível'),
        (STATUS_RESERVED,  'Reservado'),
        (STATUS_PURCHASED, 'Comprado'),
    ]

    name          = models.CharField('Nome', max_length=200)
    description   = models.TextField('Descrição', blank=True)
    image_url     = models.URLField('URL da Imagem', max_length=500)
    purchase_link = models.URLField('Link de Compra', max_length=500)
    store         = models.ForeignKey(
        Store, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Loja', related_name='gifts',
    )
    price_range   = models.CharField('Faixa de Preço', max_length=100, blank=True)
    status        = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    reserved_by   = models.CharField('Reservado por', max_length=200, blank=True)
    reserved_at   = models.DateTimeField('Reservado em', null=True, blank=True)
    purchased_by  = models.CharField('Comprado por', max_length=200, blank=True)
    purchased_at  = models.DateTimeField('Comprado em', null=True, blank=True)
    order         = models.PositiveIntegerField('Ordem', default=0)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Presente'
        verbose_name_plural = 'Presentes'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class SiteConfig(models.Model):
    event_date    = models.DateField('Data do evento', null=True, blank=True)
    event_venue   = models.CharField('Local do evento', max_length=200, blank=True,
                                     help_text='Ex: Espaço Verde, Casa da Maria')
    event_address = models.CharField('Endereço do evento', max_length=300, blank=True,
                                     help_text='Ex: Rua das Flores, 123 – Jardim Primavera')
    recipient_name       = models.CharField('Nome do destinatário', max_length=200, blank=True)
    address_street       = models.CharField('Rua e número', max_length=300, blank=True)
    address_complement   = models.CharField('Complemento', max_length=200, blank=True)
    address_neighborhood = models.CharField('Bairro', max_length=100, blank=True)
    address_city         = models.CharField('Cidade', max_length=100, blank=True)
    address_state        = models.CharField('Estado (sigla)', max_length=2, blank=True)
    address_zip          = models.CharField('CEP', max_length=9, blank=True)
    pix_key     = models.CharField(
        'Chave PIX', max_length=200, blank=True,
        help_text='CPF, e-mail, telefone ou chave aleatória',
    )
    pix_qr_code = models.ImageField(
        'QR Code PIX', upload_to='pix/', blank=True, null=True,
        help_text='Upload da imagem do QR Code gerada pelo seu banco',
    )

    class Meta:
        verbose_name = 'Configurações do Site'
        verbose_name_plural = 'Configurações do Site'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_config(cls):
        obj, _ = cls.objects.get_or_create(pk=1, defaults={})
        return obj

    _MONTHS_PT = [
        'Janeiro','Fevereiro','Março','Abril','Maio','Junho',
        'Julho','Agosto','Setembro','Outubro','Novembro','Dezembro',
    ]

    def get_event_date_display(self):
        if not self.event_date:
            return '11 de Julho de 2026'
        return f"{self.event_date.day} de {self._MONTHS_PT[self.event_date.month - 1]} de {self.event_date.year}"

    def get_event_date_short(self):
        if not self.event_date:
            return '11 · 07 · 2026'
        return self.event_date.strftime('%d · %m · %Y')

    def get_event_date_iso(self):
        if not self.event_date:
            return '2026-07-11'
        return self.event_date.isoformat()

    def get_full_address(self):
        lines = []
        if self.recipient_name:
            lines.append(self.recipient_name)
        if self.address_street:
            line = self.address_street
            if self.address_complement:
                line += f', {self.address_complement}'
            lines.append(line)
        if self.address_neighborhood:
            lines.append(self.address_neighborhood)
        city_state = ' – '.join(filter(None, [self.address_city, self.address_state]))
        if city_state:
            lines.append(city_state)
        if self.address_zip:
            lines.append(f'CEP: {self.address_zip}')
        return lines

    def __str__(self):
        return 'Configurações do Site'

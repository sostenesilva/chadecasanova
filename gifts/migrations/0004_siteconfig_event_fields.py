from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gifts', '0003_store_gift_store'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteconfig',
            name='event_date',
            field=models.DateField(blank=True, null=True, verbose_name='Data do evento'),
        ),
        migrations.AddField(
            model_name='siteconfig',
            name='event_venue',
            field=models.CharField(
                blank=True, max_length=200, verbose_name='Local do evento',
                help_text='Ex: Espaço Verde, Casa da Maria',
            ),
        ),
        migrations.AddField(
            model_name='siteconfig',
            name='event_address',
            field=models.CharField(
                blank=True, max_length=300, verbose_name='Endereço do evento',
                help_text='Ex: Rua das Flores, 123 – Jardim Primavera',
            ),
        ),
    ]

# Generated by Django 5.1.5 on 2025-03-10 09:58

import django.core.validators
import django.db.models.deletion
import django_extensions.db.fields
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ReservableItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(max_length=40, verbose_name='Name')),
                ('description', models.TextField(verbose_name='Description')),
                ('location', models.PositiveSmallIntegerField(choices=[(0, 'Other'), (1, 'Boardroom'), (2, 'Bastion'), (3, 'Kraaijenbergse Plassen')], default=0, verbose_name='Location')),
                ('is_reservable', models.BooleanField(default=True, help_text='When an item is unavailable for reservation, due to maintenance for example, set this to false.', verbose_name='Reservable')),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ReservableType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(max_length=40, unique=True, verbose_name='Material type')),
                ('category', models.PositiveSmallIntegerField(choices=[(0, 'Other'), (1, 'Boat'), (2, 'Room'), (3, 'Material')], default=0, verbose_name='Reservable category')),
                ('description', models.TextField(verbose_name='Type description')),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Boat',
            fields=[
                ('reservableitem_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='reservations.reservableitem')),
                ('capacity', models.PositiveSmallIntegerField(verbose_name='Capacity')),
                ('has_engine', models.BooleanField(default=False, verbose_name='Boat has an engine')),
                ('fleet', models.PositiveSmallIntegerField(choices=[(0, 'Other'), (1, 'Loefbijter'), (2, 'Ceulemans')], default=0, verbose_name='Boat provider')),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
            bases=('reservations.reservableitem',),
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('reservableitem_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='reservations.reservableitem')),
                ('size', models.CharField(max_length=10, verbose_name='Size')),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
            bases=('reservations.reservableitem',),
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('reservableitem_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='reservations.reservableitem')),
                ('capacity', models.PositiveSmallIntegerField(verbose_name='Capacity')),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
            bases=('reservations.reservableitem',),
        ),
        migrations.AddField(
            model_name='reservableitem',
            name='reservable_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservations.reservabletype', verbose_name='Reservable type'),
        ),
        migrations.CreateModel(
            name='ReservableTypePricing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('membership_type', models.PositiveSmallIntegerField(choices=[(0, 'Active membership'), (1, 'Passive membership'), (2, 'Active exceptional membership'), (3, 'Passive exceptional membership'), (4, 'Alumnus')], verbose_name='Membership type')),
                ('price', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Price')),
                ('reservable_type', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='reservations.reservabletype', verbose_name='Reservable type')),
            ],
            options={
                'unique_together': {('reservable_type', 'membership_type')},
            },
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateTimeField(verbose_name='Start time')),
                ('end', models.DateTimeField(verbose_name='End time')),
                ('reserved_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservations.reservableitem')),
            ],
            options={
                'constraints': [models.CheckConstraint(condition=models.Q(('end__gt', models.F('start'))), name='end_gt_start', violation_error_message='End time cannot be before the start time.')],
            },
        ),
    ]

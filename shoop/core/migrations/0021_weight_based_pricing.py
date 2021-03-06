# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import shoop.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('shoop', '0020_services_and_methods'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeightBasedPriceRange',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('min_value', shoop.core.fields.MeasurementField(decimal_places=9, default=0, max_digits=36, blank=True, null=True, verbose_name='min weight', unit='g')),
                ('max_value', shoop.core.fields.MeasurementField(decimal_places=9, default=0, max_digits=36, blank=True, null=True, verbose_name='max weight', unit='g')),
                ('price_value', shoop.core.fields.MoneyValueField(max_digits=36, decimal_places=9)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WeightBasedPriceRangeTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language_code', models.CharField(max_length=15, verbose_name='Language', db_index=True)),
                ('description', models.CharField(max_length=100, verbose_name='description', blank=True)),
                ('master', models.ForeignKey(related_name='translations', editable=False, to='shoop.WeightBasedPriceRange', null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'shoop_weightbasedpricerange_translation',
                'db_tablespace': '',
                'default_permissions': (),
                'verbose_name': 'weight based price range Translation',
            },
        ),
        migrations.CreateModel(
            name='WeightBasedPricingBehaviorComponent',
            fields=[
                ('servicebehaviorcomponent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='shoop.ServiceBehaviorComponent')),
            ],
            options={
                'abstract': False,
            },
            bases=('shoop.servicebehaviorcomponent',),
        ),
        migrations.AddField(
            model_name='weightbasedpricerange',
            name='component',
            field=models.ForeignKey(related_name='ranges', to='shoop.WeightBasedPricingBehaviorComponent'),
        ),
        migrations.AlterUniqueTogether(
            name='weightbasedpricerangetranslation',
            unique_together=set([('language_code', 'master')]),
        ),
    ]

# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from django.db.transaction import atomic
from django.utils.translation import ugettext_lazy as _

from shoop.admin.form_part import FormPartsViewMixin, SaveFormPartsMixin
from shoop.admin.toolbar import get_default_edit_toolbar
from shoop.admin.utils.views import CreateOrUpdateView
from shoop.apps.provides import get_provide_objects
from shoop.campaigns.admin_module.form_parts import (
    BasketBaseFormPart, BasketConditionsFormPart, BasketEffectsFormPart,
    CatalogBaseFormPart, CatalogConditionsFormPart, CatalogEffectsFormPart,
    CatalogFiltersFormPart
)
from shoop.campaigns.admin_module.forms import CouponForm
from shoop.campaigns.models.campaigns import (
    BasketCampaign, CatalogCampaign, Coupon
)
from shoop.campaigns.utils import _Breadcrumbed


class CampaignEditView(SaveFormPartsMixin, FormPartsViewMixin, CreateOrUpdateView):
    template_name = "shoop/campaigns/admin/edit_campaigns.jinja"
    context_object_name = "campaign"
    form_part_class_provide_key = "campaign"
    add_form_errors_as_messages = False
    rules_form_part_class = None  # Override in subclass
    effects_form_part_class = None  # Override in subclass
    condition_key = ""  # Override in subclass
    effect_key = ""  # Override in subclass

    @atomic
    def form_valid(self, form):
        return self.save_form_parts(form)

    def get_form_parts(self, object):
        form_parts = super(CampaignEditView, self).get_form_parts(object)
        if not object.pk:
            return form_parts

        for form in get_provide_objects(self.condition_key):
            form_parts.append(self._get_rules_form_part(form, object))

        for form in get_provide_objects(self.effect_key):
            form_parts.append(self._get_effects_form_part(form, object))

        return form_parts

    def _get_rules_form_part(self, form, object):
        return self.rules_form_part_class(
            self.request, form, "conditions_%s" % form._meta.model.__name__.lower(), object)

    def _get_effects_form_part(self, form, object):
        return self.effects_form_part_class(
            self.request, form, "effects_%s" % form._meta.model.__name__.lower(), object)

    def get_toolbar(self):
        save_form_id = self.get_save_form_id()
        return get_default_edit_toolbar(self, save_form_id)


class CatalogCampaignEditView(_Breadcrumbed, CampaignEditView):
    model = CatalogCampaign
    condition_key = "campaign_context_condition"
    filter_key = "campaign_catalog_filter"
    effect_key = "catalog_campaign_effect"
    base_form_part_classes = [CatalogBaseFormPart]
    rules_form_part_class = CatalogConditionsFormPart
    effects_form_part_class = CatalogEffectsFormPart

    parent_name = _("Catalog Campaign")
    parent_url = "shoop_admin:catalog_campaigns.list"

    def get_form_parts(self, object):
        form_parts = super(CatalogCampaignEditView, self).get_form_parts(object)
        if not object.pk:
            return form_parts

        for form in get_provide_objects(self.filter_key):
            form_parts.append(self._get_filters_form_part(form, object))

        return form_parts

    def _get_filters_form_part(self, form, object):
        return CatalogFiltersFormPart(
            self.request, form, "filters_%s" % form._meta.model.__name__.lower(), object)


class BasketCampaignEditView(_Breadcrumbed, CampaignEditView):
    model = BasketCampaign
    condition_key = "campaign_basket_condition"
    effect_key = "basket_campaign_effect"
    base_form_part_classes = [BasketBaseFormPart]
    rules_form_part_class = BasketConditionsFormPart
    effects_form_part_class = BasketEffectsFormPart

    parent_name = _("Basket Campaign")
    parent_url = "shoop_admin:basket_campaigns.list"


class CouponEditView(_Breadcrumbed, CreateOrUpdateView):
    model = Coupon
    template_name = "shoop/campaigns/admin/edit_coupons.jinja"
    form_class = CouponForm
    context_object_name = "coupon"
    add_form_errors_as_messages = True
    parent_name = _("Coupon")
    parent_url = "shoop_admin:coupons.list"

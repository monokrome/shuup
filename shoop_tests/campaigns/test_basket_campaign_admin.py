# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
# test that admin actually saves catalog
import decimal
import pytest

from django.test import override_settings

from shoop.apps.provides import override_provides
from shoop.campaigns.admin_module.form_parts import BasketBaseFormPart
from shoop.campaigns.admin_module.views import BasketCampaignEditView
from shoop.campaigns.models.campaigns import BasketCampaign
from shoop.campaigns.models.basket_conditions import BasketTotalProductAmountCondition
from shoop.campaigns.models.basket_effects import BasketDiscountAmount
from shoop.testing.factories import get_default_shop
from shoop.testing.utils import apply_request_middleware


DEFAULT_CONDITION_FORMS = [
    "shoop.campaigns.admin_module.forms:BasketTotalProductAmountConditionForm",
    "shoop.campaigns.admin_module.forms:BasketTotalAmountConditionForm",
    "shoop.campaigns.admin_module.forms:ProductsInBasketConditionForm",
    "shoop.campaigns.admin_module.forms:ContactGroupBasketConditionForm",
    "shoop.campaigns.admin_module.forms:ContactBasketConditionForm",
]

DEFAULT_EFFECT_FORMS = [
    "shoop.campaigns.admin_module.forms:BasketDiscountAmountForm",
    "shoop.campaigns.admin_module.forms:BasketDiscountPercentageForm",
    "shoop.campaigns.admin_module.forms:FreeProductLineForm",
]


def get_form_parts(request, view, object):
    with override_provides("campaign_basket_condition", DEFAULT_CONDITION_FORMS):
        with override_provides("basket_campaign_effect", DEFAULT_EFFECT_FORMS):
            initialized_view = view(request=request, kwargs={"pk": object.pk})
            return initialized_view.get_form_parts(object)


@pytest.mark.django_db
def test_admin_campaign_edit_view_works(rf, admin_user):
    shop = get_default_shop()
    view_func = BasketCampaignEditView.as_view()
    request = apply_request_middleware(rf.get("/"), user=admin_user)
    campaign = BasketCampaign.objects.create(name="test campaign", active=True, shop=shop)
    response = view_func(request, pk=campaign.pk)
    assert campaign.name in response.rendered_content

    response = view_func(request, pk=None)
    assert response.rendered_content


@pytest.mark.django_db
def test_campaign_new_mode_view_formsets(rf, admin_user):
    view = BasketCampaignEditView
    get_default_shop()
    request = apply_request_middleware(rf.get("/"), user=admin_user)
    form_parts = get_form_parts(request, view, view.model())
    assert len(form_parts) == 1
    assert issubclass(form_parts[0].__class__, BasketBaseFormPart)


@pytest.mark.django_db
def test_campaign_edit_view_formsets(rf, admin_user):
    view = BasketCampaignEditView
    shop = get_default_shop()
    object = BasketCampaign.objects.create(name="test campaign", active=True, shop=shop)
    request = apply_request_middleware(rf.get("/"), user=admin_user)
    form_parts = get_form_parts(request, view, object)
    # form parts should include forms  plus one for the base form
    assert len(form_parts) == (len(DEFAULT_CONDITION_FORMS) + len(DEFAULT_EFFECT_FORMS) + 1)


@pytest.mark.django_db
def test_campaign_creation(rf, admin_user):
    """
    To make things little bit more simple let's use only english as
    a language.
    """
    with override_settings(LANGUAGES=[("en", "en")]):
        view = BasketCampaignEditView.as_view()
        data = {
            "base-name": "Test Campaign",
            "base-public_name__en": "Test Campaign",
            "base-shop": get_default_shop().id,
            "base-active": True,
            "base-basket_line_text": "Test campaign activated!"
        }
        campaigns_before = BasketCampaign.objects.count()
        request = apply_request_middleware(rf.post("/", data=data), user=admin_user)
        response = view(request, pk=None)
        assert response.status_code in [200, 302]
        assert BasketCampaign.objects.count() == (campaigns_before + 1)


@pytest.mark.django_db
def test_campaign_edit_save(rf, admin_user):
    """
    To make things little bit more simple let's use only english as
    a language.
    """
    with override_settings(LANGUAGES=[("en", "en")]):
        shop = get_default_shop()
        object = BasketCampaign.objects.create(name="test campaign", active=True, shop=shop)
        object.save()
        view = BasketCampaignEditView.as_view()
        new_name = "Test Campaign"
        assert object.name != new_name
        data = {
            "base-name": new_name,
            "base-public_name__en": "Test Campaign",
            "base-shop": get_default_shop().id,
            "base-active": True,
            "base-basket_line_text": "Test campaign activated!"
        }
        methods_before = BasketCampaign.objects.count()
        # Conditions and effects is tested separately
        with override_provides("campaign_basket_condition", []):
            with override_provides("basket_campaign_effect", []):
                request = apply_request_middleware(rf.post("/", data=data), user=admin_user)
                response = view(request, pk=object.pk)
                assert response.status_code in [200, 302]

        assert BasketCampaign.objects.count() == methods_before
        assert BasketCampaign.objects.get(pk=object.pk).name == new_name


@pytest.mark.django_db
def test_rules_and_effects(rf, admin_user):
    """
    To make things little bit more simple let's use only english as
    a language.
    """
    get_default_shop()
    with override_settings(LANGUAGES=[("en", "en")]):
        shop = get_default_shop()
        object = BasketCampaign.objects.create(name="test campaign", active=True, shop=shop)
        assert object.conditions.count() == 0
        assert object.effects.count() == 0
        view = BasketCampaignEditView.as_view()
        data = {
            "base-name": "test campaign",
            "base-public_name__en": "Test Campaign",
            "base-shop": get_default_shop().id,
            "base-active": True,
            "base-basket_line_text": "Test campaign activated!"
        }
        with override_provides(
                "campaign_basket_condition", ["shoop.campaigns.admin_module.forms:BasketTotalProductAmountConditionForm"]):
            with override_provides(
                    "basket_campaign_effect", ["shoop.campaigns.admin_module.forms:BasketDiscountAmountForm"]):
                data.update(get_products_in_basket_data())
                data.update(get_free_product_data(object))
                request = apply_request_middleware(rf.post("/", data=data), user=admin_user)
                view(request, pk=object.pk)

        object.refresh_from_db()
        assert object.conditions.count() == 1
        assert object.effects.count() == 1


def get_products_in_basket_data():
    rule_name = BasketTotalProductAmountCondition.__name__.lower()
    data = {
        "conditions_%s-MAX_NUM_FORMS" % rule_name: 2,
        "conditions_%s-MIN_NUM_FORMS" % rule_name: 0,
        "conditions_%s-INITIAL_FORMS" % rule_name: 0,
        "conditions_%s-TOTAL_FORMS" % rule_name: 1,
    }
    data["conditions_%s-0-%s" % (rule_name, "product_count")] = 20
    return data


def get_free_product_data(object):
    effect_name = BasketDiscountAmount.__name__.lower()
    data = {
        "effects_%s-MAX_NUM_FORMS" % effect_name: 2,
        "effects_%s-MIN_NUM_FORMS" % effect_name: 0,
        "effects_%s-INITIAL_FORMS" % effect_name: 0,
        "effects_%s-TOTAL_FORMS" % effect_name: 1,
    }
    data["effects_%s-0-%s" % (effect_name, "campaign")] = object.pk
    data["effects_%s-0-%s" % (effect_name, "discount_amount")] = 20
    return data

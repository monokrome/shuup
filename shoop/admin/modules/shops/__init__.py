# -*- coding: utf-8 -*-
# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from shoop.admin.base import AdminModule, MenuEntry
from shoop.admin.utils.permissions import get_default_model_permissions
from shoop.admin.utils.urls import derive_model_url, get_edit_and_list_urls
from shoop.core.models import Shop


class ShopModule(AdminModule):
    name = _("Shops")
    breadcrumbs_menu_entry = MenuEntry(name, url="shoop_admin:shop.list")

    def get_urls(self):
        return get_edit_and_list_urls(
            url_prefix="^shops",
            view_template="shoop.admin.modules.shops.views.Shop%sView",
            name_template="shop.%s",
            permissions=get_default_model_permissions(Shop)
        )

    def get_menu_entries(self, request):
        category = _("System")  # NB: To clutter the menu a little less, shops live under System
        return [
            MenuEntry(
                text=self.name,
                icon="fa fa-house",
                url="shoop_admin:shop.list",
                category=category
            ),
        ]

    def get_required_permissions(self):
        return get_default_model_permissions(Shop)

    def get_model_url(self, object, kind):
        return derive_model_url(Shop, "shoop_admin:shop", object, kind)

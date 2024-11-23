"""Define WagTail hooks for expositions app."""
from wagtail import hooks
from wagtail.admin.menu import MenuItem

from .models.pages import harvest_control_viewset


@hooks.register("register_admin_viewset")
def register_viewset():
    return harvest_control_viewset


@hooks.register('construct_reports_menu')
def add_custom_report_menu_item(request, menu_items):
    menu_items.append(
        MenuItem(
            'Historial de Cosechamientos',
            '/wagtail/harvest-control/',
            icon_name='history',
            order=1200
        )
    )

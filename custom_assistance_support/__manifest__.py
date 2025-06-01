# Part of Odoo. See LICENSE file for full copyright and licensing details.
# flake8: noqa: B018
{
    "name": "Custom Assistance Support",
    "version": "1.0.2",
    "depends": ["helpdesk", "mail"],
    "author": "Synapsis",
    "website": "https://synapsisbpo.com/",
    "category": "Helpdesk",
    "description": "Notifies in the General channel when a ticket is created",
    "installable": True,
    "auto_install": False,
    "data": [
        "report/report_rfc_form_normal.xml",
        "report/report_rfc_form_urgent.xml",
        "data/request_type_data.xml",
        "data/ticket_type_data.xml",
        "views/request_type_views.xml",
        "views/ticket_type_views.xml",
        "views/helpdesk_ticket_views.xml",
        "views/follower_group_views.xml",
        "views/helpdesk_sla_views.xml",
        "wizard/form_action_rfc.xml",
        "security/ir.model.access.csv",
    ],
    "migrations": [
        "migrations/1.0.0/",
    ],
}

# -*- coding: utf-8 -*-
from odoo import fields, models


class HelpdeskSLA(models.Model):
    _inherit = "helpdesk.sla"

    request_type_ids = fields.Many2many(
        comodel_name="request.type",
        relation="helpdesk_sla_request_type_rel",
        column1="sla_id",
        column2="request_type_id",
        string="Request Types",
        help="Request types to which this SLA applies.",
    )

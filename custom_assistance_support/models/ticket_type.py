from random import randint

from odoo import api, fields, models


class RequestType(models.Model):
    _name = "ticket.type"
    _description = "Request Type"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(string="Name", required=True)
    color = fields.Integer(string="Color")

    _sql_constraints = [
        (
            "name_uniq",
            "unique (name)",
            "A type of request with the same name already exists.",
        ),
    ]

    @api.model
    def name_create(self, name):
        existing_tag = self.search([("name", "=ilike", name.strip())], limit=1)
        if existing_tag:
            return existing_tag.id, existing_tag.display_name
        return super().name_create(name)

from odoo import fields, models


class FollowerGroup(models.Model):
    _name = "mail.follower.group"
    _description = "Follower Group"

    name = fields.Char(required=True)
    partner_ids = fields.Many2many("res.partner", string="Contacts")
    domain = fields.Char(string="Domain Contacts")

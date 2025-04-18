from odoo import models, fields, api

class FollowerGroup(models.Model):
    _name = 'mail.follower.group'
    _description = 'Follower Group'

    name = fields.Char(required=True)
    partner_ids = fields.Many2many('res.partner', string='Contacts')
# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    ticket_type_id = fields.Many2one(
        "ticket.type", string="Ticket Type", help="Type of ticket"
    )
    request_type_id = fields.Many2one(
        "request.type", string="Request Type", help="Type of request"
    )
    ticket_category_id = fields.Many2one(
        "ticket.category.type", string="Category Type", help="Type of category"
    )

    follower_group_id = fields.Many2one(
        "mail.follower.group",
        string="Follower Group",
        help="Group of followers for this ticket",
    )

    show_button_rfc = fields.Boolean(
        string="Show RFC Button",
        compute="_compute_show_button_rfc",
    )

    @api.model
    def create(self, vals):
        ticket = super().create(vals)

        _logger.info("Ticket creado: %s (ID: %s)", ticket.name, ticket.id)

        try:
            # Buscar el canal por nombre
            canal = (
                self.env["discuss.channel"]
                .sudo()
                .search([("name", "=", "general")], limit=1)
            )

            # Obtener el usuario admin
            admin_user = self.env.ref("base.user_admin")
            partner_admin = admin_user.partner_id

            if canal and partner_admin:
                mensaje = f"Se ha creado un nuevo ticket con id: {ticket.id}"
                canal.message_post(
                    body=mensaje,
                    author_id=partner_admin.id,
                    message_type="comment",
                    subtype_xmlid="mail.mt_comment",
                )
                _logger.info(
                    "Mensaje enviado al canal General desde admin para ticket %s",
                    ticket.id,
                )
                _logger.info("Message sent for ticket %s", ticket.id)

            else:
                _logger.warning("Channel or user admin not found.")

        except Exception as e:
            _logger.error("Error to send message: %s", str(e))

        # get de current user's mail and verify FollowerGroup
        try:
            user_email = self.env.user.partner_id.email
            _logger.info("User email: %s", user_email)
            if user_email:
                domain_parts = user_email.split("@")
                if len(domain_parts) == 2:
                    group = self.env["mail.follower.group"].search(
                        [("domain", "=", domain_parts[1])], limit=1
                    )

                    domain = group.domain if group else None
                    _logger.info("Domain from FollowerGroup: %s", domain)
                    if domain:
                        _logger.info("Domain: %s", domain)
                        # add as follwer all partner of the group
                        ticket.message_subscribe(partner_ids=group.partner_ids.ids)
                        _logger.info("Followers added to ticket %s", ticket.id)

                    else:
                        _logger.warning(
                            "No domain found for the user email: %s", user_email
                        )
                else:
                    _logger.warning("Invalid domain format: %s", domain)
            else:
                _logger.warning("Domain or user email is empty.")
        except Exception as e:
            _logger.error("Error to add followers: %s", str(e))
        return ticket

    def _sla_find(self):
        """Override Odoo's SLA find logic to add x_request_type comparison."""
        tickets_map = {}
        sla_domain_map = {}

        def _generate_key(ticket):
            fields_list = self._sla_reset_trigger()
            key = list()
            for field_name in fields_list:
                if ticket._fields[field_name].type == "many2one":
                    key.append(ticket[field_name].id)
                else:
                    key.append(ticket[field_name])
            return tuple(key)

        for ticket in self:
            if ticket.team_id.use_sla:
                key = _generate_key(ticket)
                tickets_map.setdefault(key, self.env["helpdesk.ticket"])
                tickets_map[key] |= ticket
                if key not in sla_domain_map:
                    sla_domain_map[key] = expression.AND(
                        [
                            [
                                ("team_id", "=", ticket.team_id.id),
                                ("priority", "=", ticket.priority),
                                ("stage_id.sequence", ">=", ticket.stage_id.sequence),
                            ],
                            expression.OR(
                                [
                                    ticket._sla_find_extra_domain(),
                                    self._sla_find_false_domain(),
                                ]
                            ),
                        ]
                    )

        result = {}
        for key, tickets in tickets_map.items():
            domain = sla_domain_map[key]
            slas = self.env["helpdesk.sla"].search(domain)
            # add filter to field request_type_ids
            result[tickets] = slas.filtered(
                lambda s, tickets=tickets: (
                    (not s.tag_ids or (tickets.tag_ids & s.tag_ids))
                    and (
                        not s.request_type_ids
                        or tickets[0].request_type_id == s.request_type_ids
                    )
                )
            )
        return result

    def _compute_show_button_rfc(self):
        """When ticket type changes, set request_type_id to ticket_type_id."""
        for ticket in self:
            if ticket.ticket_type_id and ticket.ticket_type_id.check_event:
                ticket.show_button_rfc = True
            else:
                ticket.show_button_rfc = False

    @api.onchange("ticket_type_id")
    def _onchange_ticket_type_id(self):
        """When ticket type changes, set request_type_id to ticket_type_id."""
        for ticket in self:
            ticket._compute_show_button_rfc()

    def action_open_rfc_wizard(self):
        # If ticket type has check_event enabled, set request_type_id to ticket_type_id
        return {
            "type": "ir.actions.act_window",
            "name": "Reporte RFC",
            "res_model": "form.action.rfc.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_ticket_id": self.id},
        }

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    ticket_type_id = fields.Many2one(
        "ticket.type", string="Ticket Type", help="Type of ticket"
    )

    follower_group_id = fields.Many2one(
        "mail.follower.group",
        string="Follower Group",
        help="Group of followers for this ticket",
    )

    @api.onchange("follower_group_id")
    def _onchange_follower_group(self):
        if self.follower_group_id:
            self.message_subscribe(partner_ids=self.follower_group_id.partner_ids.ids)

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

        return ticket

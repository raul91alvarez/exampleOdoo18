import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    ticket_type_id = fields.Many2one(
        "ticket.type", string="Ticket Type", help="Type of ticket"
    )
    request_type_id = fields.Many2one(
        "request.type", string="Request Type", help="Type of request"
    )

    follower_group_id = fields.Many2one(
        "mail.follower.group",
        string="Follower Group",
        help="Group of followers for this ticket",
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

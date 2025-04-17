from odoo import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)

MAPPING = {
    'Solicitud ': 'Solicitud',
    'Incidente': 'Incidente',
    'Control de cambio': 'Control de cambio',
    'Proyecto': 'Proyecto',
    'Compra': 'Compra',
}

def migrate(cr, version):
    if not version:
        return
    _logger.info("Running post-migration script for custom_assistance_support module.")
    env = api.Environment(cr, SUPERUSER_ID, {})
    HelpdeskTicket = env['helpdesk.ticket']
    TicketType = env['ticket.type']
    
    result = HelpdeskTicket.search([('x_studio_request_type', '!=', False)])
    
    for ticket in result:
        studio_value = MAPPING.get(ticket.x_studio_request_type, '')

        request_type = TicketType.search([('name', '=', studio_value)], limit=1)
        if request_type:
            ticket.ticket_type_id = request_type.id
            _logger.info(f"Ticket {ticket.id} updated with request type '{studio_value}'.")
        else:
            _logger.warning(f"Request type not found for =>: {studio_value} (Ticket ID: {ticket.id})")
        
        
    _logger.info("Post-migration script completed.")
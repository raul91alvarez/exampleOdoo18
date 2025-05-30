import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

MAPPING = {
    "access_control": "Control de accesos",
    "team_management": "Teams",
    "email_forwarding": "Forward",
    "network_points": "Puntos de Red",
    "employee_onboarding": "Altas - Solo RRHH",
    "tech_service": "Servicio de Tecnología",
    "microstrategy_access": "Microstrategy",
    "wifi_connection": "Conexión WIFI",
    "notebook_request": "Solicitud de Notebook",
    "software_request": "Requerimiento de software",
    "interaction_desktop": "Interaction Desktop",
    "remote_pc_access": "Conexión remota a PC",
    "user_accounts_apps": "Cuentas de Usuarios Aplicaciones",
    "employee_offboarding": "Bajas - Solo RRHH",
    "equipment_handling": "Instalación / reubicación y préstamo de equipos",
    "vpn_connection": "Conexión VPN",
    "onsite_support": "Soporte en Sitio",
    "device_configuration": "Configuración de equipos",
    "printing_support": "Impresión",
    "file_transfer": "Envio de Archivos (SFTP - Correo=)",
    "office_365_access": "Office 365",
    "web_access": "Acceso a sitio web",
    "softphone_config": "Softphone",
    "zimbra_email": "Correo Zimbra",
    "user_errors": "Error de usuarios",
    "power_bi": "Power BI",
    "campaign_movement": "Movimiento de Campañas",
    "ucontact": "Ucontact",
    "antivirus_setup": "Antivirus",
    "icbm_access": "IC Business Manager",
    "desktop_apps": "Aplicaciones de escritorio",
}


def migrate(cr, version):
    if not version:
        return
    _logger.info("Running post-migration script for custom_assistance_support module.")
    env = api.Environment(cr, SUPERUSER_ID, {})
    HelpdeskTicket = env["helpdesk.ticket"]

    result = HelpdeskTicket.search(
        [("x_studio_selection_field_1pr_1il3nn5q5", "!=", False)]
    )

    for ticket in result:
        studio_value_key = next(
            (
                k
                for k, v in MAPPING.items()
                if v == ticket.x_studio_selection_field_1pr_1il3nn5q5
            ),
            "",
        )
        request_type = env.ref(
            "custom_assistance_support.%s" % studio_value_key, raise_if_not_found=False
        )
        _logger.info(
            f"""mapping => {ticket.x_studio_selection_field_1pr_1il3nn5q5} to
            {studio_value_key} and request_type: {request_type}"""
        )
        if request_type:
            ticket.request_type_id = request_type.id
            _logger.info(
                f"Ticket {ticket.id} updated with request type '{studio_value_key}'."
            )
        else:
            _logger.warning(
                f"Request type not found for{studio_value_key} (Ticket ID: {ticket.id})"
            )

    _logger.info("Post-migration script completed.")

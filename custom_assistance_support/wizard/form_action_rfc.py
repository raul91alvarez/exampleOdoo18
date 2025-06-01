# -*- coding: utf-8 -*-
import base64
from datetime import datetime

from odoo import _, fields, models
from odoo.api import UserError


class FormActionRfcWizard(models.TransientModel):
    _name = "form.action.rfc.wizard"
    _description = "Wizard for RFC Form Action"

    option = fields.Selection(
        [
            ("normal", "Normal"),
            ("urgent", "Urgente"),
        ],
        string="Elegir opción",
        required=True,
        default="normal",
    )
    ticket_id = fields.Many2one("helpdesk.ticket", string="Ticket")

    # form 1
    id_change_f1 = fields.Integer(string="ID de cambio de infraestructura")
    campo_a2 = fields.Integer(string="CI de servicio")
    campo_a3 = fields.Char(string="Resumen")
    campo_a4 = fields.Char(string="Fase de autorización")
    campo_a5 = fields.Char(string="Remitente")
    campo_a6 = fields.Date(string="Fecha programada de inicio")
    campo_a7 = fields.Date(string="Fecha programada de finalización")
    campo_a8 = fields.Date(string="Fecha deseada")
    campo_a9 = fields.Char(string="Clase")
    campo_a10 = fields.Char(string="Nivel de riesgo")
    campo_a11 = fields.Char(string="Prioridad")
    campo_a12 = fields.Char(string="Impacto")
    campo_a13 = fields.Char(string="Urgencia")
    campo_a14 = fields.Char(string="Motivo de planificación")
    campo_a15 = fields.Char(string="Estatus")
    campo_a16 = fields.Char(string="Motivo del estatus")
    campo_a17 = fields.Char(string="Gestor de cambios")
    campo_a18 = fields.Char(string="Coordinador de cambios")
    campo_a19 = fields.Char(string="Empresas Ubicaciones")
    # form 2
    type_change_f2 = fields.Char(string="Tipo de cambio")
    campo_b2 = fields.Char(string="Solicitante")
    campo_b3 = fields.Datetime(string="Fecha y hora de implementación")
    campo_b4 = fields.Text(string="¿Cuál es el cambio? / Descripción detallada:")
    campo_b5 = fields.Text(
        string=(
            "¿Por qué esta solicitud de cambio? / "
            "Impacto empresarial si este trabajo no se realiza:"
        )
    )
    campo_b6 = fields.Text(
        string=(
            "Impacto / Riesgo del Negocio (indique el SLA afectado si es posible, "
            "indique historial de riesgo si lo hay):"
        )
    )
    campo_b7 = fields.Text(
        string="¿Cuál es el impacto de no realizar el cambio como una solicitud urgente?"
    )
    campo_b8 = fields.Text(
        string="¿Quién participó en la revisión técnica (nombres de los aprobadores)?"
    )
    campo_b9 = fields.Text(
        string=(
            "¿Qué riesgo potencial se está introduciendo en el entorno mientras se "
            "realiza el cambio solicitado? ¿Qué pruebas se han completado y qué "
            "opciones de retroceso / respaldo existen?"
        )
    )
    campo_b10 = fields.Selection(
        [
            ("si", "Sí"),
            ("no", "No"),
        ],
        string="¿Se han asignado los recursos para este trabajo?",
    )

    def action_confirm(self):
        self.ensure_one()

        if self.option == "normal":
            report_data = {
                "id_change_f1": self.id_change_f1,
                "campo_a2": self.campo_a2,
                "campo_a3": self.campo_a3,
                "campo_a4": self.campo_a4,
                "campo_a5": self.campo_a5,
                "campo_a6": self.campo_a6,
                "campo_a7": self.campo_a7,
                "campo_a8": self.campo_a8,
                "campo_a9": self.campo_a9,
                "campo_a10": self.campo_a10,
                "campo_a11": self.campo_a11,
                "campo_a12": self.campo_a12,
                "campo_a13": self.campo_a13,
                "campo_a14": self.campo_a14,
                "campo_a15": self.campo_a15,
                "campo_a16": self.campo_a16,
                "campo_a17": self.campo_a17,
                "campo_a18": self.campo_a18,
                "campo_a19": self.campo_a19,
            }
            id_report_name = "action_report_normal_rfc_wizard"
        if self.option == "urgent":
            report_data = {
                "type_change_f2": self.type_change_f2,
                "campo_b2": self.campo_b2,
                "campo_b3": self.campo_b3,
                "campo_b4": self.campo_b4,
                "campo_b5": self.campo_b5,
                "campo_b6": self.campo_b6,
                "campo_b7": self.campo_b7,
                "campo_b8": self.campo_b8,
                "campo_b9": self.campo_b9,
                "campo_b10": self.campo_b10,
            }
            id_report_name = "action_report_urgent_rfc_wizard"

        pdf = self.env["ir.actions.report"]._render_qweb_pdf(
            "custom_assistance_support.%s" % id_report_name,
            self.id,
            data={"docs": [report_data]},
        )[0]

        if not pdf:
            raise UserError(_("No se pudo generar el PDF."))

        fecha = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.env["ir.attachment"].create(
            {
                "name": f"Reporte_RFC_{self.option}_{fecha}.pdf",
                "type": "binary",
                "datas": base64.b64encode(pdf),
                "res_model": "helpdesk.ticket",  # Modelo del ticket
                "res_id": self.ticket_id.id,  # ID del ticket
                "mimetype": "application/pdf",
            }
        )

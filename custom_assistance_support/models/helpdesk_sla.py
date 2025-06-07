# -*- coding: utf-8 -*-
import json
import logging
import os

from odoo import _, api, fields, models
from odoo.api import UserError

_logger = logging.getLogger(__name__)


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
    ticket_category_ids = fields.Many2many(
        comodel_name="ticket.category.type",
        relation="helpdesk_sla_ticket_category_rel",
        column1="sla_id",
        column2="ticket_category_id",
        string="Category Types",
        help="Category types to which this SLA applies.",
    )

    @api.model
    def load_sla_from_gira(self):
        # Ruta absoluta al JSON (ajústala según la ubicación real en tu módulo)
        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "data",
            "sla.json",
        )
        json_path = os.path.normpath(json_path)

        if not os.path.exists(json_path):
            raise UserError(
                _("No se encontró el archivo sla.json en la ruta esperada: %s")
                % json_path
            )

        with open(json_path, "r", encoding="utf-8") as f:
            sla_data = json.load(f)

        for item in sla_data.get("data", []):

            # Preparar datos base
            vals = {
                "name": item["name"],
                # 'working_hours_id': calendar.id,
                "time": float(item["time"]),
                "team_id": item.get("team", False),
            }

            # Prioridad: convertir de string a int si existe
            if item.get("priority") not in (False, None):
                vals["priority"] = str(item["priority"])

            # Si el SLA depende de un estado específico
            if item.get("status"):
                stage = (
                    self.env["helpdesk.stage"]
                    .with_context(lang="es_UY")
                    .search([("name", "=", item["status"])], limit=1)
                )
                if stage:
                    vals["stage_id"] = stage.id
                else:
                    raise UserError(_("Etapa no encontrada: %s") % item["status"])

            # Si tiene categoría, la guardamos como un campo ticket_category_id
            if item.get("category"):
                category = self.env.ref(
                    "custom_assistance_support.%s" % item["category"],
                    raise_if_not_found=False,
                )
                if category:
                    vals["ticket_category_ids"] = [(6, 0, category.ids)]
                else:
                    raise UserError(_("Categoría no encontrada: %s") % item["category"])

            # Si tiene tipos de solicitud
            if item.get("request_types"):
                request_types = self.env["request.type"].search(
                    [("name", "in", item["request_types"])]
                )
                if request_types:
                    vals["request_type_ids"] = [(6, 0, request_types.ids)]
                else:
                    raise UserError(
                        _("Tipos de solicitud no encontrados: %s")
                        % ", ".join(item["request_types"])
                    )

            # Crear SLA
            existing = self.env["helpdesk.sla"].search(
                [("name", "=", item["name"])], limit=1
            )
            if existing:
                existing.write(vals)
                self.env.cr.commit()
                _logger.info("Actualizado SLA existente: %s", item["name"])
            else:
                self.create(vals)
                self.env.cr.commit()
                _logger.info("Creado SLA: %s", item["name"])

        _logger.info("Carga de SLA desde Jira completada.")

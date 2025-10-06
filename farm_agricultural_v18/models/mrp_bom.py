# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    # Campo adicional para identificar planes de labores agrícolas
    is_agricultural_plan = fields.Boolean(
        string='Es Plan de Labores Agrícola',
        default=True,
        help="Indica si esta lista de materiales es un plan de labores agrícola"
    )
    
    crop_type = fields.Selection([
        ('cereal', 'Cereal'),
        ('oilseed', 'Oleaginosa'),
        ('legume', 'Leguminosa'),
        ('pasture', 'Pastura'),
        ('verdeo', 'Verdeo'),
        ('other', 'Otro')
    ], string='Tipo de Cultivo', help="Tipo de cultivo para este plan de labores")
    
    recommended_area_min = fields.Float(
        string='Área Mínima Recomendada (ha)',
        help="Área mínima recomendada para este plan de labores"
    )
    
    recommended_area_max = fields.Float(
        string='Área Máxima Recomendada (ha)',
        help="Área máxima recomendada para este plan de labores"
    )
    
    notes = fields.Text(
        string='Observaciones del Plan',
        help="Notas adicionales sobre el plan de labores"
    )


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    # Campos específicos para insumos agrícolas
    application_date = fields.Date(
        string='Fecha de Aplicación Planificada',
        help="Fecha planificada para la aplicación de este insumo"
    )
    
    cost_per_hectare = fields.Float(
        string='Costo por Hectárea',
        compute='_compute_cost_per_hectare',
        store=True,
        help="Costo por hectárea basado en la cantidad y precio del insumo"
    )
    
    application_stage = fields.Selection([
        ('pre_planting', 'Pre-Siembra'),
        ('planting', 'Siembra'),
        ('post_planting', 'Post-Siembra'),
        ('growth', 'Crecimiento'),
        ('flowering', 'Floración'),
        ('harvest', 'Cosecha')
    ], string='Etapa de Aplicación', help="Etapa del cultivo en la que se aplica")
    
    application_method = fields.Selection([
        ('broadcasting', 'Voleo'),
        ('spraying', 'Pulverización'),
        ('injection', 'Inyección'),
        ('incorporation', 'Incorporación'),
        ('foliar', 'Aplicación Foliar'),
        ('seed_treatment', 'Tratamiento de Semilla')
    ], string='Método de Aplicación', help="Método de aplicación del insumo")
    
    dose_per_hectare = fields.Float(
        string='Dosis por Hectárea',
        help="Dosis recomendada por hectárea"
    )
    
    dose_unit = fields.Selection([
        ('kg', 'Kilogramos'),
        ('l', 'Litros'),
        ('g', 'Gramos'),
        ('ml', 'Mililitros'),
        ('units', 'Unidades')
    ], string='Unidad de Dosis', default='kg')
    
    is_critical = fields.Boolean(
        string='Es Crítico',
        help="Indica si este insumo es crítico para el éxito del cultivo"
    )
    
    weather_dependent = fields.Boolean(
        string='Dependiente del Clima',
        help="Indica si la aplicación depende de condiciones climáticas específicas"
    )

    @api.depends('product_qty', 'product_id.standard_price', 'bom_id.product_qty')
    def _compute_cost_per_hectare(self):
        """Calcula el costo por hectárea del insumo"""
        for line in self:
            if line.product_id and line.product_id.standard_price:
                # Costo total del insumo para la cantidad de la BOM
                total_cost = line.product_qty * line.product_id.standard_price
                
                # Si la BOM tiene una cantidad (área base), calculamos por hectárea
                if line.bom_id.product_qty and line.bom_id.product_qty > 0:
                    line.cost_per_hectare = total_cost / line.bom_id.product_qty
                else:
                    # Asumimos 1 hectárea como base
                    line.cost_per_hectare = total_cost
            else:
                line.cost_per_hectare = 0

    @api.onchange('dose_per_hectare', 'dose_unit')
    def _onchange_dose_per_hectare(self):
        """Actualiza la cantidad del producto basada en la dosis por hectárea"""
        if self.dose_per_hectare and self.bom_id.product_qty:
            # Calculamos la cantidad total basada en la dosis y el área base de la BOM
            area = self.bom_id.product_qty or 1  # Default a 1 hectárea
            self.product_qty = self.dose_per_hectare * area

    @api.constrains('application_date', 'bom_id')
    def _check_application_date_sequence(self):
        """Valida que las fechas de aplicación estén en secuencia lógica"""
        for line in self:
            if line.application_date and line.bom_id:
                # Obtener todas las líneas de la misma BOM con fechas
                dated_lines = line.bom_id.bom_line_ids.filtered('application_date').sorted('application_date')
                
                # Verificar que las etapas estén en orden lógico
                stage_order = ['pre_planting', 'planting', 'post_planting', 'growth', 'flowering', 'harvest']
                prev_stage_index = -1
                
                for dated_line in dated_lines:
                    if dated_line.application_stage:
                        current_stage_index = stage_order.index(dated_line.application_stage)
                        if current_stage_index < prev_stage_index:
                            raise ValidationError(
                                f"Las etapas de aplicación deben estar en orden cronológico: "
                                f"{' → '.join(stage_order)}"
                            )
                        prev_stage_index = current_stage_index

    def name_get(self):
        """Personaliza la representación del nombre de la línea"""
        result = []
        for line in self:
            name = f"{line.product_id.name}"
            if line.application_stage:
                name += f" ({dict(line._fields['application_stage'].selection)[line.application_stage]})"
            if line.dose_per_hectare and line.dose_unit:
                name += f" - {line.dose_per_hectare} {line.dose_unit}/ha"
            result.append((line.id, name))
        return result
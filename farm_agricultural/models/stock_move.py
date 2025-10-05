# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    # Campos específicos para aplicaciones agrícolas
    application_date = fields.Date(
        string='Fecha de Aplicación Real',
        help="Fecha real en que se aplicó el insumo"
    )
    
    cost_per_hectare = fields.Float(
        string='Costo por Hectárea Aplicado',
        compute='_compute_cost_per_hectare_applied',
        store=True,
        help="Costo por hectárea basado en la cantidad real aplicada"
    )
    
    applied_dose_per_hectare = fields.Float(
        string='Dosis Real Aplicada por Hectárea',
        compute='_compute_applied_dose_per_hectare',
        store=True,
        help="Dosis real aplicada por hectárea"
    )
    
    # Campos relacionados de la orden de producción agrícola
    production_field_id = fields.Many2one(
        'farm.field',
        string='Campo',
        related='production_id.field_id',
        store=True
    )
    
    production_lot_id = fields.Many2one(
        'farm.lot',
        string='Lote',
        related='production_id.lot_id',
        store=True
    )
    
    production_area = fields.Float(
        string='Área de la Campaña',
        related='production_id.area',
        store=True
    )
    
    # Información adicional de aplicación
    application_weather = fields.Text(
        string='Condiciones Climáticas',
        help="Condiciones climáticas durante la aplicación"
    )
    
    application_equipment = fields.Char(
        string='Equipo Utilizado',
        help="Equipo o maquinaria utilizada para la aplicación"
    )
    
    operator_id = fields.Many2one(
        'res.partner',
        string='Operador',
        help="Persona que realizó la aplicación"
    )
    
    application_notes = fields.Text(
        string='Notas de Aplicación',
        help="Observaciones adicionales sobre la aplicación"
    )
    
    # Estado de la aplicación
    application_state = fields.Selection([
        ('planned', 'Planificada'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada')
    ], string='Estado de Aplicación', default='planned')

    @api.depends('quantity_done', 'price_unit', 'production_area')
    def _compute_cost_per_hectare_applied(self):
        """Calcula el costo por hectárea basado en la cantidad real aplicada"""
        for move in self:
            if move.production_area and move.production_area > 0:
                total_cost = move.quantity_done * move.price_unit
                move.cost_per_hectare = total_cost / move.production_area
            else:
                move.cost_per_hectare = 0

    @api.depends('quantity_done', 'production_area')
    def _compute_applied_dose_per_hectare(self):
        """Calcula la dosis real aplicada por hectárea"""
        for move in self:
            if move.production_area and move.production_area > 0:
                move.applied_dose_per_hectare = move.quantity_done / move.production_area
            else:
                move.applied_dose_per_hectare = 0

    @api.onchange('application_date')
    def _onchange_application_date(self):
        """Al cambiar la fecha de aplicación, actualiza la fecha del movimiento"""
        if self.application_date:
            self.date = self.application_date

    def action_mark_application_completed(self):
        """Marca la aplicación como completada"""
        self.ensure_one()
        self.application_state = 'completed'
        if not self.application_date:
            self.application_date = fields.Date.today()

    def action_mark_application_cancelled(self):
        """Marca la aplicación como cancelada"""
        self.ensure_one()
        self.application_state = 'cancelled'

    @api.constrains('quantity_done', 'bom_line_id')
    def _check_dose_variance(self):
        """Valida que la dosis aplicada no exceda significativamente la planificada"""
        for move in self:
            if move.bom_line_id and move.bom_line_id.dose_per_hectare and move.production_area:
                planned_total = move.bom_line_id.dose_per_hectare * move.production_area
                applied_total = move.quantity_done
                
                # Permitir hasta 20% de variación
                max_allowed = planned_total * 1.2
                min_allowed = planned_total * 0.8
                
                if applied_total > max_allowed:
                    raise ValidationError(
                        f"La cantidad aplicada ({applied_total:.2f}) excede significativamente "
                        f"la dosis planificada ({planned_total:.2f}). "
                        f"Máximo permitido: {max_allowed:.2f}"
                    )
                elif applied_total < min_allowed and move.state == 'done':
                    # Solo advertir si el movimiento está completado
                    pass  # Se podría implementar una advertencia aquí

    def write(self, vals):
        """Override write para actualizar estado de aplicación"""
        result = super(StockMove, self).write(vals)
        
        # Si se actualiza quantity_done y no está marcada como completada
        if 'quantity_done' in vals:
            for move in self:
                if move.quantity_done > 0 and move.application_state == 'planned':
                    move.application_state = 'in_progress'
                elif move.quantity_done == move.product_uom_qty and move.application_state == 'in_progress':
                    move.application_state = 'completed'
        
        return result

    def name_get(self):
        """Personaliza la representación del nombre del movimiento"""
        result = []
        for move in self:
            name = f"{move.product_id.name}"
            if move.production_lot_id:
                name += f" - {move.production_lot_id.name}"
            if move.application_date:
                name += f" ({move.application_date})"
            result.append((move.id, name))
        return result


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    # Campos adicionales para el detalle de aplicación
    application_sector = fields.Char(
        string='Sector del Lote',
        help="Sector específico del lote donde se aplicó"
    )
    
    gps_coordinates = fields.Char(
        string='Coordenadas GPS',
        help="Coordenadas GPS donde se realizó la aplicación"
    )
    
    soil_condition = fields.Selection([
        ('dry', 'Seco'),
        ('moist', 'Húmedo'),
        ('wet', 'Mojado'),
        ('flooded', 'Anegado')
    ], string='Condición del Suelo')
    
    wind_speed = fields.Float(
        string='Velocidad del Viento (km/h)',
        help="Velocidad del viento durante la aplicación"
    )
    
    temperature = fields.Float(
        string='Temperatura (°C)',
        help="Temperatura durante la aplicación"
    )
    
    humidity = fields.Float(
        string='Humedad (%)',
        help="Humedad relativa durante la aplicación"
    )
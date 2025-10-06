# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    # Campos específicos para agricultura
    field_id = fields.Many2one(
        'farm.field',
        string='Campo',
        required=True,
        help="Campo donde se realizará el cultivo"
    )
    
    lot_id = fields.Many2one(
        'farm.lot',
        string='Lote',
        required=True,
        help="Lote específico donde se realizará el cultivo"
    )
    
    crop_id = fields.Many2one(
        'product.product',
        string='Cultivo/Semilla',
        help="Semilla que se siembra (producto a producir)"
    )
    
    area = fields.Float(
        string='Área (ha)',
        required=True,
        help="Área afectada por la orden de cultivo"
    )
    
    # Fechas del ciclo agrícola
    date_fallow = fields.Date(
        string='Fecha de Barbecho',
        help="Fecha en que se realizó el barbecho del lote"
    )
    
    date_planting = fields.Date(
        string='Fecha de Siembra',
        help="Fecha en que se realizó la siembra"
    )
    
    date_harvest = fields.Date(
        string='Fecha de Cosecha',
        help="Fecha en que se realizó la cosecha"
    )
    
    # Datos de cosecha
    total_harvest_kg = fields.Float(
        string='Total Cosechado (kg)',
        help="Kilos totales cosechados al finalizar la campaña"
    )
    
    yield_per_hectare = fields.Float(
        string='Rendimiento por Hectárea (kg/ha)',
        compute='_compute_yield_per_hectare',
        store=True,
        help="Rendimiento calculado automáticamente"
    )
    
    # Tipo de cultivo
    is_pasture_or_verdeo = fields.Boolean(
        string='Es Pastura o Verdeo',
        help="Marcar si el cultivo es una pastura o verdeo (no genera producto en stock)"
    )
    
    asset_id = fields.Many2one(
        'account.asset',
        string='Activo Creado',
        readonly=True,
        help="Activo creado para pasturas o verdeos"
    )
    
    # Campos calculados adicionales
    campaign_duration = fields.Integer(
        string='Duración de Campaña (días)',
        compute='_compute_campaign_duration',
        help="Duración en días desde siembra hasta cosecha"
    )
    
    total_cost = fields.Float(
        string='Costo Total',
        compute='_compute_total_cost',
        store=True,
        help="Costo total de la campaña"
    )
    
    cost_per_hectare = fields.Float(
        string='Costo por Hectárea',
        compute='_compute_cost_per_hectare',
        store=True,
        help="Costo por hectárea de la campaña"
    )
    
    # Campos relacionados para facilitar búsquedas
    field_province_id = fields.Many2one(
        'res.country.state',
        string='Provincia',
        related='field_id.province_id',
        store=True
    )
    
    lot_aptitude = fields.Selection(
        related='lot_id.aptitude',
        string='Aptitud del Lote',
        store=True
    )

    @api.depends('total_harvest_kg', 'area')
    def _compute_yield_per_hectare(self):
        """Calcula el rendimiento por hectárea"""
        for record in self:
            if record.area > 0 and record.total_harvest_kg > 0:
                record.yield_per_hectare = record.total_harvest_kg / record.area
            else:
                record.yield_per_hectare = 0

    @api.depends('date_planting', 'date_harvest')
    def _compute_campaign_duration(self):
        """Calcula la duración de la campaña en días"""
        for record in self:
            if record.date_planting and record.date_harvest:
                delta = record.date_harvest - record.date_planting
                record.campaign_duration = delta.days
            else:
                record.campaign_duration = 0

    @api.depends('move_raw_ids.price_unit', 'move_raw_ids.move_line_ids.quantity')
    def _compute_total_cost(self):
        """Calcula el costo total de la campaña"""
        for record in self:
            total = 0
            for move in record.move_raw_ids:
                # En Odoo 18, quantity_done se calcula desde move_line_ids
                total_quantity = sum(move.move_line_ids.mapped('quantity'))
                if total_quantity > 0:
                    total += total_quantity * move.price_unit
            record.total_cost = total

    @api.depends('total_cost', 'area')
    def _compute_cost_per_hectare(self):
        """Calcula el costo por hectárea"""
        for record in self:
            if record.area > 0:
                record.cost_per_hectare = record.total_cost / record.area
            else:
                record.cost_per_hectare = 0

    @api.onchange('lot_id')
    def _onchange_lot_id(self):
        """Al cambiar el lote, autocompleta el campo y el área"""
        if self.lot_id:
            self.field_id = self.lot_id.field_id.id
            self.area = self.lot_id.area

    @api.onchange('field_id')
    def _onchange_field_id(self):
        """Al cambiar el campo, filtra los lotes disponibles"""
        if self.field_id:
            return {
                'domain': {
                    'lot_id': [('field_id', '=', self.field_id.id)]
                }
            }
        else:
            return {
                'domain': {
                    'lot_id': []
                }
            }

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Al cambiar el producto, establece el cultivo"""
        if self.product_id:
            self.crop_id = self.product_id.id
        super(MrpProduction, self)._onchange_product_id()

    @api.constrains('date_fallow', 'date_planting', 'date_harvest')
    def _check_dates_sequence(self):
        """Valida que las fechas estén en secuencia lógica"""
        for record in self:
            dates = []
            if record.date_fallow:
                dates.append(('barbecho', record.date_fallow))
            if record.date_planting:
                dates.append(('siembra', record.date_planting))
            if record.date_harvest:
                dates.append(('cosecha', record.date_harvest))
            
            # Ordenar por fecha
            dates.sort(key=lambda x: x[1])
            
            # Verificar secuencia
            expected_sequence = ['barbecho', 'siembra', 'cosecha']
            actual_sequence = [d[0] for d in dates]
            
            for i, date_type in enumerate(actual_sequence):
                expected_index = expected_sequence.index(date_type)
                if i != expected_index:
                    raise ValidationError(
                        f"Las fechas deben estar en secuencia: {' → '.join(expected_sequence)}"
                    )

    @api.constrains('area', 'lot_id')
    def _check_area_limit(self):
        """Valida que el área no exceda el área del lote"""
        for record in self:
            if record.lot_id and record.area > record.lot_id.area:
                raise ValidationError(
                    f"El área de la campaña ({record.area} ha) no puede ser mayor "
                    f"al área del lote ({record.lot_id.area} ha)."
                )

    def action_create_asset_for_pasture(self):
        """Crea un activo para pasturas o verdeos"""
        self.ensure_one()
        if not self.is_pasture_or_verdeo:
            raise ValidationError("Solo se pueden crear activos para pasturas o verdeos.")
        
        # Determinar años de depreciación
        if 'pastura' in self.product_id.name.lower():
            depreciation_years = 5
            asset_name = f"Pastura - {self.lot_id.name} - {self.name}"
        else:  # verdeo
            depreciation_years = 1
            asset_name = f"Verdeo - {self.lot_id.name} - {self.name}"
        
        # Crear el activo
        asset_vals = {
            'name': asset_name,
            'original_value': self.total_cost,
            'acquisition_date': self.date_planting or fields.Date.today(),
            'method_time': 'number',
            'method_number': depreciation_years,
            'method_period': '12',  # Mensual
            'state': 'open',
        }
        
        asset = self.env['account.asset'].create(asset_vals)
        self.asset_id = asset.id
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.asset',
            'res_id': asset.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def button_mark_done(self):
        """Override para manejar la finalización de campañas agrícolas"""
        result = super(MrpProduction, self).button_mark_done()
        
        # Si es pastura o verdeo, crear activo automáticamente
        for record in self:
            if record.is_pasture_or_verdeo and not record.asset_id:
                record.action_create_asset_for_pasture()
        
        return result

    def name_get(self):
        """Personaliza la representación del nombre"""
        result = []
        for record in self:
            name = record.name
            if record.lot_id:
                name += f" - {record.lot_id.name}"
            if record.crop_id:
                name += f" ({record.crop_id.name})"
            result.append((record.id, name))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        """Permite buscar por nombre, lote o cultivo"""
        args = args or []
        if name:
            args = [
                '|', '|', '|',
                ('name', operator, name),
                ('lot_id.name', operator, name),
                ('crop_id.name', operator, name),
                ('field_id.name', operator, name)
            ] + args
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)
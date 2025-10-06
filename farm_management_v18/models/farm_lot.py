# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import json


class FarmLot(models.Model):
    _name = 'farm.lot'
    _description = 'Lote de Campo'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'field_id, name'

    name = fields.Char(
        string='Nombre del Lote',
        required=True,
        help="Nombre o código del lote (Ej: 'Lote 3A')"
    )
    
    field_id = fields.Many2one(
        'farm.field',
        string='Campo',
        required=True,
        ondelete='cascade',
        help="Campo al que pertenece este lote"
    )
    
    area = fields.Float(
        string='Extensión (ha)',
        required=True,
        help="Extensión del lote en hectáreas"
    )
    
    geolocation_points = fields.Text(
        string='Puntos de Geolocalización',
        help="Coordenadas que definen el perímetro del lote (formato JSON)"
    )
    
    aptitude = fields.Selection([
        ('agriculture', 'Agrícola'),
        ('livestock', 'Ganadero'),
        ('mixed', 'Mixto')
    ], string='Aptitud del Suelo', help="Tipo de actividad más apropiada para este lote")
    
    # Campos adicionales útiles
    active = fields.Boolean(default=True)
    
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        related='field_id.company_id',
        store=True
    )
    
    # Campos relacionados del campo padre
    field_province_id = fields.Many2one(
        'res.country.state',
        string='Provincia del Campo',
        related='field_id.province_id',
        store=True
    )
    
    field_type = fields.Selection(
        related='field_id.field_type',
        string='Tipo de Campo',
        store=True
    )
    
    notes = fields.Text(string='Observaciones')
    
    @api.constrains('area')
    def _check_area_positive(self):
        """Valida que el área sea positiva"""
        for record in self:
            if record.area <= 0:
                raise ValidationError("El área del lote debe ser mayor a cero.")
    
    @api.constrains('name', 'field_id')
    def _check_unique_name_per_field(self):
        """Valida que no haya lotes con el mismo nombre en un campo"""
        for record in self:
            if record.field_id:
                existing = self.search([
                    ('name', '=', record.name),
                    ('field_id', '=', record.field_id.id),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(
                        f"Ya existe un lote con el nombre '{record.name}' "
                        f"en el campo '{record.field_id.name}'."
                    )
    
    def validate_geolocation_points(self):
        """Valida el formato JSON de los puntos de geolocalización"""
        for record in self:
            if record.geolocation_points:
                try:
                    json.loads(record.geolocation_points)
                except (ValueError, TypeError):
                    raise ValidationError(
                        "Los puntos de geolocalización deben estar en formato JSON válido."
                    )
    
    @api.model
    def create(self, vals):
        """Override create para validaciones adicionales"""
        record = super(FarmLot, self).create(vals)
        record.validate_geolocation_points()
        return record
    
    def write(self, vals):
        """Override write para validaciones adicionales"""
        result = super(FarmLot, self).write(vals)
        if 'geolocation_points' in vals:
            self.validate_geolocation_points()
        return result
    
    def name_get(self):
        """Personaliza la representación del nombre del lote"""
        result = []
        for record in self:
            name = f"{record.name}"
            if record.field_id:
                name = f"{record.field_id.name} - {record.name}"
            if record.area:
                name += f" ({record.area} ha)"
            result.append((record.id, name))
        return result
    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        """Permite buscar por nombre del lote o campo"""
        args = args or []
        if name:
            args = [
                '|',
                ('name', operator, name),
                ('field_id.name', operator, name)
            ] + args
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)
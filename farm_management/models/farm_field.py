# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import json


class FarmField(models.Model):
    _name = 'farm.field'
    _description = 'Campo Agropecuario'
    _order = 'name'

    name = fields.Char(
        string='Nombre del Campo',
        required=True,
        help="Nombre o identificador del campo (Ej: 'La Margarita')"
    )
    
    field_type = fields.Selection([
        ('own', 'Propio'),
        ('rented', 'Alquilado')
    ], string='Tipo de Tenencia', required=True, default='own')
    
    contract_id = fields.Many2one(
        'farm.contract',
        string='Contrato',
        help="Contrato de alquiler asociado al campo"
    )
    
    geolocation_points = fields.Text(
        string='Puntos de Geolocalización',
        help="Coordenadas geográficas que definen el perímetro del campo (formato JSON)"
    )
    
    lot_ids = fields.One2many(
        'farm.lot',
        'field_id',
        string='Lotes'
    )
    
    total_area = fields.Float(
        string='Extensión Total (ha)',
        compute='_compute_total_area',
        store=True,
        help="Extensión total calculada como suma de las áreas de los lotes"
    )
    
    province_id = fields.Many2one(
        'res.country.state',
        string='Provincia',
        required=True,
        domain=[('country_id.code', '=', 'AR')],
        help="Provincia donde se encuentra el campo"
    )
    
    department = fields.Char(
        string='Departamento/Partido',
        help="Departamento o partido administrativo"
    )
    
    location = fields.Char(
        string='Localidad',
        help="Localidad o paraje más cercano"
    )
    
    real_estate_id = fields.Char(
        string='Partida Inmobiliaria',
        help="Número de partida inmobiliaria"
    )
    
    # Campos adicionales útiles
    active = fields.Boolean(default=True)
    
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        default=lambda self: self.env.company
    )
    
    notes = fields.Text(string='Observaciones')
    
    @api.depends('lot_ids.area')
    def _compute_total_area(self):
        """Calcula el área total sumando las áreas de todos los lotes"""
        for record in self:
            record.total_area = sum(record.lot_ids.mapped('area'))
    
    @api.constrains('field_type', 'contract_id')
    def _check_contract_required(self):
        """Valida que los campos alquilados tengan un contrato asociado"""
        for record in self:
            if record.field_type == 'rented' and not record.contract_id:
                raise ValidationError(
                    "Los campos de tipo 'Alquilado' deben tener un contrato asociado."
                )
    
    @api.onchange('field_type')
    def _onchange_field_type(self):
        """Limpia el contrato cuando se cambia a campo propio"""
        if self.field_type == 'own':
            self.contract_id = False
    
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
        record = super(FarmField, self).create(vals)
        record.validate_geolocation_points()
        return record
    
    def write(self, vals):
        """Override write para validaciones adicionales"""
        result = super(FarmField, self).write(vals)
        if 'geolocation_points' in vals:
            self.validate_geolocation_points()
        return result
    
    def name_get(self):
        """Personaliza la representación del nombre del campo"""
        result = []
        for record in self:
            name = f"{record.name}"
            if record.province_id:
                name += f" ({record.province_id.name})"
            result.append((record.id, name))
        return result
    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        """Permite buscar por nombre del campo o provincia"""
        args = args or []
        if name:
            args = [
                '|',
                ('name', operator, name),
                ('province_id.name', operator, name)
            ] + args
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)
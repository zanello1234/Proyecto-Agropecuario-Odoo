# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SisaDeclarationSurfaceLine(models.Model):
    _name = 'sisa.declaration.surface.line'
    _description = 'Línea de Superficie SISA'
    _order = 'field_id, lot_id, crop_id'

    declaration_id = fields.Many2one(
        'sisa.declaration',
        string='Declaración SISA',
        required=True,
        ondelete='cascade'
    )
    
    crop_id = fields.Many2one(
        'product.product',
        string='Cultivo',
        required=True,
        help="Cultivo sembrado en el lote"
    )
    
    field_id = fields.Many2one(
        'farm.field',
        string='Campo',
        required=True,
        help="Campo donde se realizó la siembra"
    )
    
    lot_id = fields.Many2one(
        'farm.lot',
        string='Lote',
        required=True,
        help="Lote específico donde se sembró"
    )
    
    real_estate_id = fields.Char(
        string='Partida Inmobiliaria',
        readonly=True,
        help="Partida inmobiliaria del campo (campo relacionado)"
    )
    
    area = fields.Float(
        string='Superficie (ha)',
        required=True,
        digits=(16, 2),
        help="Superficie sembrada en hectáreas"
    )
    
    # Campos relacionados para facilitar la vista
    field_name = fields.Char(
        related='field_id.name',
        string='Nombre del Campo',
        readonly=True
    )
    
    lot_name = fields.Char(
        related='lot_id.name',
        string='Nombre del Lote',
        readonly=True
    )
    
    crop_name = fields.Char(
        related='crop_id.name',
        string='Nombre del Cultivo',
        readonly=True
    )
    
    lot_total_area = fields.Float(
        related='lot_id.area',
        string='Área Total del Lote',
        readonly=True
    )
    
    field_province = fields.Char(
        related='field_id.province_id.name',
        string='Provincia',
        readonly=True
    )
    
    field_type = fields.Selection(
        related='field_id.field_type',
        string='Tipo de Tenencia',
        readonly=True
    )
    
    # Campo para código AFIP del cultivo (si se necesita)
    afip_crop_code = fields.Char(
        string='Código AFIP Cultivo',
        help="Código del cultivo según nomenclatura AFIP"
    )
    
    company_id = fields.Many2one(
        related='declaration_id.company_id',
        string='Compañía',
        readonly=True,
        store=True
    )
    
    # Campos adicionales para información SISA
    planting_date = fields.Date(
        string='Fecha de Siembra',
        help="Fecha de siembra del cultivo"
    )
    
    expected_harvest_date = fields.Date(
        string='Fecha Estimada de Cosecha',
        help="Fecha estimada de cosecha"
    )

    @api.constrains('area')
    def _check_area(self):
        """Validate area is positive and not greater than lot area"""
        for record in self:
            if record.area <= 0:
                raise ValidationError("El área debe ser mayor a cero")
            
            if record.lot_id and record.area > record.lot_id.area:
                raise ValidationError(
                    f"El área sembrada ({record.area} ha) no puede ser mayor "
                    f"al área total del lote ({record.lot_id.area} ha)"
                )

    @api.constrains('lot_id', 'field_id')
    def _check_lot_belongs_to_field(self):
        """Validate that lot belongs to the selected field"""
        for record in self:
            if record.lot_id and record.field_id:
                if record.lot_id.field_id != record.field_id:
                    raise ValidationError(
                        f"El lote {record.lot_id.name} no pertenece al campo {record.field_id.name}"
                    )

    @api.onchange('field_id')
    def _onchange_field_id(self):
        """Update domain for lot_id when field changes"""
        if self.field_id:
            self.real_estate_id = self.field_id.real_estate_id or ''
            return {
                'domain': {
                    'lot_id': [('field_id', '=', self.field_id.id)]
                }
            }
        else:
            self.real_estate_id = ''
            return {
                'domain': {
                    'lot_id': []
                }
            }

    @api.onchange('lot_id')
    def _onchange_lot_id(self):
        """Update area when lot changes"""
        if self.lot_id:
            # Suggest the full lot area as default
            self.area = self.lot_id.area

    @api.onchange('crop_id')
    def _onchange_crop_id(self):
        """Set AFIP code when crop changes"""
        if self.crop_id:
            # Try to get AFIP code from product (if configured)
            self.afip_crop_code = self.crop_id.default_code or ''

    def name_get(self):
        """Custom name_get for better display"""
        result = []
        for record in self:
            name = f"{record.field_name} - {record.lot_name} - {record.crop_name} ({record.area:,.1f} ha)"
            result.append((record.id, name))
        return result

    @api.model
    def create(self, vals):
        """Override create to set real_estate_id"""
        if vals.get('field_id'):
            field = self.env['farm.field'].browse(vals['field_id'])
            vals['real_estate_id'] = field.real_estate_id or ''
        return super().create(vals)

    def write(self, vals):
        """Override write to update real_estate_id when field changes"""
        if vals.get('field_id'):
            field = self.env['farm.field'].browse(vals['field_id'])
            vals['real_estate_id'] = field.real_estate_id or ''
        return super().write(vals)
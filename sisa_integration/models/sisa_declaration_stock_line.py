# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SisaDeclarationStockLine(models.Model):
    _name = 'sisa.declaration.stock.line'
    _description = 'Línea de Existencias SISA'
    _order = 'product_id, location_id'

    declaration_id = fields.Many2one(
        'sisa.declaration',
        string='Declaración SISA',
        required=True,
        ondelete='cascade'
    )
    
    product_id = fields.Many2one(
        'product.product',
        string='Grano',
        required=True,
        domain="[('categ_id.name', 'ilike', 'grano')]",
        help="Producto de grano de producción propia"
    )
    
    quantity_kg = fields.Float(
        string='Cantidad (kg)',
        required=True,
        digits=(16, 2),
        help="Kilos totales en stock del grano"
    )
    
    location_id = fields.Many2one(
        'stock.location',
        string='Ubicación/Depósito',
        required=True,
        domain="[('usage', '=', 'internal')]",
        help="Ubicación donde se encuentra almacenado el grano"
    )
    
    # Campos relacionados para facilitar la vista
    product_name = fields.Char(
        related='product_id.name',
        string='Nombre del Producto',
        readonly=True
    )
    
    location_name = fields.Char(
        related='location_id.complete_name',
        string='Ubicación Completa',
        readonly=True
    )
    
    # Campo para código AFIP del producto (si se necesita)
    afip_code = fields.Char(
        string='Código AFIP',
        help="Código del producto según nomenclatura AFIP"
    )
    
    company_id = fields.Many2one(
        related='declaration_id.company_id',
        string='Compañía',
        readonly=True,
        store=True
    )

    @api.constrains('quantity_kg')
    def _check_quantity(self):
        """Validate quantity is positive"""
        for record in self:
            if record.quantity_kg < 0:
                raise ValidationError("La cantidad no puede ser negativa")

    @api.constrains('product_id', 'location_id', 'declaration_id')
    def _check_unique_product_location(self):
        """Ensure unique product-location combination per declaration"""
        for record in self:
            existing = self.search([
                ('declaration_id', '=', record.declaration_id.id),
                ('product_id', '=', record.product_id.id),
                ('location_id', '=', record.location_id.id),
                ('id', '!=', record.id)
            ])
            if existing:
                raise ValidationError(
                    f"Ya existe una línea para el producto {record.product_id.name} "
                    f"en la ubicación {record.location_id.name}"
                )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Set AFIP code when product changes"""
        if self.product_id:
            # Try to get AFIP code from product (if configured)
            self.afip_code = self.product_id.default_code or ''

    def name_get(self):
        """Custom name_get for better display"""
        result = []
        for record in self:
            product_name = record.product_id.name if record.product_id else 'Sin producto'
            location_name = record.location_id.name if record.location_id else 'Sin ubicación'
            name = f"{product_name} - {location_name} ({record.quantity_kg:,.0f} kg)"
            result.append((record.id, name))
        return result
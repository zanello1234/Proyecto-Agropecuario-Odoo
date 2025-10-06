# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date
import logging

_logger = logging.getLogger(__name__)


class SisaIp1Wizard(models.TransientModel):
    _name = 'sisa.ip1.wizard'
    _description = 'Asistente para Generación de Declaración IP1'

    year = fields.Integer(
        string='Año de Campaña',
        required=True,
        default=lambda self: datetime.now().year,
        help="Año de la campaña fina"
    )
    
    stock_cutoff_date = fields.Date(
        string='Fecha de Corte de Stock',
        required=True,
        help="Fecha de corte para el cálculo de existencias"
    )
    
    state = fields.Selection([
        ('init', 'Inicial'),
        ('stock_preview', 'Vista Previa Stock'),
        ('surface_preview', 'Vista Previa Superficie'),
        ('confirm', 'Confirmar')
    ], default='init', string='Estado')
    
    # Líneas de vista previa
    preview_stock_line_ids = fields.One2many(
        'sisa.ip1.wizard.stock.line',
        'wizard_id',
        string='Vista Previa - Existencias'
    )
    
    preview_surface_line_ids = fields.One2many(
        'sisa.ip1.wizard.surface.line',
        'wizard_id',
        string='Vista Previa - Superficie'
    )
    
    # Campos informativos
    total_stock_kg = fields.Float(
        string='Total Stock (kg)',
        compute='_compute_totals'
    )
    
    total_surface_ha = fields.Float(
        string='Total Superficie (ha)',
        compute='_compute_totals'
    )
    
    declaration_id = fields.Many2one(
        'sisa.declaration',
        string='Declaración Creada',
        readonly=True
    )

    @api.depends('preview_stock_line_ids.quantity_kg', 'preview_surface_line_ids.area')
    def _compute_totals(self):
        """Compute totals from preview lines"""
        for wizard in self:
            wizard.total_stock_kg = sum(wizard.preview_stock_line_ids.mapped('quantity_kg'))
            wizard.total_surface_ha = sum(wizard.preview_surface_line_ids.mapped('area'))

    @api.onchange('year')
    def _onchange_year(self):
        """Set default cutoff date when year changes"""
        if self.year:
            self.stock_cutoff_date = date(self.year, 9, 30)

    def action_calculate_stock(self):
        """Calculate stock and show preview"""
        self.ensure_one()
        
        # Clear existing preview lines
        self.preview_stock_line_ids.unlink()
        
        # Get grain products configuration
        grain_config = self.env['sisa.campaign.config'].search([
            ('campaign_type', '=', 'grain'),
            ('active', '=', True)
        ])
        
        if not grain_config:
            raise UserError(
                "No se encontró configuración de granos. "
                "Configure los productos de granos en SISA > Configuración"
            )
        
        grain_products = grain_config.mapped('product_ids')
        
        # Find stock quants for grain products
        own_locations = self.env['stock.location'].search([
            ('usage', '=', 'internal'),
            ('company_id', '=', self.env.company.id)
        ])
        
        quants = self.env['stock.quant'].search([
            ('product_id', 'in', grain_products.ids),
            ('location_id', 'in', own_locations.ids),
            ('quantity', '>', 0)
        ])
        
        # Group by product and location
        stock_data = {}
        for quant in quants:
            key = (quant.product_id.id, quant.location_id.id)
            if key not in stock_data:
                stock_data[key] = 0
            stock_data[key] += quant.quantity
        
        # Create preview lines
        for (product_id, location_id), quantity in stock_data.items():
            self.env['sisa.ip1.wizard.stock.line'].create({
                'wizard_id': self.id,
                'product_id': product_id,
                'location_id': location_id,
                'quantity_kg': quantity
            })
        
        self.state = 'stock_preview'
        return self._return_wizard_action()

    def action_calculate_surface(self):
        """Calculate surface and show preview"""
        self.ensure_one()
        
        # Clear existing preview lines
        self.preview_surface_line_ids.unlink()
        
        # Get fine campaign products configuration
        fine_config = self.env['sisa.campaign.config'].search([
            ('campaign_type', '=', 'fine'),
            ('active', '=', True)
        ])
        
        if not fine_config:
            raise UserError(
                "No se encontró configuración de campaña fina. "
                "Configure los productos en SISA > Configuración"
            )
        
        fine_products = fine_config.mapped('product_ids')
        
        # Get planting period for fine campaign (May to August)
        start_date = date(self.year, 5, 1)
        end_date = date(self.year, 8, 31)
        
        # Search for agricultural productions in the period
        productions = self.env['mrp.production'].search([
            ('crop_id', 'in', fine_products.ids),
            ('date_planting', '>=', start_date),
            ('date_planting', '<=', end_date),
            ('state', '!=', 'cancel'),
            ('field_id.company_id', '=', self.env.company.id)
        ])
        
        # Create preview lines
        for production in productions:
            real_estate_id = production.field_id.real_estate_id or ''
            
            self.env['sisa.ip1.wizard.surface.line'].create({
                'wizard_id': self.id,
                'crop_id': production.crop_id.id,
                'field_id': production.field_id.id,
                'lot_id': production.lot_id.id,
                'real_estate_id': real_estate_id,
                'area': production.area,
                'planting_date': production.date_planting
            })
        
        self.state = 'surface_preview'
        return self._return_wizard_action()

    def action_back_to_stock(self):
        """Go back to stock preview"""
        self.state = 'stock_preview'
        return self._return_wizard_action()

    def action_confirm_creation(self):
        """Create the IP1 declaration"""
        self.ensure_one()
        
        # Check if declaration already exists
        existing = self.env['sisa.declaration'].search([
            ('declaration_type', '=', 'ip1'),
            ('year', '=', self.year),
            ('company_id', '=', self.env.company.id)
        ])
        
        if existing:
            raise UserError(
                f"Ya existe una declaración IP1 para el año {self.year}. "
                f"Elimine la existente si desea crear una nueva."
            )
        
        # Create declaration
        declaration_vals = {
            'declaration_type': 'ip1',
            'year': self.year,
            'stock_cutoff_date': self.stock_cutoff_date,
            'state': 'generated'
        }
        
        declaration = self.env['sisa.declaration'].create(declaration_vals)
        
        # Create stock lines
        for preview_line in self.preview_stock_line_ids:
            self.env['sisa.declaration.stock.line'].create({
                'declaration_id': declaration.id,
                'product_id': preview_line.product_id.id,
                'location_id': preview_line.location_id.id,
                'quantity_kg': preview_line.quantity_kg
            })
        
        # Create surface lines
        for preview_line in self.preview_surface_line_ids:
            self.env['sisa.declaration.surface.line'].create({
                'declaration_id': declaration.id,
                'crop_id': preview_line.crop_id.id,
                'field_id': preview_line.field_id.id,
                'lot_id': preview_line.lot_id.id,
                'real_estate_id': preview_line.real_estate_id,
                'area': preview_line.area,
                'planting_date': preview_line.planting_date
            })
        
        self.declaration_id = declaration.id
        self.state = 'confirm'
        
        return self._return_wizard_action()

    def action_view_declaration(self):
        """View created declaration"""
        self.ensure_one()
        if not self.declaration_id:
            raise UserError("No hay declaración creada")
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sisa.declaration',
            'res_id': self.declaration_id.id,
            'view_mode': 'form',
            'target': 'current'
        }

    def _return_wizard_action(self):
        """Return action to keep wizard open"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sisa.ip1.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new'
        }


class SisaIp1WizardStockLine(models.TransientModel):
    _name = 'sisa.ip1.wizard.stock.line'
    _description = 'Línea de Stock del Asistente IP1'

    wizard_id = fields.Many2one(
        'sisa.ip1.wizard',
        string='Asistente',
        required=True,
        ondelete='cascade'
    )
    
    product_id = fields.Many2one(
        'product.product',
        string='Grano',
        required=True
    )
    
    location_id = fields.Many2one(
        'stock.location',
        string='Ubicación',
        required=True
    )
    
    quantity_kg = fields.Float(
        string='Cantidad (kg)',
        required=True
    )


class SisaIp1WizardSurfaceLine(models.TransientModel):
    _name = 'sisa.ip1.wizard.surface.line'
    _description = 'Línea de Superficie del Asistente IP1'

    wizard_id = fields.Many2one(
        'sisa.ip1.wizard',
        string='Asistente',
        required=True,
        ondelete='cascade'
    )
    
    crop_id = fields.Many2one(
        'product.product',
        string='Cultivo',
        required=True
    )
    
    field_id = fields.Many2one(
        'farm.field',
        string='Campo',
        required=True
    )
    
    lot_id = fields.Many2one(
        'farm.lot',
        string='Lote',
        required=True
    )
    
    real_estate_id = fields.Char(
        string='Partida Inmobiliaria'
    )
    
    area = fields.Float(
        string='Superficie (ha)',
        required=True
    )
    
    planting_date = fields.Date(
        string='Fecha de Siembra'
    )
# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date
import logging

_logger = logging.getLogger(__name__)


class SisaIp2Wizard(models.TransientModel):
    _name = 'sisa.ip2.wizard'
    _description = 'Asistente para Generación de Declaración IP2'

    year = fields.Integer(
        string='Año de Campaña',
        required=True,
        default=lambda self: datetime.now().year,
        help="Año de inicio de la campaña gruesa (ej: 2025 para campaña 2025/2026)"
    )
    
    state = fields.Selection([
        ('init', 'Inicial'),
        ('surface_preview', 'Vista Previa Superficie'),
        ('confirm', 'Confirmar')
    ], default='init', string='Estado')
    
    # Líneas de vista previa
    preview_surface_line_ids = fields.One2many(
        'sisa.ip2.wizard.surface.line',
        'wizard_id',
        string='Vista Previa - Superficie'
    )
    
    # Campos informativos
    total_surface_ha = fields.Float(
        string='Total Superficie (ha)',
        compute='_compute_totals'
    )
    
    total_lots = fields.Integer(
        string='Total Lotes',
        compute='_compute_totals'
    )
    
    declaration_id = fields.Many2one(
        'sisa.declaration',
        string='Declaración Creada',
        readonly=True
    )
    
    # Información del período
    period_info = fields.Html(
        string='Información del Período',
        compute='_compute_period_info'
    )

    @api.depends('preview_surface_line_ids.area')
    def _compute_totals(self):
        """Compute totals from preview lines"""
        for wizard in self:
            wizard.total_surface_ha = sum(wizard.preview_surface_line_ids.mapped('area'))
            wizard.total_lots = len(wizard.preview_surface_line_ids)

    @api.depends('year')
    def _compute_period_info(self):
        """Compute period information"""
        for wizard in self:
            if wizard.year:
                start_date = date(wizard.year, 9, 1)
                end_date = date(wizard.year + 1, 2, 28)
                wizard.period_info = f"""
                <div class="alert alert-info">
                    <strong>Período de Campaña Gruesa {wizard.year}/{wizard.year + 1}:</strong><br/>
                    Desde: {start_date.strftime('%d/%m/%Y')}<br/>
                    Hasta: {end_date.strftime('%d/%m/%Y')}<br/>
                    <em>Se buscarán siembras realizadas en este período</em>
                </div>
                """
            else:
                wizard.period_info = ""

    def action_calculate_surface(self):
        """Calculate surface and show preview"""
        self.ensure_one()
        
        # Clear existing preview lines
        self.preview_surface_line_ids.unlink()
        
        # Get coarse campaign products configuration
        coarse_config = self.env['sisa.campaign.config'].search([
            ('campaign_type', '=', 'coarse'),
            ('active', '=', True)
        ])
        
        if not coarse_config:
            raise UserError(
                "No se encontró configuración de campaña gruesa. "
                "Configure los productos en SISA > Configuración"
            )
        
        coarse_products = coarse_config.mapped('product_ids')
        
        # Get planting period for coarse campaign (September to February)
        start_date = date(self.year, 9, 1)
        end_date = date(self.year + 1, 2, 28)
        
        # Search for agricultural productions in the period
        productions = self.env['mrp.production'].search([
            ('crop_id', 'in', coarse_products.ids),
            ('date_planting', '>=', start_date),
            ('date_planting', '<=', end_date),
            ('state', '!=', 'cancel'),
            ('field_id.company_id', '=', self.env.company.id)
        ])
        
        if not productions:
            raise UserError(
                f"No se encontraron siembras de campaña gruesa en el período "
                f"del {start_date.strftime('%d/%m/%Y')} al {end_date.strftime('%d/%m/%Y')}.\n\n"
                f"Verifique que:\n"
                f"• Las órdenes de cultivo tengan fecha de siembra en el período\n"
                f"• Los cultivos estén configurados como campaña gruesa\n"
                f"• Las órdenes no estén canceladas"
            )
        
        # Create preview lines
        for production in productions:
            real_estate_id = production.field_id.real_estate_id or ''
            
            self.env['sisa.ip2.wizard.surface.line'].create({
                'wizard_id': self.id,
                'crop_id': production.crop_id.id,
                'field_id': production.field_id.id,
                'lot_id': production.lot_id.id,
                'real_estate_id': real_estate_id,
                'area': production.area,
                'planting_date': production.date_planting,
                'production_id': production.id
            })
        
        self.state = 'surface_preview'
        return self._return_wizard_action()

    def action_back_to_init(self):
        """Go back to initial state"""
        self.state = 'init'
        return self._return_wizard_action()

    def action_confirm_creation(self):
        """Create the IP2 declaration"""
        self.ensure_one()
        
        if not self.preview_surface_line_ids:
            raise UserError("No hay líneas de superficie para generar la declaración")
        
        # Check if declaration already exists
        existing = self.env['sisa.declaration'].search([
            ('declaration_type', '=', 'ip2'),
            ('year', '=', self.year),
            ('company_id', '=', self.env.company.id)
        ])
        
        if existing:
            raise UserError(
                f"Ya existe una declaración IP2 para el año {self.year}/{self.year + 1}. "
                f"Elimine la existente si desea crear una nueva."
            )
        
        # Create declaration
        declaration_vals = {
            'declaration_type': 'ip2',
            'year': self.year,
            'state': 'generated'
        }
        
        declaration = self.env['sisa.declaration'].create(declaration_vals)
        
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

    def action_view_production(self):
        """View related production orders"""
        self.ensure_one()
        production_ids = self.preview_surface_line_ids.mapped('production_id.id')
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Órdenes de Cultivo Relacionadas',
            'res_model': 'mrp.production',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', production_ids)],
            'target': 'current'
        }

    def _return_wizard_action(self):
        """Return action to keep wizard open"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sisa.ip2.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new'
        }


class SisaIp2WizardSurfaceLine(models.TransientModel):
    _name = 'sisa.ip2.wizard.surface.line'
    _description = 'Línea de Superficie del Asistente IP2'

    wizard_id = fields.Many2one(
        'sisa.ip2.wizard',
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
    
    production_id = fields.Many2one(
        'mrp.production',
        string='Orden de Cultivo',
        help="Orden de cultivo de donde se obtuvo la información"
    )
    
    # Campos relacionados para mejor visualización
    field_name = fields.Char(
        related='field_id.name',
        string='Campo'
    )
    
    lot_name = fields.Char(
        related='lot_id.name',
        string='Lote'
    )
    
    crop_name = fields.Char(
        related='crop_id.name',
        string='Cultivo'
    )
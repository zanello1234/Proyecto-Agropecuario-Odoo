# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date
import logging

_logger = logging.getLogger(__name__)


class SisaDeclaration(models.Model):
    _name = 'sisa.declaration'
    _description = 'Declaración SISA'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'year desc, declaration_type'
    _rec_name = 'display_name'

    name = fields.Char(
        string='Nombre',
        required=True,
        readonly=True,
        help="Nombre autogenerado de la declaración"
    )
    
    display_name = fields.Char(
        string='Nombre para Mostrar',
        compute='_compute_display_name',
        store=True
    )
    
    declaration_type = fields.Selection([
        ('ip1', 'IP1 - Campaña Fina'),
        ('ip2', 'IP2 - Campaña Gruesa')
    ], string='Tipo de Declaración', required=True, tracking=True,
       help="IP1: Campaña Fina (Trigo, Cebada, Avena) / IP2: Campaña Gruesa (Soja, Maíz, Girasol)")
    
    year = fields.Integer(
        string='Año de Campaña',
        required=True,
        default=lambda self: datetime.now().year,
        tracking=True,
        help="Año de la campaña agrícola"
    )
    
    generation_date = fields.Datetime(
        string='Fecha de Generación',
        default=fields.Datetime.now,
        required=True,
        tracking=True,
        help="Fecha y hora en que se generó la declaración en Odoo"
    )
    
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('generated', 'Generado'),
        ('presented', 'Presentado')
    ], string='Estado', default='draft', required=True, tracking=True,
       help="Estado actual de la declaración")
    
    # Campos específicos para IP1
    stock_cutoff_date = fields.Date(
        string='Fecha de Corte de Stock',
        help="Fecha de corte para el cálculo de existencias (por defecto 30 de septiembre)"
    )
    
    stock_line_ids = fields.One2many(
        'sisa.declaration.stock.line',
        'declaration_id',
        string='Líneas de Existencias'
    )
    
    # Campo común para ambos tipos
    surface_line_ids = fields.One2many(
        'sisa.declaration.surface.line',
        'declaration_id',
        string='Líneas de Superficie'
    )
    
    # Campos computados para resúmenes
    total_stock_kg = fields.Float(
        string='Total Stock (kg)',
        compute='_compute_totals',
        store=True,
        help="Total de kilos en stock declarados"
    )
    
    total_surface_ha = fields.Float(
        string='Total Superficie (ha)',
        compute='_compute_totals',
        store=True,
        help="Total de hectáreas sembradas declaradas"
    )
    
    # Campos de control
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        default=lambda self: self.env.company,
        required=True
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='Usuario Responsable',
        default=lambda self: self.env.user,
        required=True,
        tracking=True
    )
    
    notes = fields.Text(
        string='Observaciones',
        help="Observaciones adicionales sobre la declaración"
    )
    
    exported_file_name = fields.Char(
        string='Archivo Exportado',
        readonly=True,
        help="Nombre del último archivo exportado"
    )
    
    export_date = fields.Datetime(
        string='Fecha de Exportación',
        readonly=True,
        help="Fecha de la última exportación"
    )

    @api.depends('declaration_type', 'year')
    def _compute_display_name(self):
        """Compute display name for the declaration"""
        for record in self:
            if record.declaration_type and record.year:
                type_name = dict(record._fields['declaration_type'].selection)[record.declaration_type]
                if record.declaration_type == 'ip2':
                    # IP2 abarca dos años (ej: 2025/2026)
                    record.display_name = f"{type_name} - {record.year}/{record.year + 1}"
                else:
                    record.display_name = f"{type_name} - {record.year}"
                record.name = record.display_name
            else:
                record.display_name = 'Nueva Declaración'
                record.name = 'Nueva Declaración'

    @api.depends('stock_line_ids.quantity_kg', 'surface_line_ids.area')
    def _compute_totals(self):
        """Compute total stock and surface"""
        for record in self:
            record.total_stock_kg = sum(record.stock_line_ids.mapped('quantity_kg'))
            record.total_surface_ha = sum(record.surface_line_ids.mapped('area'))

    @api.model
    def create(self, vals):
        """Override create to set default values based on declaration type"""
        if vals.get('declaration_type') == 'ip1' and not vals.get('stock_cutoff_date'):
            year = vals.get('year', datetime.now().year)
            vals['stock_cutoff_date'] = date(year, 9, 30)
        
        record = super().create(vals)
        record._compute_display_name()
        return record

    @api.constrains('year')
    def _check_year(self):
        """Validate year field"""
        for record in self:
            current_year = datetime.now().year
            if record.year < 2020 or record.year > current_year + 2:
                raise ValidationError(
                    f"El año de campaña debe estar entre 2020 y {current_year + 2}"
                )

    @api.constrains('declaration_type', 'year', 'company_id')
    def _check_unique_declaration(self):
        """Ensure only one declaration per type, year and company"""
        for record in self:
            existing = self.search([
                ('declaration_type', '=', record.declaration_type),
                ('year', '=', record.year),
                ('company_id', '=', record.company_id.id),
                ('id', '!=', record.id)
            ])
            if existing:
                type_name = dict(record._fields['declaration_type'].selection)[record.declaration_type]
                raise ValidationError(
                    f"Ya existe una declaración {type_name} para el año {record.year} "
                    f"en la compañía {record.company_id.name}"
                )

    def action_generate_ip1_lines(self):
        """Generate IP1 lines automatically"""
        self.ensure_one()
        if self.declaration_type != 'ip1':
            raise UserError("Esta acción solo es válida para declaraciones IP1")
        
        # Clear existing lines
        self.stock_line_ids.unlink()
        self.surface_line_ids.unlink()
        
        # Generate stock lines
        self._generate_stock_lines()
        
        # Generate surface lines for fine campaign
        self._generate_surface_lines_ip1()
        
        self.state = 'generated'
        return True

    def action_generate_ip2_lines(self):
        """Generate IP2 lines automatically"""
        self.ensure_one()
        if self.declaration_type != 'ip2':
            raise UserError("Esta acción solo es válida para declaraciones IP2")
        
        # Clear existing lines
        self.surface_line_ids.unlink()
        
        # Generate surface lines for coarse campaign
        self._generate_surface_lines_ip2()
        
        self.state = 'generated'
        return True

    def _generate_stock_lines(self):
        """Generate stock lines from inventory"""
        if not self.stock_cutoff_date:
            raise UserError("Debe especificar una fecha de corte para el stock")
        
        # Get grain products configuration
        grain_config = self.env['sisa.campaign.config'].search([
            ('campaign_type', '=', 'grain')
        ])
        
        if not grain_config:
            raise UserError(
                "No se encontró configuración de granos. "
                "Configure los productos de granos en SISA > Configuración"
            )
        
        grain_products = grain_config.mapped('product_ids')
        
        # Find stock quants for grain products
        # Filter by company owned locations
        own_locations = self.env['stock.location'].search([
            ('usage', '=', 'internal'),
            ('company_id', '=', self.company_id.id)
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
        
        # Create stock lines
        for (product_id, location_id), quantity in stock_data.items():
            self.env['sisa.declaration.stock.line'].create({
                'declaration_id': self.id,
                'product_id': product_id,
                'location_id': location_id,
                'quantity_kg': quantity
            })

    def _generate_surface_lines_ip1(self):
        """Generate surface lines for IP1 (fine campaign)"""
        # Get fine campaign products configuration
        fine_config = self.env['sisa.campaign.config'].search([
            ('campaign_type', '=', 'fine')
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
        
        self._create_surface_lines_from_productions(fine_products, start_date, end_date)

    def _generate_surface_lines_ip2(self):
        """Generate surface lines for IP2 (coarse campaign)"""
        # Get coarse campaign products configuration
        coarse_config = self.env['sisa.campaign.config'].search([
            ('campaign_type', '=', 'coarse')
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
        
        self._create_surface_lines_from_productions(coarse_products, start_date, end_date)

    def _create_surface_lines_from_productions(self, products, start_date, end_date):
        """Create surface lines from MRP productions"""
        # Search for agricultural productions in the period
        productions = self.env['mrp.production'].search([
            ('crop_id', 'in', products.ids),
            ('date_planting', '>=', start_date),
            ('date_planting', '<=', end_date),
            ('state', '!=', 'cancel'),
            ('field_id.company_id', '=', self.company_id.id)
        ])
        
        for production in productions:
            # Get real estate ID from field
            real_estate_id = production.field_id.real_estate_id or ''
            
            self.env['sisa.declaration.surface.line'].create({
                'declaration_id': self.id,
                'crop_id': production.crop_id.id,
                'field_id': production.field_id.id,
                'lot_id': production.lot_id.id,
                'real_estate_id': real_estate_id,
                'area': production.area
            })

    def action_mark_presented(self):
        """Mark declaration as presented"""
        self.ensure_one()
        if self.state != 'generated':
            raise UserError("Solo se pueden marcar como presentadas las declaraciones generadas")
        
        self.state = 'presented'
        return True

    def action_reset_to_draft(self):
        """Reset declaration to draft"""
        self.ensure_one()
        self.state = 'draft'
        return True

    def action_export_afip_file(self):
        """Export AFIP file"""
        self.ensure_one()
        if self.state == 'draft':
            raise UserError("Debe generar la declaración antes de exportar")
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sisa.export.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_declaration_id': self.id}
        }
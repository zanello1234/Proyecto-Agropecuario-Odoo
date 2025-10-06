# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SisaCampaignConfig(models.Model):
    _name = 'sisa.campaign.config'
    _description = 'Configuración de Campañas SISA'
    _order = 'campaign_type, sequence'

    name = fields.Char(
        string='Nombre',
        required=True,
        help="Nombre descriptivo de la configuración"
    )
    
    campaign_type = fields.Selection([
        ('fine', 'Campaña Fina'),
        ('coarse', 'Campaña Gruesa'),
        ('grain', 'Granos (Stock)')
    ], string='Tipo de Campaña', required=True,
       help="Tipo de campaña para la cual se configuran los productos")
    
    product_ids = fields.Many2many(
        'product.product',
        'sisa_campaign_product_rel',
        'config_id',
        'product_id',
        string='Productos',
        help="Productos que pertenecen a esta campaña"
    )
    
    sequence = fields.Integer(
        string='Secuencia',
        default=10,
        help="Orden de aparición en las listas"
    )
    
    active = fields.Boolean(
        string='Activo',
        default=True,
        help="Si está desactivado, no se usará en los cálculos automáticos"
    )
    
    description = fields.Text(
        string='Descripción',
        help="Descripción detallada de la configuración"
    )
    
    # Campos para definir períodos de siembra
    planting_start_month = fields.Integer(
        string='Mes Inicio Siembra',
        help="Mes de inicio del período de siembra (1-12)"
    )
    
    planting_start_day = fields.Integer(
        string='Día Inicio Siembra',
        help="Día de inicio del período de siembra (1-31)"
    )
    
    planting_end_month = fields.Integer(
        string='Mes Fin Siembra',
        help="Mes de fin del período de siembra (1-12)"
    )
    
    planting_end_day = fields.Integer(
        string='Día Fin Siembra',
        help="Día de fin del período de siembra (1-31)"
    )
    
    # Campo para indicar si cruza años
    crosses_years = fields.Boolean(
        string='Cruza Años',
        help="Marque si el período de siembra cruza de un año al siguiente"
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        default=lambda self: self.env.company,
        required=True
    )

    @api.constrains('planting_start_month', 'planting_end_month')
    def _check_months(self):
        """Validate month values"""
        for record in self:
            if record.planting_start_month and (record.planting_start_month < 1 or record.planting_start_month > 12):
                raise ValidationError("El mes de inicio debe estar entre 1 y 12")
            if record.planting_end_month and (record.planting_end_month < 1 or record.planting_end_month > 12):
                raise ValidationError("El mes de fin debe estar entre 1 y 12")

    @api.constrains('planting_start_day', 'planting_end_day')
    def _check_days(self):
        """Validate day values"""
        for record in self:
            if record.planting_start_day and (record.planting_start_day < 1 or record.planting_start_day > 31):
                raise ValidationError("El día de inicio debe estar entre 1 y 31")
            if record.planting_end_day and (record.planting_end_day < 1 or record.planting_end_day > 31):
                raise ValidationError("El día de fin debe estar entre 1 y 31")

    @api.constrains('campaign_type', 'company_id')
    def _check_unique_campaign_type(self):
        """Ensure only one active configuration per campaign type and company"""
        for record in self:
            if record.active:
                existing = self.search([
                    ('campaign_type', '=', record.campaign_type),
                    ('company_id', '=', record.company_id.id),
                    ('active', '=', True),
                    ('id', '!=', record.id)
                ])
                if existing:
                    campaign_name = dict(record._fields['campaign_type'].selection)[record.campaign_type]
                    raise ValidationError(
                        f"Ya existe una configuración activa para {campaign_name} "
                        f"en la compañía {record.company_id.name}"
                    )

    def name_get(self):
        """Custom name_get"""
        result = []
        for record in self:
            campaign_name = dict(record._fields['campaign_type'].selection)[record.campaign_type]
            name = f"{campaign_name} - {record.name}"
            result.append((record.id, name))
        return result

    @api.model
    def get_products_by_campaign(self, campaign_type, company_id=None):
        """Helper method to get products by campaign type"""
        if not company_id:
            company_id = self.env.company.id
        
        config = self.search([
            ('campaign_type', '=', campaign_type),
            ('company_id', '=', company_id),
            ('active', '=', True)
        ], limit=1)
        
        return config.product_ids if config else self.env['product.product']

    def action_view_products(self):
        """Action to view configured products"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Productos - {self.name}',
            'res_model': 'product.product',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.product_ids.ids)],
            'context': {'default_categ_id': self.env.ref('product.product_category_all').id}
        }
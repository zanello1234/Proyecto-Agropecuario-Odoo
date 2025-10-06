# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta


class FarmContract(models.Model):
    _name = 'farm.contract'
    _description = 'Contrato de Alquiler de Campo'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc, name'

    name = fields.Char(
        string='Código de Contrato',
        compute='_compute_name',
        store=True,
        help="Generado automáticamente"
    )
    
    landlord_id = fields.Many2one(
        'res.partner',
        string='Propietario/Arrendador',
        required=True,
        domain=[('is_company', 'in', [True, False])],
        help="Contacto del propietario o arrendador del campo"
    )
    
    start_date = fields.Date(
        string='Fecha de Inicio',
        required=True,
        help="Fecha de inicio del contrato"
    )
    
    end_date = fields.Date(
        string='Fecha de Finalización',
        required=True,
        help="Fecha de finalización del contrato"
    )
    
    duration = fields.Char(
        string='Duración',
        compute='_compute_duration',
        store=True,
        help="Duración calculada automáticamente"
    )
    
    payment_method = fields.Selection([
        ('cash', 'Efectivo'),
        ('quintals', 'Quintales de Soja'),
        ('percentage', 'Porcentaje de Cosecha'),
        ('other', 'Otro')
    ], string='Forma de Pago', required=True)
    
    price = fields.Float(
        string='Precio/Valor',
        help="Precio o valor según la forma de pago"
    )
    
    notes = fields.Text(
        string='Observaciones',
        help="Detalles adicionales del contrato"
    )
    
    # Campos relacionados y calculados
    field_ids = fields.One2many(
        'farm.field',
        'contract_id',
        string='Campos Asociados'
    )
    
    field_count = fields.Integer(
        string='Cantidad de Campos',
        compute='_compute_field_count'
    )
    
    total_area = fields.Float(
        string='Área Total Contratada (ha)',
        compute='_compute_total_area',
        store=True
    )
    
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('active', 'Activo'),
        ('expired', 'Vencido'),
        ('cancelled', 'Cancelado')
    ], string='Estado', default='draft', tracking=True)
    
    # Campos adicionales
    active = fields.Boolean(default=True)
    
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        default=lambda self: self.env.company
    )
    
    @api.depends('field_ids', 'start_date')
    def _compute_name(self):
        """Genera el nombre del contrato automáticamente"""
        for record in self:
            if record.field_ids and record.start_date:
                field_name = record.field_ids[0].name if len(record.field_ids) == 1 else "VARIOS CAMPOS"
                year = record.start_date.year
                record.name = f"CONTRATO - {field_name} - {year}"
            else:
                record.name = "CONTRATO - NUEVO"
    
    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        """Calcula la duración del contrato"""
        for record in self:
            if record.start_date and record.end_date:
                if record.end_date < record.start_date:
                    record.duration = "Error: Fecha fin anterior a fecha inicio"
                    continue
                
                delta = relativedelta(record.end_date, record.start_date)
                
                duration_parts = []
                if delta.years > 0:
                    duration_parts.append(f"{delta.years} año{'s' if delta.years > 1 else ''}")
                if delta.months > 0:
                    duration_parts.append(f"{delta.months} mes{'es' if delta.months > 1 else ''}")
                if delta.days > 0:
                    duration_parts.append(f"{delta.days} día{'s' if delta.days > 1 else ''}")
                
                record.duration = ", ".join(duration_parts) if duration_parts else "0 días"
            else:
                record.duration = ""
    
    @api.depends('field_ids')
    def _compute_field_count(self):
        """Cuenta la cantidad de campos asociados"""
        for record in self:
            record.field_count = len(record.field_ids)
    
    @api.depends('field_ids.total_area')
    def _compute_total_area(self):
        """Calcula el área total de todos los campos asociados"""
        for record in self:
            record.total_area = sum(record.field_ids.mapped('total_area'))
    
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        """Valida que la fecha de fin sea posterior a la de inicio"""
        for record in self:
            if record.start_date and record.end_date:
                if record.end_date <= record.start_date:
                    raise ValidationError(
                        "La fecha de finalización debe ser posterior a la fecha de inicio."
                    )
    
    @api.constrains('price')
    def _check_price_positive(self):
        """Valida que el precio sea positivo si se especifica"""
        for record in self:
            if record.price and record.price < 0:
                raise ValidationError("El precio no puede ser negativo.")
    
    def action_activate(self):
        """Activa el contrato"""
        self.write({'state': 'active'})
    
    def action_cancel(self):
        """Cancela el contrato"""
        self.write({'state': 'cancelled'})
    
    def action_set_draft(self):
        """Vuelve el contrato a borrador"""
        self.write({'state': 'draft'})
    
    @api.model
    def _cron_check_expired_contracts(self):
        """Cron job para marcar contratos vencidos automáticamente"""
        today = fields.Date.today()
        expired_contracts = self.search([
            ('state', '=', 'active'),
            ('end_date', '<', today)
        ])
        expired_contracts.write({'state': 'expired'})
    
    def name_get(self):
        """Personaliza la representación del nombre del contrato"""
        result = []
        for record in self:
            name = record.name or "Contrato Nuevo"
            if record.landlord_id:
                name += f" - {record.landlord_id.name}"
            result.append((record.id, name))
        return result
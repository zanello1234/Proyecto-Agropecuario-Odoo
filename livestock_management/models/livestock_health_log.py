# -*- coding: utf-8 -*-

from odoo import models, fields, api


class LivestockHealthLog(models.Model):
    _name = 'livestock.health.log'
    _description = 'Registro Sanitario del Ganado'
    _order = 'date desc, id desc'

    # Relaciones principales
    animal_id = fields.Many2one(
        'livestock.animal',
        string='Animal',
        help="Animal tratado individualmente"
    )
    
    lot_id = fields.Many2one(
        'farm.lot',
        string='Lote Completo',
        help="Lote completo tratado (para registros masivos)"
    )
    
    # Información del tratamiento
    log_type = fields.Selection([
        ('vaccination', 'Vacunación'),
        ('deworming', 'Desparasitación'),
        ('treatment', 'Tratamiento'),
        ('vitamin', 'Vitaminas/Suplementos'),
        ('antibiotic', 'Antibióticos'),
        ('hormone', 'Hormonas'),
        ('other', 'Otro'),
    ], string='Tipo de Control', required=True)
    
    date = fields.Date(
        string='Fecha de Aplicación',
        required=True,
        default=fields.Date.today
    )
    
    product_id = fields.Many2one(
        'product.product',
        string='Producto Utilizado',
        domain="[('type', '=', 'product')]",
        help="Producto farmacológico utilizado"
    )
    
    dose = fields.Float(
        string='Dosis Aplicada',
        help="Dosis aplicada por animal"
    )
    
    dose_unit = fields.Selection([
        ('ml', 'Mililitros (ml)'),
        ('cc', 'Centímetros cúbicos (cc)'),
        ('mg', 'Miligramos (mg)'),
        ('g', 'Gramos (g)'),
        ('kg', 'Kilogramos (kg)'),
        ('units', 'Unidades'),
        ('doses', 'Dosis'),
    ], string='Unidad de Dosis', default='ml')
    
    veterinarian = fields.Char(
        string='Veterinario',
        help="Veterinario responsable del tratamiento"
    )
    
    notes = fields.Text(
        string='Observaciones',
        help="Observaciones adicionales (ej: Refuerzo anual, reacción adversa)"
    )
    
    # Campos calculados y relacionados
    animal_ear_tag = fields.Char(
        related='animal_id.ear_tag_id',
        string='Caravana',
        store=True,
        readonly=True
    )
    
    animal_count = fields.Integer(
        string='Cantidad de Animales',
        compute='_compute_animal_count',
        store=True,
        help="Cantidad de animales tratados"
    )
    
    cost_per_animal = fields.Float(
        string='Costo por Animal',
        compute='_compute_cost_per_animal',
        help="Costo estimado por animal"
    )
    
    total_cost = fields.Float(
        string='Costo Total',
        compute='_compute_total_cost',
        help="Costo total del tratamiento"
    )
    
    # Control de estado
    state = fields.Selection([
        ('planned', 'Planificado'),
        ('applied', 'Aplicado'),
        ('completed', 'Completado'),
    ], string='Estado', default='planned')
    
    next_application_date = fields.Date(
        string='Próxima Aplicación',
        help="Fecha sugerida para la próxima aplicación (refuerzos)"
    )

    @api.constrains('animal_id', 'lot_id')
    def _check_animal_or_lot(self):
        """Valida que se especifique animal o lote, pero no ambos"""
        for log in self:
            if not log.animal_id and not log.lot_id:
                raise models.ValidationError(
                    "Debe especificar un animal individual o un lote completo."
                )
            if log.animal_id and log.lot_id:
                raise models.ValidationError(
                    "No puede especificar tanto un animal individual como un lote completo. "
                    "Elija una opción."
                )

    @api.constrains('date')
    def _check_date(self):
        """Valida que la fecha no sea futura"""
        for log in self:
            if log.date and log.date > fields.Date.today():
                raise models.ValidationError(
                    "La fecha de aplicación no puede ser futura."
                )

    @api.depends('animal_id', 'lot_id')
    def _compute_animal_count(self):
        """Calcula la cantidad de animales tratados"""
        for log in self:
            if log.animal_id:
                log.animal_count = 1
            elif log.lot_id:
                # Contar animales activos en el lote
                log.animal_count = self.env['livestock.animal'].search_count([
                    ('current_lot_id', '=', log.lot_id.id),
                    ('status', '=', 'active')
                ])
            else:
                log.animal_count = 0

    @api.depends('product_id', 'dose')
    def _compute_cost_per_animal(self):
        """Calcula el costo por animal"""
        for log in self:
            if log.product_id and log.dose:
                # Cálculo básico basado en el precio del producto
                log.cost_per_animal = log.product_id.standard_price * (log.dose / 100.0)
            else:
                log.cost_per_animal = 0.0

    @api.depends('cost_per_animal', 'animal_count')
    def _compute_total_cost(self):
        """Calcula el costo total"""
        for log in self:
            log.total_cost = log.cost_per_animal * log.animal_count

    @api.model
    def create(self, vals):
        """Sobrescribe create para crear registros individuales si es por lote"""
        log = super(LivestockHealthLog, self).create(vals)
        
        # Si es un registro por lote, crear registros individuales
        if log.lot_id and not log.animal_id:
            log._create_individual_logs()
        
        return log

    def _create_individual_logs(self):
        """Crea registros individuales para cada animal del lote"""
        self.ensure_one()
        if not self.lot_id:
            return
        
        # Buscar todos los animales activos en el lote
        animals = self.env['livestock.animal'].search([
            ('current_lot_id', '=', self.lot_id.id),
            ('status', '=', 'active')
        ])
        
        # Crear un registro individual para cada animal
        for animal in animals:
            self.env['livestock.health.log'].create({
                'animal_id': animal.id,
                'log_type': self.log_type,
                'date': self.date,
                'product_id': self.product_id.id if self.product_id else False,
                'dose': self.dose,
                'dose_unit': self.dose_unit,
                'veterinarian': self.veterinarian,
                'notes': f"Aplicado en lote: {self.lot_id.name}. {self.notes or ''}",
                'state': self.state,
                'next_application_date': self.next_application_date,
            })

    def action_mark_applied(self):
        """Marca el registro como aplicado"""
        self.ensure_one()
        self.state = 'applied'
        return True

    def action_mark_completed(self):
        """Marca el registro como completado"""
        self.ensure_one()
        self.state = 'completed'
        return True

    def action_view_animal(self):
        """Abre la ficha del animal"""
        self.ensure_one()
        if not self.animal_id:
            return False
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'Animal {self.animal_id.ear_tag_id}',
            'res_model': 'livestock.animal',
            'res_id': self.animal_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_lot_animals(self):
        """Muestra los animales del lote"""
        self.ensure_one()
        if not self.lot_id:
            return False
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'Animales del Lote {self.lot_id.name}',
            'res_model': 'livestock.animal',
            'view_mode': 'list,form',
            'domain': [('current_lot_id', '=', self.lot_id.id), ('status', '=', 'active')],
        }

    def action_create_next_application(self):
        """Crea el siguiente registro para refuerzo"""
        self.ensure_one()
        if not self.next_application_date:
            raise models.UserError("No se ha definido una fecha para la próxima aplicación.")
        
        new_log = self.copy({
            'date': self.next_application_date,
            'state': 'planned',
            'notes': f"Refuerzo de aplicación anterior del {self.date}",
            'next_application_date': False,
        })
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nuevo Registro Sanitario',
            'res_model': 'livestock.health.log',
            'res_id': new_log.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def name_get(self):
        """Personaliza la visualización del nombre"""
        result = []
        log_types = dict(self._fields['log_type'].selection)
        
        for log in self:
            if log.animal_id:
                name = f"{log_types.get(log.log_type, log.log_type)} - {log.animal_id.ear_tag_id} ({log.date})"
            elif log.lot_id:
                name = f"{log_types.get(log.log_type, log.log_type)} - Lote {log.lot_id.name} ({log.date})"
            else:
                name = f"{log_types.get(log.log_type, log.log_type)} ({log.date})"
            
            result.append((log.id, name))
        return result
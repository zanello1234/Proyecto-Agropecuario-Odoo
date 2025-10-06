# -*- coding: utf-8 -*-

from odoo import models, fields, api


class LivestockWeighing(models.Model):
    _name = 'livestock.weighing'
    _description = 'Control de Pesaje del Ganado'
    _order = 'date desc, id desc'

    animal_id = fields.Many2one(
        'livestock.animal',
        string='Animal',
        required=True,
        help="Animal pesado"
    )
    
    date = fields.Date(
        string='Fecha del Pesaje',
        required=True,
        default=fields.Date.today
    )
    
    weight_kg = fields.Float(
        string='Peso (kg)',
        required=True,
        help="Peso del animal en kilogramos"
    )
    
    gdm = fields.Float(
        string='Ganancia Diaria Media (GDM)',
        compute='_compute_gdm',
        store=True,
        readonly=True,
        help="Ganancia diaria media calculada desde el pesaje anterior"
    )
    
    days_since_last = fields.Integer(
        string='Días desde último pesaje',
        compute='_compute_gdm',
        store=True,
        readonly=True
    )
    
    weight_gain = fields.Float(
        string='Ganancia de Peso (kg)',
        compute='_compute_gdm',
        store=True,
        readonly=True,
        help="Ganancia de peso desde el último pesaje"
    )
    
    # Campos relacionados para facilitar búsquedas y reportes
    animal_ear_tag = fields.Char(
        related='animal_id.ear_tag_id',
        string='Caravana',
        store=True,
        readonly=True
    )
    
    animal_breed = fields.Char(
        related='animal_id.breed_id.name',
        string='Raza',
        store=True,
        readonly=True
    )
    
    animal_age = fields.Char(
        related='animal_id.age',
        string='Edad',
        readonly=True
    )
    
    # Información contextual
    weighing_reason = fields.Selection([
        ('routine', 'Control Rutinario'),
        ('entry', 'Ingreso'),
        ('exit', 'Salida/Venta'),
        ('health', 'Control Sanitario'),
        ('treatment', 'Post-Tratamiento'),
        ('other', 'Otro'),
    ], string='Motivo del Pesaje', default='routine')
    
    notes = fields.Text(
        string='Observaciones',
        help="Observaciones sobre el pesaje o el estado del animal"
    )
    
    # Campo para la condición corporal (opcional)
    body_condition = fields.Selection([
        ('1', '1 - Muy Flaco'),
        ('2', '2 - Flaco'),
        ('3', '3 - Moderado'),
        ('4', '4 - Bueno'),
        ('5', '5 - Gordo'),
        ('6', '6 - Muy Gordo'),
    ], string='Condición Corporal', help="Evaluación visual de la condición corporal")
    
    # Control de calidad del pesaje
    verified = fields.Boolean(
        string='Verificado',
        default=False,
        help="Marca si el pesaje ha sido verificado/confirmado"
    )
    
    verified_by = fields.Char(
        string='Verificado por',
        help="Persona que verificó el pesaje"
    )

    @api.constrains('weight_kg')
    def _check_weight(self):
        """Valida que el peso sea positivo y razonable"""
        for weighing in self:
            if weighing.weight_kg <= 0:
                raise models.ValidationError("El peso debe ser mayor que cero.")
            
            if weighing.weight_kg > 2000:  # Peso máximo razonable para ganado
                raise models.ValidationError(
                    "El peso parece excesivo. Verifique el valor ingresado."
                )

    @api.constrains('date', 'animal_id')
    def _check_date_uniqueness(self):
        """Evita múltiples pesajes en la misma fecha para el mismo animal"""
        for weighing in self:
            duplicate = self.search([
                ('animal_id', '=', weighing.animal_id.id),
                ('date', '=', weighing.date),
                ('id', '!=', weighing.id)
            ])
            if duplicate:
                raise models.ValidationError(
                    f"Ya existe un pesaje para el animal {weighing.animal_id.ear_tag_id} "
                    f"en la fecha {weighing.date}."
                )

    @api.constrains('date')
    def _check_date(self):
        """Valida que la fecha no sea futura"""
        for weighing in self:
            if weighing.date and weighing.date > fields.Date.today():
                raise models.ValidationError(
                    "La fecha del pesaje no puede ser futura."
                )

    @api.depends('animal_id', 'date', 'weight_kg')
    def _compute_gdm(self):
        """Calcula la ganancia diaria media (GDM)"""
        for weighing in self:
            if not weighing.animal_id or not weighing.date:
                weighing.gdm = 0.0
                weighing.days_since_last = 0
                weighing.weight_gain = 0.0
                continue
            
            # Buscar el pesaje anterior
            previous_weighing = self.search([
                ('animal_id', '=', weighing.animal_id.id),
                ('date', '<', weighing.date),
                ('id', '!=', weighing.id)
            ], order='date desc', limit=1)
            
            if previous_weighing:
                # Calcular días transcurridos
                date_diff = weighing.date - previous_weighing.date
                weighing.days_since_last = date_diff.days
                
                # Calcular ganancia de peso
                weighing.weight_gain = weighing.weight_kg - previous_weighing.weight_kg
                
                # Calcular GDM
                if weighing.days_since_last > 0:
                    weighing.gdm = weighing.weight_gain / weighing.days_since_last
                else:
                    weighing.gdm = 0.0
            else:
                # Es el primer pesaje
                weighing.gdm = 0.0
                weighing.days_since_last = 0
                weighing.weight_gain = 0.0

    @api.model
    def create(self, vals):
        """Sobrescribe create para validaciones adicionales"""
        weighing = super(LivestockWeighing, self).create(vals)
        
        # Recalcular GDM para pesajes posteriores del mismo animal
        weighing._recalculate_subsequent_gdm()
        
        return weighing

    def write(self, vals):
        """Sobrescribe write para recalcular GDM si cambian valores críticos"""
        result = super(LivestockWeighing, self).write(vals)
        
        if 'weight_kg' in vals or 'date' in vals:
            for weighing in self:
                weighing._recalculate_subsequent_gdm()
        
        return result

    def _recalculate_subsequent_gdm(self):
        """Recalcula el GDM para pesajes posteriores del mismo animal"""
        self.ensure_one()
        
        # Buscar pesajes posteriores del mismo animal
        subsequent_weighings = self.search([
            ('animal_id', '=', self.animal_id.id),
            ('date', '>', self.date)
        ], order='date asc')
        
        # Forzar recálculo del GDM
        for weighing in subsequent_weighings:
            weighing._compute_gdm()

    def action_verify_weighing(self):
        """Marca el pesaje como verificado"""
        self.ensure_one()
        self.verified = True
        self.verified_by = self.env.user.name
        return True

    def action_view_animal(self):
        """Abre la ficha del animal"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Animal {self.animal_id.ear_tag_id}',
            'res_model': 'livestock.animal',
            'res_id': self.animal_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_weight_evolution(self):
        """Muestra la evolución de peso del animal"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Evolución de Peso - {self.animal_id.ear_tag_id}',
            'res_model': 'livestock.weighing',
            'view_mode': 'list,graph',
            'domain': [('animal_id', '=', self.animal_id.id)],
            'context': {
                'search_default_group_by_date': 1,
                'graph_measure': 'weight_kg',
                'graph_mode': 'line',
            }
        }

    @api.model
    def get_average_gdm_by_breed(self, date_from=None, date_to=None):
        """Obtiene la GDM promedio por raza en un período"""
        domain = [('gdm', '>', 0)]  # Solo considerar pesajes con GDM calculado
        
        if date_from:
            domain.append(('date', '>=', date_from))
        if date_to:
            domain.append(('date', '<=', date_to))
        
        weighings = self.search(domain)
        
        breed_stats = {}
        for weighing in weighings:
            breed = weighing.animal_breed
            if breed not in breed_stats:
                breed_stats[breed] = {'total_gdm': 0, 'count': 0}
            
            breed_stats[breed]['total_gdm'] += weighing.gdm
            breed_stats[breed]['count'] += 1
        
        # Calcular promedios
        for breed in breed_stats:
            if breed_stats[breed]['count'] > 0:
                breed_stats[breed]['avg_gdm'] = breed_stats[breed]['total_gdm'] / breed_stats[breed]['count']
            else:
                breed_stats[breed]['avg_gdm'] = 0
        
        return breed_stats

    def name_get(self):
        """Personaliza la visualización del nombre"""
        result = []
        for weighing in self:
            name = f"{weighing.animal_ear_tag} - {weighing.weight_kg}kg ({weighing.date})"
            if weighing.gdm > 0:
                name += f" - GDM: {weighing.gdm:.2f}kg/día"
            result.append((weighing.id, name))
        return result
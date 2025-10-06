# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class LivestockAnimal(models.Model):
    _name = 'livestock.animal'
    _description = 'Animal de Ganado'
    _order = 'ear_tag_id'
    _rec_name = 'ear_tag_id'

    # Información básica del animal
    ear_tag_id = fields.Char(
        string='Número de Caravana',
        required=True,
        copy=False,
        help="Número único de identificación del animal"
    )
    
    name = fields.Char(
        string='Nombre/Apodo',
        help="Nombre o apodo opcional del animal"
    )
    
    breed_id = fields.Many2one(
        'livestock.breed',
        string='Raza',
        required=True,
        help="Raza del animal"
    )
    
    gender = fields.Selection([
        ('male', 'Macho'),
        ('female', 'Hembra'),
    ], string='Género', required=True)
    
    birth_date = fields.Date(
        string='Fecha de Nacimiento',
        required=True,
        default=fields.Date.today
    )
    
    age = fields.Char(
        string='Edad',
        compute='_compute_age',
        store=True,
        help="Edad calculada automáticamente"
    )
    
    mother_id = fields.Many2one(
        'livestock.animal',
        string='Madre',
        domain="[('gender', '=', 'female')]",
        help="Madre del animal"
    )
    
    # Estado y ubicación
    status = fields.Selection([
        ('active', 'Activo'),
        ('sold', 'Vendido'),
        ('dead', 'Muerto'),
    ], string='Estado', default='active', required=True)
    
    current_field_id = fields.Many2one(
        'farm.field',
        string='Campo Actual',
        help="Campo donde se encuentra actualmente el animal"
    )
    
    current_lot_id = fields.Many2one(
        'farm.lot',
        string='Lote Actual',
        help="Lote donde se encuentra actualmente el animal"
    )
    
    activity_type = fields.Selection([
        ('breeding', 'Cría'),
        ('fattening', 'Invernada'),
        ('feedlot', 'Feedlot'),
        ('mixed', 'Mixto'),
    ], string='Tipo de Actividad', required=True, default='breeding')
    
    # Relaciones con otros modelos
    weighing_ids = fields.One2many(
        'livestock.weighing',
        'animal_id',
        string='Historial de Pesajes'
    )
    
    health_log_ids = fields.One2many(
        'livestock.health.log',
        'animal_id',
        string='Registro Sanitario'
    )
    
    event_ids = fields.One2many(
        'livestock.event',
        'animal_id',
        string='Eventos de Vida'
    )
    
    # Campos calculados
    current_weight = fields.Float(
        string='Peso Actual (kg)',
        compute='_compute_current_weight',
        store=True,
        help="Último peso registrado"
    )
    
    last_weighing_date = fields.Date(
        string='Última Pesada',
        compute='_compute_current_weight',
        store=True
    )
    
    total_weighings = fields.Integer(
        string='Total de Pesajes',
        compute='_compute_weighing_stats'
    )
    
    total_health_logs = fields.Integer(
        string='Registros Sanitarios',
        compute='_compute_health_stats'
    )
    
    children_ids = fields.One2many(
        'livestock.animal',
        'mother_id',
        string='Crías'
    )
    
    children_count = fields.Integer(
        string='Cantidad de Crías',
        compute='_compute_children_count'
    )
    
    notes = fields.Text(
        string='Observaciones',
        help="Observaciones generales sobre el animal"
    )
    
    active = fields.Boolean(
        string='Activo',
        default=True
    )

    # Constrains
    @api.constrains('ear_tag_id')
    def _check_ear_tag_unique(self):
        """Verifica que el número de caravana sea único"""
        for animal in self:
            if self.search_count([('ear_tag_id', '=', animal.ear_tag_id), ('id', '!=', animal.id)]) > 0:
                raise models.ValidationError(
                    f"Ya existe un animal con el número de caravana '{animal.ear_tag_id}'. "
                    "El número de caravana debe ser único."
                )

    @api.constrains('birth_date')
    def _check_birth_date(self):
        """Verifica que la fecha de nacimiento no sea futura"""
        for animal in self:
            if animal.birth_date and animal.birth_date > fields.Date.today():
                raise models.ValidationError(
                    "La fecha de nacimiento no puede ser futura."
                )

    @api.constrains('mother_id')
    def _check_mother_recursion(self):
        """Evita recursión en la relación madre-cría"""
        for animal in self:
            if animal.mother_id:
                if animal.mother_id == animal:
                    raise models.ValidationError(
                        "Un animal no puede ser su propia madre."
                    )

    # Campos calculados
    @api.depends('birth_date')
    def _compute_age(self):
        """Calcula la edad del animal"""
        today = date.today()
        for animal in self:
            if animal.birth_date:
                birth = animal.birth_date
                diff = relativedelta(today, birth)
                
                if diff.years > 0:
                    if diff.months > 0:
                        animal.age = f"{diff.years} años, {diff.months} meses"
                    else:
                        animal.age = f"{diff.years} años"
                elif diff.months > 0:
                    animal.age = f"{diff.months} meses"
                else:
                    animal.age = f"{diff.days} días"
            else:
                animal.age = "Sin fecha de nacimiento"

    @api.depends('weighing_ids.weight_kg', 'weighing_ids.date')
    def _compute_current_weight(self):
        """Calcula el peso actual y la fecha del último pesaje"""
        for animal in self:
            last_weighing = animal.weighing_ids.sorted('date', reverse=True)[:1]
            if last_weighing:
                animal.current_weight = last_weighing.weight_kg
                animal.last_weighing_date = last_weighing.date
            else:
                animal.current_weight = 0.0
                animal.last_weighing_date = False

    @api.depends('weighing_ids')
    def _compute_weighing_stats(self):
        """Calcula estadísticas de pesajes"""
        for animal in self:
            animal.total_weighings = len(animal.weighing_ids)

    @api.depends('health_log_ids')
    def _compute_health_stats(self):
        """Calcula estadísticas sanitarias"""
        for animal in self:
            animal.total_health_logs = len(animal.health_log_ids)

    @api.depends('children_ids')
    def _compute_children_count(self):
        """Calcula la cantidad de crías"""
        for animal in self:
            animal.children_count = len(animal.children_ids.filtered(lambda c: c.status == 'active'))

    def name_get(self):
        """Personaliza la visualización del nombre"""
        result = []
        for animal in self:
            if animal.name:
                name = f"[{animal.ear_tag_id}] {animal.name}"
            else:
                name = f"[{animal.ear_tag_id}]"
            result.append((animal.id, name))
        return result

    @api.model
    def create(self, vals):
        """Sobrescribe create para validaciones adicionales"""
        animal = super(LivestockAnimal, self).create(vals)
        
        # Crear evento de nacimiento automáticamente
        self.env['livestock.event'].create({
            'event_type': 'birth',
            'date': animal.birth_date,
            'animal_id': animal.id,
            'notes': f'Nacimiento registrado automáticamente para {animal.ear_tag_id}'
        })
        
        return animal

    def action_mark_as_sold(self):
        """Marca el animal como vendido"""
        self.ensure_one()
        self.status = 'sold'
        return True

    def action_mark_as_dead(self):
        """Abre wizard para registrar muerte"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Registrar Mortandad',
            'res_model': 'livestock.event',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_event_type': 'death',
                'default_animal_id': self.id,
                'default_date': fields.Date.today(),
            }
        }

    def action_add_weighing(self):
        """Abre formulario para agregar pesaje"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Registrar Pesaje',
            'res_model': 'livestock.weighing',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_animal_id': self.id,
                'default_date': fields.Date.today(),
            }
        }

    def action_add_health_log(self):
        """Abre formulario para agregar registro sanitario"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Registrar Intervención Sanitaria',
            'res_model': 'livestock.health.log',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_animal_id': self.id,
                'default_date': fields.Date.today(),
            }
        }

    def action_view_children(self):
        """Muestra las crías del animal"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Crías de {self.ear_tag_id}',
            'res_model': 'livestock.animal',
            'view_mode': 'list,form',
            'domain': [('mother_id', '=', self.id)],
            'context': {
                'default_mother_id': self.id,
                'default_breed_id': self.breed_id.id,
                'default_current_field_id': self.current_field_id.id,
                'default_current_lot_id': self.current_lot_id.id,
            }
        }
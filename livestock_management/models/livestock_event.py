# -*- coding: utf-8 -*-

from odoo import models, fields, api


class LivestockEvent(models.Model):
    _name = 'livestock.event'
    _description = 'Eventos de Vida del Ganado'
    _order = 'date desc, id desc'

    event_type = fields.Selection([
        ('birth', 'Nacimiento'),
        ('death', 'Mortandad'),
    ], string='Tipo de Evento', required=True)
    
    date = fields.Date(
        string='Fecha del Evento',
        required=True,
        default=fields.Date.today
    )
    
    animal_id = fields.Many2one(
        'livestock.animal',
        string='Animal',
        required=True,
        help="Animal afectado por el evento"
    )
    
    cause_of_death = fields.Char(
        string='Causa de la Muerte',
        help="Causa específica de la muerte del animal"
    )
    
    notes = fields.Text(
        string='Notas Adicionales',
        help="Observaciones adicionales sobre el evento"
    )
    
    # Campos relacionados para facilitar reportes
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
    
    animal_gender = fields.Selection(
        related='animal_id.gender',
        string='Género',
        store=True,
        readonly=True
    )
    
    # Campo para el nombre compuesto
    display_name = fields.Char(
        string='Descripción',
        compute='_compute_display_name',
        store=True
    )

    @api.depends('event_type', 'animal_id.ear_tag_id', 'date')
    def _compute_display_name(self):
        """Calcula el nombre para mostrar del evento"""
        event_types = dict(self._fields['event_type'].selection)
        for event in self:
            if event.animal_id and event.event_type:
                event.display_name = f"{event_types[event.event_type]} - {event.animal_id.ear_tag_id} ({event.date})"
            else:
                event.display_name = "Evento sin completar"

    @api.constrains('date')
    def _check_event_date(self):
        """Valida que la fecha del evento no sea futura"""
        for event in self:
            if event.date and event.date > fields.Date.today():
                raise models.ValidationError(
                    "La fecha del evento no puede ser futura."
                )

    @api.constrains('animal_id', 'event_type')
    def _check_death_event(self):
        """Valida que no se registren eventos en animales muertos"""
        for event in self:
            if event.animal_id and event.animal_id.status == 'dead' and event.event_type == 'birth':
                raise models.ValidationError(
                    f"No se puede registrar un nacimiento para el animal {event.animal_id.ear_tag_id} "
                    "que está marcado como muerto."
                )

    @api.model
    def create(self, vals):
        """Sobrescribe create para manejar eventos especiales"""
        event = super(LivestockEvent, self).create(vals)
        
        # Si es un evento de muerte, actualizar el estado del animal
        if event.event_type == 'death' and event.animal_id:
            event.animal_id.status = 'dead'
            
        # Si es un evento de nacimiento y se crea manualmente, validar
        elif event.event_type == 'birth' and event.animal_id:
            # Verificar que el animal no tenga ya un evento de nacimiento
            existing_birth = self.search([
                ('animal_id', '=', event.animal_id.id),
                ('event_type', '=', 'birth'),
                ('id', '!=', event.id)
            ])
            if existing_birth:
                raise models.ValidationError(
                    f"El animal {event.animal_id.ear_tag_id} ya tiene un evento de nacimiento registrado."
                )
        
        return event

    @api.model
    def create_birth_from_animal(self, animal_vals):
        """Método para crear un animal con evento de nacimiento"""
        # Primero crear el animal
        animal = self.env['livestock.animal'].create(animal_vals)
        
        # Crear el evento de nacimiento
        birth_event = self.create({
            'event_type': 'birth',
            'date': animal.birth_date,
            'animal_id': animal.id,
            'notes': f'Nacimiento de {animal.ear_tag_id}'
        })
        
        return animal, birth_event

    def action_view_animal(self):
        """Abre la ficha del animal relacionado"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Animal {self.animal_id.ear_tag_id}',
            'res_model': 'livestock.animal',
            'res_id': self.animal_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def name_get(self):
        """Personaliza la visualización del nombre"""
        result = []
        for event in self:
            result.append((event.id, event.display_name or 'Evento'))
        return result
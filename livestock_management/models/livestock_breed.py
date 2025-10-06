# -*- coding: utf-8 -*-

from odoo import models, fields, api


class LivestockBreed(models.Model):
    _name = 'livestock.breed'
    _description = 'Raza de Ganado'
    _order = 'name'

    name = fields.Char(
        string='Nombre de la Raza',
        required=True,
        help="Nombre de la raza (ej: Aberdeen Angus, Hereford, Brahman)"
    )
    
    code = fields.Char(
        string='Código',
        size=10,
        help="Código corto para identificar la raza"
    )
    
    breed_type = fields.Selection([
        ('beef', 'Carne'),
        ('dairy', 'Lechera'),
        ('dual', 'Doble Propósito'),
    ], string='Tipo de Raza', default='beef', required=True)
    
    origin_country = fields.Char(
        string='País de Origen',
        help="País de origen de la raza"
    )
    
    description = fields.Text(
        string='Descripción',
        help="Características generales de la raza"
    )
    
    average_weight_male = fields.Float(
        string='Peso Promedio Macho (kg)',
        help="Peso promedio de un macho adulto"
    )
    
    average_weight_female = fields.Float(
        string='Peso Promedio Hembra (kg)',
        help="Peso promedio de una hembra adulta"
    )
    
    # Campo para contar animales de esta raza
    animal_count = fields.Integer(
        string='Cantidad de Animales',
        compute='_compute_animal_count',
        store=True
    )
    
    active = fields.Boolean(
        string='Activo',
        default=True
    )

    @api.depends('name')
    def _compute_animal_count(self):
        """Calcula la cantidad de animales de cada raza"""
        for breed in self:
            breed.animal_count = self.env['livestock.animal'].search_count([
                ('breed_id', '=', breed.id),
                ('status', '=', 'active')
            ])

    def name_get(self):
        """Personaliza la visualización del nombre"""
        result = []
        for breed in self:
            if breed.code:
                name = f"[{breed.code}] {breed.name}"
            else:
                name = breed.name
            result.append((breed.id, name))
        return result

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """Permite buscar por nombre o código"""
        if args is None:
            args = []
        
        domain = args[:]
        if name:
            domain = ['|', ('name', operator, name), ('code', operator, name)] + domain
        
        return self.search(domain, limit=limit).name_get()
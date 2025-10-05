# -*- coding: utf-8 -*-
{
    'name': "Gestión de Campos Agropecuarios",
    'summary': """
        Módulo integral para la gestión de campos agrícolas, lotes y contratos de alquiler
    """,
    'description': """
        Módulo de Gestión de Campos Agropecuarios
        ========================================
        
        Este módulo permite la gestión integral de:
        * Campos agrícolas (propios y alquilados)
        * División en lotes operativos
        * Contratos de alquiler
        * Geolocalización y mapeo
        * Información catastral y productiva
        
        Características principales:
        * Registro de campos con geolocalización
        * Gestión de lotes con aptitudes específicas
        * Control de contratos de alquiler
        * Integración con mapas para visualización geográfica
        * Cálculo automático de áreas totales
        * Validaciones de negocio específicas del sector agropecuario
    """,
    'author': "Equipo de Desarrollo Agropecuario",
    'website': "https://www.ejemplo.com",
    'category': 'Agriculture',
    'version': '18.0.1.0.0',
    'depends': [
        'base',
        'base_geolocalize',
        'contacts',
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        
        # Data
        'data/res_country_state_data.xml',
        
        # Views
        'views/farm_contract_views.xml',
        'views/farm_field_views.xml',
        'views/farm_lot_views.xml', 
        'views/menu_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'images': ['static/description/icon.png'],
}
# -*- coding: utf-8 -*-
{
    'name': "Gestión de Campos Agropecuarios v18",
    'summary': """
        Sistema completo para Odoo 18 - Gestión de campos, lotes y contratos agropecuarios
    """,
    'description': """
        Gestión de Campos Agropecuarios v18 - MODERNIZADO PARA ODOO 18
        ==============================================================
        
        **VERSIÓN ESPECIALMENTE MIGRADA Y OPTIMIZADA PARA ODOO 18**
        
        Este módulo permite la gestión integral de:
        * Campos agrícolas (propios y alquilados)
        * División en lotes operativos
        * Contratos de alquiler con seguimiento completo
        * Geolocalización y mapeo avanzado
        * Información catastral y productiva
        
        CARACTERÍSTICAS TÉCNICAS ODOO 18:
        * Sintaxis completamente actualizada para Odoo 18
        * Vistas list modernas (migrado desde tree)
        * Sintaxis attrs moderna (invisible/required)
        * Herencia mail.thread para seguimiento
        * Dependencias optimizadas
        
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
        'mail',
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        
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
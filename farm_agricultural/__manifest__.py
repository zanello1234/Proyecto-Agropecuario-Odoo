# -*- coding: utf-8 -*-
{
    'name': "Módulo Agrícola - Gestión de Campañas",
    'summary': """
        Extensión del módulo de fabricación para gestionar campañas agrícolas completas
    """,
    'description': """
        Módulo Agrícola - Gestión de Campañas
        ====================================
        
        Este módulo extiende el sistema de fabricación de Odoo para adaptarlo
        a la gestión de campañas agrícolas:
        
        Características principales:
        * Transformación de "Órdenes de Producción" en "Órdenes de Cultivo"
        * Gestión completa del ciclo agrícola (barbecho, siembra, cosecha)
        * Integración con campos y lotes del módulo farm_management
        * Planes de labores con insumos agrícolas
        * Cálculo automático de costos por hectárea
        * Diferenciación entre granos, pasturas y verdeos
        * Gestión de activos para pasturas y verdeos
        * Seguimiento de rendimientos por hectárea
        * Subproductos (rollos de pasto)
        
        Funcionalidades específicas:
        * Órdenes de cultivo vinculadas a lotes específicos
        * Fechas clave del ciclo agrícola
        * Cálculo automático de rendimientos
        * Creación automática de activos para pasturas
        * Gestión de costos por hectárea en tiempo real
        * Reportes de producción agrícola
    """,
    'author': "Equipo de Desarrollo Agropecuario",
    'website': "https://www.ejemplo.com",
    'category': 'Manufacturing',
    'version': '18.0.1.0.0',
    'depends': [
        'base',
        'mrp',
        'stock',
        'account_asset',
        'farm_management',  # Módulo de gestión de campos
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        
        # Data
        'data/mrp_data.xml',
        
        # Views
        'views/mrp_production_views.xml',
        'views/mrp_bom_views.xml',
        'views/stock_move_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
    'images': ['static/description/icon.png'],
}
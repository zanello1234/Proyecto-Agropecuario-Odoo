# -*- coding: utf-8 -*-
{
    'name': 'Integración SISA - AFIP',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Localization',
    'summary': 'Módulo de integración con SISA para generar declaraciones IP1 e IP2 de AFIP',
    'description': """
    Módulo de Integración SISA para Odoo 18
    =======================================
    
    Este módulo automatiza la recolección de datos y generación de archivos para cumplir
    con los regímenes de información SISA IP1 (Información Productiva 1) e IP2 
    (Información Productiva 2) de AFIP.
    
    Características principales:
    ---------------------------
    * Generación automática de declaraciones IP1 (Campaña Fina)
    * Generación automática de declaraciones IP2 (Campaña Gruesa)
    * Integración con módulos de Gestión de Campos y Gestión Agrícola
    * Cálculo automático de existencias de granos
    * Cálculo automático de superficies sembradas
    * Exportación de archivos en formato AFIP
    * Configuración de productos por campaña
    * Seguimiento de estados de declaraciones
    
    Funcionalidades:
    ---------------
    * Asistentes guiados para generación de declaraciones
    * Validación automática de datos
    * Exportación de archivos .txt/.csv para AFIP
    * Vista consolidada de todas las declaraciones
    * Control de estados (Borrador, Generado, Presentado)
    """,
    'author': 'Sistema Agropecuario',
    'website': 'https://github.com/zanello1234/Proyecto-Agropecuario-Odoo',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'stock',
        'product',
        'mrp',
        'farm_management',
        'farm_agricultural'
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        'security/sisa_security.xml',
        
        # Data
        'data/sisa_campaign_config_data.xml',
        
        # Views
        'views/sisa_declaration_views.xml',
        'views/sisa_config_views.xml',
        'views/sisa_menuitem.xml',
        
        # Wizards
        'wizard/sisa_ip1_wizard_views.xml',
        'wizard/sisa_ip2_wizard_views.xml',
        'wizard/sisa_export_wizard_views.xml',
    ],
    'demo': [
        'demo/sisa_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 100,
}
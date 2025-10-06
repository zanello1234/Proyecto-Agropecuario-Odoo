# -*- coding: utf-8 -*-
{
    'name': "Gestión Ganadera - Trazabilidad de Ganado",
    'summary': """
        Sistema integral de gestión y trazabilidad de ganado con control sanitario y de pesaje
    """,
    'description': """
        Gestión Ganadera - Trazabilidad de Ganado
        ==========================================
        
        Módulo completo para la gestión integral del ganado que incluye:
        
        🐮 **Gestión de Animales:**
        * Registro individual con número de caravana único
        * Control de razas y genealogía (madre)
        * Seguimiento por género y fecha de nacimiento
        * Cálculo automático de edad
        * Estados: Activo, Vendido, Muerto
        
        📍 **Ubicación y Actividad:**
        * Asignación a campos y lotes (integración con farm_management)
        * Tipos de actividad: Cría, Invernada, Feedlot, Mixto
        * Trazabilidad completa de movimientos
        
        📊 **Control de Pesaje:**
        * Historial completo de pesajes
        * Cálculo automático de Ganancia Diaria Media (GDM)
        * Gráficos de evolución de peso
        * Análisis de rendimiento
        
        🏥 **Registro Sanitario:**
        * Vacunaciones, desparasitaciones y tratamientos
        * Registro individual o por lotes
        * Control de productos utilizados y dosis
        * Historial sanitario completo
        
        📅 **Eventos de Vida:**
        * Registro de nacimientos (crea animal automáticamente)
        * Registro de mortandad (actualiza estado)
        * Trazabilidad de causas de muerte
        
        🎯 **Características Avanzadas:**
        * Identificación única por caravana
        * Interfaz Kanban para gestión visual
        * Reportes y análisis de rendimiento
        * Integración completa con gestión de campos
        * Acciones en lote para eficiencia operativa
        
        Este módulo está diseñado para estancias, feedlots y operaciones ganaderas 
        que requieren un control preciso y trazabilidad completa de su ganado.
    """,
    'author': "Equipo de Desarrollo Agropecuario",
    'website': "https://www.ejemplo.com",
    'category': 'Industries',
    'version': '18.0.1.0.0',
    'depends': [
        'base',
        'product',
        'farm_management',  # Para integración con campos y lotes
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        
        # Data
        'data/livestock_breed_data.xml',
        
        # Views
        'views/livestock_animal_views.xml',
        'views/livestock_breed_views.xml',
        'views/livestock_event_views.xml',
        'views/livestock_health_log_views.xml',
        'views/livestock_weighing_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [
        # Demo data will be added later
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
# Módulo de Gestión de Campos Agropecuarios

## Descripción

Este módulo para Odoo 18 proporciona una solución integral para la gestión de campos agropecuarios, permitiendo administrar tanto campos propios como alquilados, dividirlos en lotes operativos y controlar los contratos de alquiler.

## Características Principales

### 🗺️ Gestión de Campos
- Registro de campos propios y alquilados
- Información catastral completa (partida inmobiliaria, ubicación)
- Geolocalización con coordenadas GPS
- Clasificación por provincia, departamento y localidad

### 📐 Administración de Lotes
- División de campos en lotes operativos
- Definición de aptitudes del suelo (agrícola, ganadero, mixto)
- Cálculo automático de áreas totales
- Geolocalización individual por lote

### 📄 Control de Contratos
- Gestión completa de contratos de alquiler
- Múltiples formas de pago (efectivo, quintales de soja, porcentaje de cosecha)
- Seguimiento automático de fechas y vencimientos
- Estados de contrato con workflow (borrador, activo, vencido, cancelado)

## Instalación

1. Copiar el módulo `farm_management` en el directorio de addons de Odoo
2. Actualizar la lista de aplicaciones
3. Instalar el módulo "Gestión de Campos Agropecuarios"

## Dependencias

- `base`: Funcionalidad básica de Odoo
- `base_geolocalize`: Soporte para geolocalización
- `contacts`: Gestión de contactos/propietarios

## Estructura del Módulo

```
farm_management/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── farm_field.py      # Modelo de campos
│   ├── farm_lot.py        # Modelo de lotes
│   └── farm_contract.py   # Modelo de contratos
├── views/
│   ├── farm_field_views.xml
│   ├── farm_lot_views.xml
│   ├── farm_contract_views.xml
│   └── menu_views.xml
├── security/
│   └── ir.model.access.csv
├── data/
│   └── res_country_state_data.xml
└── static/
    └── description/
        ├── icon.png
        └── index.html
```

## Modelos de Datos

### farm.field (Campo)
- **name**: Nombre del campo
- **field_type**: Tipo de tenencia (propio/alquilado)
- **contract_id**: Relación con contrato (si es alquilado)
- **geolocation_points**: Coordenadas GPS del perímetro
- **lot_ids**: Lotes asociados
- **total_area**: Área total calculada
- **province_id**: Provincia
- **department**: Departamento/Partido
- **location**: Localidad
- **real_estate_id**: Partida inmobiliaria

### farm.lot (Lote)
- **name**: Nombre del lote
- **field_id**: Campo al que pertenece
- **area**: Extensión en hectáreas
- **geolocation_points**: Coordenadas GPS del lote
- **aptitude**: Aptitud del suelo

### farm.contract (Contrato)
- **name**: Código del contrato (auto-generado)
- **landlord_id**: Propietario/Arrendador
- **start_date/end_date**: Fechas del contrato
- **duration**: Duración calculada automáticamente
- **payment_method**: Forma de pago
- **price**: Valor del contrato
- **state**: Estado del contrato

## Funcionalidades Destacadas

### Validaciones Automáticas
- Campos alquilados requieren contrato asociado
- Áreas deben ser positivas
- Fechas de contrato coherentes
- Nombres únicos de lotes por campo

### Cálculos Automáticos
- Área total del campo = suma de áreas de lotes
- Duración del contrato en años, meses y días
- Conteo de campos por contrato

### Búsquedas y Filtros
- Búsqueda por nombre de campo, provincia o localidad
- Filtros por tipo de tenencia, aptitud de lotes, estado de contratos
- Agrupación por diferentes criterios

## Casos de Uso

1. **Registro de Campo Propio**: Crear un campo, definir lotes y visualizar en mapa
2. **Registro de Campo Alquilado**: Crear campo, asociar contrato y gestionar información contractual
3. **Gestión de Lotes**: Dividir campos en unidades operativas con diferentes aptitudes
4. **Control de Contratos**: Seguimiento de vencimientos y condiciones de alquiler

## Roadmap Futuro

- [ ] Integración completa con Google Maps/OpenStreetMap
- [ ] Reportes avanzados de gestión
- [ ] Dashboard con métricas clave
- [ ] Alertas automáticas de vencimientos
- [ ] Integración con otros módulos agropecuarios
- [ ] Soporte para múltiples monedas en contratos
- [ ] Historial de cambios en lotes y campos

## Soporte

Para soporte técnico, reportar errores o solicitar nuevas funcionalidades, contactar al equipo de desarrollo.

## Licencia

LGPL-3

## Versión

1.0.0 - Compatible con Odoo 18.0
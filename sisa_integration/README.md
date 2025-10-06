# Módulo de Integración SISA - AFIP

## Descripción

Este módulo para Odoo 18 automatiza la recolección de datos y generación de archivos necesarios para cumplir con los regímenes de información SISA IP1 (Información Productiva 1) e IP2 (Información Productiva 2) de AFIP.

## Características Principales

### 🌾 Declaraciones Automáticas
- **IP1 (Campaña Fina)**: Genera declaraciones para cultivos de invierno (Trigo, Cebada, Avena)
- **IP2 (Campaña Gruesa)**: Genera declaraciones para cultivos de verano (Soja, Maíz, Girasol)

### 📊 Integración Completa
- Conecta con módulos de Gestión de Campos y Gestión Agrícola
- Cálculo automático de existencias de granos
- Cálculo automático de superficies sembradas
- Consolidación de información para minimizar carga manual

### 🔧 Asistentes Guiados
- Asistente paso a paso para generar declaraciones IP1
- Asistente especializado para declaraciones IP2
- Vista previa de datos antes de la generación
- Validaciones automáticas de información

### 📤 Exportación Flexible
- Múltiples formatos: CSV, TXT, Excel (XLSX)
- Configuración de separadores y codificación
- Archivos listos para importar en SISA-AFIP
- Descarga directa desde Odoo

### ⚙️ Configuración Inteligente
- Mapeo de productos por tipo de campaña
- Períodos de siembra configurables
- Validaciones de negocio incorporadas
- Soporte multi-compañía

## Flujo de Trabajo

### Para IP1 (Campaña Fina)
1. **Configuración**: Seleccione el año de campaña
2. **Cálculo de Stock**: El sistema busca existencias al 30 de septiembre
3. **Cálculo de Superficie**: Identifica siembras Mayo-Agosto
4. **Revisión**: Permite ajustar datos antes de crear la declaración
5. **Exportación**: Genera archivo para AFIP

### Para IP2 (Campaña Gruesa)
1. **Configuración**: Seleccione el año de campaña
2. **Cálculo de Superficie**: Identifica siembras Septiembre-Febrero
3. **Revisión**: Permite ajustar superficies por lote
4. **Exportación**: Genera archivo para AFIP

## Modelos de Datos

### Declaración SISA (`sisa.declaration`)
- Cabecera de cada declaración jurada
- Estados: Borrador → Generado → Presentado
- Tracking completo de cambios

### Líneas de Existencias (`sisa.declaration.stock.line`)
- Detalle de granos en stock (solo IP1)
- Cantidad por producto y ubicación
- Códigos AFIP configurables

### Líneas de Superficie (`sisa.declaration.surface.line`)
- Superficie sembrada por lote y cultivo
- Información de campos y partidas inmobiliarias
- Fechas de siembra

### Configuración de Campañas (`sisa.campaign.config`)
- Mapeo de productos por campaña
- Períodos de siembra
- Configuración por compañía

## Instalación

### Dependencias Requeridas
- `farm_management`: Gestión de campos y lotes
- `farm_agricultural`: Gestión agrícola basada en MRP
- `stock`: Control de inventarios
- `product`: Gestión de productos

### Instalación Opcional
- `openpyxl`: Para exportación a Excel (XLSX)

## Configuración Inicial

1. **Configure los productos**:
   - Vaya a SISA > Configuración > Configuración de Campañas
   - Asocie productos a cada tipo de campaña

2. **Verifique campos obligatorios**:
   - Asegúrese que los campos tengan partida inmobiliaria
   - Configure ubicaciones de stock para granos propios

3. **Configure períodos**:
   - Ajuste fechas de siembra por campaña si es necesario

## Uso del Sistema

### Generar Declaración IP1
1. Menú: SISA > Declaraciones > Nuevo IP1 (Campaña Fina)
2. Siga el asistente paso a paso
3. Revise y ajuste datos calculados
4. Confirme la creación

### Generar Declaración IP2
1. Menú: SISA > Declaraciones > Nuevo IP2 (Campaña Gruesa)
2. Configure el año de campaña
3. Revise superficie calculada
4. Confirme la creación

### Exportar para AFIP
1. Abra la declaración generada
2. Haga clic en "Exportar para AFIP"
3. Configure formato y opciones
4. Descargue el archivo generado

## Características Técnicas

### Validaciones Implementadas
- Unicidad de declaraciones por año y tipo
- Validación de rangos de años
- Control de superficies vs. área de lotes
- Verificación de pertenencia lote-campo

### Seguridad
- Grupos de usuarios específicos
- Reglas multi-compañía
- Accesos diferenciados por rol

### Rendimiento
- Cálculos optimizados con ORM
- Índices en campos clave
- Lazy loading de relaciones

## Soporte y Desarrollo

### Versión
- Odoo 18.0
- Versión del módulo: 1.0.0

### Autor
- Sistema Agropecuario
- GitHub: https://github.com/zanello1234/Proyecto-Agropecuario-Odoo

### Licencia
- LGPL-3

## Notas Importantes

- Este módulo está diseñado específicamente para el sistema SISA de AFIP Argentina
- Requiere configuración inicial de productos por campaña
- Se recomienda realizar pruebas con datos demo antes del uso en producción
- Mantenga backups regulares de las declaraciones generadas
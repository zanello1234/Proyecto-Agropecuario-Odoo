# Módulo Agrícola para Odoo - Farm Agricultural

## Descripción

El módulo **Farm Agricultural** extiende el sistema de manufactura (MRP) de Odoo para gestionar campañas agrícolas de forma integral. Este módulo permite planificar, ejecutar y hacer seguimiento de cultivos desde la siembra hasta la cosecha, integrándose perfectamente con los módulos de stock, contabilidad y gestión de campos.

## Características Principales

### 🌾 Gestión de Campañas Agrícolas
- **Planificación de cultivos**: Creación de campañas con fechas de siembra y cosecha
- **Planes de labores**: Definición de insumos y aplicaciones necesarias por cultivo
- **Seguimiento de costos**: Control detallado de gastos por campaña
- **Análisis de rentabilidad**: Cálculo automático de márgenes y ROI

### 📊 Control de Aplicaciones
- **Registro de aplicaciones**: Seguimiento detallado de cada aplicación de insumos
- **Condiciones climáticas**: Registro de condiciones al momento de aplicación
- **Trazabilidad completa**: Desde el insumo hasta el producto final
- **Alertas y notificaciones**: Para aplicaciones críticas y fechas importantes

### 🚜 Gestión de Equipos y Operadores
- **Asignación de equipos**: Control de maquinaria utilizada en cada aplicación
- **Registro de operadores**: Seguimiento del personal responsable
- **Mantenimiento**: Integración con módulos de mantenimiento de equipos
- **Eficiencia operativa**: Análisis de rendimiento por equipo y operador

### 📈 Análisis y Reportes
- **Dashboard agrícola**: Vista panorámica de todas las campañas activas
- **Reportes de rendimiento**: Análisis de yield por lote y cultivo
- **Comparativa histórica**: Evolución de rendimientos año tras año
- **Análisis de costos**: Desglose detallado de costos por categoría

## Modelos Principales

### MRP Production (Campañas Agrícolas)
Extensión del modelo de órdenes de producción para campañas agrícolas:
- **Información del cultivo**: Tipo, ciclo, fechas de siembra y cosecha
- **Área cultivada**: Superficie en hectáreas
- **Rendimiento esperado/real**: Objetivos y resultados
- **Condiciones especiales**: Riego, clima, tratamientos especiales

### MRP BOM (Planes de Labores)
Planes técnicos que definen los insumos y procedimientos:
- **Insumos por etapa**: Semillas, fertilizantes, pesticidas, etc.
- **Dosificación recomendada**: Cantidades por hectárea
- **Métodos de aplicación**: Pulverización, incorporación, etc.
- **Condiciones críticas**: Factores climáticos y temporales

### Stock Move (Aplicaciones de Insumos)
Registro detallado de cada aplicación realizada:
- **Seguimiento en tiempo real**: Estado y progreso de aplicaciones
- **Condiciones de aplicación**: Clima, equipos, operadores
- **Validación de calidad**: Verificación de dosis y métodos
- **Costo por aplicación**: Análisis económico detallado

## Instalación

### Requisitos Previos
- Odoo 18.0 Community o Enterprise
- Módulo `farm_management` instalado
- Módulos base: `mrp`, `stock`, `account_asset`

### Pasos de Instalación
1. Copiar el módulo a la carpeta de addons de Odoo
2. Actualizar la lista de módulos
3. Instalar desde Apps > Farm Agricultural
4. Configurar parámetros iniciales en Configuración

## Configuración Inicial

### 1. Configuración de Productos
- Crear productos para cultivos (soja, maíz, trigo, etc.)
- Definir categorías de insumos agrícolas
- Configurar unidades de medida específicas

### 2. Planes de Labores
- Crear BOM para cada tipo de cultivo
- Definir insumos y dosificaciones estándar
- Establecer etapas de aplicación

### 3. Configuración de Campos
- Integrar con módulo `farm_management`
- Asignar lotes a campañas
- Configurar características del suelo

## Uso del Sistema

### Planificación de Campaña
1. Crear nueva campaña desde MRP > Órdenes de Producción
2. Seleccionar cultivo y plan de labores
3. Definir fechas y área a cultivar
4. Confirmar planificación

### Ejecución de Aplicaciones
1. Acceder a aplicaciones planificadas
2. Registrar condiciones reales de aplicación
3. Validar dosis y métodos utilizados
4. Confirmar finalización

### Seguimiento y Control
1. Monitorear progreso en dashboard
2. Analizar desviaciones vs. planificado
3. Generar reportes de seguimiento
4. Ajustar planificación según necesidad

## Flujos de Trabajo

### Ciclo Completo de Campaña
```
Planificación → Preparación → Siembra → Cuidados → Cosecha → Análisis
```

### Estados de Campaña
- **Borrador**: En planificación
- **Confirmada**: Lista para ejecutar
- **En Progreso**: Aplicaciones en curso
- **Completada**: Cosecha realizada
- **Cancelada**: Campaña suspendida

## Integraciones

### Módulos de Odoo
- **Inventory**: Gestión de stock de insumos
- **Accounting**: Contabilización de costos y activos
- **Project**: Planificación de tareas agrícolas
- **Quality**: Control de calidad de productos

### Sistemas Externos
- **GPS/GIS**: Integración con sistemas de geolocalización
- **Sensores IoT**: Monitoreo de condiciones ambientales
- **Maquinaria**: Integración con sistemas de agricultura de precisión

## Reportes y Análisis

### Reportes Disponibles
- **Resumen de Campaña**: Estado general y KPIs
- **Análisis de Costos**: Desglose detallado por categoría
- **Rendimiento por Lote**: Comparativa de productividad
- **Eficiencia de Insumos**: Análisis de dosificaciones

### Indicadores Clave (KPIs)
- Rendimiento por hectárea (kg/ha)
- Costo por hectárea ($/ha)
- Margen bruto por campaña
- Eficiencia de aplicaciones

## Personalización

### Campos Adicionales
El módulo permite agregar campos específicos según necesidades:
- Variedades de cultivos
- Condiciones de suelo específicas
- Métricas de calidad particulares

### Workflows Personalizados
- Aprobaciones por gerencia
- Validaciones técnicas
- Procesos de calidad específicos

## Soporte y Mantenimiento

### Actualizaciones
- Compatible con versiones futuras de Odoo
- Migración de datos automática
- Backup de configuraciones

### Documentación Técnica
- API de integración disponible
- Documentación de desarrollador
- Ejemplos de personalización

## Casos de Uso

### Tipos de Explotaciones
- **Agricultura extensiva**: Grandes superficies, pocos cultivos
- **Agricultura intensiva**: Múltiples cultivos, rotaciones complejas
- **Agricultura orgánica**: Restricciones especiales de insumos
- **Agricultura de precisión**: Integración con tecnología avanzada

### Cultivos Soportados
- Cereales (maíz, trigo, cebada, avena)
- Oleaginosas (soja, girasol, colza)
- Legumbres (poroto, garbanzo, lenteja)
- Forrajes (alfalfa, sorgo forrajero)
- Cultivos industriales (algodón, caña de azúcar)

## Beneficios del Sistema

### Operativos
- Reducción de errores en aplicaciones
- Optimización de uso de insumos
- Mejora en planificación de recursos
- Trazabilidad completa

### Económicos
- Control preciso de costos
- Mejora en márgenes de rentabilidad
- Optimización de inventarios
- Reducción de desperdicios

### Estratégicos
- Análisis histórico para mejores decisiones
- Planificación a largo plazo
- Cumplimiento de normativas
- Integración con cadena de valor

---

**Desarrollado para el sector agropecuario argentino**  
*Versión 1.0 - Compatible con Odoo 18.0*
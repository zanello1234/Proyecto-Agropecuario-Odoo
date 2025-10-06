# Módulo de Gestión Ganadera - Livestock Management

## 🐮 Descripción

Sistema integral de gestión y trazabilidad de ganado desarrollado para Odoo 18. Este módulo permite el seguimiento completo del ciclo de vida de cada animal, desde el nacimiento hasta la venta o muerte, incluyendo control sanitario, pesajes y trazabilidad completa.

## 🎯 Características Principales

### 📊 Gestión de Animales
- **Identificación única**: Cada animal tiene un número de caravana único
- **Información genealógica**: Registro de madres y seguimiento de crías
- **Clasificación por actividad**: Cría, Invernada, Feedlot, Mixto
- **Estados**: Activo, Vendido, Muerto
- **Integración con campos y lotes**: Ubicación actual de cada animal

### ⚖️ Control de Pesaje
- **Historial completo**: Registro cronológico de todos los pesajes
- **Ganancia Diaria Media (GDM)**: Cálculo automático basado en pesajes anteriores
- **Gráficos de evolución**: Visualización del progreso de peso
- **Condición corporal**: Evaluación visual del estado del animal
- **Verificación de pesajes**: Control de calidad de los datos

### 🏥 Registro Sanitario
- **Tratamientos individuales**: Vacunas, desparasitaciones, tratamientos específicos
- **Tratamientos masivos**: Aplicación por lotes completos
- **Control de productos**: Registro de medicamentos y dosis utilizadas
- **Estados de aplicación**: Planificado, Aplicado, Completado
- **Programación de refuerzos**: Fechas automáticas para próximas aplicaciones

### 📅 Eventos de Vida
- **Nacimientos**: Registro automático al crear un animal
- **Mortandades**: Registro con causa de muerte
- **Trazabilidad completa**: Historial de eventos por animal

### 🧬 Gestión de Razas
- **Catálogo de razas**: Base de datos completa de razas ganaderas
- **Clasificación**: Carne, lechera, doble propósito
- **Estadísticas**: Pesos promedio por raza y género
- **Análisis**: Cantidad de animales por raza

## 🗂️ Estructura del Módulo

### Modelos de Datos

1. **livestock.animal** - Registro principal de cada animal
2. **livestock.breed** - Catálogo de razas
3. **livestock.event** - Eventos de nacimiento y muerte
4. **livestock.health.log** - Registros sanitarios
5. **livestock.weighing** - Control de pesajes

### Vistas Principales

- **Vista Kanban**: Gestión visual por estados o actividades
- **Vista Lista**: Tablas detalladas con filtros avanzados
- **Vista Formulario**: Fichas completas con pestañas organizadas
- **Vista Gráfico**: Evolución de peso y análisis estadísticos
- **Vista Pivot**: Análisis multidimensional de datos

## 🚀 Instalación

### Dependencias
- Odoo 18.0 Community o Enterprise
- Módulo `farm_management` (para gestión de campos y lotes)
- Módulo `product` (para productos farmacológicos)

### Pasos de Instalación
1. Copiar el módulo en el directorio de addons de Odoo
2. Actualizar la lista de módulos
3. Instalar el módulo "Gestión Ganadera - Trazabilidad de Ganado"

## 📋 Flujo de Trabajo Recomendado

### 1. Configuración Inicial
1. **Configurar razas**: Definir las razas que se manejan en el establecimiento
2. **Configurar productos**: Registrar medicamentos y productos veterinarios
3. **Configurar campos y lotes**: Utilizar el módulo `farm_management`

### 2. Registro de Animales
1. **Crear animal**: Asignar caravana única, raza, género y fecha de nacimiento
2. **Asignar ubicación**: Campo y lote actual
3. **Definir actividad**: Cría, Invernada, Feedlot o Mixto

### 3. Operaciones Diarias
1. **Pesajes**: Registrar pesos con frecuencia para calcular GDM
2. **Registros sanitarios**: Documentar vacunas, tratamientos y desparasitaciones
3. **Movimientos**: Actualizar ubicación cuando cambien de lote o campo

### 4. Eventos Especiales
1. **Nacimientos**: Se registran automáticamente al crear un animal
2. **Mortandades**: Usar botón "Registrar Mortandad" desde la ficha del animal
3. **Ventas**: Marcar animales como "Vendidos" cuando corresponda

## 📊 Reportes y Análisis

### Indicadores Clave (KPIs)
- **GDM promedio** por raza y período
- **Tasa de mortandad** por lote y época
- **Distribución de animales** por actividad y ubicación
- **Evolución de peso** individual y grupal
- **Costos sanitarios** por animal y período

### Filtros y Agrupaciones
- Por **estado** (activo, vendido, muerto)
- Por **raza** y **género**
- Por **actividad** (cría, invernada, feedlot)
- Por **ubicación** (campo, lote)
- Por **fechas** (mes, año, período personalizado)

## 🔧 Personalización

### Campos Adicionales
El módulo está diseñado para ser fácilmente extensible. Se pueden agregar campos adicionales según las necesidades específicas:

- **Campos genéticos**: ADN, genealogía extendida
- **Campos comerciales**: Precio de compra, valor estimado
- **Campos productivos**: Producción lechera, índices reproductivos

### Integración con Otros Módulos
- **Contabilidad**: Costos de producción y valorización de stock
- **Inventario**: Movimientos de animales como productos
- **Compras/Ventas**: Facturación de animales
- **Activos**: Depreciación de reproductores

## 🛡️ Seguridad

### Permisos por Defecto
- **Usuarios**: Acceso completo de lectura y escritura
- **Configuración**: Administración de razas y productos

### Validaciones Implementadas
- **Caravana única**: No se permiten duplicados
- **Fechas lógicas**: Validación de fechas de nacimiento y eventos
- **Consistencia de datos**: Validación de relaciones madre-cría
- **Pesos razonables**: Límites en los valores de peso

## 🆘 Soporte y Documentación

### Ayuda Contextual
Cada vista incluye textos de ayuda y tooltips explicativos para facilitar el uso.

### Casos de Uso
- **Estancias ganaderas**: Gestión completa de rodeos
- **Feedlots**: Control intensivo de engorde
- **Criaderos**: Seguimiento genealógico y reproductivo
- **Campos mixtos**: Diferentes actividades por lote

## 🔄 Actualizaciones Futuras

### Funcionalidades Planificadas
- **Reportes avanzados**: Dashboard ejecutivo con gráficos
- **Integración IoT**: Chips RFID y balanzas automáticas
- **Análisis predictivo**: Proyecciones de peso y rendimiento
- **App móvil**: Registro desde el campo
- **Alertas automáticas**: Notificaciones de eventos críticos

### Mejoras Continuas
- Optimización de performance para grandes volúmenes
- Nuevas vistas y filtros según feedback de usuarios
- Integración con sistemas de gestión externos
- Exportación a formatos estándar del sector

---

**Desarrollado para el sector agropecuario argentino** 🇦🇷

*Este módulo ha sido diseñado siguiendo las mejores prácticas de desarrollo de Odoo y las necesidades específicas del sector ganadero.*
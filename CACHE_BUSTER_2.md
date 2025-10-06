# Cache Buster - Force Server Update

## Timestamp: 2025-10-06 00:41:00

### Cambios Confirmados en Código Local:
- ✅ TODOS los tags `<tree>` han sido cambiados a `<list>`
- ✅ TODOS los `view_mode` con 'tree' han sido actualizados a 'list'
- ✅ TODOS los xpath con '//tree' han sido cambiados a '//list'
- ✅ TODOS los IDs de vista '*_tree' han sido cambiados a '*_list'

### Verificación Técnica:
```bash
# Búsqueda exhaustiva realizada:
Get-ChildItem -Recurse -Include "*.xml" | Select-String -Pattern "tree" -CaseSensitive

# Resultado: Solo referencias a vistas base de Odoo (correcto)
# - mrp.mrp_bom_tree_view (vista base de MRP)
# - mrp.mrp_production_tree_view (vista base de MRP)
```

### Estado del Repositorio:
- **Último commit**: 9858eaf
- **Estado**: Everything up-to-date
- **Migración**: 100% completa en código fuente

### Para el servidor de Odoo:
Si persiste el error, el servidor necesita:
1. **git pull** para obtener la última versión
2. **Update Apps List** para limpiar metadata cache
3. **Restart Odoo service** para limpiar cache completo

### Archivos Críticos Verificados:
- farm_management/views/farm_contract_views.xml:68 ✅ `<list>` confirmado
- Todos los demás archivos XML ✅ Libres de `<tree>` tags

**El código fuente está 100% correcto para Odoo 18.**
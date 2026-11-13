# Plan — Sistema de Bodega · Liceo A-26 Oscar Bonilla

Sistema para el pañol: préstamo de herramientas a los cursos de 3° y 4° medio.
Django + SQLite, sin dependencias extras.

## Colores institucionales
- Azul marino `#0F2A4A` — navbar, cabeceras, títulos.
- Amarillo `#F5B700` — acentos, botones, préstamos activos.
- Blanco `#FFFFFF` — fondo, tarjetas, texto sobre azul.

## Apps
1. `inventario` — herramientas disponibles.
2. `alumnos` — estudiantes (3° y 4° medio).
3. `historial` — préstamos y devoluciones.

## Modelos
- `alumnos.Alumno`: nombre, apellido, curso (3° Medio / 4° Medio).
- `inventario.Herramienta`: nombre, descripcion, cantidad_total, ubicacion. Prop. `disponibles`.
- `historial.Prestamo`: alumno FK, herramienta FK, cantidad, fecha_prestamo, fecha_devolucion, devuelto. Valida stock y método `devolver()`.

## Decisiones
- Préstamos a nombre de alumno individual.
- Login con auth nativo de Django (todo `login_required`).
- App de herramientas se llama `inventario` (el proyecto ya usa `bodega`).

## Vistas / URLs
- `/` dashboard (contadores).
- `/inventario/` listar + crear + editar + eliminar.
- `/alumnos/` listar + crear + editar + eliminar.
- `/historial/` listar + crear préstamo + devolver.
- `/accounts/login` y `/accounts/logout`.
- `/admin/` registro de todos los modelos.

## Pasos de implementación
1. Crear apps.
2. Configurar `settings.py` (apps, auth, `es`, `America/Santiago`, templates/static).
3. Modelos → `makemigrations` → `migrate`.
4. Admin + forms + views + urls + templates + CSS.
5. Superusuario + datos de ejemplo.
6. Verificación con `runserver` / `check`.

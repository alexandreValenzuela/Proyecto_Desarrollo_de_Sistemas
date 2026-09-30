# NeoED — Handoff para `feat/gui`

> Documento de traspaso. Al leerlo vas a saber: qué hace el sistema, qué se rompió y ya se arregló, qué falta, y qué archivos son tuyos.
>
> Fecha: 2026-09-29 · Rama del receptor: `feat/gui` · Ramas del emisor: `feat/datos` (mergeada) y `feat/seguridad` (en curso)

---

## 1. Contexto rápido

**NeoED** es un ABM escolar de escritorio. Python 3.13 + PySide6 + SQLite.

```
main.py              entrada: pregunta consola/interfaz, luego Landing → Login → Principal
auth/                autenticacion.login_unificado, permisos (decorador + tiene_permiso)
models/              Alumno, Personal, Curso, Cargo, Acceso
database/            connection (contextmanager), setup (7 tablas), seed
gui/                 estilos.py, componentes.py, 4 ventanas, 6 vistas
cli/consola.py       menú por terminal, replica las acciones de la GUI
```

Base de datos: 7 tablas (`cargo`, `curso`, `alumnos`, `personal`, `notas`, `accesos`, `ausencias`).
`notas` ya tiene modelo (`models/nota.py`); `ausencias` sigue sin modelo ni vista.

Niveles de permiso, definidos en `database/seed.py`:

| Cargo | `nivel_permisos` |
| :--- | :---: |
| Administrador | 10 |
| Profesor | 5 |
| Preceptor | 3 |
| Alumno | 0 |

---

## 2. Reglas de negocio (no son negociables)

1. **Las cuentas de personal las crea un administrador.** No hay auto-registro público para profesores, preceptores ni admins.
2. **El botón "Crear Cuenta" del inicio es solo para alumnos.** El registro público siempre entra con `autorizado = 0`.
3. **Un alumno con `autorizado = 0` no puede loguearse.** `Alumno.login` lanza `PermisoDenegadoError` y registra el intento fallido en `accesos`.
4. **Autorizar alumnos requiere nivel ≥ 3** (preceptor o superior). Está en `models/alumno.py` como `NIVEL_MINIMO_PARA_AUTORIZAR`.
5. **Asignar cargos requiere nivel ≥ 10.** Está en `Personal.asignar_cargo()`.
6. **El alta institucional de alumnos usa `autorizado = 1`.** Loader directo desde el menú.

---

## 3. Lo que YA está hecho (no lo rehagas)

### 3.1 Contratos compartidos — commit `749f9b3`, en `main`

Tu amigo debe tener esto. Verificá con `git log --oneline -1` antes de empezar: tiene que mostrar `749f9b3` o posterior.

**`auth/permisos.py`**
```python
def tiene_permiso(usuario, nivel_minimo):
    if usuario is None:
        return False
    return usuario.get("nivel_permisos", 0) >= nivel_minimo
```

**`gui/componentes.py`**
```python
def alerta_error(parent, titulo, mensaje):    # QMessageBox.warning
def alerta_exito(parent, titulo, mensaje):    # QMessageBox.information
```

Usalos. No los reimplementes.

### 3.2 Capa de datos — commit `65018ff`, ya mergeado a `main`

Cinco archivos. **Ninguno es tuyo.** No hay conflicto posible.

| Archivo | Qué se cambió |
| :--- | :--- |
| `database/seed.py` | **Agregada la carga de 6 cursos.** Antes la tabla estaba vacía y por eso NO SE PODÍA CREAR NINGÚN ALUMNO. |
| `models/curso.py` | Agregados `guardar()`, `obtener_por_id()`, `eliminar()`, validación de formato. |
| `database/connection.py` | **Reescrito.** La conexión ahora se cierra sola al salir del `with`. |
| `models/alumno.py` | `except sqlite3.Error` agregado al `guardar()`. |
| `models/personal.py` | `except sqlite3.Error` agregado al `guardar()`. |

### 3.3 Modelo de Notas — commit `feat/notas`, ya mergeado a `main`

Nuevo archivo: **`models/nota.py`**. La tabla `notas` **ya no es código muerto**: tiene modelo completo.

```python
Nota(dni, materia, nota, comentario=None)   # comentario es opcional
nota.guardar() / nota.actualizar() / Nota.eliminar(nota_id)
Nota.obtener_por_alumno(dni) / Nota.obtener_todas() / Nota.obtener_por_id(id)
Nota.existe(dni, materia) / Nota.eliminar_por_alumno(dni)
```

**El esquema de `notas` cambió.** Ahora tiene `dni` (FK a `alumnos`), `comentario` acepta NULL, y una restricción `UNIQUE(dni, materia)`: un alumno no puede tener dos notas de la misma materia. Para cambiar una nota, usá `actualizar()` sobre la existente, no `guardar()` de nuevo.

Si ya tenés una vista de notas, **revisala**: cualquier consulta que lea `notas` directo necesita el `dni`. Las notas se cargan por alumno, no todas juntas.

### 3.4 Hashing de contraseñas — commit `e15e18f`, rama `feat/seguridad`

**Las contraseñas ya NO se guardan en texto plano.** PBKDF2-HMAC-SHA256, 260.000 iteraciones, sal aleatoria de 16 bytes por usuario.

Nuevo archivo: **`auth/passwords.py`**
```python
hashear(contrasena)            # -> "pbkdf2_sha256$260000$<sal>$<hash>"
verificar(contrasena, hash)    # comparacion de tiempo constante
es_hash_contrasena(valor)
validar_contrasena(contrasena) # exige 6 caracteres minimo
```

Nuevo archivo: **`database/migraciones.py`** — agrega la columna `password_hash` y hashea las contraseñas que ya estaban en plano. Es **idempotente**: correrla de nuevo no toca nada.

**Lo que esto significa para vos — importante:**

- `Alumno(...)` y `Personal(...)` **siguen recibiendo `password` en texto plano**. El modelo hashea solo. **No cambies nada** en cómo construís los objetos.
- Los login ahora buscan por DNI y verifican el hash en Python. Antes comparaban en SQL.
- La columna `password` queda vacía en la base. La `password_hash` es la que importa.
- Si algún día querés resetear una contraseña, usá `hashear()`.

---

## 4. Dos hechos que cambian cómo escribís código

### 4.1 El combo de cursos ya tiene datos

`Curso.obtener_todos()` devuelve `1A1A`, `1B1B`, `2A2A`, `2B2B`, `3A3A`, `3B3B`. Podés probar el formulario real sin esperar el merge.

El CHECK de `database/setup.py` en la tabla `curso` exige 4 caracteres con patrón `[0-9][A-Z][0-9][A-Z]`. Nada más entra.

### 4.2 Ya NO hace falta `conexion.commit()`

El contextmanager de `database/connection.py` commitea automáticamente al salir del bloque. Los 22 call sites viejos que sí llaman `conexion.commit()` siguen funcionando (es idempotente, no rompe), pero **en código nuevo no lo agregues por costumbre**.

---

## 5. Tu trabajo — rama `feat/gui`

Tus archivos: `gui/`, `main.py`, `cli/`. Ninguno se solapa con `feat/datos`.

### Bloque A — Navegación rota (prioridad alta)

| # | Archivo: línea | Qué está roto |
| :--- | :--- | :--- |
| A1 | `main.py:59-61` | "Crear Cuenta" apunta a `ir_a_login`. Debe ir a `VentanaRegistro`, que hoy es **código muerto**. Agregá el callback `ir_a_registro` al patrón existente. |
| A2 | `gui/ventana_principal.py:63` | "Crear Alumno" salta a `stack_global` índice 1 y abre el dashboard en `VistaBienvenido`, no en el alta. Cambialo a `_abrir_seccion(2)`. |
| A3 | `gui/ventana_principal.py:150-193` | Los 6 botones del sidebar son `setCheckable(True)` sin grupo exclusivo: al navegar queda "activo" el anterior junto al nuevo. Envolvelos en un `QButtonGroup`. |
| A4 | `gui/vistas/vista_cargar_alumnos.py:118` y `gui/vistas/vista_registrar_personal.py:135` | Botón "Volver" existe pero **no tiene `.connect()`**. Botón muerto. |
| A5 | `gui/vistas/vista_ver_alumnos.py:88` | Llama a `_volver_al_menu()` pero `_menu_callback` nunca se setea: nadie invoca `set_menu_callback`. Cablealo desde `ventana_principal.py`. |
| A6 | `gui/ventana_principal.py:180-193` | "Ver Profesores" y "Cargar / Ver Notas" apuntan ambos al índice 5, así que la 2ª sección nunca muestra nada distinto. Separalos en dos placeholders. |
| A7 | `gui/ventana_login.py:41` | Placeholder dice "Nombre de usuario" pero el login busca por DNI. Corregí el texto. |
| A8 | `cli/consola.py` | La opción "0) Cerrar sesión" mata el proceso en vez de volver al login. El menú dice una cosa y hace otra. |

### Bloque B — Formularios que ahora sí guardan

Con los fixes de la capa de datos, los formularios **dejan de fallar**, pero ahora guardan basura. Hay que poner los datos reales.

**`gui/vistas/vista_cargar_alumnos.py:146-156`** — hoy hardcodea:
```python
apellido="", direccion="", telefono="0000000000", fecha_nacimiento="2000-01-01"
```
Sacalos y agregá los campos reales que `Alumno.validar_datos()` exige.

**`gui/ventana_registro.py:139-149`** — dos problemas:
1. **Los campos están cruzados.** `entradas[0]` es "Nombre Completo" y se pasa como `dni`; `entradas[1]` es "DNI / Documento" y se pasa como `apellido`.
2. Mismos valores hardcodeados que arriba.

Mantené `autorizado=0` en el registro público (regla de negocio 2).

> ⚠️ **Ojo con la altura.** El formulario de registro va de 4 filas a 8. La ventana tiene 900px fijos y **va a desbordar**. Necesitás `QScrollArea` o compactar espaciado. Es decisión de diseño tuya.
>
> ✅ **Resuelto:** el registro público **sí** pide dirección y teléfono. Ambos son obligatorios y el modelo no se relaxes. Pedilos con los labels correctos.

### Bloque C — Sidebar por permisos

Usá `tiene_permiso()` de `auth/permisos.py`. **Ocultar** los botones no permitidos (no deshabilitarlos, no bloquear al clic).

| Sección | Nivel mínimo |
| :--- | :---: |
| Ver Alumnos / Cargar Alumnos | todos |
| Autorizar Alumnos | 3 |
| Registrar Personal | 10 |
| Profesores / Notas | todos (son placeholders) |

**Dos lugares, no uno:**
- El **sidebar** (`gui/ventana_principal.py:150-193`)
- El **menú central** (`gui/ventana_principal.py:50-93`) — hoy tiene los 4 botones fijos y expone "Registrar Personal" a cualquiera. **Hoy un alumno con nivel 0 puede entrar a esa vista y crear un administrador nuevo.** Ese es el agujero más grave de la app.

Defensa en profundidad: agregá la validación de nivel también en `gui/vistas/vista_registrar_personal.py:155` (hoy no consulta el nivel) y en `gui/vistas/vista_autorizar_alumnos.py:75`.

### Bloque D — Alertas modales (Escudo de Datos)

**Corrección importante sobre el enunciado:** los formularios **NO crashean** por datos inválidos. `ValueError` ya está capturado; si escribís letras en el DNI, `Alumno.__init__` hace `int(dni)`, lanza `ValueError` y la vista la captura. Lo que falta es la **alerta gráfica**: hoy el error se escribe en un `lbl_error` rojo chico, sin diálogo ni foco.

Lo que SÍ crashea: los `except` solo cazan `(ValueError, RuntimeError)`. Un `sqlite3.OperationalError` (base bloqueada, `no such table`) no está en ninguna tupla y **mata la app**.

Qué hacer:
1. Reemplazá los `lbl_error.setText()` por `alerta_error(...)`, **conservando el label inline** como refuerzo. Un usuario escribiendo 8 campos no debería perder el foco a un modal por cada tecla.
2. Ampliá las tuplas a incluir `sqlite3.Error`.
3. Agregá un `except Exception` envolviendo `_intentar_registro` completo en cada vista. Es la red que garantiza el "NO PUEDE cerrarse".

Los 5 formularios: `vista_cargar_alumnos`, `vista_registrar_personal`, `vista_autorizar_alumnos`, `ventana_registro`, `ventana_login`.

---

## 6. Fuera de alcance (documentado, NO lo hagas)

| Tema | Riesgo actual |
| :--- | :--- |
| ~~Hashing de contraseñas~~ | **RESUELTO** en `feat/seguridad`. Ver §3.3. |
| Refactor a ventana única | `main.py` mantiene un dict de ventanas top-level y las muestra con `.show()`. Contradice la spec §1.2, que dice explícitamente que ese patrón falló. |
| Doble fila en `accesos` | `auth/autenticacion.py:19-25`: si `Personal.login` falla ya escribió un acceso fallido, y después `Alumno.login` escribe el exitoso. Cada login de alumno deja **2 filas**. |
| `notas` | **RESUELTO**: modelo en `models/nota.py`. Ver §3.3. La vista sigue siendo tuya. |
| `ausencias` | Tabla creada, **sin modelo ni vista**. |
| Doble fila en `accesos` | **Sigue pendiente.** Ver §6.1. |
| Tests | No hay ninguno. |
| `.db` versionada | Ya resuelta en `main` (commit `9b61f5a`). |

### 6.1 Doble fila en `accesos` — pendiente, archivo NUESTRO

Verificado empíricamente, no es una sospecha:

| Escenario | Filas que deja | Correcto |
| :--- | :---: | :---: |
| Login de personal válido | 1 | 1 ✅ |
| Login de alumno válido | **2** (una fallida + una exitosa) | 1 ❌ |
| Login con DNI inexistente | **2** (dos fallidas) | 1 ❌ |

Causa: `auth/autenticacion.py:19` llama a `Personal.login` para probar. Si el DNI es de un alumno, ese intento **falla y queda registrado** en `accesos` antes de que `Alumno.login` escriba el exitoso. Cada login de alumno duplica, y **los intentos fallidos se cuentan doble** — que es justo el dato que sirve para detectar fuerza bruta.

**No lo toques**: `auth/` es scope nuestro. Si te bloquea alguna prueba, avisame y lo arreglo.

---

## 7. Decisiones que hay que tomar

**Nada pendiente.** Todo lo bloqueante ya está resuelto.

**Ya decidido — no lo reviertas:**
- Los botones sin permiso se **ocultan** (no se deshabilitan)
- Autorizar alumnos: **nivel ≥ 3** (preceptor o superior)
- Registrar personal: **nivel ≥ 10**
- El registro público **exige** dirección y teléfono. `models/alumno.py` **NO se relaja**; pedilos en el formulario.

**Lo único que es decisión tuya (no bloquea):** cómo resolver el desborde del formulario de registro — `QScrollArea` o compactar espaciado.

---

## 8. Comandos

```powershell
git fetch origin
git checkout main
git pull
git log --oneline -1        # debe mostrar e15e18f o posterior
git checkout -b feat/gui
```

Al terminar:

```powershell
git add gui/ main.py cli/
git commit -m "feat: fix navigation, permission-aware sidebar, modal alerts"
```

El emisor hace el merge. `feat/datos`, `feat/seguridad` y `feat/gui` no comparten archivos, así que **el merge es limpio por construcción**.

> Nota: `main.py` es tuyo para la navegación, pero ya tiene un commit mío (`e15e18f`) que agrega `migraciones()` al arranque. Si lo tocás, mantené esas dos líneas: la migración tiene que correr antes del seed.

---

## 9. Checklist de verificación

Antes de dar por terminada tu rama:

- [ ] "Crear Cuenta" abre el registro, no el login
- [ ] "Crear Alumno" del menú abre el alta, no la bienvenida
- [ ] Solo un botón del sidebar queda activo a la vez
- [ ] Los tres "Volver" regresan al menú
- [ ] "Ver Profesores" y "Notas" muestran secciones distintas
- [ ] El login dice "DNI", no "Nombre de usuario"
- [ ] Guardar un alumno institucional persiste con `autorizado=1`
- [ ] El registro público persiste con `autorizado=0` y **no** puede loguearse hasta ser autorizado
- [ ] El registro público pide dirección y teléfono
- [ ] Un usuario del seed puede loguearse con su contraseña original (`11111111` / `1234`)
- [ ] Un preceptor (3) **no** ve "Registrar Personal"
- [ ] Un alumno (0) no ve "Autorizar Alumnos" ni "Registrar Personal"
- [ ] Campo obligatorio vacío → cartel, no crashea
- [ ] Letras en un campo numérico → cartel, no crashea
- [ ] Ningún `except` queda en `(ValueError, RuntimeError)` solamente

# Especificación Maestra de Arquitectura y Orquestación de Agentes de IA
**Proyecto:** NeoED - Plataforma EdTech Modular en Python (PySide6)  
**Versión:** 2.0  
**Estado:** Documento de Control y Orquestación Activa  

---

## 1. Visión y Objetivo del Documento

Este documento constituye la **Fuente Única de Verdad (Single Source of Truth - SSOT)** tanto para el desarrollo del proyecto **NeoED** como para la **orquestación operativa de los Agentes de Inteligencia Artificial** involucrados en su construcción.

El objetivo principal es guiar, coordinar y auditar la ejecución distribuida de tareas de desarrollo entre múltiples agentes especializados (Frontend, Backend, QA y UI/UX), garantizando la máxima coherencia arquitectónica, estricta adherencia visual y modularidad limpia en Python.

---

## 2. Especificaciones Técnicas y de Diseño (Tech & UI Stack)

### 2.1 Stack Tecnológico
* **Lenguaje Principal:** Python 3.10+
* **Framework Gráfico:** PySide6 (Qt para Python)
* **Arquitectura de Interfaz:** Ventana Única (`QMainWindow`) con navegación mediante contenedores dinámicos (`QStackedWidget` y layouts dinámicos).
* **Gestión de Estado:** Patrón modular desacoplado (Model-View-Controller / Observer).

### 2.2 Tokens Visuales e Identidad Gráfica (Draw.io SSOT)
La fuente de verdad estética proviene directamente de los diagramas y especificaciones de Draw.io. Todos los agentes visuales y de frontend deben aplicar estrictamente los siguientes parámetros:
* **Color Primario (Acento):** `#66B2FF` (Azul NeoED).
* **Tipografía Técnica y de Código:** `Cascadia Code`.
* **Tipografía General de Sistema:** Sans-Serif limpia (`Segoe UI`, `Inter` o `Roboto`).
* **Estilo de Interfaz:** Minimalista, profesional, oscuro/neutro con contrastes claros en puntos de interacción.

### 2.3 Principios Arquitectónicos
1. **Patrón de Ventana Única:** La aplicación **nunca** debe abrir ventanas emergentes secundarias para la navegación principal. Toda transición se realiza mediante reemplazo o cambio de contenedores dinámicos dentro del marco principal.
2. **Modularidad Estricta:** Desacoplamiento total entre componentes de interfaz (`ui/`), lógica de negocio (`core/`), clientes de modelos/IA (`services/`) y modelos de datos (`models/`).
3. **Tipado Estático:** Uso obligatorio de anotaciones de tipo (`typing`) en Python para prevenir errores en tiempo de ejecución.

---

## 3. Framework de Orquestación Multi-Agente (AI Orchestration Model)

Para cumplir con el objetivo del proyecto de manera eficiente y consistente, el flujo de trabajo se divide entre agentes de IA especializados bajo la supervisión del Agente Orquestador.

```
                  +-----------------------------------+
                  |  AGENTE ORQUESTADOR (Lead Arch)  |
                  +-----------------------------------+
                                    |
        +---------------------------+---------------------------+
        |                           |                           |
+---------------+           +---------------+           +---------------+
| AGENTE UI/UX  |           | AGENTE FRONT  |           | AGENTE BACK   |
|   & DESIGN    |           |   (PySide6)   |           |   & LOGIC     |
+---------------+           +---------------+           +---------------+
        |                           |                           |
        +---------------------------+---------------------------+
                                    |
                  +-----------------------------------+
                  |    AGENTE QA & CODE REVIEWER      |
                  +-----------------------------------+
```

### 3.1 Roles y Responsabilidades de los Agentes

#### 🛡️ 1. Agente Orquestador (Lead Architect)
* **Misión:** Descomponer los requerimientos generales en tareas atómicas, asignar contextos específicos a cada agente y verificar la integración final.
* **Filtro de Entrada:** Valida que cada prompt enviado a los demás agentes contenga las restricciones globales (`#66B2FF`, Ventana Única, PySide6, Cascadia Code).

#### 🎨 2. Agente Design & UI Tokens Auditor
* **Misión:** Mapear y extraer componentes, medidas y estilos desde las especificaciones visuales de Draw.io.
* **Entregable:** Hojas de estilo QSS (`style.qss`), constantes de color y especificaciones de diseño listas para implementación PySide6.

#### 💻 3. Agente Frontend (PySide6 Specialist)
* **Misión:** Implementar las vistas, widgets personalizados y transiciones de contenedores dinámicos en PySide6.
* **Regla de Oro:** Garantizar que la interfaz sea fluida, responda al redimensionamiento y aplique el color `#66B2FF` y la fuente `Cascadia Code`.

#### ⚙️ 4. Agente Backend & Logic Specialist
* **Misión:** Crear los motores de servicios, comunicación con APIs, procesamiento de datos y la arquitectura interna de la plataforma EdTech.
* **Entregables:** Módulos de Python puros, asíncronos y desacoplados de la GUI.

#### 🧪 5. Agente QA, Testing & Refactoring
* **Misión:** Revisar el código generado, ejecutar análisis estático (`mypy`, `pylint`), verificar que no haya regresiones y confirmar que la estructura de ventana única permanezca intacta.

---

## 4. Protocolo Paso a Paso para la Ejecución de Tareas

Cada ciclo de trabajo debe seguir estrictamente estas 5 fases:

1. **Fase 1: Especificación y Extracción (Design Phase)**  
   El Agente UI/UX extrae o valida los tokens visuales del diagrama Draw.io y genera las variables de estilo.

2. **Fase 2: Desglose de Tareas (Orchestration Phase)**  
   El Agente Orquestador asigna la sub-tarea al Agente Frontend o Backend especificando interfaces de contrato (APIs internas, señales y slots de PySide6).

3. **Fase 3: Desarrollo Modular (Execution Phase)**  
   Los Agentes Frontend y Backend desarrollan de forma independiente sus respectivos módulos sin modificar archivos fuera de su alcance asignado.

4. **Fase 4: Integración en Ventana Única (Integration Phase)**  
   Se integra el nuevo widget o lógica dentro del contenedor dinámico correspondiente en la `QMainWindow`.

5. **Fase 5: Auditoría y Aprobación (QA Phase)**  
   El Agente QA valida el código contra las reglas del proyecto (colores, fuentes, tipado, modularidad).

---

## 5. Directivas de Sistema y Prompts Directores para AIs

Al invocar o alimentar a cualquier modelo de IA dentro de este flujo, se debe adjuntar el siguiente encabezado de directivas:

```text
[DIRECTIVA OBLIGATORIA PARA EL AGENTE DE IA]
- Proyecto: NeoED (Plataforma EdTech en PySide6/Python)
- Interfaz: Patron de Ventana Única con contenedores dinámicos (QStackedWidget).
- Tokens Visuales: Primario `#66B2FF`, Fuente de Código `Cascadia Code`.
- Fuente de Verdad Visual: Especificaciones de Draw.io.
- Principio de Código: Modularidad estricta, desacoplamiento GUI/Lógica, anotaciones de tipo completas.
- Instrucción: Genera código directamente ejecutable, limpio y mantenible sin romper la arquitectura existente.
```

---

## 6. Estructura de Proyecto Recomendada

```text
neoed/
├── assets/
│   ├── drawio/               # Diagramas como fuente de verdad
│   └── styles/               # Archivos QSS y tokens (#66B2FF)
├── core/                     # Lógica de negocio EdTech y servicios
│   ├── __init__.py
│   ├── orchestrator.py
│   └── services.py
├── ui/                       # Componentes PySide6
│   ├── __init__.py
│   ├── main_window.py        # Ventana única contenedor
│   ├── containers/           # Contenedores dinámicos intercambiables
│   └── widgets/              # Componentes visuales atómicos
├── tests/                    # Pruebas unitarias e integración
├── main.py                   # Punto de entrada de la aplicación
└── README.md
```

---

## 7. Verificación de Cumplimiento del Documento

| Criterio | Estado | Mecanismo de Control |
| :--- | :---: | :--- |
| **Orquestación AI Definida** | ✅ | Roles, roles inter-agente y protocolo de 5 fases |
| **Especificaciones Técnicas** | ✅ | Python 3.10+, PySide6, Ventana Única |
| **Tokens Visuales Integrados** | ✅ | Color `#66B2FF`, `Cascadia Code`, Draw.io SSOT |
| **Estructura de Trabajo** | ✅ | Árbol modular e instrucciones directas para IA |

# ESPECIFICACIÓN VISUAL GUI

## 1. Objetivo

El presente documento define la especificación técnica, visual y de experiencia de usuario (UI/UX) para la remodelación y adaptación completa de la interfaz gráfica de usuario (GUI) de la aplicación de escritorio **NeoED**, desarrollada en Python 3 con **PySide6**.

Su propósito es servir como **guía estricta e inequívoca de implementación** para el agente de programación (OpenCode). El objetivo primordial es transformar el código GUI existente para reproducir con absoluta fidelidad visual, estructural y proporcional el diseño vectorial y funcional definido en el archivo de diseño **Draw.io**.

---

## 2. Fuente de Verdad y Jerarquía de Autoridad

Para la resolución de cualquier conflicto durante la refactorización de la interfaz, OpenCode deberá regirse por la siguiente jerarquía estricta de prioridad:

1. **DRAW.IO (Archivo fuente de diagramas)**: Constituye la **Fuente de Verdad Visual y de UX**. Dicta dimensiones, posiciones relativas, colores, familias tipográficas, tamaños de fuente, proporciones, disposición de elementos y flujos de pantalla.
2. **ESPECIFICACIÓN FUNCIONAL EXISTENTE**: Constituye la **Fuente de Verdad del Comportamiento del Sistema**. Dicta la lógica de negocio, persistencia en base de datos, validación de formularios, hashing de contraseñas, control de roles/permisos e integración con modelos.
3. **CÓDIGO GUI ACTUAL**: Es únicamente una **referencia de implementación técnica existente**. **NO es una autoridad sobre el diseño**.

> ⚠️ **REGLA DE ORO DE REFACTORIZACIÓN PARA OPENCODE**:
> Si el código actual entra en contradicción visual o estructural con el diseño de Draw.io, **el código debe ser modificado o reescrito inmediatamente**. Queda explícitamente autorizado eliminar widgets obsoletos, reorganizar layouts de PySide6, reemplazar componentes visuales antiguos, reestructurar `gui/estilos.py` y `gui/componentes.py`, y alterar la navegación entre ventanas. **No se debe conservar código visual antiguo únicamente por mantener compatibilidad con la versión anterior.**

---

## 3. Reglas Generales de Diseño y Sistema Visual

### 3.1. Dimensiones Globales de la Ventana
- **Resolución Canvas Base**: `1600 px` (ancho) x `900 px` (alto).
- **Relación de Aspecto**: `16:9`.
- **Comportamiento**: Centrado en pantalla al iniciar (`QScreen.availableGeometry()`). Tamaño estático o escalable proporcionalmente manteniendo el lienzo principal centrado en un contenedor contenedor de fondo completo (`QStackedWidget` dentro de un marco contenedor).

### 3.2. Paleta de Colores Oficial (Tokens Visuales)

| Token de Color | Código HEX / Valores RGB | Elemento Aplicado | Estilo CSS / QSS Recomendado |
| :--- | :--- | :--- | :--- |
| **Fondo Global (Canvas)** | `#66B2FF` / `rgb(102, 178, 255)` | Canvas principal de todas las pantallas | `background-color: #66B2FF;` |
| **Botón Primario (Fondo)** | `#dae8fc` / `rgb(218, 232, 252)` | Botón "Iniciar Sesion", "Ingresar", "Crear Alumno", "Guardar Alumno", "Registrar Usuario" | `background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #dae8fc, stop:1 #7ea6e0);` |
| **Botón Primario (Borde)** | `#6c8ebf` / `rgb(108, 142, 191)` | Borde de Botones Primarios | `border: 2px solid #6c8ebf;` |
| **Botón Secundario (Fondo)**| `#bac8d3` / `rgb(186, 200, 211)` | Botones de Menú: "Crear Cuenta", "Ver Alumnos", "Autorizar Alumnos", "Registrar Personal" | `background-color: #bac8d3;` |
| **Botón Secundario (Borde)**| `#23445d` / `rgb(35, 68, 93)` | Borde de Botones Secundarios | `border: 2px solid #23445d;` |
| **Botón Destructivo/Volver (Fondo)** | `#f8cecc` / `rgb(248, 206, 204)` | Botón "Volver" | `background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f8cecc, stop:1 #ea6b66);` |
| **Botón Destructivo/Volver (Borde)** | `#b85450` / `rgb(184, 84, 80)` | Borde de Botón "Volver" | `border: 2px solid #b85450;` |
| **Botón Éxito/Filtro (Fondo)**| `#d5e8d4` / `rgb(213, 232, 212)` | Botón "Filtrar" | `background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #d5e8d4, stop:1 #97d077);` |
| **Botón Éxito/Filtro (Borde)**| `#82b366` / `rgb(130, 179, 102)` | Borde de Botón "Filtrar" | `border: 2px solid #82b366;` |
| **Campos de Entrada (Fondo)**| `#ffffff` / `rgb(255, 255, 255)` | `QLineEdit` y `QComboBox` | `background-color: #ffffff;` |
| **Campos de Entrada (Borde)**| `#000000` / `rgb(0, 0, 0)` | Borde de Inputs y Tablas | `border: 2px solid #000000;` |
| **Texto Principal** | `#000000` / `rgb(0, 0, 0)` | Títulos, etiquetas, texto de botones, contenido de celdas | `color: #000000;` |

### 3.3. Tipografía y Estilos de Texto
- **Tipografía Unificada**: `Cascadia Code` (Monospaced, estética limpia y técnica). *Fallback: Consolas, Courier New, monospace*.
- **Jerarquía de Tamaños de Fuente**:
  - **Título Principal App (`NeoED`)**: `60 px`, Negrita (`bold`).
  - **Títulos de Ventana de Registro / Listado**: `50 px`, Negrita (`bold`).
  - **Texto Botones Grandes (Landing / Menú)**: `40 px`, Regular.
  - **Texto Botones Medianos (Login / Formularios)**: `25 px` a `35 px`, Regular.
  - **Texto Inputs Formulario**: `20 px` a `25 px`, Regular.
  - **Texto Filtros / Acciones Secundarias**: `18 px` a `20 px`, Regular.
  - **Texto Celdas de Tablas**: `14 px`, Regular.

### 3.4. Bordes, Radios y Espaciados Generales
- **Border-Radius en Botones**: `12px` (esquinas redondeadas suaves y profesionales).
- **Border-Radius en Inputs**: `8px`.
- **Grosor de Bordes Standard**: `2px solid`.
- **Margen Externo Base**: `20px` a `50px` según distribución en canvas.
- **Padding Interno de Inputs**: `10px 15px`.

---

## 4. Arquitectura Visual Reutilizable (`gui/componentes.py` y `gui/estilos.py`)

Para evitar duplicación de código en PySide6, OpenCode deberá estructurar los componentes reutilizables en `gui/componentes.py` e inyectar sus estilos mediante QSS en `gui/estilos.py`.

### 4.1. Componentes Reutilizables Recomendados

1. `HeaderTitleLabel(QLabel)`:
   - Configuración: Tipografía `Cascadia Code`, alineación central, fondo transparente (`background: transparent; border: none;`).
2. `PrimaryButton(QPushButton)`:
   - Configuración: Estilo visual azul claro degradado (`#dae8fc` -> `#7ea6e0`), borde `#6c8ebf`, fuente `Cascadia Code`.
3. `SecondaryButton(QPushButton)`:
   - Configuración: Estilo azul grisáceo tenue (`#bac8d3`), borde `#23445d`, fuente `Cascadia Code`.
4. `DestructiveButton(QPushButton)`:
   - Configuración: Estilo rosa/rojo suave degradado (`#f8cecc` -> `#ea6b66`), borde `#b85450`, fuente `Cascadia Code` (usado para "Volver").
5. `FilterButton(QPushButton)`:
   - Configuración: Estilo verde claro degradado (`#d5e8d4` -> `#97d077`), borde `#82b366`, fuente `Cascadia Code`.
6. `CustomLineEdit(QLineEdit)`:
   - Configuración: Fondo blanco, borde negro `2px`, fuente `Cascadia Code`, padding interno `10px`, placeholder text claro.
7. `CustomTableWidget(QTableWidget)`:
   - Configuración: Fondo blanco, bordes negros, encabezados con fuente `Cascadia Code 14px`, filas alternadas opcionales.

---

## 5. Especificación Detallada de Ventanas / Pantallas

---

### 5.1. Ventana: Bienvenida (`Landing-Login`)

#### Dimensiones y Fondo
- **Dimensiones**: `1600 px` x `900 px`.
- **Fondo**: `#66B2FF` sólido.

#### Estructura de Layouts (Jerarquía PySide6)
```
QWidget (LandingWindow)
└── QVBoxLayout (Main Layout, alignment=Qt.AlignCenter, spacing=40)
    ├── HeaderTitleLabel ("NeoED")
    ├── QSpacerItem (Expanding vertical distance)
    ├── QVBoxLayout (Button Container, spacing=38)
    │   ├── PrimaryButton ("Iniciar Sesión")
    │   └── SecondaryButton ("Crear Cuenta")
    └── QSpacerItem (Expanding vertical distance)
```

#### Elementos Visuales
1. **Logo / Título Principal**:
   - **Widget PySide6**: `QLabel` (`HeaderTitleLabel`)
   - **Texto**: `"NeoED"`
   - **Dimensiones**: `180 px` ancho x `100 px` alto (Canvas pos: `x=710`, `y=86`)
   - **Estilo**: Fuente `Cascadia Code`, tamaño `60 px`, color `#000000`, alineación centrada.
2. **Botón Iniciar Sesión**:
   - **Widget PySide6**: `QPushButton` (`PrimaryButton`)
   - **Texto**: `"Iniciar Sesion"`
   - **Dimensiones**: `400 px` ancho x `85 px` alto (Canvas pos: `x=605`, `y=527`)
   - **Estilo**: Fondo degradado `#dae8fc` a `#7ea6e0`, borde `#6c8ebf`, fuente `Cascadia Code 40px`.
3. **Botón Crear Cuenta**:
   - **Widget PySide6**: `QPushButton` (`SecondaryButton`)
   - **Texto**: `"Crear Cuenta"`
   - **Dimensiones**: `400 px` ancho x `85 px` alto (Canvas pos: `x=605`, `y=650`)
   - **Estilo**: Fondo `#bac8d3`, borde `#23445d`, fuente `Cascadia Code 40px`.

#### Estados Visuales
- **Normal**: Según colores HEX especificados.
- **Hover**:
  - `PrimaryButton`: Tono ligeramente más brillante (`#e8f1ff`).
  - `SecondaryButton`: Tono `#c8d6e2`.
- **Focus**: Borde con resalte suave de 3px.

#### Interacciones Visuales
- **Click en "Iniciar Sesion"**: Transición/Navegación inmediata hacia la ventana `Login`.
- **Click en "Crear Cuenta"**: Transición a flujo de alta/registro o pantalla de login según configuración del controlador.

---

### 5.2. Ventana: Inicio de Sesión (`Login`)

#### Dimensiones y Fondo
- **Dimensiones**: `1600 px` x `900 px`.
- **Fondo**: `#66B2FF` sólido.

#### Estructura de Layouts (Jerarquía PySide6)
```
QWidget (LoginWindow)
└── QVBoxLayout (Main Layout, alignment=Qt.AlignCenter, spacing=30)
    ├── HeaderTitleLabel ("NeoED")
    ├── QVBoxLayout (Form Layout, alignment=Qt.AlignCenter, spacing=25)
    │   ├── CustomLineEdit ("Nombre de usuario")
    │   └── CustomLineEdit ("Contraseña")
    └── QHBoxLayout (Actions Layout, alignment=Qt.AlignCenter, spacing=60)
        ├── PrimaryButton ("Ingresar")
        └── DestructiveButton ("Volver")
```

#### Elementos Visuales
1. **Título App**:
   - **Widget**: `QLabel`
   - **Texto**: `"NeoED"` | Dim: `180 x 100 px` (`x=710, y=86`) | Fuente: `Cascadia Code 60px`.
2. **Campo Nombre de Usuario**:
   - **Widget**: `QLineEdit` (`CustomLineEdit`)
   - **Placeholder / Value**: `"Nombre de usuario"`
   - **Dimensiones**: `500 px` ancho x `70 px` alto (Canvas pos: `x=550`, `y=300`)
   - **Estilo**: Fondo `#ffffff`, borde `#000000` 2px, fuente `Cascadia Code 25px`.
3. **Campo Contraseña**:
   - **Widget**: `QLineEdit` (`CustomLineEdit`, `setEchoMode(QLineEdit.Password)`)
   - **Placeholder / Value**: `"Contraseña"`
   - **Dimensiones**: `500 px` ancho x `70 px` alto (Canvas pos: `x=550`, `y=420`)
   - **Estilo**: Fondo `#ffffff`, borde `#000000` 2px, fuente `Cascadia Code 25px`.
4. **Botón Ingresar**:
   - **Widget**: `QPushButton` (`PrimaryButton`)
   - **Texto**: `"Ingresar"`
   - **Dimensiones**: `220 px` ancho x `70 px` alto (Canvas pos: `x=550`, `y=550`)
   - **Estilo**: Fondo degradado `#dae8fc` a `#7ea6e0`, borde `#6c8ebf`, fuente `Cascadia Code 35px`.
5. **Botón Volver**:
   - **Widget**: `QPushButton` (`DestructiveButton`)
   - **Texto**: `"Volver"`
   - **Dimensiones**: `220 px` ancho x `70 px` alto (Canvas pos: `x=830`, `y=550`)
   - **Estilo**: Fondo degradado `#f8cecc` a `#ea6b66`, borde `#b85450`, fuente `Cascadia Code 35px`.

#### Estados Visuales
- **Error (Autenticación fallida)**: El borde de los campos de entrada cambia a rojo `#ff0000` y se despliega un mensaje dinámico de alerta en pantalla.
- **Focus**: Campo activo cambia borde a `#0055ff` 2px.

#### Interacciones Visuales
- **Click en "Ingresar"**: Ejecuta la callback de verificación de credenciales con la DB. Si es correcto, navega al `Menu Principal`.
- **Click en "Volver"**: Navega de regreso a la pantalla de bienvenida (`Landing-Login`).

---

### 5.3. Ventana: Menú Principal (`Menu Principal`)

#### Dimensiones y Fondo
- **Dimensiones**: `1600 px` x `900 px`.
- **Fondo**: `#66B2FF` sólido.

#### Estructura de Layouts (Jerarquía PySide6)
```
QWidget (MainMenuWindow)
└── QVBoxLayout (Main Container, alignment=Qt.AlignCenter, spacing=28)
    ├── HeaderTitleLabel ("NeoED")
    └── QVBoxLayout (Menu Stack, alignment=Qt.AlignCenter, spacing=28)
        ├── PrimaryButton ("Crear Alumno")
        ├── SecondaryButton ("Ver Alumnos")
        ├── SecondaryButton ("Autorizar Alumnos")
        └── SecondaryButton ("Registrar Personal")
```

#### Elementos Visuales
1. **Título App**:
   - **Widget**: `QLabel`
   - **Texto**: `"NeoED"` | Dim: `180 x 100 px` (`x=710, y=86`) | Fuente: `Cascadia Code 60px`.
2. **Botón "Crear Alumno"**:
   - **Widget**: `QPushButton` (`PrimaryButton`)
   - **Texto**: `"Crear Alumno"`
   - **Dimensiones**: `400 px` ancho x `85 px` alto (`x=600, y=327`)
   - **Estilo**: Fondo degradado azul `#dae8fc` -> `#7ea6e0`, fuente `Cascadia Code 40px`.
3. **Botón "Ver Alumnos"**:
   - **Widget**: `QPushButton` (`SecondaryButton`)
   - **Texto**: `"Ver Alumnos"`
   - **Dimensiones**: `400 px` ancho x `85 px` alto (`x=600, y=440`)
   - **Estilo**: Fondo `#bac8d3`, borde `#23445d`, fuente `Cascadia Code 40px`.
4. **Botón "Autorizar Alumnos"**:
   - **Widget**: `QPushButton` (`SecondaryButton`)
   - **Texto**: `"Autorizar Alumnos"`
   - **Dimensiones**: `400 px` ancho x `85 px` alto (`x=600, y=553`)
   - **Estilo**: Fondo `#bac8d3`, borde `#23445d`, fuente `Cascadia Code 40px`.
5. **Botón "Registrar Personal"**:
   - **Widget**: `QPushButton` (`SecondaryButton`)
   - **Texto**: `"Registrar Personal"`
   - **Dimensiones**: `400 px` ancho x `85 px` alto (`x=600, y=666`)
   - **Estilo**: Fondo `#bac8d3`, borde `#23445d`, fuente `Cascadia Code 40px`.

#### Interacciones Visuales
- **Click en "Crear Alumno"**: Navega a la vista `Crear Alumno`.
- **Click en "Ver Alumnos"**: Navega a la vista `Ver Alumnos`.
- **Click en "Autorizar Alumnos"**: Navega a la vista `Autorizar Alumnos` (o vista filtrada según decisión a confirmar).
- **Click en "Registrar Personal"**: Navega a la vista `Registrar Personal` (sujeto a validación de roles de usuario, p. ej. Admin/Directivo).

---

### 5.4. Ventana: Registro de Alumno (`Crear Alumno`)

#### Dimensiones y Fondo
- **Dimensiones**: `1600 px` x `900 px`.
- **Fondo**: `#66B2FF` sólido.

#### Estructura de Layouts (Jerarquía PySide6)
```
QWidget (CreateStudentWindow)
└── QVBoxLayout (Main Layout, spacing=20)
    ├── HeaderTitleLabel ("Registro de Alumno")
    ├── QVBoxLayout (Form Fields Container, alignment=Qt.AlignCenter, spacing=20)
    │   ├── CustomLineEdit ("Nombre Completo")
    │   ├── CustomLineEdit ("DNI / Documento")
    │   ├── CustomLineEdit / QComboBox ("Año (Ej: 1°, 2°, 3°...)")
    │   ├── CustomLineEdit / QComboBox ("División (Ej: 1ra, 2da...)")
    │   ├── CustomLineEdit / QComboBox ("Especialidad / Orientación")
    │   ├── CustomLineEdit ("Tutor / Adulto Responsable")
    │   └── CustomLineEdit ("Teléfono de Contacto")
    └── QHBoxLayout (Actions Row, alignment=Qt.AlignCenter, spacing=30)
        ├── PrimaryButton ("Guardar Alumno")
        └── DestructiveButton ("Volver")
```

#### Elementos Visuales
1. **Título de Formulario**:
   - **Widget**: `QLabel` | **Texto**: `"Registro de Alumno"` | Dim: `600 x 80 px` (`x=500, y=50`) | Fuente: `Cascadia Code 50px`.
2. **Campos de Formulario** (7 inputs apilados verticalmente, dimensiones individuales: `450 px` ancho x `50 px` alto, `x=575`):
   - **Campo 1**: `"Nombre Completo"` (`y=160`)
   - **Campo 2**: `"DNI / Documento"` (`y=230`)
   - **Campo 3**: `"Año (Ej: 1°, 2°, 3°...)"` (`y=300`)
   - **Campo 4**: `"División (Ej: 1ra, 2da...)"` (`y=370`)
   - **Campo 5**: `"Especialidad / Orientación"` (`y=440`)
   - **Campo 6**: `"Tutor / Adulto Responsable"` (`y=510`)
   - **Campo 7**: `"Teléfono de Contacto"` (`y=580`)
   - **Estilo de Inputs**: Fondo `#ffffff`, borde `#000000` 2px, fuente `Cascadia Code 20px`.
3. **Botón Guardar Alumno**:
   - **Widget**: `QPushButton` (`PrimaryButton`)
   - **Texto**: `"Guardar Alumno"`
   - **Dimensiones**: `210 px` ancho x `60 px` alto (`x=575, y=670`)
   - **Estilo**: Fondo degradado `#dae8fc` a `#7ea6e0`, fuente `Cascadia Code 25px`.
4. **Botón Volver**:
   - **Widget**: `QPushButton` (`DestructiveButton`)
   - **Texto**: `"Volver"`
   - **Dimensiones**: `210 px` ancho x `60 px` alto (`x=815, y=670`)
   - **Estilo**: Fondo degradado `#f8cecc` a `#ea6b66`, fuente `Cascadia Code 25px`.

#### Interacciones Visuales
- **Click en "Guardar Alumno"**: Ejecuta callback de almacenamiento de alumno en base de datos. Si la validación pasa, muestra banner/modal de éxito y retorna o limpia el formulario.
- **Click en "Volver"**: Regresa al `Menu Principal`.

---

### 5.5. Ventana: Listado de Alumnos (`Ver Alumnos`)

#### Dimensiones y Fondo
- **Dimensiones**: `1600 px` x `900 px`.
- **Fondo**: `#66B2FF` sólido.

#### Estructura de Layouts (Jerarquía PySide6)
```
QWidget (ViewStudentsWindow)
└── QVBoxLayout (Main Layout, spacing=15)
    ├── HeaderTitleLabel ("Listado de Alumnos")
    ├── QHBoxLayout (Search & Filter Bar, alignment=Qt.AlignLeft, spacing=20)
    │   ├── CustomLineEdit ("Buscar por Nombre o DNI...")
    │   └── FilterButton ("Filtrar")
    ├── CustomTableWidget (Grid Data View)
    └── QHBoxLayout (Footer Bar, alignment=Qt.AlignRight)
        └── DestructiveButton ("Volver")
```

#### Elementos Visuales
1. **Título de Pantalla**:
   - **Widget**: `QLabel` | **Texto**: `"Listado de Alumnos"` | Dim: `600 x 70 px` (`x=500, y=40`) | Fuente: `Cascadia Code 50px`.
2. **Barra de Búsqueda**:
   - **Widget**: `QLineEdit` (`CustomLineEdit`)
   - **Placeholder**: `"Buscar por Nombre o DNI..."`
   - **Dimensiones**: `500 px` ancho x `45 px` alto (`x=200, y=130`)
   - **Estilo**: Fondo `#ffffff`, borde `#000000` 2px, fuente `Cascadia Code 18px`.
3. **Botón Filtrar**:
   - **Widget**: `QPushButton` (`FilterButton`)
   - **Texto**: `"Filtrar"`
   - **Dimensiones**: `140 px` ancho x `45 px` alto (`x=720, y=130`)
   - **Estilo**: Fondo degradado verde `#d5e8d4` a `#97d077`, borde `#82b366`, fuente `Cascadia Code 20px`.
4. **Tabla de Datos**:
   - **Widget**: `QTableWidget` (`CustomTableWidget`)
   - **Encabezados de Columnas**: `DNI | Nombre | Año | División | Especialidad | Estado`
   - **Dimensiones**: `1200 px` ancho x `520 px` alto (`x=200, y=200`)
   - **Estilo**: Fondo `#ffffff`, borde `#000000` 2px, fuente de celdas `Cascadia Code 14px`.
5. **Botón Volver**:
   - **Widget**: `QPushButton` (`DestructiveButton`)
   - **Texto**: `"Volver"`
   - **Dimensiones**: `180 px` ancho x `55 px` alto (`x=1220, y=740`)
   - **Estilo**: Fondo degradado rojo/rosa `#f8cecc` a `#ea6b66`, fuente `Cascadia Code 25px`.

#### Interacciones Visuales
- **Click en "Filtrar" / Cambio en búsqueda**: Actualiza dinámicamente el contenido del `QTableWidget` mediante filtrado en tiempo real sobre la base de datos o modelo.
- **Click en "Volver"**: Regresa al `Menu Principal`.

---

### 5.6. Ventana: Registro de Personal (`Registrar Personal`)

#### Dimensiones y Fondo
- **Dimensiones**: `1600 px` x `900 px`.
- **Fondo**: `#66B2FF` sólido.

#### Estructura de Layouts (Jerarquía PySide6)
```
QWidget (RegisterStaffWindow)
└── QVBoxLayout (Main Layout, spacing=25)
    ├── HeaderTitleLabel ("Registro de Personal")
    ├── QVBoxLayout (Form Fields Stack, alignment=Qt.AlignCenter, spacing=25)
    │   ├── CustomLineEdit ("Nombre de Usuario")
    │   ├── CustomLineEdit ("Contraseña")
    │   ├── QComboBox / CustomLineEdit ("Rol (Ej: Preceptor, Directivo, Admin)")
    │   └── CustomLineEdit ("Email / Contacto")
    └── QHBoxLayout (Actions Row, alignment=Qt.AlignCenter, spacing=30)
        ├── PrimaryButton ("Registrar Usuario")
        └── DestructiveButton ("Volver")
```

#### Elementos Visuales
1. **Título de Formulario**:
   - **Widget**: `QLabel` | **Texto**: `"Registro de Personal"` | Dim: `600 x 80 px` (`x=500, y=50`) | Fuente: `Cascadia Code 50px`.
2. **Campos de Entrada** (Dimensiones individuales: `450 px` ancho x `55 px` alto, `x=575`):
   - **Campo 1**: `"Nombre de Usuario"` (`y=180`)
   - **Campo 2**: `"Contraseña"` (`y=260`, modo contraseña oculto)
   - **Campo 3**: `"Rol (Ej: Preceptor, Directivo, Admin)"` (`y=340`, `QComboBox` interactivo)
   - **Campo 4**: `"Email / Contacto"` (`y=420`)
   - **Estilo**: Fondo `#ffffff`, borde `#000000` 2px, fuente `Cascadia Code 20px`.
3. **Botón Registrar Usuario**:
   - **Widget**: `QPushButton` (`PrimaryButton`)
   - **Texto**: `"Registrar Usuario"`
   - **Dimensiones**: `210 px` ancho x `60 px` alto (`x=575, y=530`)
   - **Estilo**: Fondo degradado azul `#dae8fc` a `#7ea6e0`, fuente `Cascadia Code 25px`.
4. **Botón Volver**:
   - **Widget**: `QPushButton` (`DestructiveButton`)
   - **Texto**: `"Volver"`
   - **Dimensiones**: `210 px` ancho x `60 px` alto (`x=815, y=530`)
   - **Estilo**: Fondo degradado rosa/rojo `#f8cecc` a `#ea6b66`, fuente `Cascadia Code 25px`.

---

### 5.7. Ventana / Sección: Autorización de Alumnos (`Autorizar Alumnos`)

> ⚠️ **DECISIÓN A CONFIRMAR**:
> En el diagrama `Menu Principal` de Draw.io se encuentra presente el botón **"Autorizar Alumnos"**, pero en el archivo visual de Draw.io **no existe un diagrama o pantalla independiente con el layout explícito para esta función**.
> 
> **Recomendación de implementación para OpenCode**:
> 1. Opción A (Reutilización con filtro): Reutilizar la vista `Ver Alumnos` (Listado) aplicando de manera predeterminada el filtro por estado `Pendiente de Autorización` e incorporando una columna de acciones con botones de "Autorizar" / "Rechazar".
> 2. Opción B (Vista Dedicada): Implementar una vista dedicada idéntica a `Ver Alumnos`, pero con el título `"Autorización de Alumnos"` y botones dedicados de gestión por cada fila.

---

## 6. Mapa de Navegación Visual (Flujo UX)

```
[ Landing / Bienvenida ] (Landing-Login)
  │
  ├──► Click "Iniciar Sesión" ───────► [ Ventana Login ]
  │                                      │
  │                                      ├──► Click "Volver" ──────► [ Landing / Bienvenida ]
  │                                      │
  │                                      └──► Click "Ingresar" (Auth Exitosa)
  │                                             │
  │                                             ▼
  │                                    [ Menú Principal ]
  │                                      │
  │                                      ├──► Click "Crear Alumno" ────► [ Crear Alumno ]
  │                                      │                                  │
  │                                      │                                  └──► Click "Volver" / Guardar ──► [ Menú Principal ]
  │                                      │
  │                                      ├──► Click "Ver Alumnos" ─────► [ Ver Alumnos ]
  │                                      │                                  │
  │                                      │                                  └──► Click "Volver" ───────────► [ Menú Principal ]
  │                                      │
  │                                      ├──► Click "Autorizar Alumnos" ► [ Autorizar Alumnos ] (DECISIÓN A CONFIRMAR)
  │                                      │                                  │
  │                                      │                                  └──► Click "Volver" ───────────► [ Menú Principal ]
  │                                      │
  │                                      └──► Click "Registrar Personal"► [ Registrar Personal ]
  │                                                                         │
  │                                                                         └──► Click "Volver" / Registrar ─► [ Menú Principal ]
  │
  └──► Click "Crear Cuenta" ─────────► [ Flujo de Alta / Directo a Login ]
```

---

## 7. Estilos Centralizados y Refactorización Permitida

OpenCode debe concentrar la personalización estética utilizando hojas de estilo QSS inyectadas en la aplicación.

### 7.1. Esquema QSS Recomendado (`gui/estilos.py`)

```python
# gui/estilos.py

QSS_STYLE = """
/* Fondo Global */
QWidget#CanvasBase {
    background-color: #66B2FF;
    font-family: 'Cascadia Code', 'Consolas', monospace;
}

/* Títulos */
QLabel#HeaderTitle {
    font-family: 'Cascadia Code', 'Consolas', monospace;
    color: #000000;
    font-weight: bold;
    background: transparent;
}

/* Botón Primario */
QPushButton#PrimaryButton {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #dae8fc, stop:1 #7ea6e0);
    border: 2px solid #6c8ebf;
    border-radius: 12px;
    color: #000000;
    font-family: 'Cascadia Code', monospace;
}
QPushButton#PrimaryButton:hover {
    background-color: #e8f1ff;
}

/* Botón Secundario */
QPushButton#SecondaryButton {
    background-color: #bac8d3;
    border: 2px solid #23445d;
    border-radius: 12px;
    color: #000000;
    font-family: 'Cascadia Code', monospace;
}
QPushButton#SecondaryButton:hover {
    background-color: #c8d6e2;
}

/* Botón Destructivo / Volver */
QPushButton#DestructiveButton {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f8cecc, stop:1 #ea6b66);
    border: 2px solid #b85450;
    border-radius: 12px;
    color: #000000;
    font-family: 'Cascadia Code', monospace;
}
QPushButton#DestructiveButton:hover {
    background-color: #ffdede;
}

/* Botón Filtro / Éxito */
QPushButton#FilterButton {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #d5e8d4, stop:1 #97d077);
    border: 2px solid #82b366;
    border-radius: 12px;
    color: #000000;
    font-family: 'Cascadia Code', monospace;
}

/* Inputs de Texto */
QLineEdit, QComboBox {
    background-color: #ffffff;
    border: 2px solid #000000;
    border-radius: 8px;
    padding: 8px 12px;
    color: #000000;
    font-family: 'Cascadia Code', monospace;
}
QLineEdit:focus, QComboBox:focus {
    border: 2px solid #0055ff;
}

/* Tablas */
QTableWidget {
    background-color: #ffffff;
    border: 2px solid #000000;
    gridline-color: #000000;
    font-family: 'Cascadia Code', monospace;
    font-size: 14px;
    color: #000000;
}
QHeaderView::section {
    background-color: #dae8fc;
    color: #000000;
    font-weight: bold;
    border: 1px solid #000000;
    font-family: 'Cascadia Code', monospace;
}
"""
```

### 7.2. Acciones de Refactorización Permitidas para OpenCode
- **Reorganizar Archivos**: Mover, renombrar o modularizar vistas en `gui/vistas/` (`login_view.py`, `menu_view.py`, `student_view.py`, etc.).
- **Reemplazo de Layouts**: Sustituir layouts rígidos por `QVBoxLayout`, `QHBoxLayout` o contenedores absolutos dentro de un canvas escalable de 1600x900.
- **Eliminación de Código Obsoleto**: Borrar componentes, estilos o controles heredados de versiones anteriores que no encajen en el diseño de Draw.io.

---

## 8. Restricciones Funcionales y Conexiones Lógicas

A pesar de la refactorización integral de la interfaz gráfica, OpenCode **NO debe eliminar ni romper** las funcionalidades de backend previamente implementadas:

1. **Autenticación y Sesiones**: Mantener la verificación de contraseñas y obtención del rol del usuario actual.
2. **Control de Accesos (RBAC)**: Mantener las restricciones que ocultan o deshabilitan opciones según el rol (Admin, Directivo, Preceptor).
3. **Persistencia de Alumnos y Personal**: Conservar las llamadas a los controladores / modelos de base de datos para guardar, consultar y filtrar registros.
4. **Validación de Formularios**: Garantizar que los campos obligatorios (DNI, Nombre, Contraseña) continúen siendo validados antes de realizar operaciones I/O.

---

# Criterios de Aceptación Visual (Checklist de Verificación)

- [ ] **Canvas y Proporciones**: Todas las pantallas utilizan el fondo `#66B2FF` y respetan la proporción de canvas `1600 x 900 px`.
- [ ] **Tipografía Unificada**: Se aplica la fuente `Cascadia Code` de forma consistente en todos los títulos, etiquetas, botones, inputs y tablas.
- [ ] **Título NeoED**: El título de la app aparece centrado con tamaño `60 px` en las pantallas de Bienvenida, Login y Menú Principal.
- [ ] **Estilo de Botones Primarios**: Los botones "Iniciar Sesion", "Ingresar", "Crear Alumno", "Guardar Alumno" y "Registrar Usuario" cuentan con fondo degradado azul `#dae8fc` a `#7ea6e0`, borde `#6c8ebf` y esquinas redondeadas.
- [ ] **Estilo de Botones Secundarios**: Los botones de menú ("Crear Cuenta", "Ver Alumnos", "Autorizar Alumnos", "Registrar Personal") presentan el color de fondo `#bac8d3` y borde `#23445d`.
- [ ] **Estilo de Botones "Volver"**: El botón "Volver" posee el estilo destructivo degradado `#f8cecc` a `#ea6b66` con borde `#b85450`.
- [ ] **Campos de Entrada (Inputs)**: Tienen fondo blanco `#ffffff`, borde negro `#000000` de 2px, esquinas redondeadas y texto claro.
- [ ] **Tabla de Alumnos**: `QTableWidget` implementado en `Ver Alumnos` con dimensiones `1200 x 520 px` y encabezados alineados a los especificados en Draw.io: `DNI | Nombre | Año | División | Especialidad | Estado`.
- [ ] **Navegación Fluida**: El flujo de navegación respeta rigurosamente el mapa de visualización UX, permitiendo ir y volver entre vistas sin errores de contexto en PySide6.
- [ ] **Centralización de Estilos**: Toda la capa de presentación utiliza los componentes reutilizables de `gui/componentes.py` y las reglas QSS centralizadas de `gui/estilos.py`.
- [ ] **Preservación Funcional**: La conexión con la base de datos, el login, la creación de alumnos y la gestión de permisos continúan operando correctamente tras los cambios visuales.

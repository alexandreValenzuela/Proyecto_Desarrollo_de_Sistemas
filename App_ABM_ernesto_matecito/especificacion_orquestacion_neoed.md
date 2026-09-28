# Especificación Técnica Arquitectónica y Guía de Orquestación de IA: Proyecto NeoED

> **Documento Maestro de Arquitectura, Sistema de Diseño, Reglas de Negocio y Prompts de IA**  
> **Proyecto:** NeoED - Sistema de Gestión Escolar / Plataforma EdTech  
> **Tecnologías Target:** Python 3.x | PyQt5 / PyQt6 / PySide6 | SQLite  
> **Patrón Arquitectónico:** Single Window Container (`QMainWindow`) + Stacked Views (`QStackedWidget`) + Modular Views  
> **Versión:** 3.0 (Definitiva y Perfecta para Presentación Técnica)  

---

## 1. Diagnóstico de Arquitectura y Corrección de Navegación

### 1.1 El Problema de la Arquitectura Anterior (Multi-Ventana Independiente)
El intento previo de implementación falló debido a un desacople entre el diseño visual y la arquitectura del motor GUI (Qt):
- **Cierre y Apertura Discontinua:** Se intentaba manejar el flujo mediante llamadas directas `ventana.close()` y `nueva_ventana.show()`.
- **Destrucción de Contexto:** Al destruir/cerrar la ventana principal para abrir vistas secundarias, las señales y slots de Qt se desconectaban, perdiendo referencias de memoria y sesiones de usuario (`usuario_logueado`).
- **Colisión de Diseños:** Intentar encajar un dashboard con Sidebar lateral en ventanas modales sueltas rompe los layouts responsivos (`QLayout`) y causa desbordamiento de widgets.

### 1.2 La Solución Definitiva: Arquitectura Contenedora Única (`QStackedWidget`)
El layout definido exige una arquitectura de **Ventana Contenedora Única**:
1. **Flujo de Acceso:** `VentanaLanding` ➔ `VentanaLogin` / `VentanaRegistro`.
2. **Dashboard Unificado (`VentanaPrincipal`):**
   - **Sidebar Lateral Fijo (250px):** Menú vertical agrupado por secciones (*Alumnos*, *Profesores*, *Notas*). No cambia ni se recarga.
   - **Panel Contenedor Dinámico (`QStackedWidget`):** Ocupa el área derecha de la ventana. Intercambia pantallas (`VistaBienvenido`, `VistaVerAlumnos`, `VistaCargarAlumnos`, `VistaPlaceholder`) de forma instantánea sin regenerar ni cerrar la ventana.

---

## 2. Reglas de Negocio y Decisiones de Diseño Aprobadas

1. **Campo Contraseña en Formulario "Cargar Alumnos":**
   - **Regla:** Se incluye explícitamente el campo `Contraseña` en la interfaz de alta de alumnos (`VistaCargarAlumnos`).
   - **Justificación:** Garantiza la integridad del modelo de base de datos (`models/alumno.py`), evitando depender de valores por defecto o campos nulos en la contraseña.

2. **Estado de Autorización de Alumnos Registrados:**
   - **Regla:** Todo alumno creado a través de la sección "Cargar Alumnos" por un preceptor, profesor o administrador se registra automáticamente con `autorizado = 1`.
   - **Diferenciación:** El auto-registro público desde la pantalla de login/registro permanece con `autorizado = 0` (pendiente de aprobación).

3. **Alcance de Entrega Priorizado (Estrategia MVP):**
   - **Componentes Completa y 100% Funcionales:**
     - Pantalla Landing (`VentanaLanding`).
     - Login (`VentanaLogin`) y Registro (`VentanaRegistro`).
     - Contenedor Dashboard (`VentanaPrincipal`) con Sidebar dinámico.
     - Vista "Ver Alumnos" (`VistaVerAlumnos`): Tabla completa + Filtros de búsqueda en tiempo real (por DNI, Nombre/Apellido y Curso).
     - Vista "Cargar Alumnos" (`VistaCargarAlumnos`): Formulario estructurado con guardado directo en SQLite.
   - **Componentes Secundarios (Placeholders Profesionales):**
     - Las secciones "Profesores" e "Notas" mostrarán la interfaz `VistaPlaceholder` estilizada ("*Módulo en fase de mantenimiento / actualización*") o conectarán con modales existentes, respetando la estructura del Sidebar sin romper la experiencia del usuario.

4. **Compartimentación y Modularidad Extrema:**
   - Cada vista, modelo y componente de interfaz habitará en su propio archivo dentro de la estructura modular del proyecto.

---

## 3. Estructura Modular Completa del Proyecto

```text
proyecto_neoed/
├── main.py                        # Punto de entrada principal (Inicia QApplication y el Stack Base)
├── database/
│   ├── __init__.py
│   ├── conexion.py                # Helper de gestión de conexiones SQLite
│   └── setup.py                   # Script de inicialización de tablas e índices
├── models/
│   ├── __init__.py
│   ├── alumno.py                  # CRUD del Alumno + Búsquedas SQL filtradas
│   ├── curso.py                   # Consultas de Cursos y Mapeo de IDs
│   └── personal.py                # Modelo de Preceptores/Profesores/Admins
├── gui/
│   ├── __init__.py
│   ├── estilos.py                 # Design Tokens y hojas de estilo globales (QSS)
│   ├── componentes.py             # Custom Widgets reutilizables (Inputs, Tablas, Botones)
│   ├── ventana_landing.py         # Pantalla Inicial con opciones Login / Registro
│   ├── ventana_login.py           # Formulario de autenticación
│   ├── ventana_registro.py        # Formulario de registro de usuario público
│   ├── ventana_principal.py       # Layout Maestro (Sidebar + QStackedWidget)
│   └── vistas/
│       ├── __init__.py
│       ├── vista_bienvenido.py    # Pantalla de bienvenida dentro del Dashboard
│       ├── vista_ver_alumnos.py   # Grilla interactiva + Filtros (DNI, Nombre, Curso)
│       ├── vista_cargar_alumnos.py# Formulario de alta institucional de alumnos
│       └── vista_placeholder.py   # Pantalla genérica para secciones en desarrollo
```

---

## 4. Tokens Visuales y Sistema de Estilos QSS (Qt Style Sheet)

El archivo `gui/estilos.py` concentra los colores, degradados y tipografías para garantizar una interfaz idéntica al layout proyectado.

```python
# gui/estilos.py

ESTILO_GLOBAL = """
/* ============================================================================
   ESTILOS GENERALES Y VENTANAS
   ============================================================================ */
QMainWindow, QDialog {
    background-color: #66B2FF;
    font-family: 'Cascadia Code', 'Segoe UI', 'Consolas', monospace;
}

QWidget#CentralContainer {
    background-color: #F8FAFC;
}

/* ============================================================================
   HEADER Y TÍTULOS ESTRUCTURALES
   ============================================================================ */
QLabel#TituloNeoED {
    font-size: 48px;
    font-weight: 800;
    color: #FFFFFF;
    font-family: 'Cascadia Code', monospace;
    qproperty-alignment: AlignCenter;
}

QLabel#SubtituloNeoED {
    font-size: 18px;
    color: #E2E8F0;
    font-family: 'Segoe UI', sans-serif;
    qproperty-alignment: AlignCenter;
}

QLabel#TituloSeccion {
    font-size: 24px;
    font-weight: bold;
    color: #0F172A;
    margin-bottom: 12px;
}

/* ============================================================================
   BOTONES Y ACCIONES (LANDING & FORMS)
   ============================================================================ */
QPushButton#BtnIniciarSesion {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #DAE8FC, stop:1 #7EA6E0);
    border: 2px solid #6C8EBF;
    border-radius: 12px;
    font-size: 22px;
    font-weight: bold;
    color: #1A202C;
    padding: 10px 24px;
    min-width: 320px;
    min-height: 54px;
}
QPushButton#BtnIniciarSesion:hover {
    background-color: #7EA6E0;
    border-color: #4A75B5;
}

QPushButton#BtnCrearCuenta {
    background-color: #BAC8D3;
    border: 2px solid #23445D;
    border-radius: 12px;
    font-size: 22px;
    font-weight: bold;
    color: #1A202C;
    padding: 10px 24px;
    min-width: 320px;
    min-height: 54px;
}
QPushButton#BtnCrearCuenta:hover {
    background-color: #9CB1C2;
}

QPushButton#BtnVolver {
    background-color: transparent;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    color: #475569;
    font-size: 14px;
    font-weight: 600;
    padding: 6px 16px;
}
QPushButton#BtnVolver:hover {
    background-color: #E2E8F0;
    color: #0F172A;
}

QPushButton#BtnAccionGuardar {
    background-color: #2563EB;
    border: none;
    border-radius: 8px;
    color: #FFFFFF;
    font-size: 16px;
    font-weight: bold;
    padding: 10px 20px;
}
QPushButton#BtnAccionGuardar:hover {
    background-color: #1D4ED8;
}

/* ============================================================================
   SIDEBAR LATERAL DE NAVEGACIÓN
   ============================================================================ */
QFrame#SidebarFrame {
    background-color: #1E293B;
    border-right: 1px solid #334155;
    min-width: 250px;
    max-width: 250px;
}

QLabel#SidebarHeader {
    color: #38BDF8;
    font-size: 20px;
    font-weight: bold;
    padding: 20px 16px 10px 16px;
}

QLabel#SidebarGroupLabel {
    color: #94A3B8;
    font-size: 12px;
    font-weight: bold;
    text-transform: uppercase;
    padding: 16px 16px 6px 16px;
}

QPushButton#BtnSidebarItem {
    background-color: transparent;
    border: none;
    border-radius: 6px;
    color: #E2E8F0;
    font-size: 14px;
    font-weight: 500;
    text-align: left;
    padding: 10px 16px;
    margin: 2px 8px;
}
QPushButton#BtnSidebarItem:hover {
    background-color: #334155;
    color: #FFFFFF;
}
QPushButton#BtnSidebarItem:checked, QPushButton#BtnSidebarItem[active="true"] {
    background-color: #2563EB;
    color: #FFFFFF;
    font-weight: bold;
}

/* ============================================================================
   CAMPOS DE ENTRADA, SELECCIÓN Y TABLAS
   ============================================================================ */
QLineEdit, QComboBox {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 14px;
    color: #1E293B;
}
QLineEdit:focus, QComboBox:focus {
    border: 2px solid #2563EB;
}

QTableWidget {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    gridline-color: #F1F5F9;
    font-size: 14px;
    color: #334155;
}
QHeaderView::section {
    background-color: #F8FAFC;
    color: #475569;
    font-weight: bold;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #E2E8F0;
}
"""
```

---

## 5. Especificación Técnica Módulo por Módulo

### 5.1 Capa de Datos: `models/alumno.py`
Proporciona consultas SQL preparadas para ejecutar búsquedas en tiempo real con filtros dinámicos.

```python
# models/alumno.py
import sqlite3
from database.conexion import obtener_conexion

class Alumno:
    @staticmethod
    def buscar_filtrado(dni=None, nombre=None, id_curso=None):
        """
        Realiza una consulta filtrada en SQLite concatenando parámetros dinámicos.
        """
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        query = """
            SELECT a.dni, a.nombre, a.apellido, c.nombre_curso, a.autorizado
            FROM alumnos a
            LEFT JOIN cursos c ON a.id_curso = c.id
            WHERE 1=1
        """
        params = []
        
        if dni and dni.strip():
            query += " AND a.dni LIKE ?"
            params.append(f"%{dni.strip()}%")
            
        if nombre and nombre.strip():
            query += " AND (a.nombre LIKE ? OR a.apellido LIKE ?)"
            params.append(f"%{nombre.strip()}%")
            params.append(f"%{nombre.strip()}%")
            
        if id_curso and str(id_curso).isdigit() and int(id_curso) > 0:
            query += " AND a.id_curso = ?"
            params.append(int(id_curso))
            
        query += " ORDER BY a.apellido, a.nombre ASC"
        
        cursor.execute(query, params)
        resultados = cursor.fetchall()
        conn.close()
        return resultados

    @staticmethod
    def crear_alumno(dni, nombre, apellido, id_curso, password, autorizado=1):
        """
        Registra un alumno institucionalmente con autorizado=1 por defecto.
        """
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO alumnos (dni, nombre, apellido, id_curso, password, autorizado)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (dni, nombre, apellido, id_curso, password, autorizado))
            conn.commit()
            return True, "Alumno registrado exitosamente."
        except sqlite3.IntegrityError:
            return False, "Error: El DNI ingresado ya se encuentra registrado."
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"
        finally:
            conn.close()
```

---

### 5.2 Capa de Presentación: `gui/ventana_principal.py`
Ensambla el Sidebar lateral fijo con el `QStackedWidget` central para conmutar paneles.

```python
# gui/ventana_principal.py
from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QFrame, QLabel, QPushButton, QStackedWidget, QMessageBox)
from PyQt5.QtCore import Qt

from gui.vistas.vista_bienvenido import VistaBienvenido
from gui.vistas.vista_ver_alumnos import VistaVerAlumnos
from gui.vistas.vista_cargar_alumnos import VistaCargarAlumnos
from gui.vistas.vista_placeholder import VistaPlaceholder

class VentanaPrincipal(QMainWindow):
    def __init__(self, usuario_logueado=None, on_logout_callback=None):
        super().__init__()
        self.usuario_logueado = usuario_logueado
        self.on_logout_callback = on_logout_callback
        
        self.setWindowTitle("NeoED - Sistema de Gestión Escolar")
        self.resize(1440, 900)
        self.setMinimumSize(1200, 768)
        
        self.init_ui()
        
    def init_ui(self):
        # Widget Contenedor Raíz
        main_widget = QWidget()
        main_widget.setObjectName("CentralContainer")
        self.setCentralWidget(main_widget)
        
        layout_principal = QHBoxLayout(main_widget)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)
        
        # 1. Sidebar Lateral
        sidebar = self.crear_sidebar()
        layout_principal.addWidget(sidebar)
        
        # 2. QStackedWidget de Vistas Centrales
        self.stack = QStackedWidget()
        layout_principal.addWidget(self.stack)
        
        # Instanciar e Indizar Vistas
        self.vista_bienvenido = VistaBienvenido(self.usuario_logueado)
        self.vista_ver_alumnos = VistaVerAlumnos()
        self.vista_cargar_alumnos = VistaCargarAlumnos(on_guardado=self.refrescar_tabla_alumnos)
        self.vista_placeholder = VistaPlaceholder()
        
        self.stack.addWidget(self.vista_bienvenido)     # Index 0
        self.stack.addWidget(self.vista_ver_alumnos)    # Index 1
        self.stack.addWidget(self.vista_cargar_alumnos) # Index 2
        self.stack.addWidget(self.vista_placeholder)    # Index 3
        
        self.stack.setCurrentIndex(0)
        
    def crear_sidebar(self):
        frame = QFrame()
        frame.setObjectName("SidebarFrame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(4)
        
        # Header del Sidebar
        lbl_logo = QLabel("NeoED Admin")
        lbl_logo.setObjectName("SidebarHeader")
        layout.addWidget(lbl_logo)
        
        # Grupo Alumnos
        layout.addWidget(self._crear_label_grupo("ALUMNOS"))
        
        btn_ver_alumnos = QPushButton("📋 Ver Alumnos")
        btn_ver_alumnos.setObjectName("BtnSidebarItem")
        btn_ver_alumnos.clicked.connect(lambda: self.navegar_a(1))
        layout.addWidget(btn_ver_alumnos)
        
        btn_cargar_alumno = QPushButton("➕ Cargar Alumnos")
        btn_cargar_alumno.setObjectName("BtnSidebarItem")
        btn_cargar_alumno.clicked.connect(lambda: self.navegar_a(2))
        layout.addWidget(btn_cargar_alumno)
        
        # Grupo Profesores
        layout.addWidget(self._crear_label_grupo("PROFESORES"))
        
        btn_ver_profes = QPushButton("👨‍🏫 Ver Profesores")
        btn_ver_profes.setObjectName("BtnSidebarItem")
        btn_ver_profes.clicked.connect(lambda: self.navegar_a(3))
        layout.addWidget(btn_ver_profes)
        
        # Grupo Notas
        layout.addWidget(self._crear_label_grupo("NOTAS Y INFORMES"))
        
        btn_notas = QPushButton("📊 Cargar / Ver Notas")
        btn_notas.setObjectName("BtnSidebarItem")
        btn_notas.clicked.connect(lambda: self.navegar_a(3))
        layout.addWidget(btn_notas)
        
        layout.addStretch()
        
        # Botón Cerrar Sesión
        btn_logout = QPushButton("🚪 Cerrar Sesión")
        btn_logout.setObjectName("BtnSidebarItem")
        btn_logout.clicked.connect(self.ejecutar_logout)
        layout.addWidget(btn_logout)
        
        return frame

    def _crear_label_grupo(self, texto):
        lbl = QLabel(texto)
        lbl.setObjectName("SidebarGroupLabel")
        return lbl
        
    def navegar_a(self, index):
        self.stack.setCurrentIndex(index)
        if index == 1:
            self.vista_ver_alumnos.cargar_datos()
            
    def refrescar_tabla_alumnos(self):
        self.vista_ver_alumnos.cargar_datos()
        self.stack.setCurrentIndex(1)
        
    def ejecutar_logout(self):
        if self.on_logout_callback:
            self.on_logout_callback()
```

---

### 5.3 Vista "Ver Alumnos": `gui/vistas/vista_ver_alumnos.py`

```python
# gui/vistas/vista_ver_alumnos.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QPushButton)
from models.alumno import Alumno
from models.curso import Curso

class VistaVerAlumnos(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Encabezado
        lbl_titulo = QLabel("Listado General de Alumnos")
        lbl_titulo.setObjectName("TituloSeccion")
        layout.addWidget(lbl_titulo)
        
        # Barra de Filtros
        layout_filtros = QHBoxLayout()
        
        self.txt_buscar_dni = QLineEdit()
        self.txt_buscar_dni.setPlaceholderText("🔎 Buscar por DNI...")
        self.txt_buscar_dni.textChanged.connect(self.cargar_datos)
        
        self.txt_buscar_nombre = QLineEdit()
        self.txt_buscar_nombre.setPlaceholderText("🔎 Buscar por Nombre/Apellido...")
        self.txt_buscar_nombre.textChanged.connect(self.cargar_datos)
        
        self.cmb_cursos = QComboBox()
        self.cmb_cursos.addItem("Todos los Cursos", 0)
        self.poblar_combo_cursos()
        self.cmb_cursos.currentIndexChanged.connect(self.cargar_datos)
        
        btn_limpiar = QPushButton("Limpiar Filtros")
        btn_limpiar.setObjectName("BtnVolver")
        btn_limpiar.clicked.connect(self.limpiar_filtros)
        
        layout_filtros.addWidget(self.txt_buscar_dni)
        layout_filtros.addWidget(self.txt_buscar_nombre)
        layout_filtros.addWidget(self.cmb_cursos)
        layout_filtros.addWidget(btn_limpiar)
        
        layout.addLayout(layout_filtros)
        
        # Grilla de Datos
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["DNI", "Apellido", "Nombre", "Curso", "Estado"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tabla)
        
        self.cargar_datos()

    def poblar_combo_cursos(self):
        try:
            cursos = Curso.obtener_todos()
            for c_id, c_nombre in cursos:
                self.cmb_cursos.addItem(c_nombre, c_id)
        except Exception:
            pass

    def cargar_datos(self):
        dni = self.txt_buscar_dni.text()
        nombre = self.txt_buscar_nombre.text()
        id_curso = self.cmb_cursos.currentData()
        
        registros = Alumno.buscar_filtrado(dni, nombre, id_curso)
        
        self.tabla.setRowCount(0)
        for row_idx, row_data in enumerate(registros):
            self.tabla.insertRow(row_idx)
            # DNI, Nombre, Apellido, Curso, Autorizado
            dni_val, nom_val, ape_val, curso_val, aut_val = row_data
            
            self.tabla.setItem(row_idx, 0, QTableWidgetItem(str(dni_val)))
            self.tabla.setItem(row_idx, 1, QTableWidgetItem(str(ape_val)))
            self.tabla.setItem(row_idx, 2, QTableWidgetItem(str(nom_val)))
            self.tabla.setItem(row_idx, 3, QTableWidgetItem(str(curso_val or "Sin Asignar")))
            
            estado_txt = "Autorizado" if aut_val == 1 else "Pendiente"
            self.tabla.setItem(row_idx, 4, QTableWidgetItem(estado_txt))

    def limpiar_filtros(self):
        self.txt_buscar_dni.clear()
        self.txt_buscar_nombre.clear()
        self.cmb_cursos.setCurrentIndex(0)
        self.cargar_datos()
```

---

## 6. Prompting para Agentes de IA (Multi-Agent PyQt Orchestration)

Utiliza estos prompts estructurados para indicar a las IAs generadoras (Cursor / Claude / OpenAI) cómo desarrollar módulos aislados sin colisionar.

### 🤖 Agente 1: Orquestador de Ventana Maestro (`gui/ventana_principal.py`)
```text
[SYSTEM PROMPT: PYQT GUI ARCHITECT]
Actúa como un Senior Desktop Developer experto en PyQt5/PySide.
Desarrolla el archivo `gui/ventana_principal.py` asegurando:
1. Heredar de QMainWindow e integrar un widget central con QHBoxLayout.
2. Crear un Sidebar lateral estático a la izquierda con ancho fijo 250px (Frame con id 'SidebarFrame').
3. El Sidebar debe agrupar los siguientes botones navegables con señales para cambiar el índice de un QStackedWidget a la derecha:
   - "📋 Ver Alumnos" (Navega a Index 1)
   - "➕ Cargar Alumnos" (Navega a Index 2)
   - "👨‍🏫 Ver Profesores" (Navega a Index 3 - Placeholder)
   - "📊 Cargar / Ver Notas" (Navega a Index 3 - Placeholder)
   - "🚪 Cerrar Sesión" (Invoca callback de retorno a Landing)
4. Configurar el QStackedWidget con las instancias de VistaBienvenido, VistaVerAlumnos, VistaCargarAlumnos y VistaPlaceholder.
```

### ⚙️ Agente 2: Capa de Persistencia y Consultas Filtradas (`models/alumno.py`)
```text
[SYSTEM PROMPT: PYTHON DATABASE SPECIALIST]
Actúa como un Desarrollador Backend experto en SQLite.
Crea o actualiza `models/alumno.py`:
1. Implementa `buscar_filtrado(dni=None, nombre=None, id_curso=None)` ejecutando un SELECT dinámico con LEFT JOIN a la tabla `cursos`.
2. Utiliza consultas parametrizadas (?) para prevenir inyecciones SQL y soporta búsquedas parciales con LIKE.
3. Implementa `crear_alumno(dni, nombre, apellido, id_curso, password, autorizado=1)` que inserte registros e informe excepciones de clave duplicada (IntegrityError por DNI).
```

### 🎨 Agente 3: Componentes de Vistas e Interfaz Dinámica (`gui/vistas/`)
```text
[SYSTEM PROMPT: PYQT UI DEVELOPER]
Crea las vistas de contenido para el contenedor dinámico:
1. `gui/vistas/vista_ver_alumnos.py`: Construye un panel con filtros superiores (QLineEdit para DNI, QLineEdit para Nombre, QComboBox para Cursos) y un QTableWidget de 5 columnas. Conecta las señales textChanged y currentIndexChanged a la actualización de datos.
2. `gui/vistas/vista_cargar_alumnos.py`: Construye un formulario ordenado para el alta de alumnos que solicite DNI, Nombre, Apellido, Curso y Contraseña. Al presionar "Guardar Alumno", debe ejecutar Alumno.crear_alumno con autorizado=1 por defecto y emitir una señal/callback para actualizar la tabla.
```

---

## 7. Comando Orquestador Final para Claude / Cursor

Copia y pega la siguiente instrucción directa para pedir la generación de código sin ambigüedades:

> **Comando Ejecutivo:**  
> *"Lee el archivo `especificacion_orquestacion_neoed.md` versión 3.0. Aplica la arquitectura de Contenedor Único con `QStackedWidget` y Sidebar lateral en PyQt. Entrégame en orden los módulos completos y funcionales:*
> 1. `gui/estilos.py`
> 2. `models/alumno.py`
> 3. `gui/vistas/vista_ver_alumnos.py`
> 4. `gui/vistas/vista_cargar_alumnos.py`
> 5. `gui/ventana_principal.py`
> 6. `main.py`
> *Asegúrate de que no existan llamadas a `.show()` en ventanas secundarias descartadas y que toda la navegación ocurra dentro del contenedor `QStackedWidget`."*

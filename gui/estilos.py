"""
Design Tokens y Hoja de Estilos QSS (Qt Style Sheet) para NeoED.

Fuente de Verdad: Especificacion Visual GUI (Draw.io SSOT) v2.0
Adaptado a PySide6.

 Jerarquia de autoridad:
 1. DRAW.IO (Fuente de Verdad Visual)
 2. ESPECIFICACION FUNCIONAL (Comportamiento del Sistema)
 3. CODIGO GUI (Referencia tecnica, NO autoridad de diseno)
"""

# ============================================================================
# TOKENS VISUALES — Draw.io SSOT
# ============================================================================

# Colores
COLOR_CANVAS = "#66B2FF"
COLOR_TEXTO = "#000000"
COLOR_BLANCO = "#FFFFFF"
COLOR_NEGRO = "#000000"

# Botones
COLOR_BTN_PRIMARIO_START = "#dae8fc"
COLOR_BTN_PRIMARIO_END = "#7ea6e0"
COLOR_BTN_PRIMARIO_BORDER = "#6c8ebf"
COLOR_BTN_PRIMARIO_HOVER = "#e8f1ff"

COLOR_BTN_SECUNDARIO = "#bac8d3"
COLOR_BTN_SECUNDARIO_BORDER = "#23445d"
COLOR_BTN_SECUNDARIO_HOVER = "#c8d6e2"

COLOR_BTN_DESTRUCTIVO_START = "#f8cecc"
COLOR_BTN_DESTRUCTIVO_END = "#ea6b66"
COLOR_BTN_DESTRUCTIVO_BORDER = "#b85450"
COLOR_BTN_DESTRUCTIVO_HOVER = "#ffdede"

COLOR_BTN_FILTRO_START = "#d5e8d4"
COLOR_BTN_FILTRO_END = "#97d077"
COLOR_BTN_FILTRO_BORDER = "#82b366"

# Inputs
COLOR_INPUT_BG = "#ffffff"
COLOR_INPUT_BORDER = "#000000"
COLOR_INPUT_FOCUS = "#0055ff"

# Tablas
COLOR_TABLA_BG = "#ffffff"
COLOR_TABLA_BORDER = "#000000"
COLOR_TABLA_HEADER_BG = "#dae8fc"

# Sidebar
COLOR_SIDEBAR_BG = "#1E293B"
COLOR_SIDEBAR_BORDER = "#334155"
COLOR_SIDEBAR_HEADER = "#38BDF8"
COLOR_SIDEBAR_GROUP = "#94A3B8"
COLOR_SIDEBAR_ITEM = "#E2E8F0"
COLOR_SIDEBAR_ITEM_HOVER = "#334155"
COLOR_SIDEBAR_ITEM_ACTIVE = "#2563EB"

# Tipografia
FUENTE_CODIGO = "'Cascadia Code', 'Consolas', monospace"

# Tamanos de fuente
TAMANO_TITULO_APP = 60
TAMANO_TITULO_VENTANA = 50
TAMANO_BOTON_GRANDE = 40
TAMANO_BOTON_MEDIO = 35
TAMANO_BOTON_FORM = 25
TAMANO_INPUT = 20
TAMANO_FILTRO = 18
TAMANO_CELDA = 14

# Dimensiones globales
ANCHO_VENTANA = 1600
ALTO_VENTANA = 900

# Botones landing/menu
ANCHO_BOTON_LANDING = 400
ALTO_BOTON_LANDING = 85

# Botones login
ANCHO_BOTON_LOGIN = 220
ALTO_BOTON_LOGIN = 70

# Botones form (Volver, Guardar)
ANCHO_BOTON_FORM = 210
ALTO_BOTON_FORM = 60

# Inputs
ANCHO_INPUT_LOGIN = 500
ALTO_INPUT_LOGIN = 70
ANCHO_INPUT_FORM = 450
ALTO_INPUT_FORM = 50

# Tabla
ANCHO_TABLA = 1200
ALTO_TABLA = 520

# ============================================================================
# QSS GLOBAL — Draw.io SSOT
# ============================================================================
ESTILO_GLOBAL = """
/* ============================================================================
   FONDO GLOBAL Y CANVAS
   ============================================================================ */
QWidget {
    background-color: #66B2FF;
    font-family: 'Cascadia Code', 'Consolas', monospace;
}

QWidget#CanvasBase {
    background-color: #66B2FF;
}

/* ============================================================================
   TITULOS
   ============================================================================ */
QLabel#HeaderTitle {
    font-family: 'Cascadia Code', 'Consolas', monospace;
    color: #000000;
    font-weight: bold;
    background: transparent;
    border: none;
}

QLabel#SectionTitle {
    font-family: 'Cascadia Code', 'Consolas', monospace;
    color: #000000;
    font-weight: bold;
    background: transparent;
    border: none;
}

/* ============================================================================
   RESUMEN DEL DASHBOARD (Vista Bienvenido)
   ============================================================================ */
QLabel#ResumenTitulo {
    color: #334155;
    font-size: 16px;
    font-weight: bold;
    text-transform: uppercase;
    padding: 12px 0 4px 0;
    background: transparent;
    border: none;
}

QLabel#ResumenLinea {
    font-family: 'Cascadia Code', 'Consolas', monospace;
    font-size: 20px;
    color: #0F172A;
    background: transparent;
    border: none;
}

/* ============================================================================
   BOTON PRIMARIO (Iniciar Sesion, Ingresar, Crear Alumno, Guardar, Registrar)
   ============================================================================ */
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

/* ============================================================================
   BOTON SECUNDARIO (Crear Cuenta, Ver Alumnos, Autorizar, Registrar Personal)
   ============================================================================ */
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

/* ============================================================================
   BOTON DESTRUCTIVO / VOLVER
   ============================================================================ */
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

/* ============================================================================
   BOTON FILTRO / EXITO
   ============================================================================ */
QPushButton#FilterButton {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #d5e8d4, stop:1 #97d077);
    border: 2px solid #82b366;
    border-radius: 12px;
    color: #000000;
    font-family: 'Cascadia Code', monospace;
}
QPushButton#FilterButton:hover {
    background-color: #e2f0dc;
}

/* ============================================================================
   CAMPOS DE ENTRADA (INPUTS)
   ============================================================================ */
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

/* ============================================================================
   TABLAS
   ============================================================================ */
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

/* ============================================================================
   SIDEBAR (Dashboard Interno)
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
    background: transparent;
}

QLabel#SidebarGroupLabel {
    color: #94A3B8;
    font-size: 12px;
    font-weight: bold;
    text-transform: uppercase;
    padding: 16px 16px 6px 16px;
    background: transparent;
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
    font-family: 'Cascadia Code', monospace;
}
QPushButton#BtnSidebarItem:hover {
    background-color: #334155;
    color: #FFFFFF;
}
QPushButton#BtnSidebarItem:checked {
    background-color: #2563EB;
    color: #FFFFFF;
    font-weight: bold;
}

/* ============================================================================
   CONTENEDOR CENTRAL DEL DASHBOARD
   ============================================================================ */
QWidget#DashboardContainer {
    background-color: #66B2FF;
}
"""

"""
Componentes reutilizables de NeoED — Widgets nombrados segun Draw.io SSOT.

Cada widget tiene un objectName que el QSS global estiliza automaticamente.
"""
from PySide6.QtWidgets import QPushButton, QLabel, QLineEdit, QComboBox
from PySide6.QtCore import Qt


def HeaderTitleLabel(texto: str, size: int = 60) -> QLabel:
    """Titulo principal de la app (NeoED) — centrado, Cascadia Code."""
    label = QLabel(texto)
    label.setObjectName("HeaderTitle")
    label.setAlignment(Qt.AlignCenter)
    label.setStyleSheet(f"""
        font-size: {size}px;
        font-family: 'Cascadia Code', 'Consolas', monospace;
        color: #000000;
        font-weight: bold;
        background: transparent;
        border: none;
    """)
    return label


def SectionTitle(texto: str, size: int = 50) -> QLabel:
    """Titulo de seccion/ventana — centrado, Cascadia Code."""
    label = QLabel(texto)
    label.setObjectName("SectionTitle")
    label.setAlignment(Qt.AlignCenter)
    label.setStyleSheet(f"""
        font-size: {size}px;
        font-family: 'Cascadia Code', 'Consolas', monospace;
        color: #000000;
        font-weight: bold;
        background: transparent;
        border: none;
    """)
    return label


def PrimaryButton(texto: str, comando=None, size: int = 35) -> QPushButton:
    """
    Boton primario: degradado azul #dae8fc -> #7ea6e0, borde #6c8ebf.
    Uso: Iniciar Sesion, Ingresar, Crear Alumno, Guardar Alumno, Registrar.
    """
    boton = QPushButton(texto)
    boton.setObjectName("PrimaryButton")
    boton.setCursor(Qt.PointingHandCursor)
    boton.setStyleSheet(f"font-size: {size}px;")
    if comando:
        boton.clicked.connect(comando)
    return boton


def SecondaryButton(texto: str, comando=None, size: int = 40) -> QPushButton:
    """
    Boton secundario: fondo #bac8d3, borde #23445d.
    Uso: Crear Cuenta, Ver Alumnos, Autorizar Alumnos, Registrar Personal.
    """
    boton = QPushButton(texto)
    boton.setObjectName("SecondaryButton")
    boton.setCursor(Qt.PointingHandCursor)
    boton.setStyleSheet(f"font-size: {size}px;")
    if comando:
        boton.clicked.connect(comando)
    return boton


def DestructiveButton(texto: str, comando=None, size: int = 25) -> QPushButton:
    """
    Boton destructivo/volver: degradado #f8cecc -> #ea6b66, borde #b85450.
    Uso: Volver.
    """
    boton = QPushButton(texto)
    boton.setObjectName("DestructiveButton")
    boton.setCursor(Qt.PointingHandCursor)
    boton.setStyleSheet(f"font-size: {size}px;")
    if comando:
        boton.clicked.connect(comando)
    return boton


def FilterButton(texto: str, comando=None, size: int = 20) -> QPushButton:
    """
    Boton filtro/exito: degradado #d5e8d4 -> #97d077, borde #82b366.
    Uso: Filtrar.
    """
    boton = QPushButton(texto)
    boton.setObjectName("FilterButton")
    boton.setCursor(Qt.PointingHandCursor)
    boton.setStyleSheet(f"font-size: {size}px;")
    if comando:
        boton.clicked.connect(comando)
    return boton


def CustomLineEdit(placeholder: str = "", es_password: bool = False,
                   size: int = 20) -> QLineEdit:
    """
    Campo de entrada estilizado: fondo blanco, borde negro 2px, Cascadia Code.
    """
    entrada = QLineEdit()
    entrada.setPlaceholderText(placeholder)
    if es_password:
        entrada.setEchoMode(QLineEdit.Password)
    entrada.setStyleSheet(f"font-size: {size}px;")
    return entrada


def CustomComboBox(items: list, size: int = 20) -> QComboBox:
    """
    ComboBox estilizado: fondo blanco, borde negro 2px, Cascadia Code.
    items: lista de tuplas (valor_data, texto_visible)
    """
    combo = QComboBox()
    combo.addItem("Seleccionar", None)
    for valor, texto in items:
        combo.addItem(texto, valor)
    combo.setStyleSheet(f"font-size: {size}px;")
    return combo


def CustomLabel(texto: str, size: int = 20) -> QLabel:
    """Label de formulario — Cascadia Code, color negro."""
    label = QLabel(texto)
    label.setStyleSheet(f"""
        font-family: 'Cascadia Code', 'Consolas', monospace;
        font-size: {size}px;
        color: #000000;
        background: transparent;
    """)
    return label


def ErrorLabel(texto: str = "") -> QLabel:
    """Label para mensajes de error — rojo, centrado."""
    label = QLabel(texto)
    label.setAlignment(Qt.AlignCenter)
    label.setStyleSheet("""
        font-family: 'Cascadia Code', 'Consolas', monospace;
        font-size: 18px;
        color: #ff0000;
        font-weight: bold;
        background: transparent;
    """)
    return label

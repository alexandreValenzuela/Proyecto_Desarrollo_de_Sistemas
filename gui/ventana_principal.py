"""
Ventana Principal de NeoED — Menu Centralizado + Dashboard con Sidebar.

Hibrida segun ambas especificaciones:
- Menu Principal: botones centrados (Draw.io SSOT)
- Dashboard interno: Sidebar fijo + QStackedWidget (Spec 1)

Flujo:
  Menu Principal (botones centrados)
    └─ click seccion → Dashboard (Sidebar + vistas apiladas)

Las secciones con riesgo (autorizar alumnos, registrar personal) se OCULTAN
segun el nivel de permisos del usuario. Ocultar y no deshabilitar: un boton
deshabilitado segue dejando ver que la accion existe.
"""
from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                                QStackedWidget, QFrame, QLabel, QPushButton,
                                QButtonGroup)
from PySide6.QtCore import Qt

from auth.permisos import tiene_permiso
from gui.componentes import (HeaderTitleLabel, PrimaryButton, SecondaryButton,
                              DestructiveButton)
from gui.vistas.vista_bienvenido import VistaBienvenido
from gui.vistas.vista_ver_alumnos import VistaVerAlumnos
from gui.vistas.vista_cargar_alumnos import VistaCargarAlumnos
from gui.vistas.vista_autorizar_alumnos import VistaAutorizarAlumnos
from gui.vistas.vista_registrar_personal import VistaRegistrarPersonal
from gui.vistas.vista_notas import VistaNotas
from gui.vistas.vista_ausencias import VistaAusencias
from gui.vistas.vista_profesores import VistaProfesores
from gui.vistas.vista_mis_notas import VistaMisNotas
from gui.vistas.vista_mis_ausencias import VistaMisAusencias
from gui.vistas.vista_mis_datos import VistaMisDatos
from gui.vistas.vista_accesos import VistaAccesos
from gui.vistas.vista_cambiar_password import VistaCambiarPassword

# Indices de stack_vistas.
VISTA_BIENVENIDO = 0
VISTA_VER_ALUMNOS = 1
VISTA_CARGAR_ALUMNOS = 2
VISTA_AUTORIZAR = 3
VISTA_REGISTRAR_PERSONAL = 4
VISTA_PROFESORES = 5
VISTA_NOTAS = 6
VISTA_AUSENCIAS = 7
VISTA_MIS_NOTAS = 8
VISTA_MIS_AUSENCIAS = 9
VISTA_MIS_DATOS = 10
VISTA_ACCESOS = 11
VISTA_CAMBIAR_PASSWORD = 12

# Niveles minimos de las secciones restringidas.
NIVEL_ALUMNOS = 3            # ver / cargar alumnos (alta institucional)
NIVEL_AUTORIZAR = 3
NIVEL_REGISTRAR_PERSONAL = 10
NIVEL_PROFESORES = 3         # listado de personal (expone DNI del staff)
NIVEL_NOTAS = 5
NIVEL_AUSENCIAS = 3
NIVEL_ACCESOS = 5            # historial de intentos de login


class VentanaPrincipal(QMainWindow):

    # Candado de navegacion: nivel minimo por vista. Las secciones que no
    # aparecen acá son públicas para cualquier nivel.
    NIVELES_POR_VISTA = {
        VISTA_VER_ALUMNOS: NIVEL_ALUMNOS,
        VISTA_CARGAR_ALUMNOS: NIVEL_ALUMNOS,
        VISTA_AUTORIZAR: NIVEL_AUTORIZAR,
        VISTA_REGISTRAR_PERSONAL: NIVEL_REGISTRAR_PERSONAL,
        VISTA_PROFESORES: NIVEL_PROFESORES,
        VISTA_NOTAS: NIVEL_NOTAS,
        VISTA_AUSENCIAS: NIVEL_AUSENCIAS,
        VISTA_ACCESOS: NIVEL_ACCESOS,
    }

    # Vistas exclusivas del alumno (tipo=alumno): se abren solo con su DNI.
    VISTAS_ALUMNO = frozenset({
        VISTA_MIS_NOTAS,
        VISTA_MIS_AUSENCIAS,
        VISTA_MIS_DATOS,
    })

    def __init__(self, usuario, on_logout_callback=None):
        super().__init__()
        self.usuario = usuario
        self.on_logout_callback = on_logout_callback
        self.es_alumno = usuario.get("tipo") == "alumno"

        self.setWindowTitle("NeoED - Sistema de Gestion Escolar")
        self.resize(1600, 900)
        self.setMinimumSize(1280, 800)
        self.setObjectName("CanvasBase")

        # Botones del sidebar por indice de vista, para el resaltado.
        self.botones_sidebar = {}

        # Stack global: [0] = Menu Centralizado, [1] = Dashboard Sidebar
        self.stack_global = QStackedWidget()
        self.setCentralWidget(self.stack_global)

        self._crear_menu_central()
        self._crear_dashboard_sidebar()

        # Un alumno (nivel 0) no tiene secciones en el menu central: entra
        # directo al dashboard de bienvenida, donde puede cerrar sesion.
        if tiene_permiso(self.usuario, NIVEL_ALUMNOS):
            self.stack_global.setCurrentIndex(0)
        else:
            self.stack_global.setCurrentIndex(1)

    # ========================================================================
    # MENU CENTRALIZADO (Draw.io SSOT — spec 5.3)
    # ========================================================================

    def _crear_menu_central(self):
        menu_widget = QWidget()
        menu_widget.setObjectName("CanvasBase")
        layout = QVBoxLayout(menu_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(28)

        # Titulo
        layout.addWidget(HeaderTitleLabel("NeoED", 60))

        layout.addSpacing(40)

        # Botones del menu
        self.btn_crear = PrimaryButton(
            "Crear Alumno", lambda: self._abrir_seccion(VISTA_CARGAR_ALUMNOS), 40
        )
        self.btn_crear.setMinimumSize(400, 80)
        layout.addLayout(self._centrar(self.btn_crear))

        self.btn_ver_menu = SecondaryButton(
            "Ver Alumnos", lambda: self._abrir_seccion(VISTA_VER_ALUMNOS), 40
        )
        self.btn_ver_menu.setMinimumSize(400, 80)
        layout.addLayout(self._centrar(self.btn_ver_menu))

        self.btn_autorizar_menu = SecondaryButton(
            "Autorizar Alumnos", lambda: self._abrir_seccion(VISTA_AUTORIZAR), 40
        )
        self.btn_autorizar_menu.setMinimumSize(400, 80)
        layout.addLayout(self._centrar(self.btn_autorizar_menu))

        self.btn_personal_menu = SecondaryButton(
            "Registrar Personal",
            lambda: self._abrir_seccion(VISTA_REGISTRAR_PERSONAL), 40
        )
        self.btn_personal_menu.setMinimumSize(400, 80)
        layout.addLayout(self._centrar(self.btn_personal_menu))

        # Secciones restringidas: ocultas, nunca deshabilitadas.
        self.btn_crear.setVisible(tiene_permiso(self.usuario, NIVEL_ALUMNOS))
        self.btn_ver_menu.setVisible(tiene_permiso(self.usuario, NIVEL_ALUMNOS))
        self.btn_autorizar_menu.setVisible(
            tiene_permiso(self.usuario, NIVEL_AUTORIZAR)
        )
        self.btn_personal_menu.setVisible(
            tiene_permiso(self.usuario, NIVEL_REGISTRAR_PERSONAL)
        )

        layout.addStretch()

        self.stack_global.addWidget(menu_widget)  # Index 0

    def _centrar(self, boton):
        contenedor = QHBoxLayout()
        contenedor.setAlignment(Qt.AlignCenter)
        contenedor.addWidget(boton)
        return contenedor

    # ========================================================================
    # DASHBOARD CON SIDEBAR (Spec 1 — QStackedWidget interno)
    # ========================================================================

    def _crear_dashboard_sidebar(self):
        dashboard = QWidget()
        dashboard.setObjectName("DashboardContainer")
        layout = QHBoxLayout(dashboard)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar
        sidebar = self._crear_sidebar()
        layout.addWidget(sidebar)

        # Stack de vistas
        self.stack_vistas = QStackedWidget()
        layout.addWidget(self.stack_vistas)

        al_menu = self._volver_al_menu_central

        # Instanciar vistas
        self.vista_bienvenido = VistaBienvenido(self.usuario)
        self.vista_ver_alumnos = VistaVerAlumnos()
        self.vista_ver_alumnos.set_menu_callback(al_menu)
        self.vista_cargar_alumnos = VistaCargarAlumnos(
            on_guardado=self._refrescar_tabla_alumnos,
            on_volver=al_menu
        )
        self.vista_autorizar = VistaAutorizarAlumnos(self.usuario, on_volver=al_menu)
        self.vista_registrar_personal = VistaRegistrarPersonal(
            self.usuario, on_volver=al_menu
        )
        self.vista_profesores = VistaProfesores(self.usuario, on_volver=al_menu)
        self.vista_notas = VistaNotas(self.usuario, on_volver=al_menu)
        self.vista_ausencias = VistaAusencias(self.usuario, on_volver=al_menu)

        # Vistas exclusivas del alumno: sin boton "Volver" (no hay menu para
        # el alumno; navega por el sidebar y cierra sesion desde el dashboard).
        self.vista_mis_notas = VistaMisNotas(self.usuario)
        self.vista_mis_ausencias = VistaMisAusencias(self.usuario)
        self.vista_mis_datos = VistaMisDatos(self.usuario)

        # Vistas para todo tipo de cuenta.
        self.vista_accesos = VistaAccesos(self.usuario, on_volver=al_menu)
        self.vista_cambiar_password = VistaCambiarPassword(self.usuario)

        self.stack_vistas.addWidget(self.vista_bienvenido)             # 0
        self.stack_vistas.addWidget(self.vista_ver_alumnos)            # 1
        self.stack_vistas.addWidget(self.vista_cargar_alumnos)         # 2
        self.stack_vistas.addWidget(self.vista_autorizar)              # 3
        self.stack_vistas.addWidget(self.vista_registrar_personal)     # 4
        self.stack_vistas.addWidget(self.vista_profesores)             # 5
        self.stack_vistas.addWidget(self.vista_notas)                  # 6
        self.stack_vistas.addWidget(self.vista_ausencias)              # 7
        self.stack_vistas.addWidget(self.vista_mis_notas)              # 8
        self.stack_vistas.addWidget(self.vista_mis_ausencias)          # 9
        self.stack_vistas.addWidget(self.vista_mis_datos)              # 10
        self.stack_vistas.addWidget(self.vista_accesos)                # 11
        self.stack_vistas.addWidget(self.vista_cambiar_password)       # 12

        self.stack_vistas.setCurrentIndex(VISTA_BIENVENIDO)

        self.stack_global.addWidget(dashboard)  # Index 1

    def _crear_sidebar(self):
        frame = QFrame()
        frame.setObjectName("SidebarFrame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(4)

        # Grupo excluyente: el QSS ":checked" solo se activa si hay uno solo
        # marcado, y eso lo garantiza el grupo, no cada click.
        self.grupo_sidebar = QButtonGroup(self)
        self.grupo_sidebar.setExclusive(True)

        # Header
        lbl_logo = QLabel("NeoED Alumno" if self.es_alumno else "NeoED Admin")
        lbl_logo.setObjectName("SidebarHeader")
        layout.addWidget(lbl_logo)

        # Grupo Mi Cuenta (solo alumno)
        self.lbl_grupo_mi_cuenta = self._label_grupo("MI CUENTA")
        layout.addWidget(self.lbl_grupo_mi_cuenta)

        self.btn_mis_notas = self._boton_sidebar("Mis Notas", VISTA_MIS_NOTAS)
        layout.addWidget(self.btn_mis_notas)

        self.btn_mis_ausencias = self._boton_sidebar(
            "Mis Ausencias", VISTA_MIS_AUSENCIAS
        )
        layout.addWidget(self.btn_mis_ausencias)

        self.btn_mis_datos = self._boton_sidebar("Mis Datos", VISTA_MIS_DATOS)
        layout.addWidget(self.btn_mis_datos)

        self.btn_cambiar_password = self._boton_sidebar(
            "Cambiar Contraseña", VISTA_CAMBIAR_PASSWORD
        )
        layout.addWidget(self.btn_cambiar_password)

        self.btn_mis_notas.setVisible(self.es_alumno)
        self.btn_mis_ausencias.setVisible(self.es_alumno)
        self.btn_mis_datos.setVisible(self.es_alumno)

        # Grupo Alumnos
        self.lbl_grupo_alumnos = self._label_grupo("ALUMNOS")
        layout.addWidget(self.lbl_grupo_alumnos)

        self.btn_ver = self._boton_sidebar("Ver Alumnos", VISTA_VER_ALUMNOS)
        layout.addWidget(self.btn_ver)

        self.btn_cargar = self._boton_sidebar("Cargar Alumnos", VISTA_CARGAR_ALUMNOS)
        layout.addWidget(self.btn_cargar)

        # Grupo Personal
        self.lbl_grupo_personal = self._label_grupo("PERSONAL")
        layout.addWidget(self.lbl_grupo_personal)

        self.btn_autorizar = self._boton_sidebar("Autorizar Alumnos", VISTA_AUTORIZAR)
        layout.addWidget(self.btn_autorizar)

        self.btn_registrar = self._boton_sidebar(
            "Registrar Personal", VISTA_REGISTRAR_PERSONAL
        )
        layout.addWidget(self.btn_registrar)

        # Secciones restringidas: ocultas, nunca deshabilitadas.
        self.btn_ver.setVisible(tiene_permiso(self.usuario, NIVEL_ALUMNOS))
        self.btn_cargar.setVisible(tiene_permiso(self.usuario, NIVEL_ALUMNOS))
        self.btn_autorizar.setVisible(
            tiene_permiso(self.usuario, NIVEL_AUTORIZAR)
        )
        self.btn_registrar.setVisible(
            tiene_permiso(self.usuario, NIVEL_REGISTRAR_PERSONAL)
        )

        # Grupo Profesores
        self.lbl_grupo_profesores = self._label_grupo("PROFESORES")
        layout.addWidget(self.lbl_grupo_profesores)

        self.btn_profes = self._boton_sidebar("Ver Profesores", VISTA_PROFESORES)
        layout.addWidget(self.btn_profes)
        self.btn_profes.setVisible(tiene_permiso(self.usuario, NIVEL_PROFESORES))

        # Grupo Notas
        self.lbl_grupo_notas = self._label_grupo("NOTAS Y INFORMES")
        layout.addWidget(self.lbl_grupo_notas)

        self.btn_notas = self._boton_sidebar("Cargar / Ver Notas", VISTA_NOTAS)
        layout.addWidget(self.btn_notas)

        self.btn_ausencias = self._boton_sidebar(
            "Cargar / Ver Ausencias", VISTA_AUSENCIAS
        )
        layout.addWidget(self.btn_ausencias)

        self.btn_accesos = self._boton_sidebar(
            "Historial de Accesos", VISTA_ACCESOS
        )
        layout.addWidget(self.btn_accesos)

        # Secciones restringidas: ocultas, nunca deshabilitadas.
        self.btn_notas.setVisible(tiene_permiso(self.usuario, NIVEL_NOTAS))
        self.btn_ausencias.setVisible(
            tiene_permiso(self.usuario, NIVEL_AUSENCIAS)
        )
        self.btn_accesos.setVisible(
            tiene_permiso(self.usuario, NIVEL_ACCESOS)
        )

        # Un grupo sin botones visibles no muestra su rotulo.
        self._sincronizar_grupos()

        layout.addStretch()

        # Volver al Menu
        self.btn_menu = QPushButton("Volver al Menu")
        self.btn_menu.setObjectName("BtnSidebarItem")
        # El alumno entra directo al dashboard: volver al menu no le aporta.
        self.btn_menu.setVisible(tiene_permiso(self.usuario, NIVEL_ALUMNOS))
        self.btn_menu.clicked.connect(self._volver_al_menu_central)
        layout.addWidget(self.btn_menu)

        # Cerrar Sesion
        self.btn_logout = QPushButton("Cerrar Sesion")
        self.btn_logout.setObjectName("BtnSidebarItem")
        self.btn_logout.clicked.connect(self._ejecutar_logout)
        layout.addWidget(self.btn_logout)

        return frame

    def _boton_sidebar(self, texto, index_vista):
        """Crea un boton de seccion del sidebar y lo registra en el grupo."""
        boton = QPushButton(texto)
        boton.setObjectName("BtnSidebarItem")
        boton.setCheckable(True)
        boton.clicked.connect(lambda: self._navegar_vista(index_vista))
        self.grupo_sidebar.addButton(boton)
        self.botones_sidebar[index_vista] = boton
        return boton

    def _label_grupo(self, texto):
        lbl = QLabel(texto)
        lbl.setObjectName("SidebarGroupLabel")
        return lbl

    def _sincronizar_grupos(self):
        """Oculta los rotulos de grupo cuando no queda ningun boton visible.

        Usa isHidden(): durante la construccion la ventana todavia no se
        mostro, asi que isVisible() devolveria False para todo. isHidden()
        refleja la visibilidad explicita de cada boton.
        """
        grupos = {
            self.lbl_grupo_mi_cuenta: [
                self.btn_mis_notas, self.btn_mis_ausencias,
                self.btn_mis_datos, self.btn_cambiar_password
            ],
            self.lbl_grupo_alumnos: [self.btn_ver, self.btn_cargar],
            self.lbl_grupo_personal: [self.btn_autorizar, self.btn_registrar],
            self.lbl_grupo_profesores: [self.btn_profes],
            self.lbl_grupo_notas: [
                self.btn_notas, self.btn_ausencias, self.btn_accesos
            ],
        }
        for label, botones in grupos.items():
            label.setVisible(any(not b.isHidden() for b in botones))

    # ========================================================================
    # NAVEGACION
    # ========================================================================

    def _puede_abrir(self, index_vista):
        """Defensa en profundidad: oculta el boton, pero ninguna ruta de
        navegacion abre una seccion restringida sin el nivel necesario.

        Las vistas "Mi Cuenta" son exclusivas del alumno: el staff no las
        ve (sus datos no existen en notas/ausencias), y el alumno jamás
        accede a las del staff.
        """
        if index_vista in self.VISTAS_ALUMNO:
            return self.es_alumno

        nivel = self.NIVELES_POR_VISTA.get(index_vista)

        if nivel is None:
            return True

        return tiene_permiso(self.usuario, nivel)

    def _abrir_seccion(self, index_vista):
        """Abre el dashboard directamente en la vista indicada."""
        if not self._puede_abrir(index_vista):
            return

        self.stack_vistas.setCurrentIndex(index_vista)
        self._marcar_activo_sidebar(index_vista)
        self._cargar_vista(index_vista)
        self.stack_global.setCurrentIndex(1)

    def _navegar_vista(self, index):
        """Navega entre vistas dentro del dashboard sidebar."""
        if not self._puede_abrir(index):
            return

        self.stack_vistas.setCurrentIndex(index)
        self._marcar_activo_sidebar(index)
        self._cargar_vista(index)

    def _marcar_activo_sidebar(self, index_vista):
        """El grupo excluyente desmarca el resto automaticamente."""
        boton = self.botones_sidebar.get(index_vista)
        if boton:
            boton.setChecked(True)

    def _cargar_vista(self, index_vista):
        """Refresca los datos de las vistas que los piden al entrar."""
        if index_vista == VISTA_VER_ALUMNOS:
            self.vista_ver_alumnos.cargar_datos()
        elif index_vista == VISTA_PROFESORES:
            self.vista_profesores.cargar_datos()
        elif index_vista == VISTA_MIS_NOTAS:
            self.vista_mis_notas.cargar_datos()
        elif index_vista == VISTA_MIS_AUSENCIAS:
            self.vista_mis_ausencias.cargar_datos()
        elif index_vista == VISTA_MIS_DATOS:
            self.vista_mis_datos.cargar_datos()
        elif index_vista == VISTA_ACCESOS:
            self.vista_accesos.cargar_datos()

    def _refrescar_tabla_alumnos(self):
        self.vista_ver_alumnos.cargar_datos()
        self.stack_vistas.setCurrentIndex(VISTA_VER_ALUMNOS)
        self._marcar_activo_sidebar(VISTA_VER_ALUMNOS)

    def _ejecutar_logout(self):
        if self.on_logout_callback:
            self.on_logout_callback()

    def _volver_al_menu_central(self):
        """Cierra el dashboard y vuelve al Menu Centralizado."""
        self.stack_global.setCurrentIndex(0)

"""
Punto de entrada principal de NeoED.
Inicia la base de datos, los datos semilla, y lanza la interfaz grafica.

Flujo de navegacion (Draw.io SSOT):
  Landing -> Login -> Menu Principal (centralizado) -> Dashboard (Sidebar + vistas)
"""
from database.setup import inicio
from database.seed import cargar_datos_iniciales


def ejecutar_por_consola():
    from cli.consola import ejecutar_menu_consola
    ejecutar_menu_consola()


def ejecutar_por_interfaz():
    import sys
    from PySide6.QtWidgets import QApplication
    from gui.estilos import ESTILO_GLOBAL
    from gui.ventana_landing import VentanaLanding
    from gui.ventana_login import VentanaLogin
    from gui.ventana_principal import VentanaPrincipal

    app = QApplication(sys.argv)
    app.setStyleSheet(ESTILO_GLOBAL)

    ventanas = {}

    # --- Callbacks de navegacion ---

    def ir_a_login():
        ventanas["landing"].close()
        ventanas["login"] = VentanaLogin(
            al_loguear=al_loguear,
            al_volver=ir_a_landing
        )
        ventanas["login"].show()

    def ir_a_landing():
        for key in list(ventanas.keys()):
            ventanas[key].close()
            del ventanas[key]
        ventanas["landing"] = VentanaLanding(
            al_iniciar_sesion=ir_a_login,
            al_crear_cuenta=ir_a_login
        )
        ventanas["landing"].show()

    def al_loguear(usuario):
        ventanas["login"].close()
        ventanas["dashboard"] = VentanaPrincipal(
            usuario, on_logout_callback=ir_a_landing
        )
        ventanas["dashboard"].show()

    # --- Pantalla inicial: Landing ---
    ventanas["landing"] = VentanaLanding(
        al_iniciar_sesion=ir_a_login,
        al_crear_cuenta=ir_a_login
    )
    ventanas["landing"].show()

    sys.exit(app.exec())


def ejecutar_aplicacion():
    inicio()
    cargar_datos_iniciales()

    modo = input("Consola o interfaz? (c/i): ").strip().lower()

    if modo == "i":
        ejecutar_por_interfaz()
    else:
        ejecutar_por_consola()


if __name__ == "__main__":
    ejecutar_aplicacion()

"""Ventana principal con navegación lateral por módulos y panel principal."""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QMainWindow, QPushButton, QStackedWidget, QVBoxLayout, QWidget, QMessageBox,
)

from app.api_client import ApiClient, AuthError, ApiClientError
from app.ui.theme import (
    ACENTO, FONDO_PANEL, FONDO_PRINCIPAL, TEXTO_PRIMARIO, TEXTO_SECUNDARIO,
)
from app.views.login_view import LoginView
from app.views.dashboard_view import DashboardView
from app.views.consulta_bd_view import ConsultaBDView
from app.views.empleados_view import EmpleadosView
from app.views.asistencia_view import AsistenciaView
from app.views.incidencias_view import IncidenciasView
from app.views.justificantes_view import JustificantesView
from app.views.nomina_view import NominaView
from app.views.reportes_view import ReportesView
from app.views.auditoria_view import AuditoriaView
from app.views.usuarios_view import UsuariosView


class MainWindow(QMainWindow):
    def __init__(self, api_url: str = "http://127.0.0.1:8001"):
        super().__init__()
        self.setWindowTitle("Hamelín RH - Cool Circle")
        self.resize(1200, 760)
        self.api = ApiClient(api_url)
        self.usuario_actual = None  # Información del usuario logueado

        self._construir_interfaz()
        self._conectar_navegacion()

        # Mostrar login al inicio
        self.mostrar_login()

    def _construir_interfaz(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Panel lateral
        self.panel_lateral = QFrame()
        self.panel_lateral.setObjectName("panelLateral")
        self.panel_lateral.setFixedWidth(220)
        lateral_layout = QVBoxLayout(self.panel_lateral)
        lateral_layout.setContentsMargins(0, 16, 0, 16)
        lateral_layout.setSpacing(8)

        lbl_app = QLabel("Hamelín RH")
        lbl_app.setStyleSheet("font-size: 16px; font-weight: 700; color: #4f8bc4; padding-left: 14px;")
        lbl_app.setAlignment(Qt.AlignLeft)
        lateral_layout.addWidget(lbl_app)

        lbl_cliente = QLabel("Cool Circle")
        lbl_cliente.setStyleSheet("font-size: 11px; color: #9aa0a6; padding-left: 14px;")
        lateral_layout.addWidget(lbl_cliente)
        lateral_layout.addSpacing(12)

        self.lista_modulos = QListWidget()
        self.lista_modulos.setStyleSheet("""
            QListWidget { background: transparent; border: none; color: #e8e8ea; font-size: 13px; }
            QListWidget::item { padding: 10px 14px; border-radius: 6px; margin: 2px 12px; }
            QListWidget::item:selected { background: #4f8bc4; color: #ffffff; }
        """)
        self.lista_modulos.addItem("Panel de dirección")
        self.lista_modulos.addItem("Empleados")
        self.lista_modulos.addItem("Registro de asistencia")
        self.lista_modulos.addItem("Incidencias")
        self.lista_modulos.addItem("Justificantes")
        self.lista_modulos.addItem("Prenómina")
        self.lista_modulos.addItem("Reportes")
        self.lista_modulos.addItem("Auditoría")
        self.lista_modulos.addItem("Usuarios y permisos")
        self.lista_modulos.addItem("Consulta BD")
        self.lista_modulos.setCurrentRow(0)
        lateral_layout.addWidget(self.lista_modulos)
        lateral_layout.addStretch()

        btn_salir = QPushButton("Cerrar sesión")
        btn_salir.setObjectName("btnPeligro")
        btn_salir.clicked.connect(self.cerrar_sesion)
        lateral_layout.addWidget(btn_salir)

        # Contenido principal
        self.contenido = QStackedWidget()
        self.contenido.setObjectName("contenidoPrincipal")

        self.vista_login = LoginView(self.api, self)
        self.vista_dashboard = DashboardView(self.api, self)
        self.contenido.addWidget(self.vista_login)
        self.contenido.addWidget(self.vista_dashboard)

        # Crear vistas de módulos (se inicializan perezosamente)
        self.vistas = {}

        layout.addWidget(self.panel_lateral)
        layout.addWidget(self.contenido)

        self.panel_lateral.setVisible(False)

    def _conectar_navegacion(self) -> None:
        self.lista_modulos.currentRowChanged.connect(self._cambiar_modulo)

    def _cambiar_modulo(self, fila: int) -> None:
        if not self.api.get_token():
            self.lista_modulos.setCurrentRow(0)
            return

        nombres = [
            "dashboard", "empleados", "asistencia", "incidencias",
            "justificantes", "nomina", "reportes", "auditoria", "usuarios", "consulta_bd",
        ]
        nombre = nombres[fila] if 0 <= fila < len(nombres) else "dashboard"

        # Ocultar módulos restringidos si no es administrador
        modulos_admin = ["usuarios", "consulta_bd"]
        if nombre in modulos_admin and not self.es_administrador():
            mensaje_padre(self, "Acceso restringido", "Este módulo solo está disponible para el Administrador del sistema.", "advertencia")
            self.lista_modulos.setCurrentRow(0)
            return

        if nombre == "dashboard":
            self.contenido.setCurrentWidget(self.vista_dashboard)
            self.vista_dashboard.refrescar_metricas()
        else:
            self._cargar_modulo(nombre)

    def es_administrador(self) -> bool:
        """Verifica si el usuario actual es el administrador."""
        return self.usuario_actual == "admin.coolcircle"

    def _cargar_modulo(self, nombre: str):
        """Carga o reutiliza la vista del módulo solicitado."""
        if nombre in self.vistas:
            vista = self.vistas[nombre]
        else:
            if nombre == "empleados":
                vista = EmpleadosView(self.api, self, puede_eliminar=self.es_administrador())
            elif nombre == "asistencia":
                vista = AsistenciaView(self.api, self)
            elif nombre == "incidencias":
                vista = IncidenciasView(self.api, self)
            elif nombre == "justificantes":
                vista = JustificantesView(self.api, self)
            elif nombre == "nomina":
                vista = NominaView(self.api, self)
            elif nombre == "reportes":
                vista = ReportesView(self.api, self)
            elif nombre == "auditoria":
                vista = AuditoriaView(self.api, self)
            elif nombre == "usuarios":
                vista = UsuariosView(self.api, self)
            elif nombre == "consulta_bd":
                vista = ConsultaBDView(self.api, self)
            else:
                vista = QWidget()
            self.vistas[nombre] = vista
            self.contenido.addWidget(vista)

        self.contenido.setCurrentWidget(vista)

    def mostrar_login(self) -> None:
        self.contenido.setCurrentWidget(self.vista_login)
        self.panel_lateral.setVisible(False)
        self.setWindowTitle("Hamelín RH - Inicio de sesión")

    def mostrar_principal(self, username: str) -> None:
        self.usuario_actual = username
        self.panel_lateral.setVisible(True)
        self.contenido.setCurrentWidget(self.vista_dashboard)
        self.setWindowTitle(f"Hamelín RH - Cool Circle - Usuario: {username}")
        # Cargar métricas ahora que hay sesión activa
        self.vista_dashboard.refrescar_metricas()

    def cerrar_sesion(self) -> None:
        try:
            self.api.post("/api/v1/auth/logout")
        except Exception:
            pass
        self.api.clear_token()
        self.usuario_actual = None
        self.mostrar_login()

    def evento_error_api(self, error: Exception) -> None:
        if isinstance(error, AuthError):
            self.cerrar_sesion()
        else:
            QMessageBox.critical(self, "Error", str(error))

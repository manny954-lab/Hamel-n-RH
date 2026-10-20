"""Vista de inicio de sesión."""

from __future__ import annotations

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QWidget, QMessageBox,
)

from app.api_client import ApiClient, AuthError, ApiClientError
from app.ui.theme import ACENTO, ERROR, FONDO_TARJETA, TEXTO_PRIMARIO, TEXTO_SECUNDARIO


class HiloLogin(QThread):
    """Ejecuta el login en segundo plano para no bloquear la UI."""

    terminado = Signal(object)
    fallido = Signal(str)

    def __init__(self, api: ApiClient, username: str, password: str):
        super().__init__()
        self.api = api
        self.username = username
        self.password = password

    def run(self) -> None:
        try:
            self.api.login(self.username, self.password)
            self.terminado.emit(None)
        except AuthError as e:
            self.fallido.emit(str(e))
        except ApiClientError as e:
            self.fallido.emit(str(e))


class LoginView(QWidget):
    def __init__(self, api: ApiClient, ventana_principal):
        super().__init__()
        self.api = api
        self.ventana_principal = ventana_principal
        self._construir()

    def _construir(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)

        tarjeta = QFrame()
        tarjeta.setObjectName("tarjetaLogin")
        tarjeta.setFixedWidth(380)
        tarjeta.setStyleSheet(f"""
            QFrame#tarjetaLogin {{
                background-color: {FONDO_TARJETA};
                border: 1px solid {ACENTO};
                border-radius: 12px;
            }}
        """)
        t_layout = QVBoxLayout(tarjeta)
        t_layout.setContentsMargins(32, 32, 32, 32)
        t_layout.setSpacing(18)

        lbl_titulo = QLabel("Hamelín RH")
        lbl_titulo.setStyleSheet("font-size: 24px; font-weight: 800; color: #4f8bc4;")
        lbl_sub = QLabel("Sistema de control de asistencia, incidencias y prenómina")
        lbl_sub.setStyleSheet(f"font-size: 12px; color: {TEXTO_SECUNDARIO};")

        self.input_usuario = QLineEdit()
        self.input_usuario.setPlaceholderText("Usuario")
        self.input_clave = QLineEdit()
        self.input_clave.setPlaceholderText("Contraseña")
        self.input_clave.setEchoMode(QLineEdit.Password)

        self.btn_entrar = QPushButton("Iniciar sesión")
        self.btn_entrar.setObjectName("btnPrimario")
        self.btn_entrar.clicked.connect(self._intentar_login)

        self.lbl_mensaje = QLabel("")
        self.lbl_mensaje.setStyleSheet(f"color: {ERROR}; font-size: 12px;")
        self.lbl_mensaje.setWordWrap(True)

        t_layout.addWidget(lbl_titulo)
        t_layout.addWidget(lbl_sub)
        t_layout.addSpacing(10)
        t_layout.addWidget(self.input_usuario)
        t_layout.addWidget(self.input_clave)
        t_layout.addWidget(self.btn_entrar)
        t_layout.addWidget(self.lbl_mensaje)

        layout.addWidget(tarjeta)

    def _intentar_login(self):
        self.username = self.input_usuario.text().strip()
        clave = self.input_clave.text()
        if not self.username or not clave:
            self.lbl_mensaje.setText("Ingrese usuario y contraseña.")
            return
        self.lbl_mensaje.setText("")
        self.btn_entrar.setEnabled(False)
        self.btn_entrar.setText("Ingresando...")
        self.hilo = HiloLogin(self.api, self.username, clave)
        self.hilo.terminado.connect(self._login_exitoso)
        self.hilo.fallido.connect(self._login_fallido)
        self.hilo.start()

    def _login_exitoso(self, _):
        self.btn_entrar.setEnabled(True)
        self.btn_entrar.setText("Iniciar sesión")
        self.ventana_principal.mostrar_principal(self.username)

    def _login_fallido(self, mensaje: str):
        self.btn_entrar.setEnabled(True)
        self.btn_entrar.setText("Iniciar sesión")
        self.lbl_mensaje.setText(mensaje or "Credenciales incorrectas.")
        QMessageBox.warning(self, "Acceso denegado", mensaje or "Credenciales incorrectas.")

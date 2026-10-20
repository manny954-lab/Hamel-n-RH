"""Vista de usuarios y permisos (solo administrador)."""

from __future__ import annotations

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget, QComboBox,
)

from app.api_client import ApiClient, ApiClientError
from app.components.componentes import BotonAccion, mensaje_padre


class CargarUsuarios(QThread):
    listo = Signal(list)
    fallido = Signal(str)

    def __init__(self, api: ApiClient):
        super().__init__()
        self.api = api

    def run(self):
        try:
            self.listo.emit(self.api.get("/api/v1/usuarios"))
        except ApiClientError as e:
            self.fallido.emit(str(e))


class UsuariosView(QWidget):
    def __init__(self, api: ApiClient, parent=None):
        super().__init__(parent)
        self.api = api
        self._construir()
        self.cargar()

    def _construir(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        lbl = QLabel("Usuarios y roles")
        lbl.setStyleSheet("font-size: 18px; font-weight: 700;")
        layout.addWidget(lbl)
        layout.addWidget(QLabel(
            "Los permisos se verifican en el servidor. Un usuario no puede elevar sus propios privilegios."
        ))

        barra = QHBoxLayout()
        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("Buscar por usuario...")
        btn_refresh = BotonAccion("Actualizar")
        btn_refresh.clicked.connect(self.cargar)
        barra.addWidget(self.input_buscar, stretch=1)
        barra.addWidget(btn_refresh)
        layout.addLayout(barra)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["Usuario", "Nombre", "Email", "Activo", "Último acceso", "ID"])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.tabla, stretch=1)

        self.lbl_estado = QLabel("")
        self.lbl_estado.setStyleSheet("color: #9aa0a6; font-size: 12px;")
        layout.addWidget(self.lbl_estado)

    def cargar(self):
        self.lbl_estado.setText("Cargando usuarios...")
        self.hilo = CargarUsuarios(self.api)
        self.hilo.listo.connect(self._listo)
        self.hilo.fallido.connect(self._error)
        self.hilo.start()

    def _listo(self, datos):
        self.tabla.setRowCount(0)
        texto = self.input_buscar.text().lower()
        for u in datos:
            if (texto in u.get("username", "").lower()
                    or texto in u.get("nombre_completo", "").lower()):
                self._agregar_fila(u)
        self.lbl_estado.setText(f"{self.tabla.rowCount()} usuario(s).")

    def _agregar_fila(self, u):
        fila = self.tabla.rowCount()
        self.tabla.insertRow(fila)
        valores = [
            u.get("username", ""),
            u.get("nombre_completo", ""),
            u.get("email") or "",
            "Sí" if u.get("activo") else "No",
            u.get("ultimo_acceso") or "",
            str(u.get("id", ""))[:8],
        ]
        for col, v in enumerate(valores):
            self.tabla.setItem(fila, col, QTableWidgetItem(str(v)))

    def _error(self, mensaje):
        self.lbl_estado.setText(f"Error: {mensaje}")
        mensaje_padre(self, "Error", mensaje, "error")

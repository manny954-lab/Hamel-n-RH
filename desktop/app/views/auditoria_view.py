"""Vista de auditoría (solo lectura)."""

from __future__ import annotations

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget,
)

from app.api_client import ApiClient, ApiClientError
from app.components.componentes import BotonAccion, mensaje_padre


class CargarAuditoria(QThread):
    listo = Signal(list)
    fallido = Signal(str)

    def __init__(self, api: ApiClient, params=None):
        super().__init__()
        self.api = api
        self.params = params or {}

    def run(self):
        try:
            self.listo.emit(self.api.get("/api/v1/auditoria", params=self.params))
        except ApiClientError as e:
            self.fallido.emit(str(e))


class AuditoriaView(QWidget):
    def __init__(self, api: ApiClient, parent=None):
        super().__init__(parent)
        self.api = api
        self._construir()
        self.cargar()

    def _construir(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        lbl = QLabel("Auditoría (solo lectura)")
        lbl.setStyleSheet("font-size: 18px; font-weight: 700;")
        layout.addWidget(lbl)

        barra = QHBoxLayout()
        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("Buscar por entidad o operación...")
        btn_refresh = BotonAccion("Actualizar")
        btn_refresh.clicked.connect(self.cargar)
        barra.addWidget(self.input_buscar, stretch=1)
        barra.addWidget(btn_refresh)
        layout.addLayout(barra)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(8)
        self.tabla.setHorizontalHeaderLabels([
            "Fecha y hora", "Usuario", "Operación", "Entidad", "Registro",
            "Resultado", "Motivo", "ID",
        ])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.tabla, stretch=1)

        self.lbl_estado = QLabel("")
        self.lbl_estado.setStyleSheet("color: #9aa0a6; font-size: 12px;")
        layout.addWidget(self.lbl_estado)

    def cargar(self):
        self.lbl_estado.setText("Cargando auditoría...")
        self.hilo = CargarAuditoria(self.api)
        self.hilo.listo.connect(self._listo)
        self.hilo.fallido.connect(self._error)
        self.hilo.start()

    def _listo(self, datos):
        self.tabla.setRowCount(0)
        texto = self.input_buscar.text().lower()
        for r in datos:
            if (texto in r.get("entidad", "").lower()
                    or texto in r.get("operacion", "").lower()
                    or texto in (r.get("usuario_id") or "")):
                self._agregar_fila(r)
        self.lbl_estado.setText(f"{self.tabla.rowCount()} registro(s) de auditoría.")

    def _agregar_fila(self, r):
        fila = self.tabla.rowCount()
        self.tabla.insertRow(fila)
        valores = [
            r.get("fecha_hora", ""),
            str(r.get("usuario_id", ""))[:8] if r.get("usuario_id") else "sistema",
            r.get("operacion", ""),
            r.get("entidad", ""),
            r.get("registro_id") or "",
            r.get("resultado", ""),
            r.get("motivo") or "",
            str(r.get("id", ""))[:8],
        ]
        for col, v in enumerate(valores):
            self.tabla.setItem(fila, col, QTableWidgetItem(str(v)))

    def _error(self, mensaje):
        self.lbl_estado.setText(f"Error: {mensaje}")
        mensaje_padre(self, "Error", mensaje, "error")

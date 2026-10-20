"""Vista de justificantes."""

from __future__ import annotations

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget, QComboBox,
)
import uuid

from app.api_client import ApiClient, ApiClientError
from app.components.componentes import BotonAccion, mensaje_padre


class CargarLista(QThread):
    listo = Signal(list)
    fallido = Signal(str)

    def __init__(self, api: ApiClient, ruta: str, params=None):
        super().__init__()
        self.api = api
        self.ruta = ruta
        self.params = params or {}

    def run(self):
        try:
            self.listo.emit(self.api.get(self.ruta, params=self.params))
        except ApiClientError as e:
            self.fallido.emit(str(e))


class JustificantesView(QWidget):
    def __init__(self, api: ApiClient, parent=None):
        super().__init__(parent)
        self.api = api
        self._construir()
        self.cargar()

    def _construir(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        lbl = QLabel("Justificantes")
        lbl.setStyleSheet("font-size: 18px; font-weight: 700;")
        layout.addWidget(lbl)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels([
            "Núm. Empleado", "Nombre Empleado", "Tipo", "Fecha incidencia",
            "Descripción", "Estado", "Fecha solicitud",
        ])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.tabla, stretch=1)

        form = QHBoxLayout()
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(["pendiente", "en_revision", "aprobada", "rechazada", "cancelada"])
        self.edit_motivo = QLineEdit()
        self.edit_motivo.setPlaceholderText("Motivo (requerido si rechaza)")
        btn_aprobar = BotonAccion("Aprobar seleccionada", primario=True)
        btn_aprobar.clicked.connect(self.aprobar)
        btn_rechazar = BotonAccion("Rechazar seleccionada")
        btn_rechazar.setObjectName("btnPeligro")
        btn_rechazar.clicked.connect(self.rechazar)
        btn_refresh = BotonAccion("Actualizar")
        btn_refresh.clicked.connect(self.cargar)
        form.addWidget(self.combo_estado)
        form.addWidget(self.edit_motivo)
        form.addWidget(btn_aprobar)
        form.addWidget(btn_rechazar)
        form.addWidget(btn_refresh)
        layout.addLayout(form)

        self.lbl_estado = QLabel("")
        self.lbl_estado.setStyleSheet("color: #9aa0a6; font-size: 12px;")
        layout.addWidget(self.lbl_estado)

    def cargar(self):
        self.lbl_estado.setText("Cargando justificantes...")
        self.hilo = CargarLista(self.api, "/api/v1/incidencias/justificantes")
        self.hilo.listo.connect(self._listo)
        self.hilo.fallido.connect(self._error)
        self.hilo.start()

    def _listo(self, datos):
        self.tabla.setRowCount(0)
        self._datos = datos
        for j in datos:
            fila = self.tabla.rowCount()
            self.tabla.insertRow(fila)
            valores = [
                j.get("numero_empleado", ""),
                j.get("nombre_empleado", ""),
                j.get("tipo", ""),
                j.get("fecha_incidencia", ""),
                j.get("descripcion") or "",
                j.get("estado", ""),
                j.get("fecha_solicitud", ""),
            ]
            for col, v in enumerate(valores):
                self.tabla.setItem(fila, col, QTableWidgetItem(str(v)))
        self.lbl_estado.setText(f"{len(datos)} justificante(s).")

    def _error(self, mensaje):
        self.lbl_estado.setText(f"Error: {mensaje}")
        mensaje_padre(self, "Error", mensaje, "error")

    def _id_seleccionado(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            return None
        if fila >= len(self._datos):
            return None
        jid = self._datos[fila].get("id", "")
        if not jid:
            return None
        try:
            uuid.UUID(str(jid))
        except (ValueError, AttributeError):
            return None
        return str(jid)

    def aprobar(self):
        jid = self._id_seleccionado()
        if not jid:
            mensaje_padre(self, "Validación", "Seleccione un justificante de la tabla.", "advertencia")
            return
        try:
            self.api.post(f"/api/v1/incidencias/justificantes/{jid}/decidir",
                          params={"estado": "aprobada", "motivo": ""})
            mensaje_padre(self, "Éxito", "Justificante aprobado.", "exito")
            self.cargar()
        except ApiClientError as e:
            mensaje_padre(self, "Error", str(e), "error")

    def rechazar(self):
        jid = self._id_seleccionado()
        if not jid:
            mensaje_padre(self, "Validación", "Seleccione un justificante de la tabla.", "advertencia")
            return
        motivo = self.edit_motivo.text().strip()
        if not motivo:
            mensaje_padre(self, "Validación", "El motivo es obligatorio para rechazar.", "advertencia")
            return
        try:
            self.api.post(f"/api/v1/incidencias/justificantes/{jid}/decidir",
                          params={"estado": "rechazada", "motivo": motivo})
            mensaje_padre(self, "Éxito", "Justificante rechazado.", "exito")
            self.cargar()
        except ApiClientError as e:
            mensaje_padre(self, "Error", str(e), "error")

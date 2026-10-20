"""Vista de incidencias y justificantes."""

from __future__ import annotations

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget, QComboBox, QDateEdit,
)

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


class IncidenciasView(QWidget):
    def __init__(self, api: ApiClient, parent=None):
        super().__init__(parent)
        self.api = api
        self._construir()
        self.cargar_incidencias()

    def _construir(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        barra = QHBoxLayout()
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(["todos", "pendiente", "en_revision", "aprobada", "rechazada"])
        btn_refresh = BotonAccion("Actualizar")
        btn_refresh.clicked.connect(self.cargar_incidencias)
        barra.addWidget(QLabel("Estado:"))
        barra.addWidget(self.combo_estado)
        barra.addStretch()
        barra.addWidget(btn_refresh)
        layout.addLayout(barra)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(9)
        self.tabla.setHorizontalHeaderLabels([
            "Núm. Empleado", "Nombre Empleado", "Fecha", "Tipo",
            "Minutos retardo", "Tiempo (min)", "Regla aplicada",
            "Justificada", "Estado",
        ])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.tabla, stretch=1)

        self.lbl_estado = QLabel("")
        self.lbl_estado.setStyleSheet("color: #9aa0a6; font-size: 12px;")
        layout.addWidget(self.lbl_estado)

    def cargar_incidencias(self):
        estado = self.combo_estado.currentText()
        params = None if estado == "todos" else {"estado": estado}
        self.lbl_estado.setText("Cargando incidencias...")
        self.hilo = CargarLista(self.api, "/api/v1/incidencias", params)
        self.hilo.listo.connect(self._listo)
        self.hilo.fallido.connect(self._error)
        self.hilo.start()

    def _listo(self, datos):
        self.tabla.setRowCount(0)
        for inc in datos:
            fila = self.tabla.rowCount()
            self.tabla.insertRow(fila)
            valores = [
                inc.get("numero_empleado", ""),
                inc.get("nombre_empleado", ""),
                inc.get("fecha", ""),
                inc.get("tipo_incidencia", ""),
                str(inc.get("minutos_retardo", 0)),
                str(inc.get("tiempo_incidencia_minutos", 0)),
                inc.get("regla_aplicada", ""),
                "Sí" if inc.get("justificada") else "No",
                inc.get("estado", ""),
            ]
            for col, v in enumerate(valores):
                self.tabla.setItem(fila, col, QTableWidgetItem(str(v)))
        self.lbl_estado.setText(f"{len(datos)} incidencia(s).")

    def _error(self, mensaje):
        self.lbl_estado.setText(f"Error: {mensaje}")
        mensaje_padre(self, "Error", mensaje, "error")


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
        from PySide6.QtWidgets import QLabel as _QL
        lbl.setStyleSheet("font-size: 18px; font-weight: 700;")
        layout.addWidget(lbl)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels([
            "Empleado", "Tipo", "Fecha incidencia", "Descripción", "Estado",
            "Fecha solicitud", "ID",
        ])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.tabla, stretch=1)

        form = QHBoxLayout()
        self.edit_estado = QComboBox()
        self.edit_estado.addItems(["pendiente", "en_revision", "aprobada", "rechazada", "cancelada"])
        self.edit_motivo = QLineEdit()
        self.edit_motivo.setPlaceholderText("Motivo (requerido si rechaza)")
        btn_aprobar = BotonAccion("Aprobar seleccionada", primario=True)
        btn_aprobar.clicked.connect(self.aprobar)
        btn_rechazar = BotonAccion("Rechazar seleccionada")
        btn_rechazar.setObjectName("btnPeligro")
        btn_rechazar.clicked.connect(self.rechazar)
        btn_refresh = BotonAccion("Actualizar")
        btn_refresh.clicked.connect(self.cargar)
        form.addWidget(self.edit_estado)
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
                str(j.get("empleado_id", ""))[:8],
                j.get("tipo", ""),
                j.get("fecha_incidencia", ""),
                j.get("descripcion") or "",
                j.get("estado", ""),
                j.get("fecha_solicitud", ""),
                str(j.get("id", ""))[:8],
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
        return self._datos[fila]["id"]

    def aprobar(self):
        jid = self._id_seleccionado()
        if not jid:
            mensaje_padre(self, "Validación", "Seleccione un justificante.", "advertencia")
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
            mensaje_padre(self, "Validación", "Seleccione un justificante.", "advertencia")
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

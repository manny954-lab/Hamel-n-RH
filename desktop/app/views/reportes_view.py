"""Vista de reportes."""

from __future__ import annotations

from PySide6.QtCore import QDate, QThread, Signal
from PySide6.QtWidgets import (
    QDateEdit, QHBoxLayout, QLabel, QMessageBox, QPushButton, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)

from app.api_client import ApiClient, ApiClientError
from app.components.componentes import BotonAccion, mensaje_padre


class CargarReporte(QThread):
    listo = Signal(dict)
    fallido = Signal(str)

    def __init__(self, api: ApiClient, ruta: str, params):
        super().__init__()
        self.api = api
        self.ruta = ruta
        self.params = params

    def run(self):
        try:
            self.listo.emit(self.api.get(self.ruta, params=self.params))
        except ApiClientError as e:
            self.fallido.emit(str(e))


class ReportesView(QWidget):
    def __init__(self, api: ApiClient, parent=None):
        super().__init__(parent)
        self.api = api
        self._construir()
        self.ejecutar()

    def _construir(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        lbl = QLabel("Reportes")
        lbl.setStyleSheet("font-size: 18px; font-weight: 700;")
        layout.addWidget(lbl)

        form = QHBoxLayout()
        self.edit_inicio = QDateEdit()
        self.edit_inicio.setDate(self.edit_inicio.date().addDays(-15))
        self.edit_inicio.setDisplayFormat("dd/MM/yyyy")
        self.edit_fin = QDateEdit()
        self.edit_fin.setDate(QDate.currentDate())
        self.edit_fin.setDisplayFormat("dd/MM/yyyy")
        btn_ejecutar = BotonAccion("Reporte quincenal", primario=True)
        btn_ejecutar.clicked.connect(self.ejecutar)
        btn_exportar = BotonAccion("Exportar CSV")
        btn_exportar.clicked.connect(self.exportar)
        form.addWidget(QLabel("Desde:"))
        form.addWidget(self.edit_inicio)
        form.addWidget(QLabel("Hasta:"))
        form.addWidget(self.edit_fin)
        form.addStretch()
        form.addWidget(btn_ejecutar)
        form.addWidget(btn_exportar)
        layout.addLayout(form)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(8)
        self.tabla.setHorizontalHeaderLabels([
            "Número empleado", "Nombre", "Departamento", "Fecha",
            "Tipo incidencia", "Minutos retardo", "Justificada", "Estado",
        ])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.tabla, stretch=1)

        self.lbl_estado = QLabel("")
        self.lbl_estado.setStyleSheet("color: #9aa0a6; font-size: 12px;")
        layout.addWidget(self.lbl_estado)

    def ejecutar(self):
        params = {
            "fecha_inicio": self.edit_inicio.date().toString("yyyy-MM-dd"),
            "fecha_fin": self.edit_fin.date().toString("yyyy-MM-dd"),
        }
        self.lbl_estado.setText("Generando reporte...")
        self.hilo = CargarReporte(self.api, "/api/v1/reportes/quincenal", params)
        self.hilo.listo.connect(self._listo)
        self.hilo.fallido.connect(self._error)
        self.hilo.start()

    def _listo(self, datos):
        self.tabla.setRowCount(0)
        self._datos = datos.get("filas", [])
        total = datos.get("total", 0)
        for f in self._datos:
            fila = self.tabla.rowCount()
            self.tabla.insertRow(fila)
            valores = [
                f.get("numero_empleado", ""),
                f.get("nombre", ""),
                f.get("departamento", ""),
                f.get("fecha_incidencia", ""),
                f.get("tipo_incidencia", ""),
                str(f.get("minutos_retardo", 0)),
                "Sí" if f.get("justificada") else "No",
                f.get("estado", ""),
            ]
            for col, v in enumerate(valores):
                self.tabla.setItem(fila, col, QTableWidgetItem(str(v)))
        self.lbl_estado.setText(f"{total} registro(s) en el reporte.")

    def _error(self, mensaje):
        self.lbl_estado.setText(f"Error: {mensaje}")
        mensaje_padre(self, "Error", mensaje, "error")

    def exportar(self):
        if not getattr(self, "_datos", []):
            mensaje_padre(self, "Validación", "No hay datos para exportar.", "advertencia")
            return
        mensaje_padre(self, "Exportar", "La exportación a CSV se genera desde el servidor. "
                        "Esta versión de escritorio consulta y muestra el reporte.", "info")

"""Vista de control de nómina y prenómina."""

from __future__ import annotations

from datetime import date
from typing import Optional
from uuid import UUID

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QDateEdit, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget, QComboBox,
)

from app.api_client import ApiClient, ApiClientError
from app.components.componentes import BotonAccion, mensaje_padre


class CargarLista(QThread):
    """Hilo para peticiones GET."""

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


class CalcularPrenomina(QThread):
    """Hilo para calcular prenómina (usa POST)."""

    listo = Signal(list)
    fallido = Signal(str)

    def __init__(self, api: ApiClient, periodo_id: UUID):
        super().__init__()
        self.api = api
        self.periodo_id = periodo_id

    def run(self):
        try:
            self.listo.emit(self.api.post(f"/api/v1/nomina/periodos/{self.periodo_id}/calcular"))
        except ApiClientError as e:
            self.fallido.emit(str(e))


class NominaView(QWidget):
    def __init__(self, api: ApiClient, parent=None):
        super().__init__(parent)
        self.api = api
        self._construir()
        self.cargar_periodos()

    def _construir(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        lbl = QLabel("Prenómina revisable")
        lbl.setStyleSheet("font-size: 18px; font-weight: 700;")
        layout.addWidget(lbl)
        layout.addWidget(QLabel(
            "La prenómina es revisable y no sustituye procesos oficiales de nómina sin validación."
        ))

        form = QHBoxLayout()
        self.edit_nombre = QLineEdit()
        self.edit_nombre.setPlaceholderText("Nombre del periodo (ej. Quincena 1 Enero 2026)")
        self.edit_inicio = QDateEdit(date(2026, 1, 1))
        self.edit_inicio.setDisplayFormat("dd/MM/yyyy")
        self.edit_fin = QDateEdit(date(2026, 1, 15))
        self.edit_fin.setDisplayFormat("dd/MM/yyyy")
        btn_crear = BotonAccion("Crear periodo", primario=True)
        btn_crear.clicked.connect(self.crear_periodo)
        btn_calcular = BotonAccion("Calcular prenómina")
        btn_calcular.clicked.connect(self.calcular)
        btn_cerrar = BotonAccion("Cerrar periodo")
        btn_cerrar.setObjectName("btnAdvertencia")
        btn_cerrar.clicked.connect(self.cerrar)
        form.addWidget(self.edit_nombre, stretch=1)
        form.addWidget(self.edit_inicio)
        form.addWidget(self.edit_fin)
        form.addWidget(btn_crear)
        form.addWidget(btn_calcular)
        form.addWidget(btn_cerrar)
        layout.addLayout(form)

        self.tabla_periodos = QTableWidget()
        self.tabla_periodos.setColumnCount(5)
        self.tabla_periodos.setHorizontalHeaderLabels(["Nombre", "Inicio", "Fin", "Estado", "ID"])
        self.tabla_periodos.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(QLabel("Periodos de nómina:"))
        layout.addWidget(self.tabla_periodos, stretch=1)

        self.tabla_resultados = QTableWidget()
        self.tabla_resultados.setColumnCount(12)
        self.tabla_resultados.setHorizontalHeaderLabels([
            "Empleado", "Sueldo base", "Días laborables", "Días asistidos",
            "Faltas", "Faltas just.", "Retardos", "Minutos retardo",
            "Ajustes prop.", "Ajustes apr.", "Total preliminar", "Estado",
        ])
        self.tabla_resultados.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(QLabel("Resultados de prenómina (periodo seleccionado):"))
        layout.addWidget(self.tabla_resultados, stretch=1)

        self.lbl_estado = QLabel("")
        self.lbl_estado.setStyleSheet("color: #9aa0a6; font-size: 12px;")
        layout.addWidget(self.lbl_estado)

    def cargar_periodos(self):
        self.lbl_estado.setText("Cargando periodos...")
        self.hilo = CargarLista(self.api, "/api/v1/nomina/periodos")
        self.hilo.listo.connect(self._periodos_listos)
        self.hilo.fallido.connect(self._error)
        self.hilo.start()

    def _periodos_listos(self, datos):
        self.tabla_periodos.setRowCount(0)
        self._periodos = datos
        for p in datos:
            fila = self.tabla_periodos.rowCount()
            self.tabla_periodos.insertRow(fila)
            for col, v in enumerate([p.get("nombre", ""), p.get("fecha_inicio", ""),
                                     p.get("fecha_fin", ""), p.get("estado", ""),
                                     str(p.get("id", ""))[:8]]):
                self.tabla_periodos.setItem(fila, col, QTableWidgetItem(str(v)))
        self.lbl_estado.setText(f"{len(datos)} periodo(s).")

    def _error(self, mensaje: str):
        self.lbl_estado.setText(f"Error: {mensaje}")
        mensaje_padre(self, "Error", mensaje, "error")

    def crear_periodo(self):
        nombre = self.edit_nombre.text().strip()
        if not nombre:
            mensaje_padre(self, "Validación", "Ingrese un nombre de periodo.", "advertencia")
            return
        datos = {
            "nombre": nombre,
            "fecha_inicio": self.edit_inicio.date().toString("yyyy-MM-dd"),
            "fecha_fin": self.edit_fin.date().toString("yyyy-MM-dd"),
        }
        try:
            self.api.post("/api/v1/nomina/periodos", json=datos)
            mensaje_padre(self, "Éxito", "Periodo creado.", "exito")
            self.cargar_periodos()
        except ApiClientError as e:
            mensaje_padre(self, "Error", str(e), "error")

    def calcular(self):
        fila = self.tabla_periodos.currentRow()
        if fila < 0:
            mensaje_padre(self, "Validación", "Seleccione un periodo.", "advertencia")
            return
        pid = self._periodos[fila]["id"]
        self.lbl_estado.setText("Calculando prenómina...")
        self.hilo = CalcularPrenomina(self.api, pid)
        self.hilo.listo.connect(self._resultados_listos)
        self.hilo.fallido.connect(self._error)
        self.hilo.start()

    def _resultados_listos(self, datos):
        self.tabla_resultados.setRowCount(0)
        for r in datos:
            fila = self.tabla_resultados.rowCount()
            self.tabla_resultados.insertRow(fila)
            valores = [
                str(r.get("empleado_id", ""))[:8],
                str(r.get("sueldo_base_periodo", 0)),
                str(r.get("dias_laborables", 0)),
                str(r.get("dias_asistidos", 0)),
                str(r.get("faltas_registradas", 0)),
                str(r.get("faltas_justificadas", 0)),
                str(r.get("retardos", 0)),
                str(r.get("minutos_retardo_acumulados", 0)),
                str(r.get("ajustes_propuestos", 0)),
                str(r.get("ajustes_aprobados", 0)),
                str(r.get("total_preliminar", 0)),
                r.get("estado_aprobacion", ""),
            ]
            for col, v in enumerate(valores):
                self.tabla_resultados.setItem(fila, col, QTableWidgetItem(str(v)))
        self.lbl_estado.setText(f"{len(datos)} resultado(s) de prenómina.")

    def cerrar(self):
        fila = self.tabla_periodos.currentRow()
        if fila < 0:
            mensaje_padre(self, "Validación", "Seleccione un periodo.", "advertencia")
            return
        pid = self._periodos[fila]["id"]
        try:
            self.api.post(f"/api/v1/nomina/periodos/{pid}/cerrar")
            mensaje_padre(self, "Éxito", "Periodo cerrado.", "exito")
            self.cargar_periodos()
        except ApiClientError as e:
            mensaje_padre(self, "Error", str(e), "error")

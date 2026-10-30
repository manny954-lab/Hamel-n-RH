"""Vista de control de nómina y prenómina con tarjetas de resumen."""

from __future__ import annotations

from datetime import date
from typing import Optional
from uuid import UUID

from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDateEdit, QFrame, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QComboBox, QHeaderView,
)

from app.api_client import ApiClient, ApiClientError
from app.components.componentes import BotonAccion, mensaje_padre
from app.ui.theme import (
    ACENTO, ADVERTENCIA, ERROR, EXITO, FONDO_PRINCIPAL, FONDO_PANEL,
    FONDO_TARJETA, TEXTO_PRIMARIO, TEXTO_SECUNDARIO,
)


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


class AccionAPI(QThread):
    listo = Signal(object)
    fallido = Signal(str)

    def __init__(self, api: ApiClient, metodo: str, ruta: str, datos=None):
        super().__init__()
        self.api = api
        self.metodo = metodo
        self.ruta = ruta
        self.datos = datos or {}

    def run(self):
        try:
            if self.metodo == "GET":
                self.listo.emit(self.api.get(self.ruta))
            elif self.metodo == "POST":
                self.listo.emit(self.api.post(self.ruta, json=self.datos))
        except ApiClientError as e:
            self.fallido.emit(str(e))


class TarjetaResumen(QFrame):
    def __init__(self, etiqueta: str, valor: str = "0", color=ACENTO):
        super().__init__()
        self.setObjectName("tarjetaResumen")
        self.setFixedSize(190, 110)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)
        lbl_etq = QLabel(etiqueta.upper())
        lbl_etq.setStyleSheet(f"color: {TEXTO_SECUNDARIO}; font-size: 11px; font-weight: 700;")
        self.lbl_valor = QLabel(valor)
        self.lbl_valor.setObjectName("valorResumen")
        color_hex = color.name if hasattr(color, "name") else str(color)
        self.lbl_valor.setStyleSheet(f"color: {color_hex}; font-size: 28px; font-weight: 800;")
        layout.addWidget(lbl_etq)
        layout.addWidget(self.lbl_valor)
        layout.addStretch()
        barra = QFrame()
        barra.setFixedHeight(4)
        barra.setStyleSheet(f"background-color: {color_hex}; border-radius: 2px;")
        layout.addWidget(barra)
        color_hex = color.name if hasattr(color, "name") else str(color)
        self.setStyleSheet(f"""
            QFrame#tarjetaResumen {{
                background-color: {FONDO_TARJETA};
                border: 1px solid #3a3a45;
                border-radius: 12px;
            }}
        """)

    def set_valor(self, valor: str):
        self.lbl_valor.setText(str(valor))


class NominaView(QWidget):
    def __init__(self, api: ApiClient, parent=None):
        super().__init__(parent)
        self.api = api
        self._periodos = []
        self._resultados = []
        self._periodo_seleccionado = None
        self._construir()
        self.cargar_periodos()

    def _construir(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        lbl = QLabel("Prenómina revisable")
        lbl.setStyleSheet("font-size: 22px; font-weight: 800; color: #e8e8ea;")
        layout.addWidget(lbl)
        layout.addWidget(QLabel(
            "La prenómina es revisable y no sustituye procesos oficiales de nómina "
            "sin validación adicional de Recursos Humanos."
        ))

        # Crear periodo
        form = QFrame()
        form.setObjectName("formPeriodo")
        form.setStyleSheet(f"""
            QFrame#formPeriodo {{
                background-color: {FONDO_TARJETA};
                border: 1px solid #3a3a45;
                border-radius: 12px;
            }}
        """)
        fl = QHBoxLayout(form)
        fl.setContentsMargins(16, 14, 16, 14)
        fl.setSpacing(10)

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

        fl.addWidget(QLabel("Nombre:"))
        fl.addWidget(self.edit_nombre, stretch=1)
        fl.addWidget(QLabel("Inicio:"))
        fl.addWidget(self.edit_inicio)
        fl.addWidget(QLabel("Fin:"))
        fl.addWidget(self.edit_fin)
        fl.addWidget(btn_crear)
        fl.addWidget(btn_calcular)
        fl.addWidget(btn_cerrar)
        layout.addWidget(form)

        # KPIs del periodo seleccionado
        self.grid_kpis = QHBoxLayout()
        self.grid_kpis.setSpacing(12)
        self.tarjetas = {}
        for clave, etiqueta, color in [
            ("total_empleados", "Empleados", ACENTO),
            ("total_nomina", "Total nómina", EXITO),
            ("total_faltas", "Faltas", ERROR),
            ("total_retardos", "Retardos", ADVERTENCIA),
        ]:
            t = TarjetaResumen(etiqueta, "0", color)
            self.tarjetas[clave] = t
            self.grid_kpis.addWidget(t)
        layout.addLayout(self.grid_kpis)

        # Tabla de periodos
        layout.addWidget(QLabel("Periodos de nómina:"))
        self.tabla_periodos = QTableWidget()
        self.tabla_periodos.setColumnCount(5)
        self.tabla_periodos.setHorizontalHeaderLabels(["Nombre", "Inicio", "Fin", "Estado", "ID"])
        self.tabla_periodos.horizontalHeader().setStretchLastSection(True)
        self.tabla_periodos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_periodos.setAlternatingRowColors(True)
        self.tabla_periodos.itemSelectionChanged.connect(self._periodo_seleccionado_cambiado)
        layout.addWidget(self.tabla_periodos, stretch=1)

        # Tabla de resultados
        layout.addWidget(QLabel("Resultados de prenómina (periodo seleccionado):"))
        self.tabla_resultados = QTableWidget()
        self.tabla_resultados.setColumnCount(12)
        self.tabla_resultados.setHorizontalHeaderLabels([
            "Empleado", "Sueldo base", "Días lab.", "Días asist.",
            "Faltas", "Faltas just.", "Retardos", "Min. retardo",
            "Ajustes prop.", "Ajustes apr.", "Total preliminar", "Estado",
        ])
        self.tabla_resultados.horizontalHeader().setStretchLastSection(True)
        self.tabla_resultados.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_resultados.setAlternatingRowColors(True)
        layout.addWidget(self.tabla_resultados, stretch=1)

        self.lbl_estado = QLabel("")
        self.lbl_estado.setStyleSheet(f"color: {TEXTO_SECUNDARIO}; font-size: 12px;")
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
            for col, v in enumerate([
                p.get("nombre", ""), p.get("fecha_inicio", ""),
                p.get("fecha_fin", ""), p.get("estado", ""),
                str(p.get("id", ""))[:8]
            ]):
                item = QTableWidgetItem(str(v))
                self.tabla_periodos.setItem(fila, col, item)
                if col == 3:
                    if str(v) == "cerrado":
                        item.setForeground(QColor("#4caf50"))
                    elif str(v) == "calculado":
                        item.setForeground(QColor("#2196f3"))
                    else:
                        item.setForeground(QColor("#ff9800"))
        self.lbl_estado.setText(f"{len(datos)} periodo(s).")

    def _error(self, mensaje: str):
        self.lbl_estado.setText(f"Error: {mensaje}")
        mensaje_padre(self, "Error", mensaje, "error")

    def _periodo_seleccionado_cambiado(self):
        fila = self.tabla_periodos.currentRow()
        if fila < 0:
            return
        self._periodo_seleccionado = self._periodos[fila]
        self.cargar_resultados()

    def cargar_resultados(self):
        if not self._periodo_seleccionado:
            return
        pid = self._periodo_seleccionado["id"]
        self.lbl_estado.setText("Cargando resultados de prenómina...")
        self.hilo = AccionAPI(
            self.api, "GET",
            f"/api/v1/reportes/nomina?periodo_id={pid}"
        )
        self.hilo.listo.connect(self._resultados_listos)
        self.hilo.fallido.connect(self._error)
        self.hilo.start()

    def _resultados_listos(self, datos):
        self.tabla_resultados.setRowCount(0)
        self._resultados = datos.get("filas", [])
        total_nomina = datos.get("total_nomina", 0)
        total_emp = datos.get("total_empleados", 0)

        total_faltas = sum(f.get("faltas_registradas", 0) for f in self._resultados)
        total_retardos = sum(f.get("retardos", 0) for f in self._resultados)

        self.tarjetas["total_empleados"].set_valor(str(total_emp))
        self.tarjetas["total_nomina"].set_valor(f"${total_nomina:,.2f}")
        self.tarjetas["total_faltas"].set_valor(str(total_faltas))
        self.tarjetas["total_retardos"].set_valor(str(total_retardos))

        for r in self._resultados:
            fila = self.tabla_resultados.rowCount()
            self.tabla_resultados.insertRow(fila)
            valores = [
                r.get("numero_empleado", ""),
                f"{r.get('sueldo_base', 0):,.2f}",
                str(r.get("dias_laborables", 0)),
                str(r.get("dias_asistidos", 0)),
                str(r.get("faltas_registradas", 0)),
                str(r.get("faltas_justificadas", 0)),
                str(r.get("retardos", 0)),
                str(r.get("minutos_retardo", 0)),
                f"{r.get('ajustes_propuestos', 0):,.2f}",
                f"{r.get('ajustes_aprobados', 0):,.2f}",
                f"{r.get('total_preliminar', 0):,.2f}",
                r.get("estado", ""),
            ]
            for col, v in enumerate(valores):
                item = QTableWidgetItem(str(v))
                self.tabla_resultados.setItem(fila, col, item)
                if col == 11:
                    est = str(v)
                    if est == "pendiente":
                        item.setForeground(QColor("#ff9800"))
                    elif est == "aprobado":
                        item.setForeground(QColor("#4caf50"))
                    elif est == "rechazado":
                        item.setForeground(QColor("#f44336"))

        self.lbl_estado.setText(
            f"{len(self._resultados)} resultado(s) | Total nómina: ${total_nomina:,.2f} MXN"
        )

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
            mensaje_padre(self, "Éxito", "Periodo creado correctamente.", "exito")
            self.cargar_periodos()
        except ApiClientError as e:
            mensaje_padre(self, "Error", str(e), "error")

    def calcular(self):
        if not self._periodo_seleccionado:
            mensaje_padre(self, "Validación", "Seleccione un periodo de la lista.", "advertencia")
            return
        pid = self._periodo_seleccionado["id"]
        self.lbl_estado.setText("Calculando prenómina...")
        self.hilo = AccionAPI(
            self.api, "POST",
            f"/api/v1/nomina/periodos/{pid}/calcular"
        )
        self.hilo.listo.connect(self._calculado)
        self.hilo.fallido.connect(self._error)
        self.hilo.start()

    def _calculado(self, datos):
        mensaje_padre(self, "Éxito", "Prenómina calculada correctamente.", "exito")
        self.cargar_resultados()

    def cerrar(self):
        if not self._periodo_seleccionado:
            mensaje_padre(self, "Validación", "Seleccione un periodo de la lista.", "advertencia")
            return
        pid = self._periodo_seleccionado["id"]
        try:
            self.api.post(f"/api/v1/nomina/periodos/{pid}/cerrar")
            mensaje_padre(self, "Éxito", "Periodo cerrado correctamente.", "exito")
            self.cargar_periodos()
        except ApiClientError as e:
            mensaje_padre(self, "Error", str(e), "error")

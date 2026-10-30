"""Vista de incidencias y justificantes con generación automática y aprobaciones."""

from __future__ import annotations

from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget, QComboBox, QDateEdit,
    QFrame, QHeaderView,
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
    listo = Signal(dict)
    fallido = Signal(str)

    def __init__(self, api: ApiClient, metodo: str, ruta: str, datos=None, params=None):
        super().__init__()
        self.api = api
        self.metodo = metodo
        self.ruta = ruta
        self.datos = datos
        self.params = params or {}

    def run(self):
        try:
            if self.metodo == "GET":
                self.listo.emit(self.api.get(self.ruta, params=self.params))
            elif self.metodo == "POST":
                self.listo.emit(self.api.post(self.ruta, json=self.datos, params=self.params))
        except ApiClientError as e:
            self.fallido.emit(str(e))


class TarjetaEstado(QFrame):
    def __init__(self, etiqueta: str, valor: str = "0", color=ACENTO):
        super().__init__()
        self.setObjectName("tarjetaEstado")
        self.setFixedSize(170, 100)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)
        lbl_etq = QLabel(etiqueta.upper())
        lbl_etq.setStyleSheet(f"color: {TEXTO_SECUNDARIO}; font-size: 10px; font-weight: 700;")
        self.lbl_valor = QLabel(valor)
        self.lbl_valor.setObjectName("valorEstado")
        color_hex = color.name if hasattr(color, "name") else str(color)
        self.lbl_valor.setStyleSheet(f"color: {color_hex}; font-size: 26px; font-weight: 800;")
        layout.addWidget(lbl_etq)
        layout.addWidget(self.lbl_valor)
        layout.addStretch()
        barra = QFrame()
        barra.setFixedHeight(3)
        barra.setStyleSheet(f"background-color: {color_hex}; border-radius: 1px;")
        layout.addWidget(barra)
        color_hex = color.name if hasattr(color, "name") else str(color)
        self.setStyleSheet(f"""
            QFrame#tarjetaEstado {{
                background-color: {FONDO_TARJETA};
                border: 1px solid #3a3a45;
                border-radius: 10px;
            }}
        """)

    def set_valor(self, valor: str):
        self.lbl_valor.setText(str(valor))


class IncidenciasView(QWidget):
    def __init__(self, api: ApiClient, parent=None):
        super().__init__(parent)
        self.api = api
        self._datos = []
        self._construir()
        self.cargar_incidencias()

    def _construir(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        lbl = QLabel("Incidencias y Justificantes")
        lbl.setStyleSheet("font-size: 22px; font-weight: 800; color: #e8e8ea;")
        layout.addWidget(lbl)

        # Acciones rápidas
        acciones = QHBoxLayout()
        btn_faltas = BotonAccion("Generar faltas automáticas", primario=True)
        btn_faltas.setObjectName("btnFaltas")
        btn_faltas.clicked.connect(self.generar_faltas)
        btn_refresh = BotonAccion("Actualizar")
        btn_refresh.clicked.connect(self.cargar_incidencias)
        acciones.addWidget(btn_faltas)
        acciones.addWidget(btn_refresh)
        acciones.addStretch()
        layout.addLayout(acciones)

        # Filtro
        filtro = QHBoxLayout()
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(["todos", "pendiente", "en_revision", "aprobada", "rechazada"])
        self.combo_estado.currentIndexChanged.connect(self.cargar_incidencias)
        filtro.addWidget(QLabel("Estado:"))
        filtro.addWidget(self.combo_estado)
        filtro.addStretch()
        layout.addLayout(filtro)

        # KPIs
        self.grid_kpis = QHBoxLayout()
        self.grid_kpis.setSpacing(12)
        self.tarjetas = {}
        for clave, etiqueta, color in [
            ("total", "Total incidencias", ACENTO),
            ("pendientes", "Pendientes", ADVERTENCIA),
            ("aprobadas", "Aprobadas", EXITO),
            ("rechazadas", "Rechazadas", ERROR),
        ]:
            t = TarjetaEstado(etiqueta, "0", color)
            self.tarjetas[clave] = t
            self.grid_kpis.addWidget(t)
        layout.addLayout(self.grid_kpis)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(9)
        self.tabla.setHorizontalHeaderLabels([
            "Núm. Empleado", "Nombre Empleado", "Fecha", "Tipo",
            "Retardo (min)", "Tiempo (min)", "Regla aplicada", "Justificada", "Estado",
        ])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        layout.addWidget(self.tabla, stretch=1)

        self.lbl_estado = QLabel("")
        self.lbl_estado.setStyleSheet(f"color: {TEXTO_SECUNDARIO}; font-size: 12px;")
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
        self._datos = datos
        total = len(datos)
        pendientes = sum(1 for d in datos if d.get("estado") == "pendiente")
        aprobadas = sum(1 for d in datos if d.get("estado") == "aprobada")
        rechazadas = sum(1 for d in datos if d.get("estado") == "rechazada")

        self.tarjetas["total"].set_valor(str(total))
        self.tarjetas["pendientes"].set_valor(str(pendientes))
        self.tarjetas["aprobadas"].set_valor(str(aprobadas))
        self.tarjetas["rechazadas"].set_valor(str(rechazadas))

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
                item = QTableWidgetItem(str(v))
                self.tabla.setItem(fila, col, item)
                if col == 8:
                    est = str(v)
                    if est == "pendiente":
                        item.setForeground(QColor("#ff9800"))
                    elif est == "aprobada":
                        item.setForeground(QColor("#4caf50"))
                    elif est == "rechazada":
                        item.setForeground(QColor("#f44336"))

        self.lbl_estado.setText(f"{total} incidencia(s) | {pendientes} pendiente(s).")

    def _error(self, mensaje):
        self.lbl_estado.setText(f"Error: {mensaje}")
        mensaje_padre(self, "Error", mensaje, "error")

    def generar_faltas(self):
        self.lbl_estado.setText("Generando faltas automáticas...")
        self.hilo_accion = AccionAPI(
            self.api, "POST", "/api/v1/demo/generar-faltas"
        )
        self.hilo_accion.listo.connect(self._faltas_listo)
        self.hilo_accion.fallido.connect(self._error)
        self.hilo_accion.start()

    def _faltas_listo(self, datos: dict):
        self.lbl_estado.setText(
            f"Faltas generadas: {datos.get('faltas_creadas', 0)} "
            f"({datos.get('empleados_con_entrada', 0)} ya tenían entrada)."
        )
        mensaje_padre(self, "Éxito", "Faltas automáticas generadas correctamente.", "exito")
        self.cargar_incidencias()

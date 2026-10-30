"""Vista de registro de asistencia con simulación masiva para demostración."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from PySide6.QtCore import QThread, Signal, QDateTime
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget, QDateTimeEdit, QComboBox,
    QFrame, QHeaderView,
)

from app.api_client import ApiClient, ApiClientError
from app.components.componentes import BotonAccion, mensaje_padre
from app.ui.theme import (
    ACENTO, ADVERTENCIA, ERROR, EXITO, FONDO_PRINCIPAL, FONDO_PANEL,
    FONDO_TARJETA, TEXTO_PRIMARIO, TEXTO_SECUNDARIO,
)


class CargarEventos(QThread):
    listo = Signal(list)
    fallido = Signal(str)

    def __init__(self, api: ApiClient, empleado_id: Optional[str] = None):
        super().__init__()
        self.api = api
        self.empleado_id = empleado_id

    def run(self):
        try:
            params = {}
            if self.empleado_id:
                params["empleado_id"] = self.empleado_id
            self.listo.emit(self.api.get("/api/v1/asistencia/eventos", params=params))
        except ApiClientError as e:
            self.fallido.emit(str(e))


class SimularAsistencia(QThread):
    """Hilo para generar asistencias de demostración masivamente."""

    listo = Signal(dict)
    fallido = Signal(str)

    def __init__(self, api: ApiClient, dias: int):
        super().__init__()
        self.api = api
        self.dias = dias

    def run(self):
        try:
            self.listo.emit(
                self.api.post(f"/api/v1/demo/generar-asistencias?dias_atras={self.dias}")
            )
        except ApiClientError as e:
            self.fallido.emit(str(e))


class TarjetaAccionRapida(QFrame):
    """Tarjeta de acción rápida con ícono y color."""

    def __init__(self, titulo: str, descripcion: str, color=ACENTO):
        super().__init__()
        self.setObjectName("tarjetaAccionRapida")
        self.setFixedSize(220, 130)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet(
            "color: #e8e8ea; font-size: 14px; font-weight: 700;"
        )
        lbl_desc = QLabel(descripcion)
        lbl_desc.setStyleSheet(
            f"color: {TEXTO_SECUNDARIO}; font-size: 11px;"
        )
        lbl_desc.setWordWrap(True)

        layout.addWidget(lbl_titulo)
        layout.addWidget(lbl_desc)
        layout.addStretch()

        color_hex = color.name if hasattr(color, "name") else str(color)
        self.setStyleSheet(f"""
            QFrame#tarjetaAccionRapida {{
                background-color: {FONDO_TARJETA};
                border: 1px solid #3a3a45;
                border-radius: 12px;
            }}
            QFrame#tarjetaAccionRapida:hover {{
                border-color: {color_hex};
                background-color: #32323e;
            }}
        """)


class AsistenciaView(QWidget):
    def __init__(self, api: ApiClient, parent=None):
        super().__init__(parent)
        self.api = api
        self._construir()
        self.cargar()

    def _construir(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Encabezado
        encabezado = QHBoxLayout()
        lbl_titulo = QLabel("Registro de Asistencia")
        lbl_titulo.setStyleSheet("font-size: 22px; font-weight: 800; color: #e8e8ea;")
        encabezado.addWidget(lbl_titulo)
        encabezado.addStretch()
        btn_refresh = BotonAccion("Actualizar")
        btn_refresh.clicked.connect(self.cargar)
        encabezado.addWidget(btn_refresh)
        layout.addLayout(encabezado)

        # Acciones rápidas (tarjetas)
        acciones = QHBoxLayout()
        acciones.setSpacing(12)

        tarjeta_sim = TarjetaAccionRapida(
            "Simular semana de asistencia",
            "Genera entradas y salidas realistas para los 45 empleados "
            "de los últimos 5 días (ideal para demostración).",
            ACENTO,
        )
        tarjeta_sim.mousePressEvent = lambda e: self.simular_masiva()
        acciones.addWidget(tarjeta_sim)

        tarjeta_faltas = TarjetaAccionRapida(
            "Generar faltas automáticas",
            "Crea incidencias de 'falta' para empleados que no marcaron "
            "entrada el día anterior.",
            ADVERTENCIA,
        )
        tarjeta_faltas.mousePressEvent = lambda e: self.generar_faltas()
        acciones.addWidget(tarjeta_faltas)

        acciones.addStretch()
        layout.addLayout(acciones)

        # Formulario de registro manual
        form = QFrame()
        form.setObjectName("formRegistro")
        form.setStyleSheet(f"""
            QFrame#formRegistro {{
                background-color: {FONDO_TARJETA};
                border: 1px solid #3a3a45;
                border-radius: 12px;
            }}
        """)
        form_layout = QHBoxLayout(form)
        form_layout.setContentsMargins(16, 14, 16, 14)
        form_layout.setSpacing(10)

        self.edit_empleado = QLineEdit()
        self.edit_empleado.setPlaceholderText("Número de empleado (ej. EMP-001)")
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["entrada", "salida", "otro"])
        self.fecha_hora = QDateTimeEdit(QDateTime.currentDateTime())
        self.fecha_hora.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.edit_metodo = QComboBox()
        self.edit_metodo.addItems(["manual", "biometrico", "tarjeta", "simulador"])
        btn_registrar = BotonAccion("Registrar evento", primario=True)
        btn_registrar.clicked.connect(self.registrar)

        form_layout.addWidget(QLabel("Empleado:"))
        form_layout.addWidget(self.edit_empleado, stretch=1)
        form_layout.addWidget(QLabel("Tipo:"))
        form_layout.addWidget(self.combo_tipo)
        form_layout.addWidget(QLabel("Fecha/hora:"))
        form_layout.addWidget(self.fecha_hora)
        form_layout.addWidget(QLabel("Método:"))
        form_layout.addWidget(self.edit_metodo)
        form_layout.addWidget(btn_registrar)

        layout.addWidget(form)

        # Tabla de eventos
        barra = QHBoxLayout()
        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("Buscar por empleado, tipo o resultado...")
        self.input_buscar.textChanged.connect(self.filtrar)
        btn_limpiar = BotonAccion("Limpiar")
        btn_limpiar.clicked.connect(lambda: (self.input_buscar.clear(), self.filtrar()))
        barra.addWidget(self.input_buscar, stretch=1)
        barra.addWidget(btn_limpiar)
        layout.addLayout(barra)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(8)
        self.tabla.setHorizontalHeaderLabels([
            "Núm. Empleado", "Nombre Empleado", "Tipo", "Fecha y hora",
            "Método", "Resultado", "Incidencia", "ID",
        ])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        layout.addWidget(QLabel("Eventos de asistencia:"))
        layout.addWidget(self.tabla, stretch=1)

        self.lbl_estado = QLabel("")
        self.lbl_estado.setStyleSheet(f"color: {TEXTO_SECUNDARIO}; font-size: 12px;")
        layout.addWidget(self.lbl_estado)

    def cargar(self):
        self.lbl_estado.setText("Cargando eventos...")
        self.hilo = CargarEventos(self.api)
        self.hilo.listo.connect(self._eventos_listos)
        self.hilo.fallido.connect(self._error)
        self.hilo.start()

    def _eventos_listos(self, datos):
        self._datos = datos
        self.filtrar()
        self.lbl_estado.setText(f"{len(datos)} evento(s) cargado(s).")

    def _error(self, mensaje):
        self.lbl_estado.setText(f"Error: {mensaje}")
        mensaje_padre(self, "Error", mensaje, "error")

    def filtrar(self):
        texto = self.input_buscar.text().lower()
        self.tabla.setRowCount(0)
        for ev in getattr(self, "_datos", []):
            nombre = f"{ev.get('nombre_empleado', '')}".lower()
            if (texto in ev.get("numero_empleado", "").lower()
                    or texto in nombre
                    or texto in ev.get("tipo_evento", "").lower()
                    or texto in ev.get("resultado_validacion", "").lower()):
                self._agregar_fila(ev)

    def _agregar_fila(self, ev):
        fila = self.tabla.rowCount()
        self.tabla.insertRow(fila)
        valores = [
            ev.get("numero_empleado", ""),
            ev.get("nombre_empleado", ""),
            ev.get("tipo_evento", ""),
            ev.get("fecha_hora", ""),
            ev.get("metodo_registro", ""),
            ev.get("resultado_validacion", ""),
            "Sí" if ev.get("incidencia_detectada") else "No",
            str(ev.get("id", ""))[:8],
        ]
        for col, v in enumerate(valores):
            item = QTableWidgetItem(str(v))
            self.tabla.setItem(fila, col, item)
            # Colorear resultado
            if col == 5:
                if str(v) == "valido":
                    item.setForeground(QColor("#4caf50"))
                elif str(v) == "duplicado":
                    item.setForeground(QColor("#ff9800"))
                elif str(v) == "imposible":
                    item.setForeground(QColor("#f44336"))

    def registrar(self):
        numero = self.edit_empleado.text().strip()
        if not numero:
            mensaje_padre(self, "Validación", "Ingrese el número de empleado.", "advertencia")
            return
        datos = {
            "empleado_id": numero,
            "tipo_evento": self.combo_tipo.currentText(),
            "fecha_hora": self.fecha_hora.dateTime().toString("yyyy-MM-ddTHH:mm:ss"),
            "metodo_registro": self.edit_metodo.currentText(),
        }
        try:
            self.api.post("/api/v1/asistencia/eventos", json=datos)
            mensaje_padre(self, "Éxito", "Evento de asistencia registrado.", "exito")
            self.edit_empleado.clear()
            self.cargar()
        except ApiClientError as e:
            mensaje_padre(self, "Error", str(e), "error")

    def simular_masiva(self):
        self.lbl_estado.setText("Generando asistencias simuladas...")
        self.hilo_sim = SimularAsistencia(self.api, dias=5)
        self.hilo_sim.listo.connect(self._sim_listo)
        self.hilo_sim.fallido.connect(self._error)
        self.hilo_sim.start()

    def _sim_listo(self, datos: dict):
        self.lbl_estado.setText(
            f"Simulación completa: {datos.get('eventos_creados', 0)} eventos, "
            f"{datos.get('incidencias_creadas', 0)} incidencias en "
            f"{datos.get('empleados', 0)} empleados ({datos.get('dias', 0)} días)."
        )
        mensaje_padre(self, "Éxito", "Asistencias simuladas generadas correctamente.", "exito")
        self.cargar()

    def generar_faltas(self):
        self.lbl_estado.setText("Generando faltas automáticas...")
        try:
            resultado = self.api.post("/api/v1/demo/generar-faltas")
            self.lbl_estado.setText(
                f"Faltas generadas: {resultado.get('faltas_creadas', 0)} "
                f"({resultado.get('empleados_con_entrada', 0)} ya tenían entrada)."
            )
            mensaje_padre(self, "Éxito", "Faltas automáticas generadas.", "exito")
            self.cargar()
        except ApiClientError as e:
            self._error(str(e))

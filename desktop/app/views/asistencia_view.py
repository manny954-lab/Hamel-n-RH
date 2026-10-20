"""Vista de registro de asistencia."""

from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import QThread, Signal, QDateTime
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget, QDateTimeEdit, QComboBox,
)

from app.api_client import ApiClient, ApiClientError
from app.components.componentes import BotonAccion, mensaje_padre


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


class AsistenciaView(QWidget):
    def __init__(self, api: ApiClient, parent=None):
        super().__init__(parent)
        self.api = api
        self._construir()
        self.cargar()

    def _construir(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        form = QHBoxLayout()
        self.edit_empleado = QLineEdit()
        self.edit_empleado.setPlaceholderText("Número de empleado")
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["entrada", "salida", "otro"])
        self.fecha_hora = QDateTimeEdit(QDateTime.currentDateTime())
        self.fecha_hora.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.edit_metodo = QComboBox()
        self.edit_metodo.addItems(["manual", "biometrico", "tarjeta", "simulador"])
        btn_registrar = BotonAccion("Registrar evento", primario=True)
        btn_registrar.clicked.connect(self.registrar)
        form.addWidget(self.edit_empleado, stretch=1)
        form.addWidget(self.combo_tipo)
        form.addWidget(self.fecha_hora)
        form.addWidget(self.edit_metodo)
        form.addWidget(btn_registrar)
        layout.addLayout(form)

        barra = QHBoxLayout()
        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("Buscar por empleado...")
        self.input_buscar.textChanged.connect(self.filtrar)
        btn_refresh = BotonAccion("Actualizar")
        btn_refresh.clicked.connect(self.cargar)
        barra.addWidget(self.input_buscar, stretch=1)
        barra.addWidget(btn_refresh)
        layout.addLayout(barra)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels([
            "Núm. Empleado", "Nombre Empleado", "Tipo", "Fecha y hora",
            "Método", "Resultado", "Incidencia",
        ])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.tabla, stretch=1)

        self.lbl_estado = QLabel("")
        self.lbl_estado.setStyleSheet("color: #9aa0a6; font-size: 12px;")
        layout.addWidget(self.lbl_estado)

        lbl_nota = QLabel(
            "Método 'simulador': para demostraciones sin lector biométrico conectado. "
            "No representa un dispositivo real."
        )
        lbl_nota.setStyleSheet("color: #9aa0a6; font-size: 11px; font-style: italic;")
        layout.addWidget(lbl_nota)

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
        ]
        for col, v in enumerate(valores):
            item = QTableWidgetItem(str(v))
            self.tabla.setItem(fila, col, item)

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

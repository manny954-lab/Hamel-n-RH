"""Vista de gestión de empleados."""

from __future__ import annotations

from datetime import date
from typing import Optional

from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtWidgets import (
    QComboBox, QDateEdit, QDialog, QDialogButtonBox, QHBoxLayout, QLabel,
    QLineEdit, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget,
)

from app.api_client import ApiClient, ApiClientError
from app.components.componentes import BotonAccion, mensaje_padre
from app.ui.theme import ACENTO, ERROR, TEXTO_PRIMARIO, TEXTO_SECUNDARIO


class CargarEmpleados(QThread):
    listo = Signal(list)
    fallido = Signal(str)

    def __init__(self, api: ApiClient):
        super().__init__()
        self.api = api

    def run(self):
        try:
            self.listo.emit(self.api.get("/api/v1/empleados"))
        except ApiClientError as e:
            self.fallido.emit(str(e))


class EliminarEmpleado(QThread):
    listo = Signal(str)
    fallido = Signal(str)

    def __init__(self, api: ApiClient, empleado_id: str):
        super().__init__()
        self.api = api
        self.empleado_id = empleado_id

    def run(self):
        try:
            self.api.delete(f"/api/v1/empleados/{self.empleado_id}")
            self.listo.emit(self.empleado_id)
        except ApiClientError as e:
            self.fallido.emit(str(e))


class EmpleadoDialog(QDialog):
    """Diálogo para crear o editar un empleado."""

    def __init__(self, api: ApiClient, empleado: Optional[dict] = None, parent=None):
        super().__init__(parent)
        self.api = api
        self.empleado = empleado
        self.es_nuevo = empleado is None
        self.setWindowTitle("Nuevo empleado" if self.es_nuevo else "Editar empleado")
        self.setModal(True)
        self.resize(450, 400)
        self._construir()
        self._cargar_departamentos()
        if self.empleado:
            self._cargar_datos()

    def _construir(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        self.edit_numero = QLineEdit()
        self.edit_numero.setPlaceholderText("Ej. EMP-001")
        self.edit_nombre = QLineEdit()
        self.edit_nombre.setPlaceholderText("Nombres")
        self.edit_paterno = QLineEdit()
        self.edit_paterno.setPlaceholderText("Apellido paterno")
        self.edit_materno = QLineEdit()
        self.edit_materno.setPlaceholderText("Apellido materno")
        self.edit_ingreso = QDateEdit()
        self.edit_ingreso.setDisplayFormat("dd/MM/yyyy")
        self.edit_ingreso.setDate(date.today())
        self.combo_depto = QComboBox()
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(["activo", "licencia", "suspendido", "baja_voluntaria", "baja_involuntaria"])

        layout.addWidget(QLabel("Número de empleado *"))
        layout.addWidget(self.edit_numero)
        layout.addWidget(QLabel("Nombre *"))
        layout.addWidget(self.edit_nombre)
        layout.addWidget(QLabel("Apellido paterno *"))
        layout.addWidget(self.edit_paterno)
        layout.addWidget(QLabel("Apellido materno"))
        layout.addWidget(self.edit_materno)
        layout.addWidget(QLabel("Fecha de ingreso *"))
        layout.addWidget(self.edit_ingreso)
        layout.addWidget(QLabel("Departamento *"))
        layout.addWidget(self.combo_depto)
        layout.addWidget(QLabel("Estado *"))
        layout.addWidget(self.combo_estado)

        botones = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        botones.button(QDialogButtonBox.StandardButton.Save).setText("Guardar")
        botones.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")
        botones.button(QDialogButtonBox.StandardButton.Save).setObjectName("btnPrimario")
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)
        layout.addWidget(botones)

    def _cargar_departamentos(self):
        try:
            datos = self.api.get("/api/v1/catalogos/departamentos")
            self.combo_depto.clear()
            for d in datos:
                self.combo_depto.addItem(d["nombre"], d["id"])
        except ApiClientError as e:
            mensaje_padre(self, "Error", f"No se pudieron cargar departamentos: {e}", "error")

    def _cargar_datos(self):
        if not self.empleado:
            return
        self.edit_numero.setText(self.empleado.get("numero_empleado", ""))
        self.edit_nombre.setText(self.empleado.get("nombre", ""))
        self.edit_paterno.setText(self.empleado.get("apellido_paterno", ""))
        self.edit_materno.setText(self.empleado.get("apellido_materno") or "")
        fecha = self.empleado.get("fecha_ingreso", "")
        if fecha:
            try:
                from PySide6.QtCore import QDate
                partes = fecha.split("-")
                self.edit_ingreso.setDate(QDate(int(partes[0]), int(partes[1]), int(partes[2])))
            except Exception:
                pass
        depto_id = self.empleado.get("departamento_id", "")
        idx = self.combo_depto.findData(depto_id)
        if idx >= 0:
            self.combo_depto.setCurrentIndex(idx)
        self.combo_estado.setCurrentText(self.empleado.get("estado", "activo"))

    def accept(self):
        numero = self.edit_numero.text().strip()
        nombre = self.edit_nombre.text().strip()
        paterno = self.edit_paterno.text().strip()

        if not numero or not nombre or not paterno:
            mensaje_padre(self, "Validación", "Número, nombre y apellido paterno son obligatorios.", "advertencia")
            return

        datos = {
            "numero_empleado": numero,
            "nombre": nombre,
            "apellido_paterno": paterno,
            "apellido_materno": self.edit_materno.text().strip() or None,
            "departamento_id": self.combo_depto.currentData(),
            "fecha_ingreso": self.edit_ingreso.date().toString("yyyy-MM-dd"),
            "estado": self.combo_estado.currentText(),
        }

        try:
            if self.es_nuevo:
                self.api.post("/api/v1/empleados", json=datos)
            else:
                emp_id = self.empleado["id"]
                self.api.patch(f"/api/v1/empleados/{emp_id}", json=datos)
            super().accept()
        except ApiClientError as e:
            mensaje_padre(self, "Error", str(e), "error")


class EmpleadosView(QWidget):
    def __init__(self, api: ApiClient, parent=None, puede_eliminar: bool = False):
        super().__init__(parent)
        self.api = api
        self.puede_eliminar = puede_eliminar
        self._construir()
        self.cargar()

    def _construir(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        # Barra de título y acciones
        barra_superior = QHBoxLayout()
        lbl_titulo = QLabel("Gestión de Empleados")
        lbl_titulo.setStyleSheet("font-size: 18px; font-weight: 700; color: #e8e8ea;")
        barra_superior.addWidget(lbl_titulo)
        barra_superior.addStretch()

        self.lbl_rol = QLabel("")
        self.lbl_rol.setStyleSheet(f"color: {TEXTO_SECUNDARIO}; font-size: 11px; font-style: italic;")
        barra_superior.addWidget(self.lbl_rol)
        layout.addLayout(barra_superior)

        barra = QHBoxLayout()
        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("Buscar por número, nombre o departamento...")
        self.input_buscar.textChanged.connect(self.filtrar)
        btn_nuevo = BotonAccion("Nuevo empleado", primario=True)
        btn_nuevo.clicked.connect(self.nuevo_empleado)
        btn_editar = BotonAccion("Editar seleccionado")
        btn_editar.clicked.connect(self.editar_seleccionado)
        btn_refresh = BotonAccion("Actualizar")
        btn_refresh.clicked.connect(self.cargar)
        barra.addWidget(self.input_buscar, stretch=1)
        barra.addWidget(btn_refresh)
        barra.addWidget(btn_editar)
        barra.addWidget(btn_nuevo)

        # Botón eliminar solo para administradores
        self.btn_eliminar = BotonAccion("Eliminar seleccionado")
        self.btn_eliminar.setObjectName("btnPeligro")
        self.btn_eliminar.clicked.connect(self.eliminar_seleccionado)
        self.btn_eliminar.setVisible(self.puede_eliminar)
        barra.addWidget(self.btn_eliminar)

        layout.addLayout(barra)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(8)
        self.tabla.setHorizontalHeaderLabels([
            "Número", "Nombre", "Apellido paterno", "Apellido materno",
            "Departamento", "Estado", "Fecha ingreso", "ID interno",
        ])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tabla.doubleClicked.connect(self.editar_seleccionado)
        layout.addWidget(self.tabla, stretch=1)

        self.lbl_estado = QLabel("")
        self.lbl_estado.setStyleSheet("color: #9aa0a6; font-size: 12px;")
        layout.addWidget(self.lbl_estado)

    def set_rol_usuario(self, rol_nombre: str):
        self.lbl_rol.setText(f"Usuario: {rol_nombre}")
        if "administrador" in rol_nombre.lower():
            self.puede_eliminar = True
            self.btn_eliminar.setVisible(True)
        else:
            self.puede_eliminar = False
            self.btn_eliminar.setVisible(False)

    def cargar(self):
        self.lbl_estado.setText("Cargando empleados...")
        self.hilo = CargarEmpleados(self.api)
        self.hilo.listo.connect(self._empleados_listos)
        self.hilo.fallido.connect(self._error)
        self.hilo.start()

    def _empleados_listos(self, datos):
        self._datos = datos
        self.filtrar()
        self.lbl_estado.setText(f"{len(datos)} empleado(s) cargado(s).")

    def _error(self, mensaje):
        self.lbl_estado.setText(f"Error: {mensaje}")
        mensaje_padre(self, "Error", mensaje, "error")

    def filtrar(self):
        texto = self.input_buscar.text().lower()
        self.tabla.setRowCount(0)
        datos = getattr(self, "_datos", [])
        for emp in datos:
            nombre = f"{emp.get('nombre','')} {emp.get('apellido_paterno','')}".lower()
            if (texto in emp.get("numero_empleado", "").lower()
                    or texto in nombre
                    or texto in emp.get("departamento_nombre", "").lower()
                    or texto in emp.get("estado", "").lower()):
                self._agregar_fila(emp)

    def _agregar_fila(self, emp):
        fila = self.tabla.rowCount()
        self.tabla.insertRow(fila)
        valores = [
            emp.get("numero_empleado", ""),
            emp.get("nombre", ""),
            emp.get("apellido_paterno", ""),
            emp.get("apellido_materno") or "",
            emp.get("departamento_nombre", ""),
            emp.get("estado", ""),
            emp.get("fecha_ingreso", ""),
            str(emp.get("id", ""))[:8],
        ]
        for col, v in enumerate(valores):
            item = QTableWidgetItem(str(v))
            self.tabla.setItem(fila, col, item)
        # Guardar el ID completo en el primer item para referencia
        self.tabla.item(fila, 0).setData(Qt.ItemDataRole.UserRole, emp.get("id", ""))

    def _empleado_seleccionado(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            return None
        return self._datos[fila] if fila < len(getattr(self, "_datos", [])) else None

    def nuevo_empleado(self):
        dlg = EmpleadoDialog(self.api, None, self)
        if dlg.exec():
            self.cargar()

    def editar_seleccionado(self):
        emp = self._empleado_seleccionado()
        if not emp:
            mensaje_padre(self, "Validación", "Seleccione un empleado de la tabla.", "advertencia")
            return
        dlg = EmpleadoDialog(self.api, emp, self)
        if dlg.exec():
            self.cargar()

    def eliminar_seleccionado(self):
        emp = self._empleado_seleccionado()
        if not emp:
            mensaje_padre(self, "Validación", "Seleccione un empleado de la tabla.", "advertencia")
            return

        nombre_completo = f"{emp.get('nombre', '')} {emp.get('apellido_paterno', '')}"
        respuesta = QMessageBox.question(
            self,
            "Eliminar empleado",
            f"¿Está seguro de eliminar al empleado:\n{emp.get('numero_empleado', '')} - {nombre_completo}?\n\n"
            "Esta acción marcará al empleado como eliminado (eliminación lógica).",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if respuesta != QMessageBox.StandardButton.Yes:
            return

        emp_id = emp.get("id")
        self.lbl_estado.setText("Eliminando empleado...")
        self.hilo_eliminar = EliminarEmpleado(self.api, emp_id)
        self.hilo_eliminar.listo.connect(self._empleado_eliminado)
        self.hilo_eliminar.fallido.connect(self._error)
        self.hilo_eliminar.start()

    def _empleado_eliminado(self, empleado_id: str):
        self.lbl_estado.setText(f"Empleado {empleado_id[:8]}... eliminado correctamente.")
        self.cargar()

"""Vista de consulta de base de datos (solo administradores)."""

from __future__ import annotations

from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
    QTextEdit, QSplitter, QFrame,
)

from app.api_client import ApiClient, ApiClientError
from app.components.componentes import BotonAccion, mensaje_padre
from app.ui.theme import ACENTO, ERROR, EXITO, TEXTO_PRIMARIO, TEXTO_SECUNDARIO


class EjecutarConsulta(QThread):
    listo = Signal(dict)
    fallido = Signal(str)

    def __init__(self, api: ApiClient, consulta: str):
        super().__init__()
        self.api = api
        self.consulta = consulta

    def run(self):
        try:
            self.listo.emit(self.api.post("/api/v1/consulta/ejecutar", json={"consulta": self.consulta}))
        except ApiClientError as e:
            self.fallido.emit(str(e))


class ConsultaBDView(QWidget):
    def __init__(self, api: ApiClient, parent=None):
        super().__init__(parent)
        self.api = api
        self._construir()

    def _construir(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        lbl = QLabel("Consulta de Base de Datos")
        lbl.setStyleSheet("font-size: 20px; font-weight: 700; color: #e8e8ea;")
        layout.addWidget(lbl)

        lbl_sub = QLabel("Solo consultas SELECT. Acceso restringido a administradores.")
        lbl_sub.setStyleSheet(f"color: {TEXTO_SECUNDARIO}; font-size: 12px;")
        layout.addWidget(lbl_sub)

        # Splitter para dividir consulta y resultados
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Panel de consulta
        panel_consulta = QFrame()
        panel_consulta.setStyleSheet(f"""
            QFrame {{
                background-color: #25252e;
                border: 1px solid #3a3a45;
                border-radius: 8px;
            }}
        """)
        layout_consulta = QVBoxLayout(panel_consulta)
        layout_consulta.setContentsMargins(16, 16, 16, 16)
        layout_consulta.setSpacing(10)

        lbl_consulta = QLabel("Consulta SQL:")
        lbl_consulta.setStyleSheet(f"color: {TEXTO_SECUNDARIO}; font-size: 12px; font-weight: 600;")
        layout_consulta.addWidget(lbl_consulta)

        self.editor_sql = QTextEdit()
        self.editor_sql.setPlaceholderText(
            "Ejemplo:\n"
            "SELECT numero_empleado, nombre, apellido_paterno, sueldo_base "
            "FROM empleados e JOIN configuracion_salarial cs ON cs.empleado_id = e.id "
            "WHERE e.departamento_id = '...';"
        )
        self.editor_sql.setStyleSheet(f"""
            QTextEdit {{
                background-color: #1f1f27;
                color: #e8e8ea;
                border: 1px solid #3a3a45;
                border-radius: 6px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 13px;
                padding: 10px;
            }}
        """)
        self.editor_sql.setMinimumHeight(200)
        layout_consulta.addWidget(self.editor_sql)

        btn_ejecutar = QPushButton("Ejecutar Consulta")
        btn_ejecutar.setObjectName("btnPrimario")
        btn_ejecutar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ejecutar.clicked.connect(self.ejecutar)
        layout_consulta.addWidget(btn_ejecutar)

        splitter.addWidget(panel_consulta)

        # Panel de resultados
        panel_resultados = QFrame()
        layout_resultados = QVBoxLayout(panel_resultados)
        layout_resultados.setContentsMargins(16, 16, 16, 16)
        layout_resultados.setSpacing(10)

        lbl_resultados = QLabel("Resultados:")
        lbl_resultados.setStyleSheet(f"color: {TEXTO_SECUNDARIO}; font-size: 12px; font-weight: 600;")
        layout_resultados.addWidget(lbl_resultados)

        self.tabla = QTableWidget()
        self.tabla.setStyleSheet(f"""
            QTableWidget {{
                background-color: #2d2d36;
                color: {TEXTO_PRIMARIO};
                border: 1px solid #3a3a45;
                border-radius: 6px;
                gridline-color: #33333d;
                selection-background-color: {ACENTO};
                selection-color: #ffffff;
            }}
            QTableWidget::item {{ padding: 6px 8px; border-bottom: 1px solid #2a2a33; }}
            QHeaderView::section {{
                background-color: #25252e;
                color: {TEXTO_SECUNDARIO};
                padding: 6px 8px;
                border: none;
                border-bottom: 1px solid #3a3a45;
                font-weight: 600;
            }}
        """)
        layout_resultados.addWidget(self.tabla)

        self.lbl_estado = QLabel("Listo para consultar.")
        self.lbl_estado.setStyleSheet(f"color: {TEXTO_SECUNDARIO}; font-size: 11px;")
        layout_resultados.addWidget(self.lbl_estado)

        splitter.addWidget(panel_resultados)
        splitter.setSizes([400, 400])
        layout.addWidget(splitter)

    def ejecutar(self):
        consulta = self.editor_sql.toPlainText().strip()
        if not consulta:
            mensaje_padre(self, "Validación", "Ingrese una consulta SQL.", "advertencia")
            return

        self.lbl_estado.setText("Ejecutando consulta...")
        self.hilo = EjecutarConsulta(self.api, consulta)
        self.hilo.listo.connect(self._resultado_listo)
        self.hilo.fallido.connect(self._error)
        self.hilo.start()

    def _resultado_listo(self, datos: dict):
        columnas = datos.get("columnas", [])
        filas = datos.get("filas", [])
        total = datos.get("total", 0)

        self.tabla.setColumnCount(len(columnas))
        self.tabla.setHorizontalHeaderLabels(columnas)
        self.tabla.setRowCount(len(filas))

        for i, fila in enumerate(filas):
            for j, col in enumerate(columnas):
                valor = fila.get(col, "")
                if valor is None:
                    valor = ""
                self.tabla.setItem(i, j, QTableWidgetItem(str(valor)))

        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.lbl_estado.setText(f"{total} fila(s) encontrada(s).")

    def _error(self, mensaje: str):
        self.lbl_estado.setText(f"Error: {mensaje}")
        mensaje_padre(self, "Error", mensaje, "error")

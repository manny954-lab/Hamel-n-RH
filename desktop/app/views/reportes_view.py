"""Vista de reportes profesional con KPIs, múltiples reportes y exportación CSV."""

from __future__ import annotations

from PySide6.QtCore import QDate, QThread, Signal, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDateEdit, QFrame, QHBoxLayout, QLabel, QMessageBox, QPushButton,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QComboBox,
    QHeaderView, QFileDialog,
)

from app.api_client import ApiClient, ApiClientError
from app.components.componentes import BotonAccion, mensaje_padre
from app.ui.theme import (
    ACENTO, ADVERTENCIA, ERROR, EXITO, FONDO_PRINCIPAL, FONDO_PANEL,
    FONDO_TARJETA, TEXTO_PRIMARIO, TEXTO_SECUNDARIO,
)


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


class TarjetaKPI(QFrame):
    """Tarjeta de indicador clave con color y valor grande."""

    def __init__(self, etiqueta: str, valor: str = "0", subtitulo: str = "",
                 color=ACENTO):
        super().__init__()
        self.setObjectName("tarjetaKPI")
        self.setFixedSize(200, 120)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        lbl_etiqueta = QLabel(etiqueta.upper())
        lbl_etiqueta.setStyleSheet(
            f"color: {TEXTO_SECUNDARIO}; font-size: 11px; font-weight: 700;"
        )

        self.lbl_valor = QLabel(valor)
        self.lbl_valor.setObjectName("valorKPI")
        color_hex = color.name if hasattr(color, "name") else str(color)
        self.lbl_valor.setStyleSheet(
            f"color: {color_hex}; font-size: 32px; font-weight: 800;"
        )

        if subtitulo:
            lbl_sub = QLabel(subtitulo)
            lbl_sub.setStyleSheet(
                f"color: {TEXTO_SECUNDARIO}; font-size: 10px;"
            )
            layout.addWidget(lbl_sub)

        layout.addWidget(lbl_etiqueta)
        layout.addWidget(self.lbl_valor)
        layout.addStretch()

        barra = QFrame()
        barra.setFixedHeight(4)
        barra.setStyleSheet(f"background-color: {color_hex}; border-radius: 2px;")
        layout.addWidget(barra)

        color_hex = color.name if hasattr(color, "name") else str(color)
        self.setStyleSheet(f"""
            QFrame#tarjetaKPI {{
                background-color: {FONDO_TARJETA};
                border: 1px solid #3a3a45;
                border-radius: 12px;
            }}
            QFrame#tarjetaKPI:hover {{
                border-color: {color_hex};
                background-color: #32323e;
            }}
        """)

    def set_valor(self, valor: str) -> None:
        self.lbl_valor.setText(str(valor))


class ReportesView(QWidget):
    def __init__(self, api: ApiClient, parent=None):
        super().__init__(parent)
        self.api = api
        self._datos_actuales = []
        self._tipo_actual = "quincenal"
        self._construir()
        self.cargar_kpis()
        self.ejecutar()

    def _construir(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Encabezado
        encabezado = QHBoxLayout()
        lbl_titulo = QLabel("Reportes y Exportación")
        lbl_titulo.setStyleSheet("font-size: 22px; font-weight: 800; color: #e8e8ea;")
        encabezado.addWidget(lbl_titulo)
        encabezado.addStretch()
        btn_actualizar = BotonAccion("Actualizar todo", primario=True)
        btn_actualizar.clicked.connect(self._actualizar_todo)
        encabezado.addWidget(btn_actualizar)
        layout.addLayout(encabezado)

        # Filtros de fecha
        form = QHBoxLayout()
        form.addWidget(QLabel("Desde:"))
        self.edit_inicio = QDateEdit()
        self.edit_inicio.setDate(QDate.currentDate().addDays(-15))
        self.edit_inicio.setDisplayFormat("dd/MM/yyyy")
        form.addWidget(self.edit_inicio)

        form.addWidget(QLabel("Hasta:"))
        self.edit_fin = QDateEdit()
        self.edit_fin.setDate(QDate.currentDate())
        self.edit_fin.setDisplayFormat("dd/MM/yyyy")
        form.addWidget(self.edit_fin)

        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems([
            "Reporte quincenal (incidencias)",
            "Reporte de asistencia (entradas/salidas)",
            "Reporte de nómina (prenómina)",
        ])
        self.combo_tipo.currentIndexChanged.connect(self._cambio_tipo)
        form.addWidget(QLabel("Tipo:"))
        form.addWidget(self.combo_tipo)
        form.addStretch()

        btn_ejecutar = BotonAccion("Generar reporte", primario=True)
        btn_ejecutar.clicked.connect(self.ejecutar)
        form.addWidget(btn_ejecutar)

        self.btn_exportar = BotonAccion("Exportar CSV")
        self.btn_exportar.clicked.connect(self.exportar_csv)
        self.btn_exportar.setEnabled(False)
        form.addWidget(self.btn_exportar)

        layout.addLayout(form)

        # Tarjetas KPI
        self.grid_kpis = QHBoxLayout()
        self.grid_kpis.setSpacing(12)
        self.tarjetas_kpi = {}
        kpis = [
            ("total_registros", "Registros", ACENTO),
            ("total_empleados", "Empleados", ACENTO),
            ("total_retardos", "Retardos", ADVERTENCIA),
            ("total_faltas", "Faltas", ERROR),
        ]
        for clave, etiqueta, color in kpis:
            tarjeta = TarjetaKPI(etiqueta, "0", "", color)
            self.tarjetas_kpi[clave] = tarjeta
            self.grid_kpis.addWidget(tarjeta)
        layout.addLayout(self.grid_kpis)

        # Tabla de resultados
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(10)
        self.tabla.setHorizontalHeaderLabels([
            "Núm. Empleado", "Nombre", "Departamento", "Fecha",
            "Tipo", "Retardo (min)", "Tiempo (min)", "Justificada", "Estado", "Regla",
        ])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        layout.addWidget(QLabel("Resultados del reporte:"))
        layout.addWidget(self.tabla, stretch=1)

        self.lbl_estado = QLabel("")
        self.lbl_estado.setStyleSheet(f"color: {TEXTO_SECUNDARIO}; font-size: 12px;")
        layout.addWidget(self.lbl_estado)

    def _cambio_tipo(self, indice: int):
        tipos = ["quincenal", "asistencia", "nomina"]
        self._tipo_actual = tipos[indice]
        # Ajustar columnas según tipo
        if self._tipo_actual == "asistencia":
            self.tabla.setColumnCount(8)
            self.tabla.setHorizontalHeaderLabels([
                "Núm. Empleado", "Nombre", "Departamento", "Tipo evento",
                "Fecha y hora", "Método", "Resultado", "Incidencia",
            ])
        elif self._tipo_actual == "nomina":
            self.tabla.setColumnCount(12)
            self.tabla.setHorizontalHeaderLabels([
                "Núm. Empleado", "Nombre", "Departamento", "Sueldo base",
                "Días lab.", "Días asist.", "Faltas", "Faltas just.",
                "Retardos", "Min. retardo", "Total preliminar", "Estado",
            ])
        else:
            self.tabla.setColumnCount(10)
            self.tabla.setHorizontalHeaderLabels([
                "Núm. Empleado", "Nombre", "Departamento", "Fecha",
                "Tipo", "Retardo (min)", "Tiempo (min)", "Justificada", "Estado", "Regla",
            ])
        self.ejecutar()

    def _actualizar_todo(self):
        self.cargar_kpis()
        self.ejecutar()

    def cargar_kpis(self):
        self.lbl_estado.setText("Cargando indicadores...")
        self.hilo_kpi = CargarReporte(
            self.api, "/api/v1/reportes/resumen-direccion", {}
        )
        self.hilo_kpi.listo.connect(self._kpis_listos)
        self.hilo_kpi.fallido.connect(self._error)
        self.hilo_kpi.start()

    def _kpis_listos(self, datos: dict):
        self.tarjetas_kpi["total_registros"].set_valor(
            str(datos.get("incidencias_mes", 0))
        )
        self.tarjetas_kpi["total_empleados"].set_valor(
            str(datos.get("total_empleados_activos", 0))
        )
        self.tarjetas_kpi["total_retardos"].set_valor(
            str(datos.get("retardos_hoy", 0))
        )
        self.tarjetas_kpi["total_faltas"].set_valor(
            str(datos.get("faltas_hoy", 0))
        )
        self.lbl_estado.setText("Indicadores actualizados.")

    def ejecutar(self):
        params = {
            "fecha_inicio": self.edit_inicio.date().toString("yyyy-MM-dd"),
            "fecha_fin": self.edit_fin.date().toString("yyyy-MM-dd"),
        }
        if self._tipo_actual == "quincenal":
            params["formato"] = "json"
            ruta = "/api/v1/reportes/quincenal"
        elif self._tipo_actual == "asistencia":
            params["formato"] = "json"
            ruta = "/api/v1/reportes/asistencia"
        else:
            # Para nómina necesitamos un periodo_id; usamos el reporte quincenal
            # como fallback si no hay periodo seleccionado
            ruta = "/api/v1/reportes/quincenal"
            params["formato"] = "json"

        self.lbl_estado.setText("Generando reporte...")
        self.btn_exportar.setEnabled(False)
        self.hilo = CargarReporte(self.api, ruta, params)
        self.hilo.listo.connect(self._listo)
        self.hilo.fallido.connect(self._error)
        self.hilo.start()

    def _listo(self, datos):
        self.tabla.setRowCount(0)
        self._datos_actuales = datos.get("filas", [])
        total = datos.get("total", 0)

        # Actualizar KPIs de la tabla
        if self._tipo_actual == "nomina":
            total_nomina = datos.get("total_nomina", 0)
            self.lbl_estado.setText(
                f"{total} empleado(s) | Total nómina: ${total_nomina:,.2f} MXN"
            )
        else:
            self.lbl_estado.setText(f"{total} registro(s) en el reporte.")

        self.btn_exportar.setEnabled(len(self._datos_actuales) > 0)

        for f in self._datos_actuales:
            fila = self.tabla.rowCount()
            self.tabla.insertRow(fila)
            if self._tipo_actual == "asistencia":
                valores = [
                    f.get("numero_empleado", ""),
                    f.get("nombre", ""),
                    f.get("departamento", ""),
                    f.get("tipo_evento", ""),
                    f.get("fecha_hora", ""),
                    f.get("metodo_registro", ""),
                    f.get("resultado", ""),
                    "Sí" if f.get("incidencia") == "Sí" else "No",
                ]
            elif self._tipo_actual == "nomina":
                valores = [
                    f.get("numero_empleado", ""),
                    f.get("nombre", ""),
                    f.get("departamento", ""),
                    f"{f.get('sueldo_base', 0):,.2f}",
                    str(f.get("dias_laborables", 0)),
                    str(f.get("dias_asistidos", 0)),
                    str(f.get("faltas_registradas", 0)),
                    str(f.get("faltas_justificadas", 0)),
                    str(f.get("retardos", 0)),
                    str(f.get("minutos_retardo", 0)),
                    f"{f.get('total_preliminar', 0):,.2f}",
                    f.get("estado", ""),
                ]
            else:
                valores = [
                    f.get("numero_empleado", ""),
                    f.get("nombre", ""),
                    f.get("departamento", ""),
                    f.get("fecha_incidencia", ""),
                    f.get("tipo_incidencia", ""),
                    str(f.get("minutos_retardo", 0)),
                    str(f.get("tiempo_incidencia_minutos", 0)),
                    f.get("justificada", ""),
                    f.get("estado", ""),
                    f.get("regla_aplicada", ""),
                ]
            for col, v in enumerate(valores):
                item = QTableWidgetItem(str(v))
                self.tabla.setItem(fila, col, item)
                # Colorear estado de incidencia
                if col == 8 and self._tipo_actual == "quincenal":
                    if str(v) == "pendiente":
                        item.setForeground(QColor("#ff9800"))
                    elif str(v) == "aprobada":
                        item.setForeground(QColor("#4caf50"))
                    elif str(v) == "rechazada":
                        item.setForeground(QColor("#f44336"))

    def _error(self, mensaje):
        self.lbl_estado.setText(f"Error: {mensaje}")
        mensaje_padre(self, "Error", mensaje, "error")

    def exportar_csv(self):
        if not self._datos_actuales:
            mensaje_padre(self, "Validación", "No hay datos para exportar.", "advertencia")
            return
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar reporte CSV", f"reporte_{self._tipo_actual}.csv",
            "Archivos CSV (*.csv)"
        )
        if not ruta:
            return
        try:
            params = {
                "fecha_inicio": self.edit_inicio.date().toString("yyyy-MM-dd"),
                "fecha_fin": self.edit_fin.date().toString("yyyy-MM-dd"),
                "formato": "csv",
            }
            if self._tipo_actual == "quincenal":
                ruta_api = "/api/v1/reportes/quincenal"
            elif self._tipo_actual == "asistencia":
                ruta_api = "/api/v1/reportes/asistencia"
            else:
                mensaje_padre(self, "Exportar", "Usa el reporte de nómina desde la vista de Prenómina.", "info")
                return

            # Obtener CSV del servidor
            import urllib.request
            url = self.api.base_url + ruta_api
            query = "&".join(f"{k}={v}" for k, v in params.items())
            req = urllib.request.Request(f"{url}?{query}")
            with urllib.request.urlopen(req, timeout=30) as resp:
                contenido = resp.read()
            with open(ruta, "wb") as f:
                f.write(contenido)
            mensaje_padre(self, "Éxito", f"Reporte exportado a:\n{ruta}", "exito")
        except Exception as e:
            mensaje_padre(self, "Error", f"No se pudo exportar: {e}", "error")

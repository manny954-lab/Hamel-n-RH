"""Panel principal con módulos y métricas visuales."""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton,
    QStackedWidget, QVBoxLayout, QWidget, QMessageBox,
)

from app.api_client import ApiClient, ApiClientError
from app.ui.theme import (
    ACENTO, ADVERTENCIA, ERROR, EXITO, FONDO_PRINCIPAL, FONDO_PANEL,
    FONDO_TARJETA, TEXTO_PRIMARIO, TEXTO_SECUNDARIO,
)


class CargarDatos(QThread):
    """Carga métricas en segundo plano."""

    listo = Signal(dict)
    fallido = Signal(str)

    def __init__(self, api: ApiClient):
        super().__init__()
        self.api = api

    def run(self) -> None:
        try:
            datos = self.api.get("/api/v1/reportes/resumen-direccion")
            self.listo.emit(datos)
        except ApiClientError as e:
            self.fallido.emit(str(e))


class TarjetaMetricaModerna(QFrame):
    """Tarjeta de métrica con diseño moderno y colorido."""

    def __init__(self, etiqueta: str, valor: str = "0", color=ACENTO):
        super().__init__()
        self.setObjectName("tarjetaMetricaModerna")
        self.setFixedSize(210, 130)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        # Etiqueta superior
        lbl_etiqueta = QLabel(etiqueta.upper())
        lbl_etiqueta.setStyleSheet(
            f"color: {TEXTO_SECUNDARIO}; font-size: 11px; font-weight: 600; letter-spacing: 0.5px;"
        )
        lbl_etiqueta.setAlignment(Qt.AlignLeft)

        # Valor grande
        self.lbl_valor = QLabel(valor)
        self.lbl_valor.setObjectName("valorMetrica")
        color_hex = color.name if hasattr(color, "name") else str(color)
        self.lbl_valor.setStyleSheet(
            f"color: {color_hex}; font-size: 34px; font-weight: 800;"
        )
        self.lbl_valor.setAlignment(Qt.AlignLeft)

        # Barra de acento inferior
        barra = QFrame()
        barra.setFixedHeight(4)
        barra.setStyleSheet(f"background-color: {color_hex}; border-radius: 2px;")

        layout.addWidget(lbl_etiqueta)
        layout.addWidget(self.lbl_valor)
        layout.addStretch()
        layout.addWidget(barra)

        # Hoja de estilo de la tarjeta
        self.setStyleSheet(f"""
            QFrame#tarjetaMetricaModerna {{
                background-color: {FONDO_TARJETA};
                border: 1px solid #3a3a45;
                border-radius: 12px;
            }}
            QFrame#tarjetaMetricaModerna:hover {{
                border-color: {color_hex};
                background-color: #32323e;
            }}
        """)

    def set_valor(self, valor: str) -> None:
        self.lbl_valor.setText(str(valor))


class DashboardView(QWidget):
    def __init__(self, api: ApiClient, ventana_principal):
        super().__init__()
        self.api = api
        self.ventana_principal = ventana_principal
        self._construir()

    def _construir(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Encabezado
        encabezado = QHBoxLayout()
        lbl_titulo = QLabel("Panel de Dirección")
        lbl_titulo.setObjectName("lblTitulo")
        lbl_titulo.setStyleSheet(
            "font-size: 24px; font-weight: 800; color: #e8e8ea;"
        )
        encabezado.addWidget(lbl_titulo)
        encabezado.addStretch()

        btn_actualizar = QPushButton("Actualizar")
        btn_actualizar.setObjectName("btnPrimario")
        btn_actualizar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_actualizar.clicked.connect(self.refrescar_metricas)
        encabezado.addWidget(btn_actualizar)

        layout.addLayout(encabezado)

        lbl_sub = QLabel("Indicadores calculados a partir de datos reales de la base de datos.")
        lbl_sub.setStyleSheet(f"color: {TEXTO_SECUNDARIO}; font-size: 13px;")
        layout.addWidget(lbl_sub)

        # Estado de conexión
        self.lbl_estado_conexion = QLabel("● Sin conexión")
        self.lbl_estado_conexion.setStyleSheet(f"color: {ERROR}; font-size: 12px; font-weight: 600;")
        layout.addWidget(self.lbl_estado_conexion)

        # Métricas en grid
        self.grid_metricas = QGridLayout()
        self.grid_metricas.setSpacing(16)
        self.tarjetas = {}
        metricas = [
            ("total_empleados_activos", "Empleados activos", ACENTO),
            ("incidencias_hoy", "Incidencias hoy", ADVERTENCIA),
            ("incidencias_pendientes", "Incidencias pendientes", ADVERTENCIA),
            ("justificantes_pendientes", "Justificantes pendientes", EXITO),
            ("periodos_nomina_abiertos", "Periodos abiertos", ACENTO),
        ]
        for i, (clave, etiqueta, color) in enumerate(metricas):
            tarjeta = TarjetaMetricaModerna(etiqueta, "0", color)
            self.tarjetas[clave] = tarjeta
            self.grid_metricas.addWidget(tarjeta, 0, i)
        layout.addLayout(self.grid_metricas)

        # Espaciador
        layout.addStretch()

        # Barra de estado inferior
        self.lbl_estado = QLabel("Listo.")
        self.lbl_estado.setStyleSheet(f"color: {TEXTO_SECUNDARIO}; font-size: 11px;")
        layout.addWidget(self.lbl_estado)

    def mostrarEvento(self, event):
        """Se llama cuando el widget se muestra. Carga métricas si hay token."""
        super().mostrarEvento(event)
        if self.api.get_token():
            self.refrescar_metricas()

    def refrescar_metricas(self):
        if not self.api.get_token():
            self.lbl_estado.setText("Sin sesión activa. Inicie sesión primero.")
            self.lbl_estado_conexion.setText("● Sin sesión")
            self.lbl_estado_conexion.setStyleSheet(f"color: {ERROR}; font-size: 12px; font-weight: 600;")
            return

        self.lbl_estado.setText("Cargando indicadores...")
        self.lbl_estado_conexion.setText("● Conectado")
        self.lbl_estado_conexion.setStyleSheet(f"color: {EXITO}; font-size: 12px; font-weight: 600;")

        self.hilo = CargarDatos(self.api)
        self.hilo.listo.connect(self._metricas_listas)
        self.hilo.fallido.connect(self._metricas_error)
        self.hilo.start()

    def _metricas_listas(self, datos: dict):
        self.lbl_estado.setText("Datos actualizados correctamente.")
        for clave, tarjeta in self.tarjetas.items():
            valor = datos.get(clave, 0)
            tarjeta.set_valor(str(valor))

    def _metricas_error(self, mensaje: str):
        self.lbl_estado.setText(f"No se pudieron cargar los indicadores: {mensaje}")
        self.lbl_estado_conexion.setText("● Error de conexión")
        self.lbl_estado_conexion.setStyleSheet(f"color: {ERROR}; font-size: 12px; font-weight: 600;")

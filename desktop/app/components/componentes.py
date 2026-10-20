"""Componentes reutilizables de la interfaz."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QLabel, QPushButton, QVBoxLayout, QWidget, QMessageBox,
)

from app.ui.theme import (
    FONDO_TARJETA, BORDE, TEXTO_PRIMARIO, TEXTO_SECUNDARIO, ACENTO,
    EXITO, ADVERTENCIA, ERROR,
)


def mensaje_padre(parent, titulo: str, texto: str, tipo: str = "info"):
    """Muestra un cuadro de diálogo informativo en español."""
    msg = QMessageBox(parent)
    msg.setWindowTitle(titulo)
    msg.setText(texto)
    iconos = {
        "error": QMessageBox.Critical,
        "advertencia": QMessageBox.Warning,
        "exito": QMessageBox.Information,
    }
    msg.setIcon(iconos.get(tipo, QMessageBox.Information))
    msg.exec()


class TarjetaMetrica(QFrame):
    """Tarjeta de métrica para el panel de dirección."""

    def __init__(self, etiqueta: str, valor: str = "0", color_valor=TEXTO_PRIMARIO):
        super().__init__()
        self.setObjectName("tarjetaMetrica")
        layout = QVBoxLayout(self)
        lbl_etiqueta = QLabel(etiqueta)
        lbl_etiqueta.setObjectName("metricaEtiqueta")
        self.lbl_valor = QLabel(valor)
        self.lbl_valor.setObjectName("metricaValor")
        color = color_valor.name if hasattr(color_valor, "name") else color_valor
        self.lbl_valor.setStyleSheet(f"color: {color};")
        layout.addWidget(lbl_etiqueta)
        layout.addWidget(self.lbl_valor)

    def set_valor(self, valor: str) -> None:
        self.lbl_valor.setText(valor)


class BotonAccion(QPushButton):
    """Botón de acción con estilo consistente."""

    def __init__(self, texto: str, primario: bool = False):
        super().__init__(texto)
        if primario:
            self.setObjectName("btnPrimario")


class CampoValidado(QFrame):
    """Campo con etiqueta y mensaje de validación."""

    def __init__(self, etiqueta: str, widget, obligatorio: bool = True):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        lbl = QLabel(etiqueta + (" *" if obligatorio else ""))
        lbl.setStyleSheet(f"color: {TEXTO_SECUNDARIO}; font-size: 12px; font-weight: 600;")
        layout.addWidget(lbl)
        layout.addWidget(widget)
        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet(f"color: {ERROR}; font-size: 11px;")
        self.lbl_error.hide()
        layout.addWidget(self.lbl_error)
        self.widget = widget

    def mostrar_error(self, mensaje: str) -> None:
        self.lbl_error.setText(mensaje)
        self.lbl_error.show()
        self.widget.setProperty("error", True)
        self.widget.style().unpolish(self.widget)
        self.widget.style().polish(self.widget)

    def limpiar_error(self) -> None:
        self.lbl_error.hide()
        self.widget.setProperty("error", False)
        self.widget.style().unpolish(self.widget)
        self.widget.style().polish(self.widget)

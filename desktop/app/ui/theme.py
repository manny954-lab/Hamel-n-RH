"""Tema oscuro profesional para Hamelín RH.

Paleta:
- Fondo: gris carbón (#1a1a1f)
- Paneles: ligeramente contrastados (#25252e / #2d2d36)
- Acento: azul suave (#4f8bc4)
- Texto: gris claro (#e8e8ea)
- Éxito: verde (#4caf8f)
- Advertencia: ámbar (#e3b341)
- Error: rojo (#d9534f)
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette

FONDO_PRINCIPAL = "#1a1a1f"
FONDO_PANEL = "#25252e"
FONDO_TARJETA = "#2d2d36"
BORDE = "#3a3a45"
TEXTO_PRIMARIO = "#e8e8ea"
TEXTO_SECUNDARIO = "#9aa0a6"
ACENTO = "#4f8bc4"
ACENTO_HOVER = "#639edb"
EXITO = "#4caf8f"
ADVERTENCIA = "#e3b341"
ERROR = "#d9534f"
SUPERFICIE_INPUT = "#1f1f27"

HOJA_ESTILO_OSCURO = f"""
QWidget {{
    background-color: {FONDO_PRINCIPAL};
    color: {TEXTO_PRIMARIO};
    font-size: 13px;
    font-family: "Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif;
}}
QToolTip {{
    background-color: {FONDO_TARJETA};
    color: {TEXTO_PRIMARIO};
    border: 1px solid {BORDE};
    padding: 4px;
    border-radius: 4px;
}}
QLabel {{ color: {TEXTO_PRIMARIO}; background: transparent; }}
QLabel#lblTitulo {{ font-size: 20px; font-weight: 700; color: {TEXTO_PRIMARIO}; }}
QLabel#lblSubtitulo {{ font-size: 13px; color: {TEXTO_SECUNDARIO}; }}
QFrame#panelLateral {{
    background-color: {FONDO_PANEL};
    border-right: 1px solid {BORDE};
}}
QPushButton {{
    background-color: {FONDO_TARJETA};
    color: {TEXTO_PRIMARIO};
    border: 1px solid {BORDE};
    border-radius: 6px;
    padding: 8px 14px;
    min-height: 36px;
}}
QPushButton:hover {{ background-color: #35353f; border-color: {ACENTO}; }}
QPushButton:pressed {{ background-color: #2e2e38; }}
QPushButton#btnPrimario {{ background-color: {ACENTO}; color: #ffffff; border: none; }}
QPushButton#btnPrimario:hover {{ background-color: {ACENTO_HOVER}; }}
QPushButton#btnPrimario:disabled {{ background-color: #3a3a45; color: {TEXTO_SECUNDARIO}; }}
QPushButton#btnExito {{ background-color: {EXITO}; color: #ffffff; border: none; }}
QPushButton#btnExito:hover {{ background-color: #5bc09e; }}
QPushButton#btnAdvertencia {{ background-color: {ADVERTENCIA}; color: #1a1a1f; border: none; }}
QPushButton#btnAdvertencia:hover {{ background-color: #f0c55a; }}
QPushButton#btnPeligro {{ background-color: {ERROR}; color: #ffffff; border: none; }}
QPushButton#btnPeligro:hover {{ background-color: #e06660; }}
QLineEdit, QSpinBox, QDoubleSpinBox, QDateEdit, QDateTimeEdit, QComboBox {{
    background-color: {SUPERFICIE_INPUT};
    color: {TEXTO_PRIMARIO};
    border: 1px solid {BORDE};
    border-radius: 6px;
    padding: 6px 10px;
    min-height: 34px;
}}
QLineEdit:focus, QComboBox:focus {{ border-color: {ACENTO}; }}
QTableWidget {{
    background-color: {FONDO_TARJETA};
    color: {TEXTO_PRIMARIO};
    border: 1px solid {BORDE};
    border-radius: 6px;
    gridline-color: #33333d;
    selection-background-color: {ACENTO};
    selection-color: #ffffff;
}}
QTableWidget::item {{ padding: 6px 8px; border-bottom: 1px solid #2a2a33; }}
QTableWidget::item:selected {{ background-color: {ACENTO}; color: #ffffff; }}
QHeaderView::section {{
    background-color: {FONDO_PANEL};
    color: {TEXTO_SECUNDARIO};
    padding: 6px 8px;
    border: none;
    border-bottom: 1px solid {BORDE};
    font-weight: 600;
}}
QTabWidget::pane {{
    border: 1px solid {BORDE};
    background-color: {FONDO_TARJETA};
    border-radius: 6px;
}}
QTabBar::tab {{
    background-color: #25252e;
    color: {TEXTO_SECUNDARIO};
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}}
QTabBar::tab:selected {{
    background-color: {FONDO_TARJETA};
    color: {TEXTO_PRIMARIO};
    border-bottom: 2px solid {ACENTO};
}}
QScrollBar:vertical {{
    background: {FONDO_PRINCIPAL};
    width: 12px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {BORDE};
    border-radius: 6px;
    min-height: 40px;
}}
QScrollBar::handle:vertical:hover {{ background: {TEXTO_SECUNDARIO}; }}
QFrame#tarjetaMetrica {{
    background-color: {FONDO_TARJETA};
    border: 1px solid {BORDE};
    border-radius: 10px;
}}
QLabel#metricaValor {{ font-size: 26px; font-weight: 700; color: {TEXTO_PRIMARIO}; }}
QLabel#metricaEtiqueta {{ font-size: 12px; color: {TEXTO_SECUNDARIO}; }}
"""


def aplicar_tema_oscuro(app) -> None:
    """Aplica el tema oscuro como hoja de estilo global de la aplicación."""
    app.setStyle("Fusion")
    app.setStyleSheet(HOJA_ESTILO_OSCURO)
    paleta = QPalette()
    paleta.setColor(QPalette.Window, QColor(FONDO_PRINCIPAL))
    paleta.setColor(QPalette.WindowText, QColor(TEXTO_PRIMARIO))
    paleta.setColor(QPalette.Base, QColor(SUPERFICIE_INPUT))
    paleta.setColor(QPalette.AlternateBase, QColor(FONDO_TARJETA))
    paleta.setColor(QPalette.Text, QColor(TEXTO_PRIMARIO))
    paleta.setColor(QPalette.Button, QColor(FONDO_TARJETA))
    paleta.setColor(QPalette.ButtonText, QColor(TEXTO_PRIMARIO))
    paleta.setColor(QPalette.Highlight, QColor(ACENTO))
    paleta.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    app.setPalette(paleta)

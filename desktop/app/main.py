"""Punto de entrada de la aplicación de escritorio Hamelín RH."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app.ui.theme import aplicar_tema_oscuro
from app.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    aplicar_tema_oscuro(app)
    ventana = MainWindow()
    ventana.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

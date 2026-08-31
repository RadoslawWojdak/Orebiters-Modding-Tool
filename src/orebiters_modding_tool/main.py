import sys

from PySide6.QtWidgets import QApplication

from orebiters_modding_tool.app.main_window import MainWindow


def main() -> None:
    """Start the application."""

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

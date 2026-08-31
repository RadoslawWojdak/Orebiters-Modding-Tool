from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget


class MainWindow(QMainWindow):
    """Main window of the application."""

    DEFAULT_WIDTH = 800
    DEFAULT_HEIGHT = 600

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Orebiters Modding Tool")
        self.resize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)

        self._setup_central_widget()

    def _setup_central_widget(self) -> None:
        """Set up the central application widget."""

        central_widget = QWidget()
        QVBoxLayout(central_widget)

        self.setCentralWidget(central_widget)

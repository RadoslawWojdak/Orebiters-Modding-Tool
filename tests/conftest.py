import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """Provide a QApplication instance for widget tests."""
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    return app

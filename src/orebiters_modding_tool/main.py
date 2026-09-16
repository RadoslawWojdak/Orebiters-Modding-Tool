import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from orebiters_modding_tool.app.main_window import MainWindow
from orebiters_modding_tool.infrastructure.localization_repository import LocalizationRepository
from orebiters_modding_tool.infrastructure.material_repository import MaterialRepository
from orebiters_modding_tool.infrastructure.project_repository import ProjectRepository
from orebiters_modding_tool.resources import resources_rc  # noqa: F401
from orebiters_modding_tool.services.project_service import ProjectService


def main() -> None:
    """Start the application."""
    app = QApplication(sys.argv)
    QApplication.setStyle("Fusion")

    mods_directory = Path.home() / "AppData" / "Roaming" / "Orebiters" / "mods"

    project_repository = ProjectRepository(mods_directory)
    localization_repository = LocalizationRepository(mods_directory)
    material_repository = MaterialRepository(mods_directory)

    project_service = ProjectService(
        project_repository,
        localization_repository,
        material_repository,
    )

    window = MainWindow(project_service)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

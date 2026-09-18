import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from orebiters_modding_tool.app.main_window import MainWindow
from orebiters_modding_tool.domain.content import ContentType
from orebiters_modding_tool.infrastructure.content_repository import ContentRepository
from orebiters_modding_tool.infrastructure.localization_repository import LocalizationRepository
from orebiters_modding_tool.infrastructure.project_repository import ProjectRepository
from orebiters_modding_tool.resources import resources_rc  # noqa: F401
from orebiters_modding_tool.services.project_service import ProjectService


def main() -> None:
    """Start the application."""
    app = QApplication(sys.argv)
    QApplication.setStyle("Fusion")

    mods_directory = Path.home() / "AppData" / "Roaming" / "Orebiters" / "mods"

    project_service = ProjectService(
        project_repository=ProjectRepository(mods_directory),
        localization_repository=LocalizationRepository(mods_directory),
        content_repositories={
            content_type: ContentRepository.get_class(content_type)(mods_directory)
            for content_type in ContentType
        },
    )

    window = MainWindow(project_service)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

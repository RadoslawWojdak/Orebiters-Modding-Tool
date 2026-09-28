from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from orebiters_modding_tool.app.widgets.workspace import Workspace
from orebiters_modding_tool.domain.content import ContentReference, ContentType
from orebiters_modding_tool.domain.project import Project
from orebiters_modding_tool.infrastructure.content_repository import ContentRepository
from orebiters_modding_tool.infrastructure.localization_repository import LocalizationRepository
from orebiters_modding_tool.infrastructure.project_repository import ProjectRepository
from orebiters_modding_tool.services.project_service import ProjectService


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """Provide a QApplication instance for widget tests."""
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    return app


@pytest.fixture
def project() -> Project:
    """Provide a project."""
    return Project(
        namespace="test",
        mod_id="test_mod",
        name="Test Mod",
    )


@pytest.fixture
def project_service(tmp_path: Path) -> ProjectService:
    """Provide a project service with temporary repositories."""
    content_repositories = {
        content_type: ContentRepository.get_class(content_type)(tmp_path)
        for content_type in ContentType
    }

    return ProjectService(
        project_repository=ProjectRepository(tmp_path),
        localization_repository=LocalizationRepository(tmp_path),
        content_repositories=content_repositories,
    )


@pytest.fixture
def active_project_service(project_service: ProjectService) -> ProjectService:
    """Provide a project service with an active project."""
    project = project_service.create_project(namespace="test", name="Test Mod")
    project_service.open_project(project.qualified_id)

    return project_service


@pytest.fixture
def workspace(qapp: QApplication, project_service: ProjectService) -> Workspace:
    """Provide a workspace with an active project."""
    project_service.create_project(
        namespace="test",
        name="Test Mod",
    )

    return Workspace(project_service)


@pytest.fixture
def materials_category_reference() -> ContentReference:
    """Provide a reference to the materials content category."""
    return ContentReference(content_type=ContentType.MATERIALS)

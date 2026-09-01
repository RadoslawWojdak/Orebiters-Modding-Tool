from pathlib import Path

from orebiters_modding_tool.domain.content import ContentReference

IMAGE_EXTENSION = ".png"


def get_content_image_path(
    project_path: Path,
    content_directory_name: str,
    content_reference: ContentReference,
) -> Path:
    """Get the absolute path to a content image.

    :param project_path: Root directory of the project.
    :param content_directory_name: Directory containing the content type.
    :param content_reference: Reference to the content.
    :returns: Absolute path to the content image.
    """
    return (
        project_path
        / content_reference.mod_id
        / content_directory_name
        / f"{content_reference.content_id}{IMAGE_EXTENSION}"
    )

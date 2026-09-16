from typing import TypeVar

from orebiters_modding_tool.domain.content import (
    Content,
    ContentLocalization,
    ContentReference,
    ContentState,
    ContentType,
)

TLocalization = TypeVar("TLocalization", bound=ContentLocalization)


class ContentReferenceFactory:
    """Create content references for tests."""

    _counter = 0

    @classmethod
    def create(
        cls,
        *,
        content_type: ContentType = ContentType.MATERIALS,
        qualified_id: str | None = None,
    ) -> ContentReference:
        """Create a content reference.

        :param content_type: Type of referenced content.
        :param qualified_id: Fully qualified content ID.
        :returns: Created content reference.
        """
        if qualified_id is None:
            cls._counter += 1
            qualified_id = f"test.content_{cls._counter}"

        return ContentReference(
            content_type=content_type,
            qualified_id=qualified_id,
        )

    @staticmethod
    def from_content(
        content: Content[TLocalization],
        *,
        mod_id: str = "test.test_mod",
    ) -> ContentReference:
        """Create a reference to existing content.

        :param content: Content to reference.
        :param mod_id: ID of the owning mod.
        :returns: Reference to the content.
        """
        return ContentReference(
            content_type=content.CONTENT_TYPE,
            qualified_id=content.get_qualified_id(mod_id),
        )


class ContentFactory:
    """Create content for tests."""

    _counter = 0

    @classmethod
    def create(
        cls,
        *,
        id: str | None = None,
        localizations: dict[str, ContentLocalization] | None = None,
        state: ContentState = ContentState.SAVED,
    ) -> Content[ContentLocalization]:
        """Create content.

        :param id: Local content ID.
        :param localizations: Localized content text.
        :param state: Current persistence state of the content.
        :returns: Created content.
        """
        if id is None:
            cls._counter += 1
            id = f"content_{cls._counter}"

        if localizations is None:
            localizations = {
                "en": ContentLocalization(
                    one=id.replace("_", " ").title(),
                    few=id.replace("_", " ").title(),
                    many=id.replace("_", " ").title(),
                ),
            }

        return Content(id=id, localizations=localizations, state=state)

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
        qualified_id: str | None = None,
        *,
        content_type: ContentType | None = None,
    ) -> ContentReference:
        """Create a content reference.

        :param content_type: Type of referenced content.
            If omitted, it is inferred from the qualified ID.
        :param qualified_id: Fully qualified content ID.
        :returns: Created content reference.
        :raises ValueError: If the content type cannot be inferred.
        """
        if qualified_id is None:
            cls._counter += 1
            qualified_id = f"test.test_mod.materials.content_{cls._counter}"

        if content_type is None:
            content_type = cls._infer_content_type(qualified_id)

        return ContentReference(
            content_type=content_type,
            qualified_id=qualified_id,
        )

    @staticmethod
    def _infer_content_type(qualified_id: str) -> ContentType:
        """Infer the content type from a qualified ID.

        :param qualified_id: Fully qualified content ID.
        :returns: Inferred content type.
        :raises ValueError: If the qualified ID does not contain a known type.
        """
        parts = qualified_id.split(".")

        if len(parts) != 4:
            raise ValueError(f"Cannot infer content type from qualified ID: {qualified_id!r}.")

        for content_type in ContentType:
            if parts[-2] == content_type.value:
                return content_type

        raise ValueError(f"Cannot infer content type from qualified ID: {qualified_id!r}.")

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
            name = id.replace("_", " ").title()
            localizations = {
                "en": ContentLocalization(
                    one=name,
                    few=name,
                    many=name,
                ),
            }

        return Content(id=id, localizations=localizations, state=state)

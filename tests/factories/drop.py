from orebiters_modding_tool.domain.content import ContentReference, ContentType
from orebiters_modding_tool.domain.mineable import Drop
from tests.factories.content import ContentReferenceFactory


class DropFactory:
    """Create drops for tests."""

    @staticmethod
    def create(*, item: ContentReference | None = None, probability: float = 1.0) -> Drop:
        """Create a drop."""
        if item is None:
            item = ContentReferenceFactory.create(content_type=ContentType.MATERIALS)

        return Drop(item=item, probability=probability)

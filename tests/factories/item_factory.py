from orebiters_modding_tool.domain.content import ContentState
from orebiters_modding_tool.domain.item import Item, ItemLocalization
from orebiters_modding_tool.domain.material import MaterialRequirement


class ItemFactory:
    """Create items for tests."""

    _counter = 0

    @classmethod
    def create(
        cls,
        *,
        id: str | None = None,
        localizations: dict[str, ItemLocalization] | None = None,
        max_stack_size: int | None = None,
        base_price: int | None = None,
        crafting_materials: list[MaterialRequirement] | None = None,
        state: ContentState = ContentState.SAVED,
    ) -> Item:
        """Create an item.

        :param id: Local item ID.
        :param localizations: Localized item text.
        :param max_stack_size: Maximum stack size.
        :param base_price: Base price of the item.
        :param crafting_materials: Materials required for crafting.
        :param state: Current persistence state of the item.
        :returns: Created item.
        """
        if id is None:
            cls._counter += 1
            id = f"item_{cls._counter}"

        if localizations is None:
            name = id.replace("_", " ").title()
            localizations = {
                "en": ItemLocalization(
                    one=name,
                    few=name,
                    many=name,
                    hint="Test item.",
                    description="Item created for testing.",
                ),
            }

        if crafting_materials is None:
            crafting_materials = []

        return Item(
            id=id,
            localizations=localizations,
            max_stack_size=max_stack_size,
            base_price=base_price,
            crafting_materials=crafting_materials,
            state=state,
        )

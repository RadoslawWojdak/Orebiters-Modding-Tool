from orebiters_modding_tool.domain.content import ContentState
from orebiters_modding_tool.domain.material import (
    Material,
    MaterialLocalization,
    MaterialRequirement,
)


class MaterialFactory:
    """Create materials for tests."""

    _counter = 0

    @classmethod
    def create(
        cls,
        *,
        id: str | None = None,
        localizations: dict[str, MaterialLocalization] | None = None,
        crafting_materials: list[MaterialRequirement] | None = None,
        state: ContentState = ContentState.SAVED,
    ) -> Material:
        """Create a material.

        :param id: Local material ID.
        :param localizations: Localized material text.
        :param crafting_materials: Materials required for crafting.
        :param state: Current persistence state of the material.
        :returns: Created material.
        """
        if id is None:
            cls._counter += 1
            id = f"material_{cls._counter}"

        if localizations is None:
            localizations = {
                "en": MaterialLocalization(
                    one=id.replace("_", " ").title(),
                    few=id.replace("_", " ").title(),
                    many=id.replace("_", " ").title(),
                    hint="Test material.",
                    description="Material created for testing.",
                ),
            }

        if crafting_materials is None:
            crafting_materials = []

        return Material(
            id=id,
            localizations=localizations,
            crafting_materials=crafting_materials,
            state=state,
        )

from orebiters_modding_tool.domain.content import ContentReference, ContentType
from orebiters_modding_tool.domain.material import MaterialRequirement
from tests.factories.content import ContentReferenceFactory


class MaterialRequirementFactory:
    """Create material requirements for tests."""

    @staticmethod
    def create(
        material_reference: ContentReference | None = None,
        amount: int = 2,
    ) -> MaterialRequirement:
        """Create a material requirement.

        :param material_reference: Reference to the required material.
        :param amount: Amount of the material.
        :return: Created material requirement.
        """
        if material_reference is None:
            material_reference = ContentReferenceFactory.create(content_type=ContentType.MATERIALS)

        return MaterialRequirement(material_reference, amount)

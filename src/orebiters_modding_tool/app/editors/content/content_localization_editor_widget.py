from orebiters_modding_tool.app.editors.base_editor_widget import BaseEditorWidget
from orebiters_modding_tool.app.editors.editor_field import EditorField, EditorVariantField
from orebiters_modding_tool.domain.content import ContentLocalization


class ContentLocalizationEditorWidget[TLocalization: ContentLocalization](
    BaseEditorWidget[TLocalization]
):
    """Base editor for content localization."""

    FIELDS: tuple[EditorField | EditorVariantField, ...] = (
        EditorField(name="one", label="One"),
        EditorField(name="few", label="Few"),
        EditorField(name="many", label="Many"),
    )

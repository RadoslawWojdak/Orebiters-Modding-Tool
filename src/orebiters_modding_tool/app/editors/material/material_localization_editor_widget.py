from orebiters_modding_tool.app.editors.content.content_localization_editor_widget import (
    ContentLocalizationEditorWidget,
)
from orebiters_modding_tool.app.editors.editor_field import EditorField, EditorVariantField
from orebiters_modding_tool.domain.material import MaterialLocalization


class MaterialLocalizationEditorWidget(ContentLocalizationEditorWidget[MaterialLocalization]):
    """Editor for material localization."""

    FIELDS: tuple[EditorField | EditorVariantField, ...] = (
        *ContentLocalizationEditorWidget.FIELDS,
        EditorField(name="hint", label="Hint"),
        EditorField(name="description", label="Description"),
    )

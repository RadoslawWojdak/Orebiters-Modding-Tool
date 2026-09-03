from orebiters_modding_tool.app.editors.base_editor_widget import BaseEditorWidget
from orebiters_modding_tool.app.editors.editor_field import EditorField
from orebiters_modding_tool.domain.material import MaterialLocalization


class MaterialLocalizationEditorWidget(BaseEditorWidget[MaterialLocalization]):
    """Editor for material localization."""

    FIELDS = (
        EditorField(name="one", label="One"),
        EditorField(name="few", label="Few"),
        EditorField(name="many", label="Many"),
        EditorField(name="hint", label="Hint"),
        EditorField(name="description", label="Description"),
    )

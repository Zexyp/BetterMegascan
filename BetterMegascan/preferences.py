import bpy
from bpy.types import AddonPreferences
from bpy.props import EnumProperty, StringProperty


class BETTERMS_AddonPreferences(AddonPreferences):
    bl_idname = __package__

    import_menu_type: EnumProperty(
        name="Import Menu Type",
        items=(
            ('NORMAL', "Normal", "Opens as regular menu"),
            ('PIE', "Pie", "Opens as pie menu"),
        ),
        default='PIE',
    )

    name_template_model: StringProperty(
        name="Model",
        description="Specifies template for model name.\n(name, id, model, lod)",
        default="${name}_${id}_${model}_LOD${lod}"
    )

    name_template_group_asset: StringProperty(
        name="Asset Collection",
        description="Specifies template for asset collection name.\n(name, id)",
        default="${name}_${id}"
    )

    name_template_group_model: StringProperty(
        name="Model Collection",
        description="Specifies template for model collection name.\n(name, id, model)",
        default="${name}_${id}_${model}"
    )

    name_template_material: StringProperty(
        name="Material",
        description="Specifies template for material name.\n(name, id)",
        default="${name}_${id}"
    )

    name_template_map: StringProperty(
        name="Map",
        description="Specifies template for map name.\n(name, id, type)",
        default="${name}_${id}_${type}"
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "import_menu_type")

        layout.separator()

        col = layout.column(heading="Name Templates")
        col.prop(self, "name_template_model")
        col.prop(self, "name_template_material")
        col.prop(self, "name_template_map")
        col.prop(self, "name_template_group_asset")
        col.prop(self, "name_template_group_model")


def get(context) -> BETTERMS_AddonPreferences:
    preferences = context.preferences
    return preferences.addons[__package__].preferences

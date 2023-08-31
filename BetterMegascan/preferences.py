import bpy
from bpy.types import AddonPreferences
from bpy.props import EnumProperty


class BETTERMS_AddonPreferences(AddonPreferences):
    bl_idname = __package__

    import_menu_type: EnumProperty(
        name="Import Menu Type",
        items=[
            ('NORMAL', "Normal", "Opens as regular menu"),
            ('PIE', "Pie", "Opens as pie menu"),
        ],
        default='PIE',
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "import_menu_type")


def get(context):
    preferences = context.preferences
    return preferences.addons[__package__].preferences

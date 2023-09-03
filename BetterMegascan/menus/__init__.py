import bpy

from ..operators import *
from .. import preferences

class BETTERMS_MT_import(bpy.types.Menu):
    bl_idname = "BETTERMS_MT_import"
    bl_label = "Import As..."

    def draw(self, context):
        layout = self.layout

        if preferences.get(context).import_menu_type == 'PIE':
            layout = layout.menu_pie()

        layout.operator(BETTERMS_OT_import_model.bl_idname, icon='OUTLINER_OB_MESH')
        layout.operator(BETTERMS_OT_import_surface.bl_idname, icon='MATERIAL')
        layout.operator(BETTERMS_OT_import_brush.bl_idname, icon='BRUSH_DATA')


classes = [
    BETTERMS_MT_import,
]

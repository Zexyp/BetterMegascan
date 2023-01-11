import bpy

from ..menus import BETTERMS_MT_import
from .. import preferences

class BETTERMS_OT_init_import_menu(bpy.types.Operator):
    bl_idname = "betterms.init_menu"
    bl_label = "Megascan"
    bl_description = "Load a Megascan asset (works for both directory and .zip)"

    def execute(self, context):
        if preferences.get(context).import_menu_type == 'PIE':
            bpy.ops.wm.call_menu_pie(name=BETTERMS_MT_import.bl_idname)
        else:
            bpy.ops.wm.call_menu(name=BETTERMS_MT_import.bl_idname)
        return {'INTERFACE'}

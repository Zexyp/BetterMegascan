import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty

import os

from .. import ui


class BETTERMS_OT_import_library(Operator, ImportHelper):
    bl_idname = "betterms.import_library"
    bl_label = "Bake Megascan Library"
    bl_options = {'PRESET'}

    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'}
    )

    def invoke(self, context, event):
        if not bpy.data.filepath:
            self.report({'WARNING'}, 'File not saved.')
            ui.popup_message_info('Please save your file first.')
            return {'CANCELLED'}
        return ImportHelper.invoke(self, context, event)

    def execute(self, context):
        if not (os.path.exists(self.filepath) and os.path.isfile(self.filepath)):
            self.report({'WARNING'}, "File does not exist.")
            return {'CANCELLED'}

        bpy.ops.betterms.bake_library('INVOKE_DEFAULT', filepath=self.filepath)

        return {'FINISHED'}

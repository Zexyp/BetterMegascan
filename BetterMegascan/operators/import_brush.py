from bpy.props import EnumProperty

import os

from .base_importer import BaseImporter
from .. import loader

from . import log

class BETTERMS_OT_import_brush(BaseImporter):
    bl_idname = "betterms.import_brush"
    bl_label = "Brush"
    bl_description = "Load surface as brush"
    bl_options = {'UNDO'}

    use_filetype_maps: EnumProperty(
        name="Textures",
        items=[
            ('PREFER_EXR', "Prefer EXR", "Fallback is JPEG"),
            ('JPEG', "JPEG only", "(.jpeg/.jpg)"),
            ('EXR', "EXR only", "(.exr)")
        ],
        default='PREFER_EXR',
    )

    able_to_import = ["brush", "surface", "decal", "atlas", "3D plant", "3D asset"]

    def finish_execute(self, context) -> set:
        load_ret = loader.load_brush(self.mdata,
                                     self.dir_path,
                                     use_filetype_maps=self.use_filetype_maps,
                                     pack_maps=os.path.isfile(self.dir_path))

        if load_ret["texture"] is None:
            self.report({'WARNING'}, f"No desired map found.")
            return {'CANCELED'}

        # info
        self.report({'INFO'}, f"Loaded brush")
        return {'FINISHED'}

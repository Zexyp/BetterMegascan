import bpy
from bpy.props import StringProperty, EnumProperty, BoolVectorProperty

import os
import traceback

from . import base_importer
from .base_importer import BaseImporter, SurfaceImportProps
from .. import parser
from .. import loader

from . import log


class BETTERMS_OT_import_surface(BaseImporter, SurfaceImportProps):
    bl_idname = "betterms.import_surface"
    bl_label = "Surface"
    bl_description = "Load material and its textures"
    bl_options = {'UNDO', 'PRESET'}

    able_to_import = ["surface", "decal", "atlas", "3D plant", "3D asset"]

    def finish_execute(self, context) -> set:
        load_ret = loader.load_material(self.mdata,
                                        self.dir_path,
                                        use_filetype_maps=self.use_filetype_maps,
                                        use_maps=[base_importer.map_options[i] for i, e in enumerate(self.use_maps) if e],
                                        pack_maps=os.path.isfile(self.dir_path))

        # info
        self.report({'INFO'}, f"Loaded {len(load_ret['images'])} maps")
        return {'FINISHED'}

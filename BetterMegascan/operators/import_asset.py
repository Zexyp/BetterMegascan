import bpy
from bpy.props import StringProperty, EnumProperty, BoolProperty, BoolVectorProperty

import os
import traceback

from . import base_importer
from .base_importer import BaseImporter, AssetImportProps
from .. import parser
from .. import loader

from . import log

'''
map_options_names = [
    "Albedo",
    "Cavity",
    "Curvature",
    "Gloss",
    "Normal",
    "Normal Bump",
    "Normal Object",
    "Displacement",
    "Bump",
    "AO",
    "Metalness",
    "Diffuse",
    "Roughness",
    "Specular",
    "Fuzz",
    "Translucency",
    "Thickness",
    "Opacity",
    "Brush",
    "Mask",
    "Transmission",
]
'''


class BETTERMS_OT_import_asset(BaseImporter, AssetImportProps):
    bl_idname = "betterms.import_asset"
    bl_label = "3D Asset"
    bl_description = "Load model with material and its textures"
    bl_options = {'UNDO', 'PRESET'}

    able_to_import = ["3D asset", "3D plant"]

    def finish_execute(self, context) -> set:
        if self.use_filetype_lods == 'ABC':
            self.report({'WARNING'}, "Alembic files are not supported.")
            # raise NotImplemented
            return {'CANCELLED'}

        load_ret = loader.load_asset(self.mdata,
                                     self.dir_path,
                                     group_by_model=self.group_by_model,
                                     group_by_lod=self.group_by_lod,
                                     use_filetype_lods=self.use_filetype_lods,
                                     use_filetype_maps=self.use_filetype_maps,
                                     use_lods=[base_importer.lod_options[i] for i, e in enumerate(self.use_lods) if e],
                                     use_maps=[base_importer.map_options[i] for i, e in enumerate(self.use_maps) if e],
                                     pack_maps=os.path.isfile(self.dir_path),
                                     apply_transform=self.apply_transform)

        for o in load_ret["objects"]:
            o.select_set(True)

        # info
        self.report({'INFO'}, f"Loaded {len(load_ret['objects'])} models and {len(load_ret['images'])} maps")
        return {'FINISHED'}

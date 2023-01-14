import bpy
from bpy.props import StringProperty, EnumProperty, BoolProperty, BoolVectorProperty

import os
import traceback

from .base_importer import BaseImporter
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


class BETTERMS_OT_import_3dasset(BaseImporter):
    bl_idname = "betterms.import_3dasset"
    bl_label = "3D Asset"
    bl_description = "Load model with material and its textures"
    bl_options = {'UNDO', 'PRESET'}

    lod_options = [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
    ]

    map_options = [
        "albedo",
        "cavity",
        "curvature",
        "gloss",
        "normal",
        "displacement",
        "bump",
        "ao",
        "metalness",
        "diffuse",
        "roughness",
        "specular",
        "fuzz",
        "translucency",
        "thickness",
        "opacity",
        "brush",
        "mask",
        "transmission",
    ]

    use_filetype_lods: EnumProperty(
        name="Models",
        items=(
            ('FBX', "FBX", "Filmbox (.fbx)"),
            ('OBJ', "OBJ", "Wavefront (.obj)"),
            ('ABC', "ABC", "Alembic (.abc)")
        ),
        default='FBX',
    )

    use_filetype_maps: EnumProperty(
        name="Textures",
        items=(
            ('PREFER_EXR', "Prefer EXR", "Fallback is JPEG"),
            ('JPEG', "JPEG only", "(.jpeg/.jpg)"),
            ('EXR', "EXR only", "(.exr)")
        ),
        default='PREFER_EXR',
    )

    use_lods: BoolVectorProperty(
        name="Import LODs",
        size=len(lod_options),
        default=(
            True,   # 0
            False,  # 1
            False,  # 2
            False,  # 3
            False,  # 4
            False,  # 5
            False,  # 6
            False,  # 7
            False,  # 8
        )
    )

    use_maps: BoolVectorProperty(
        name="Import Maps",
        size=len(map_options),
        default=(
            True,   # albedo
            False,  # cavity
            False,  # curvature
            False,  # gloss
            True,   # normal
            False,  # displacement
            False,  # bump
            False,  # ao
            True,   # metalness
            False,  # diffuse
            True,   # roughness
            False,  # specular
            False,  # fuzz
            False,  # translucency
            False,  # thickness
            True,   # opacity
            False,  # brush
            False,  # mask
            False,  # transmission
        )
    )

    group_by_model: BoolProperty(
        name="Group Models",
        default=True,
    )

    group_by_lod: BoolProperty(
        name="Group LODs",
        default=False,
    )

    able_to_import = ["3D asset", "3D plant"]

    def finxish_execute(self, context) -> set:
        if self.use_filetype_lods == 'ABC':
            self.report({'WARNING'}, "Alembic files are not supported.")
            # raise NotImplemented
            return {'CANCELLED'}

        load_ret = loader.load_asset(self.mdata,
                                     self.selected_filepath,
                                     group_by_model=self.group_by_model,
                                     group_by_lod=self.group_by_lod,
                                     use_filetype_lods=self.use_filetype_lods,
                                     use_filetype_maps=self.use_filetype_maps,
                                     use_lods=[self.lod_options[i] for i, e in enumerate(self.use_lods) if e],
                                     use_maps=[self.map_options[i] for i, e in enumerate(self.use_maps) if e],
                                     pack_maps=os.path.isfile(self.selected_filepath))

        for o in load_ret["objects"]:
            o.select_set(True)

        # info
        self.report({'INFO'}, f"Loaded {len(load_ret['objects'])} models and {len(load_ret['images'])} maps")
        return {'FINISHED'}

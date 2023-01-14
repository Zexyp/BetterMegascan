import bpy
from bpy.props import StringProperty, EnumProperty, BoolVectorProperty

import os
import traceback

from .base_importer import BaseImporter
from .. import parser
from .. import loader

from . import log


class BETTERMS_OT_import_surface(BaseImporter):
    bl_idname = "betterms.import_surface"
    bl_label = "Surface"
    bl_description = "Load material and its textures"
    bl_options = {'UNDO', 'PRESET'}

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

    use_filetype_maps: EnumProperty(
        name="Textures",
        items=(
            ('PREFER_EXR', "Prefer EXR", "Fallback is JPEG"),
            ('JPEG', "JPEG only", "(.jpeg/.jpg)"),
            ('EXR', "EXR only", "(.exr)")
        ),
        default='PREFER_EXR',
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

    able_to_import = ["surface", "decal", "atlas", "3D plant", "3D asset"]

    def finish_execute(self, context) -> set:
        load_ret = loader.load_material(self.mdata,
                                        self.selected_filepath,
                                        use_filetype_maps=self.use_filetype_maps,
                                        use_maps=[self.map_options[i] for i, e in enumerate(self.use_maps) if e],
                                        pack_maps=os.path.isfile(self.selected_filepath))

        # info
        self.report({'INFO'}, f"Loaded {len(load_ret['images'])} maps")
        return {'FINISHED'}

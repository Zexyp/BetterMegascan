import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, EnumProperty, BoolVectorProperty

import os
import traceback

from .. import parser
from .. import loader

from . import log


class BETTERMS_OT_import_surface(Operator, ImportHelper):
    bl_idname = "betterms.import_surface"
    bl_label = "Surface"
    bl_description = "Load material and its textures"
    bl_options = {'UNDO', 'PRESET'}

    # ImportHelper mixin class uses this
    filename_ext = ".zip"
    filter_glob: StringProperty(
        default="*.zip",
        options={'HIDDEN'}
    )

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

    def draw(self, context):
        pass

    def execute(self, context):
        if not self.filepath:
            return {'CANCELLED'}

        selected_filepath = self.filepath

        if not os.path.exists(selected_filepath):
            selected_filepath = os.path.dirname(selected_filepath)

        log.debug(f"selected {selected_filepath}")

        mdata = None

        try:
            if os.path.isfile(selected_filepath):
                mdata = parser.parse_zip(selected_filepath)
            if os.path.isdir(selected_filepath):
                mdata = parser.parse(selected_filepath)
        except parser.InvalidStructureError:
            log.debug(traceback.format_exc())
            self.report({'ERROR'}, "Structure was not recognized.")
            return {'CANCELLED'}
        assert mdata

        if mdata.type not in ["surface", "decal", "atlas", "3D plant", "3D asset"]:
            self.report({'WARNING'}, "Invalid asset type.")
            return {'CANCELLED'}

        load_ret = loader.load_material(mdata,
                                        selected_filepath,
                                        use_filetype_maps=self.use_filetype_maps,
                                        use_maps=[self.map_options[i] for i, e in enumerate(self.use_maps) if e],
                                        pack_maps=os.path.isfile(selected_filepath))

        # info
        self.report({'INFO'}, f"Loaded {len(load_ret['images'])} maps")
        return {'FINISHED'}

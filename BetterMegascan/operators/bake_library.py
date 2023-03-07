import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, BoolVectorProperty

import os

from . import log

class BETTERMS_OT_bake_library_helper(Operator, ImportHelper):
    bl_idname = "betterms.bake_library_helper"
    bl_label = "Bake Megascan Library"

    # ImportHelper mixin
    filename_ext = ".json"
    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'}
    )

    def execute(self, context):
        if not (os.path.exists(self.filepath) and os.path.isfile(self.filepath)):
            self.report({'WARNING'}, "No file selected")
            return {'CANCELLED'}

        log.debug(f"library selected {self.filepath}")

        bpy.ops.betterms.bake_library('INVOKE_DEFAULT', json_path=self.filepath)

        return {'FINISHED'}


class BETTERMS_OT_bake_library(Operator):
    bl_idname = "betterms.bake_library"
    bl_label = "Bake Megascan Library"
    bl_options = {'PRESET'}

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

    use_lods: BoolVectorProperty(
        name="Import LODs",
        size=len(lod_options),
        default=(
            True,  # 0
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
            True,  # albedo
            False,  # cavity
            False,  # curvature
            False,  # gloss
            True,  # normal
            False,  # displacement
            False,  # bump
            False,  # ao
            True,  # metalness
            False,  # diffuse
            True,  # roughness
            False,  # specular
            False,  # fuzz
            False,  # translucency
            False,  # thickness
            True,  # opacity
            False,  # brush
            False,  # mask
            False,  # transmission
        )
    )

    include_assets_options = [
        "3D asset", "3D plant",
    ]

    include_surfaces_options = [
        "surface", "decal", "atlas",
    ]

    include_assets: BoolVectorProperty(
        name="Include Assets",
        size=len(include_assets_options),
        default=(
            True,
            True,
        )
    )

    include_surfaces: BoolVectorProperty(
        name="Include Surfaces",
        size=len(include_surfaces_options),
        default=(
            True,
            True,
            True,
        )
    )

    json_path: StringProperty()

    def draw(self, context):
        layout = self.layout

        split = layout.split()

        col = split.column(heading="Include Assets", align=True)
        for i, omap in enumerate(self.include_assets_options):
            col.prop(self, "include_assets", index=i, text=omap)

        col = split.column(heading="Include Surfaces", align=True)
        for i, omap in enumerate(self.include_surfaces_options):
            col.prop(self, "include_surfaces", index=i, text=omap)

        split = layout.split()

        box = split.column().box()
        col = box.column(heading="LODs", align=True)
        col.prop(self, "use_lods", index=0, text=str(self.lod_options[0]))
        row = box.row()
        for i in range(1, 5):
            row.prop(self, "use_lods", index=i, text=str(self.lod_options[i]))
        row = box.row()
        for i in range(5, 9):
            row.prop(self, "use_lods", index=i, text=str(self.lod_options[i]))
        box.enabled = any(self.include_assets)

        box = split.column().box()
        col = box.column(heading="Maps", align=True)
        for i, omap in enumerate(self.map_options):
            col.prop(self, "use_maps", index=i, text=omap)
        box.enabled = any(self.include_surfaces)

    def execute(self, context):
        assert self.directory
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

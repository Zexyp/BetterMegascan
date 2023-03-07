import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, BoolVectorProperty

import os

from . import log
from .. import ui
from .base_importer import AssetImportProps


class BETTERMS_OT_bake_library(Operator, ImportHelper, AssetImportProps):
    bl_idname = "betterms.bake_library"
    bl_label = "Bake Megascan Library"
    bl_options = {'PRESET'}

    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'}
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
        ui.filetype_lods(box, self)
        ui.group(box, self)
        ui.lods(box, self)
        box.enabled = any(self.include_assets)

        box = split.column().box()
        ui.filetype_maps(box, self)
        ui.maps(box, self)

    def execute(self, context):
        if not (os.path.exists(self.filepath) and os.path.isfile(self.filepath)):
            self.report({'WARNING'}, "File does not exist.")
            return {'CANCELLED'}
        if not (any(self.include_assets) or any(self.include_surfaces)):
            self.report({'WARNING'}, "Nothing to bake.")
            return {'CANCELLED'}



        return {'FINISHED'}

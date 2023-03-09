import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, BoolVectorProperty

import os

from . import log
from .. import parser
from .. import loader
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

    generate_previews: BoolProperty(
        name="Generate Previews",
        description="Generates previews for all assets",
        default=True,
    )

    use_collections: BoolProperty(
        name="Use Collections",
        description="Encapsulate models in collections",
        default=False,
    )

    split_models: BoolProperty(
        name="Split Models",
        description="Split individual models or variants",
        default=True,
    )

    def draw(self, context):
        layout = self.layout

        layout.prop(self, "generate_previews")

        split = layout.split()

        col = split.column(heading="Include Assets", align=True)
        for i, omap in enumerate(self.include_assets_options):
            col.prop(self, "include_assets", index=i, text=omap)

        col = split.column(heading="Include Surfaces", align=True)
        for i, omap in enumerate(self.include_surfaces_options):
            col.prop(self, "include_surfaces", index=i, text=omap)

        split = layout.split()

        column = split.column()
        column.label(text="Asset")
        column.prop(self, "use_collections")
        column.prop(self, "split_models")

        box = column.box()
        column.enabled = any(self.include_assets)

        ui.filetype_lods(box, self)
        ui.group(box, self)
        ui.lods(box, self)

        column = split.column()
        column.label(text="Surface")

        box = column.box()

        ui.filetype_maps(box, self)
        ui.maps(box, self)

    def execute(self, context):
        if not (os.path.exists(self.filepath) and os.path.isfile(self.filepath)):
            self.report({'WARNING'}, "File does not exist.")
            return {'CANCELLED'}
        if not (any(self.include_assets) or any(self.include_surfaces)):
            self.report({'WARNING'}, "Nothing to bake.")
            return {'CANCELLED'}

        mdataarr = parser.parse_library(self.filepath)

        loader.load_library(
            mdataarr=mdataarr,
            group_by_model=self.group_by_model,
            group_by_lod=self.group_by_lod,
            use_filetype_lods=self.use_filetype_lods,
            use_filetype_maps=self.use_filetype_maps,
            split_models=self.split_models,
            use_collections=self.use_collections,
            generate_previews=self.generate_previews,
            apply_transform=self.apply_transform,
            use_lods=[ui.lod_options[i] for i, e in enumerate(self.use_lods) if e],
            use_maps=[ui.map_options[i] for i, e in enumerate(self.use_maps) if e],
            include_assets=[self.include_assets_options[i] for i, e in enumerate(self.include_assets) if e],
            include_surfaces=[self.include_surfaces_options[i] for i, e in enumerate(self.include_surfaces) if e]
        )

        return {'FINISHED'}

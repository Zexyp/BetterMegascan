import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, BoolVectorProperty, EnumProperty

import os

from . import log
from .. import parser
from .. import loader
from .. import ui
from .base_importer import ModelImportProps, AssetImportProps


class BETTERMS_OT_bake_library(Operator, ModelImportProps, AssetImportProps):
    bl_idname = "betterms.bake_library"
    bl_label = "Bake Megascan Library"
    bl_options = {'PRESET'}

    filepath: StringProperty(
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
        default=(True,) * len(include_assets_options)
    )

    include_surfaces: BoolVectorProperty(
        name="Include Surfaces",
        size=len(include_surfaces_options),
        default=(True,) * len(include_surfaces_options)
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

        ui.library(layout, self)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def execute(self, context):
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
            use_lods=[ModelImportProps.lod_options[i] for i, e in enumerate(self.use_lods) if e],
            use_maps=[ModelImportProps.map_options[i] for i, e in enumerate(self.use_maps) if e],
            include_assets=[self.include_assets_options[i] for i, e in enumerate(self.include_assets) if e],
            include_surfaces=[self.include_surfaces_options[i] for i, e in enumerate(self.include_surfaces) if e],
            use_tags=self.use_tags,
            #semantic_tags_categories=[self.additional_tags_options[i] for i, e in enumerate(self.additional_tags) if e]
        )

        return {'FINISHED'}

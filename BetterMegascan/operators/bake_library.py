import bpy.props
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty, BoolVectorProperty, EnumProperty, CollectionProperty, IntProperty

from .base_importer import ModelImportProps, AssetImportProps
from .. import parser
from .. import loader
from .. import ui
from .. import preferences
from .. import spawn_logger

log = spawn_logger(__name__)


class BETTERMS_PG_bake_library_asset(bpy.types.PropertyGroup):
    selected: BoolProperty()
    id: StringProperty()
    name: StringProperty()
    type: StringProperty()

class BETTERMS_OT_bake_library(Operator, ModelImportProps, AssetImportProps):
    bl_idname = "betterms.bake_library"
    bl_label = "Bake Megascan Library"
    bl_options = {'PRESET'}

    filepath:  StringProperty(
        options={'HIDDEN'}
    )

    include_assets_options = [
        "3D asset", "3D plant",
    ]

    include_surfaces_options = [
        "surface", "decal", "atlas",
    ]

    def filter_update(self, context=None):
        for a in self.assets:
            a.selected = (
                (a.type in
                    [BETTERMS_OT_bake_library.include_assets_options[i] for i, e in enumerate(self.include_assets) if e])
                or
                (a.type in
                    [BETTERMS_OT_bake_library.include_surfaces_options[i] for i, e in enumerate(self.include_surfaces) if e])
            )

    include_assets: BoolVectorProperty(
        name="Include Assets",
        size=len(include_assets_options),
        default=(True,) * len(include_assets_options),
        update=filter_update
    )

    include_surfaces: BoolVectorProperty(
        name="Include Surfaces",
        size=len(include_surfaces_options),
        default=(True,) * len(include_surfaces_options),
        update=filter_update
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

    options_tab: EnumProperty(
        name='Tab',
        items=[
            ("SETTINGS", "Settings", ""),
            ("LIST", "List", ""),
        ]
    )

    assets: CollectionProperty(type=BETTERMS_PG_bake_library_asset)
    active_asset_index: IntProperty()

    # TODO: add presets for settings sections

    def __init__(self):
        self.mdataarr: list = []

    def draw(self, context):
        layout = self.layout

        ui.library(layout, self)

    def invoke(self, context, event):
        self.mdataarr = parser.parse_library(self.filepath)
        for mdata in self.mdataarr:
            item = self.assets.add()
            item.name = mdata.name
            item.id = mdata.id
            item.type = mdata.type
        self.filter_update()

        self.options_tab = 'SETTINGS'

        return context.window_manager.invoke_props_dialog(self, width=480)

    def execute(self, context):
        loadarr = [a for a in self.mdataarr if a.id in [e.id for e in self.assets if e.selected]]
        if not loadarr:
            self.report({'WARNING'}, "Nothing to bake.")
            return {'CANCELLED'}
        prefs = preferences.get(context)

        log.debug(f"loading {len(loadarr)} assets")

        loader.load_library(mdataarr=loadarr,
                            group_by_model=self.group_by_model,
                            group_by_lod=self.group_by_lod,
                            use_filetype_lods=self.use_filetype_lods,
                            use_filetype_maps=self.use_filetype_maps,
                            split_models=self.split_models,
                            use_collections=self.use_collections,
                            generate_previews=self.generate_previews,
                            apply_transform=self.apply_transform,
                            use_lods=[ModelImportProps.lod_options[i][0] for i, e in enumerate(self.use_lods) if e],
                            use_maps=[ModelImportProps.map_options[i][0] for i, e in enumerate(self.use_maps) if e],
                            include_assets=[self.include_assets_options[i] for i, e in enumerate(self.include_assets) if e],
                            include_surfaces=[self.include_surfaces_options[i] for i, e in enumerate(self.include_surfaces) if e],
                            use_tags=self.use_tags,
                            # semantic_tags_categories=[self.additional_tags_options[i] for i, e in enumerate(self.additional_tags) if e]
                            name_template_material=prefs.name_template_material,
                            name_template_map=prefs.name_template_map,
                            name_template_model=prefs.name_template_model,
                            name_template_group_asset=prefs.name_template_group_asset,
                            name_template_group_model=prefs.name_template_group_model)

        return {'FINISHED'}

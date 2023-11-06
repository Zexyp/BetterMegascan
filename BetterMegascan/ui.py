import bpy

from . import operators
from .operators.base_importer import ModelImportProps, SurfaceImportProps
from . import icons

include_assets_options_display_names = [
    "3D Asset", "3D Plant",
]

include_surfaces_options_display_names = [
    "Surface", "Decal", "Atlas",
]

additional_tags_options_display_names = [
    "Contains", "Theme", "Descriptive", "Collection", "Environment", "State", "Color", "Industry"
]

def group(layout, operator):
    col = layout.column(heading="Group", align=True)
    col.prop(operator, "group_by_model", text="Asset")
    col.prop(operator, "group_by_lod", text="LODs")


def lods(layout, operator):
    layout.prop(operator, "apply_transform")

    layout.separator()

    col = layout.column(heading="LODs", align=True)
    col.prop(operator, "use_lods", index=0, text=str(ModelImportProps.lod_options[0][1]))
    row = layout.row()
    for i in range(1, 5):
        row.prop(operator, "use_lods", index=i, text=str(ModelImportProps.lod_options[i][1]))
    row = layout.row()
    for i in range(5, 9):
        row.prop(operator, "use_lods", index=i, text=str(ModelImportProps.lod_options[i][1]))

    layout.prop(operator, "name_template_model")


def maps(layout, operator):
    layout.prop(operator, "force_pack_maps")

    layout.separator()

    col = layout.column(heading="Maps", align=True)
    for i in range(len(SurfaceImportProps.map_options)):
        col.prop(operator, "use_maps", index=i, text=SurfaceImportProps.map_options[i][1])

    layout.separator()

    layout.prop(operator, "name_template_material")
    layout.prop(operator, "name_template_map")


def filetype_lods(layout, operator):
    layout.prop(operator, "use_filetype_lods")


def filetype_maps(layout, operator):
    layout.prop(operator, "use_filetype_maps")


def library(layout, operator, mdataarr: list = []):
    layout.prop(operator, "options_tab", text="")

    if operator.options_tab == 'SETTINGS':
        # general
        layout.label(text="General")

        layout.prop(operator, "generate_previews")

        # tags
        layout.prop(operator, "use_tags", expand=True)
        # layout.label(text="Additional Tags")
        # box = layout.box()
        # box.enabled = self.use_tags
        # column = box.column(heading="Semantic")
        # for i, name in enumerate(ui.additional_tags_options_display_names):
        #    column.prop(self, "additional_tags", index=i, text=name)

        split = layout.split()

        # includes
        column = split.column(heading="Include Assets", align=True)
        for i, name in enumerate(include_assets_options_display_names):
            column.prop(operator, "include_assets", index=i, text=name)
        column = split.column(heading="Include Surfaces", align=True)
        for i, name in enumerate(include_surfaces_options_display_names):
            column.prop(operator, "include_surfaces", index=i, text=name)

        split = layout.split()

        # asset
        column = split.column()
        column.label(text="Asset")
        column.prop(operator, "use_collections")
        column.prop(operator, "split_models")
        box = column.box()
        column.enabled = any(operator.include_assets)
        filetype_lods(box, operator)
        group(box, operator)
        lods(box, operator)

        # surface
        column = split.column()
        column.label(text="Surface")
        box = column.box()
        filetype_maps(box, operator)
        maps(box, operator)
    elif operator.options_tab == 'LIST':
        for mdata in mdataarr:
            layout.label(text=mdata.name)


def menu_append_topbar_file_import(self, context):
    layout = self.layout
    layout.separator()
    layout.operator(operators.BETTERMS_OT_init_import_menu.bl_idname, icon_value=icons.icons["megascans"].icon_id)
    layout.operator(operators.BETTERMS_OT_import_library.bl_idname, icon='ASSET_MANAGER')


def register():
    bpy.types.TOPBAR_MT_file_import.append(menu_append_topbar_file_import)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_append_topbar_file_import)

def popup_message(message="", title="Message", icon='INFO'):
    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)

def popup_message_info(message):
    popup_message(message, "Info", 'INFO')

def popup_message_warn(message):
    popup_message(message, "Warning", 'ERROR')

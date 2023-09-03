import bpy

from . import operators
from . import icons

lod_options_display_names = [
    '0',
    '1',
    '2',
    '3',
    '4',
    '5',
    '6',
    '7',
    '8',
]

map_options_display_names = [
    "Albedo",
    "Cavity",
    "Curvature",
    "Gloss",
    "Normal",
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

    col = layout.column(heading="LODs", align=True)
    col.prop(operator, "use_lods", index=0, text=str(lod_options_display_names[0]))
    row = layout.row()
    for i in range(1, 5):
        row.prop(operator, "use_lods", index=i, text=str(lod_options_display_names[i]))
    row = layout.row()
    for i in range(5, 9):
        row.prop(operator, "use_lods", index=i, text=str(lod_options_display_names[i]))


def maps(layout, operator):
    col = layout.column(heading="Maps", align=True)
    for i, omap in enumerate(map_options_display_names):
        col.prop(operator, "use_maps", index=i, text=omap)


def filetype_lods(layout, operator):
    layout.prop(operator, "use_filetype_lods")


def filetype_maps(layout, operator):
    layout.prop(operator, "use_filetype_maps")


def menu_append_topbar_file_import(self, context):
    layout = self.layout
    layout.separator()
    layout.operator(operators.BETTERMS_OT_init_import_menu.bl_idname, icon_value=icons.icons["megascans"].icon_id)
    layout.operator(operators.BETTERMS_OT_bake_library.bl_idname, icon='ASSET_MANAGER')
    layout.separator()


def menu_append_assetbrowser_editor_menus(self, context):
    layout = self.layout
    layout.label(text="Import")


def register():
    bpy.types.TOPBAR_MT_file_import.append(menu_append_topbar_file_import)
    bpy.types.ASSETBROWSER_MT_editor_menus.append(menu_append_assetbrowser_editor_menus)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_append_topbar_file_import)
    bpy.types.ASSETBROWSER_MT_editor_menus.remove(menu_append_assetbrowser_editor_menus)

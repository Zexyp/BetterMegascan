# reference: scripts\addons\io_scene_fbx\__init__.py
import bpy

from ..operators import BETTERMS_OT_import_3dasset, BETTERMS_OT_import_surface


class BETTERMS_PT_import_collections(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Create Collections"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == bpy.ops.betterms.import_3dasset.idname()

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, "group_by_model")
        layout.prop(operator, "group_by_lod")


class BETTERMS_PT_import_filetypes(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "File Types"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname in [bpy.ops.betterms.import_3dasset.idname(),
                                      bpy.ops.betterms.import_surface.idname()]

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        if operator.bl_idname == bpy.ops.betterms.import_3dasset.idname():
            layout.prop(operator, "use_filetype_lods")
        layout.prop(operator, "use_filetype_maps")


class BETTERMS_PT_import_lods(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Models"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == bpy.ops.betterms.import_3dasset.idname()

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        col = layout.column(heading="LODs", align=True)
        col.prop(operator, "use_lods", index=0, text=str(BETTERMS_OT_import_3dasset.lod_options[0]))
        row = layout.row()
        for i in range(1, 5):
            row.prop(operator, "use_lods", index=i, text=str(BETTERMS_OT_import_3dasset.lod_options[i]))
        row = layout.row()
        for i in range(5, 9):
            row.prop(operator, "use_lods", index=i, text=str(BETTERMS_OT_import_3dasset.lod_options[i]))


class BETTERMS_PT_import_textures(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Textures"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname in [bpy.ops.betterms.import_3dasset.idname(),
                                      bpy.ops.betterms.import_surface.idname()]

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        col = layout.column(heading="Maps", align=True)
        for i, omap in enumerate(BETTERMS_OT_import_3dasset.map_options):
            col.prop(operator, "use_maps", index=i, text=omap)

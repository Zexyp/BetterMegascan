# reference: scripts\addons\io_scene_fbx\__init__.py
import bpy
from bpy.types import Panel

from abc import abstractmethod

from .. import ui

class BaseFilePanel(Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname in cls.draw_on()

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        self.draw_ui(layout, operator)

    @classmethod
    @abstractmethod
    def draw_on(cls) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def draw_ui(self, layout, operator):
        raise NotImplementedError


class BETTERMS_PT_import_collections(BaseFilePanel):
    bl_label = "Create Collections"

    def draw_on() -> list[str]:
        return [
            bpy.ops.betterms.import_model.idname()
        ]

    def draw_ui(self, layout, operator):
        ui.group(layout, operator)


class BETTERMS_PT_import_filetypes(BaseFilePanel):
    bl_label = "File Types"

    def draw_on() -> list[str]:
        return [
            bpy.ops.betterms.import_model.idname(),
            bpy.ops.betterms.import_surface.idname(),
            bpy.ops.betterms.import_brush.idname()
        ]

    def draw_ui(self, layout, operator):
        if operator.bl_idname == bpy.ops.betterms.import_model.idname():
            ui.filetype_lods(layout, operator)
        ui.filetype_maps(layout, operator)


class BETTERMS_PT_import_lods(BaseFilePanel):
    bl_label = "Models"

    def draw_on() -> list[str]:
        return [
            bpy.ops.betterms.import_model.idname()
        ]

    def draw_ui(self, layout, operator):
        ui.models(layout, operator)


class BETTERMS_PT_import_textures(BaseFilePanel):
    bl_label = "Textures"

    def draw_on() -> list[str]:
        return [
            bpy.ops.betterms.import_model.idname(),
            bpy.ops.betterms.import_surface.idname()
        ]

    def draw_ui(self, layout, operator):
        ui.maps(layout, operator)

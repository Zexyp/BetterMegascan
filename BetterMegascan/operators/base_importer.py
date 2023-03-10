import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, EnumProperty, BoolVectorProperty, BoolProperty

import os
import traceback
from abc import abstractmethod

from .. import parser
from .. import loader
from .. import ui

from . import log


class BaseImporter(Operator, ImportHelper):
    filter_glob: StringProperty(
        default="*.zip;*.json",
        options={'HIDDEN'}
    )

    def __init__(self):
        self.mdata: parser.structures.MegascanData = None
        self.dir_path: str = None

    def draw(self, context):
        pass

    def execute(self, context):
        if not self.filepath:
            return {'CANCELLED'}

        log.debug(f"selected {self.filepath}")

        try:
            ext = os.path.splitext(self.filepath)[1]
            match ext:
                case ".zip":
                    self.mdata = parser.parse_zip(self.filepath)
                    self.dir_path = self.filepath
                case ".json":
                    self.mdata = parser.parse(self.filepath)
                    self.dir_path = os.path.dirname(self.filepath)
                case _:
                    log.debug(f"unexpected extension {ext}")
                    self.report({"ERROR"}, "Unexpected file extension.")
                    return {'CANCELLED'}
        except parser.InvalidStructureError:
            log.debug(traceback.format_exc())
            self.report({'ERROR'}, "Structure was not recognized.")
            return {'CANCELLED'}
        assert self.mdata

        if self.mdata.type not in self.able_to_import:
            self.report({'WARNING'}, "Invalid asset type.")
            return {'CANCELLED'}

        return self.finish_execute(context)

    @abstractmethod
    def finish_execute(self, context) -> set:
        raise NotImplementedError


class SurfaceImportProps:
    use_filetype_maps: EnumProperty(
        name="Textures",
        description="Determines which image filetype will be used",
        items=(
            ('PREFER_EXR', "Prefer EXR", "Fallback is JPEG"),
            ('JPEG', "JPEG only", "(.jpeg/.jpg)"),
            ('EXR', "EXR only", "(.exr)")
        ),
        default='PREFER_EXR',
    )

    use_maps: BoolVectorProperty(
        name="Import Maps",
        description="Select all PBR maps to look for",
        size=len(ui.map_options),
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


class AssetImportProps(SurfaceImportProps):
    use_filetype_lods: EnumProperty(
        name="Models",
        description="Determines which model filetype will be used",
        items=(
            ('FBX', "FBX", "Filmbox (.fbx)"),
            ('OBJ', "OBJ", "Wavefront (.obj)"),
            ('ABC', "ABC", "Alembic (.abc)")
        ),
        default='FBX',
    )

    use_lods: BoolVectorProperty(
        name="Import LODs",
        description="Select all LODs to look for",
        size=len(ui.lod_options),
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

    group_by_model: BoolProperty(
        name="Group Asset",
        description="Create a collection for the asset",
        default=True,
    )

    group_by_lod: BoolProperty(
        name="Group LODs",
        description="Create a collection for each model's LODs",
        default=False,
    )

    apply_transform: BoolProperty(
        name="Apply Transform",
        description="Models might get rotated to meet the desired orientation. This option will afterwards apply the transformation",
        default=False,
    )
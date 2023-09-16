from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, EnumProperty, BoolVectorProperty, BoolProperty

import os
import traceback
from abc import abstractmethod

from .. import parser

from . import log


class AssetImportProps:
    # TODO: better integration in the loader - make use of grouping

    mark_asset: BoolProperty(
        name="Mark Asset",
        description="Mark this megascan as asset",
        default=False,
    )

    use_tags: BoolProperty(
        name="Tags",
        description="Apply asset tags to asset in library",
        default=True,
    )

    #additional_tag_options = [
    #    "contains", "theme", "descriptive", "collection", "environment", "state", "color", "industry"
    #]

    #additional_tags: BoolVectorProperty(
    #   name="Additional Tags",
    #   size=len(additional_tag_options),
    #   default=(False,) * len(additional_tag_options)
    #)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "mark_asset")
        col = layout.column()
        col.enabled = self.mark_asset
        col.prop(self, "use_tags")


class BaseImporter(Operator, ImportHelper):
    filter_glob: StringProperty(
        default="*.zip;*.json",
        options={'HIDDEN'}
    )

    def __init__(self):
        self.mdata: parser.structures.MegascanData | None = None
        self.dir_path: str | None = None

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
    force_pack_maps: BoolProperty(
        name="Force Pack Maps",
        description="Force packing of maps into blend file (idc if you drive explodes)",
        default=False
    )

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

    use_maps: BoolVectorProperty(
        name="Import Maps",
        description="Select all PBR maps to look for",
        size=len(map_options),
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


class ModelImportProps(SurfaceImportProps):
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

    use_lods: BoolVectorProperty(
        name="Import LODs",
        description="Select all LODs to look for",
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

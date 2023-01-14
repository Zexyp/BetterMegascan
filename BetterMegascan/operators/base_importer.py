import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty

import os
import traceback
from abc import ABCMeta, abstractmethod

from .. import parser
from .. import loader

from . import log


class BaseImporter(Operator, ImportHelper):
    # ImportHelper mixin class uses this
    filename_ext = ".zip"
    filter_glob: StringProperty(
        default="*.zip",
        options={'HIDDEN'}
    )

    def __init__(self):
        self.mdata: parser.structures.MegascanData = None
        self.selected_filepath: str = None

    def draw(self, context):
        pass

    def execute(self, context):
        if not self.filepath:
            return {'CANCELLED'}

        self.selected_filepath = self.filepath

        if not os.path.exists(self.selected_filepath):
            selected_filepath = os.path.dirname(self.selected_filepath)

        log.debug(f"selected {self.selected_filepath}")

        try:
            if os.path.isfile(self.selected_filepath):
                self.mdata = parser.parse_zip(self.selected_filepath)
            if os.path.isdir(self.selected_filepath):
                self.mdata = parser.parse(self.selected_filepath)
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

import os

from .base_importer import BaseImporter, SurfaceImportProps, AssetImportProps
from .. import loader

from . import log


class BETTERMS_OT_import_surface(BaseImporter, SurfaceImportProps, AssetImportProps):
    bl_idname = "betterms.import_surface"
    bl_label = "Surface"
    bl_description = "Load material and its textures"
    bl_options = {'UNDO', 'PRESET'}

    able_to_import = ["surface", "decal", "atlas", "3D plant", "3D asset"]

    def draw(self, context):
        AssetImportProps.draw(self, context)

    def finish_execute(self, context) -> set:
        load_ret = loader.load_material(self.mdata,
                                        self.dir_path,
                                        use_filetype_maps=self.use_filetype_maps,
                                        use_maps=[SurfaceImportProps.map_options[i][0] for i, e in enumerate(self.use_maps) if e],
                                        pack_maps=os.path.isfile(self.dir_path) if not self.force_pack_maps else True,
                                        mark_asset=self.mark_asset,
                                        use_tags=self.use_tags,
                                        name_template_material=self.name_template_material,
                                        name_template_map=self.name_template_map)

        # info
        self.report({'INFO'}, f"Loaded {len(load_ret['images'])} maps")
        return {'FINISHED'}

import os

from .base_importer import BaseImporter, ModelImportProps, AssetImportProps
from .. import loader
from .. import preferences

'''
map_options_names = [
    "Albedo",
    "Cavity",
    "Curvature",
    "Gloss",
    "Normal",
    "Normal Bump",
    "Normal Object",
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
'''


class BETTERMS_OT_import_model(BaseImporter, ModelImportProps, AssetImportProps):
    bl_idname = "betterms.import_model"
    bl_label = "Model"
    bl_description = "Load model with material and its textures"
    bl_options = {'UNDO', 'PRESET'}

    able_to_import = ["3D asset", "3D plant"]

    def draw(self, context):
        AssetImportProps.draw(self, context)

    def finish_execute(self, context) -> set:
        if self.use_filetype_lods == 'ABC':
            self.report({'WARNING'}, "Alembic files are not supported.")
            # raise NotImplemented
            return {'CANCELLED'}

        prefs = preferences.get(context)

        load_ret = loader.load_model(self.mdata,
                                     self.dir_path,
                                     group_by_model=self.group_by_model,
                                     group_by_lod=self.group_by_lod,
                                     use_filetype_lods=self.use_filetype_lods,
                                     use_filetype_maps=self.use_filetype_maps,
                                     use_lods=[ModelImportProps.lod_options[i][0] for i, e in enumerate(self.use_lods) if e],
                                     use_maps=[ModelImportProps.map_options[i][0] for i, e in enumerate(self.use_maps) if e],
                                     pack_maps=os.path.isfile(self.dir_path) if not self.force_pack_maps else True,
                                     apply_transform=self.apply_transform,
                                     mark_asset=self.mark_asset,
                                     use_tags=self.use_tags,
                                     name_template_model=prefs.name_template_model,
                                     name_template_material=prefs.name_template_material,
                                     name_template_map=prefs.name_template_map,
                                     name_template_group_asset=prefs.name_template_group_asset,
                                     name_template_group_model=prefs.name_template_group_model)

        for o in load_ret["objects"]:
            o.select_set(True)

        # info
        self.report({'INFO'}, f"Loaded {len(load_ret['objects'])} models and {len(load_ret['images'])} maps")
        return {'FINISHED'}

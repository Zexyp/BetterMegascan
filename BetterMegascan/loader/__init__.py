"""
yes, it is a bit messy
"""

import bpy

import os
import string

from .. import parser
from .. import spawn_logger
from ..parser.structures import MegascanData, MegascanMap

from .node_spawner import NodeSpawner

log = spawn_logger(__name__)


# utility function
def add_asset(asset, mdata, generate_previews: bool, use_tags: bool, semantic_tags_categories: list[str] = []):
    # add
    asset.asset_mark()

    # path
    # TODO: catalogs

    # optional
    if generate_previews:
        asset.asset_generate_preview()
    if use_tags:
        for tag in mdata.tags:
            asset.asset_data.tags.new(tag, skip_if_exists=True)

        for cat in semantic_tags_categories:
            if cat in mdata.semanticTags:
                for tag in mdata.semanticTags[cat]:
                    asset.asset_data.tags.new(tag, skip_if_exists=True)


def load_model(mdata: MegascanData,
               filepath: str,
               group_by_model: bool,
               group_by_lod: bool,
               use_filetype_lods: str,
               use_filetype_maps: str,
               use_lods: list[int] | tuple[int] | set[int],
               use_maps: list[str] | tuple[str] | set[str],
               pack_maps: bool,
               apply_transform: bool = False,
               mark_asset: bool = False,
               use_tags: bool = False,
               name_template_model: str = None,
               name_template_material: str = None,
               name_template_map: str = None,
               name_template_group_asset: str = None,
               name_template_group_model: str = None):

    def add_collection(name):
        collection = bpy.data.collections.new(name)
        bpy.context.collection.children.link(collection)
        return collection

    def activate_collection(collection):
        layer = layer_collection_recursive_search(bpy.context.view_layer.layer_collection, collection.name)
        prev = bpy.context.view_layer.active_layer_collection
        bpy.context.view_layer.active_layer_collection = layer
        return prev

    def layer_collection_recursive_search(collection, name):
        if collection.name == name:
            return collection

        found = None
        for child in collection.children:
            found = layer_collection_recursive_search(child, name)
            if found:
                return found

    loaded_objects = []

    def load_model(mmodel):
        log.debug(f"loading model {mmodel.name}")

        varianttype = None
        match use_filetype_lods:
            case 'FBX':
                varianttype = 'application/x-fbx'
            case 'OBJ':
                varianttype = 'application/x-obj'
            case 'ABC':
                varianttype = 'application/x-abc'
            case _:
                assert False
        assert varianttype

        # extract files
        for keylod in mmodel.lods:
            # filter lods
            if keylod not in use_lods:
                continue

            if varianttype not in mmodel.lods[keylod]:
                continue

            fp = mmodel.lods[keylod][varianttype].filepath
            fp = parser.ensure_file(filepath, fp)

            match use_filetype_lods:
                case 'FBX':
                    # use fbx operator
                    bpy.ops.import_scene.fbx(filepath=fp, bake_space_transform=apply_transform)
                case 'OBJ':
                    # use obj operator
                    bpy.ops.import_scene.obj(filepath=fp, use_split_objects=True, use_split_groups=True,
                                             global_clamp_size=1.0)
                case _:
                    assert False

            for o in bpy.context.selected_objects:
                o.name = string.Template(name_template_model).safe_substitute(name=mdata.name, id=mdata.id, lod=keylod, model=mmodel.name)

            loaded_objects.extend(bpy.context.selected_objects)

    def load_models(mdata):
        cols = [] if len(mdata.models) else None
        for keymodel in mdata.models:
            # create new collection for model and change collection context
            prevmodelcol = None

            mmodel = mdata.models[keymodel]
            if group_by_lod:
                col = add_collection(keymodel)
                if name_template_group_model:
                    col.name = string.Template(name_template_group_model).safe_substitute(name=mdata.name, id=mdata.id, model=mmodel.name)
                prevmodelcol = activate_collection(col)
                cols.append(col)

            load_model(mmodel)

            # change back collection context
            if group_by_lod:
                activate_collection(prevmodelcol)

        return {"model_collections": cols}

    log.debug(f"loading asset {mdata.name}")

    # create new collection for asset and change collection context
    prevcol = None
    newcol = None
    if group_by_model:
        newcol = add_collection(mdata.name)
        if name_template_group_asset:
            newcol.name = string.Template(name_template_group_asset).safe_substitute(name=mdata.name, id=mdata.id)
        prevcol = activate_collection(newcol)

    mod_ret = load_models(mdata)

    # change back collection context
    if group_by_model:
        activate_collection(prevcol)

    mat_ret = load_material(mdata, filepath,
                            use_filetype_maps=use_filetype_maps,
                            use_maps=use_maps,
                            pack_maps=pack_maps,
                            name_template_material=name_template_material,
                            name_template_map=name_template_map)

    for o in loaded_objects:
        if not o.data:
            continue
        while len(o.data.materials):
            bpy.data.materials.remove(o.data.materials.pop())
        o.data.materials.append(mat_ret["material"])

        # mark individualy as asset
        if mark_asset:
            add_asset(o, mdata, use_tags=use_tags, generate_previews=True)

    ret = {
        "objects": loaded_objects,
        "collection": newcol,
    }
    ret.update(mod_ret)
    ret.update(mat_ret)
    return ret


def load_material(mdata: MegascanData,
                  filepath: str,
                  use_filetype_maps: str,
                  use_maps: list[str] | tuple[str] | set[str],
                  pack_maps: bool,
                  mark_asset: bool = False,
                  use_tags: bool = False,
                  name_template_material: str = None,
                  name_template_map: str = None):

    loaded_images = {}

    def load_maps(mdata):
        pass
        for mapkey in mdata.maps:
            # filter maps
            try:
                if mapkey not in use_maps:
                    continue
            except ValueError:
                continue

            mmap = mdata.maps[mapkey]
            image = load_map(mmap,
                             filepath=filepath,
                             use_filetype_maps=use_filetype_maps,
                             pack_maps=pack_maps)
            if image is not None:
                if name_template_map:
                    image.name = string.Template(name_template_map).safe_substitute(name=mdata.name, id=mdata.id, type=mmap.type)

                loaded_images[mmap.type] = image

    # prepare maps
    load_maps(mdata)

    # init material
    log.debug("creating material")
    material = bpy.data.materials.new(f"{mdata.name}_{mdata.id}")
    if name_template_material:
        material.name = string.Template(name_template_material).safe_substitute(name=mdata.name, id=mdata.id)
    material.use_nodes = True
    nodes = material.node_tree.nodes

    spawner = NodeSpawner(material.node_tree)

    # prepare mapping
    mappingnode = None
    if mdata.type not in ["3d", "3dplant"]:
        mappingnode = spawner.create_generic_node("ShaderNodeMapping", (-1950, 0))
        mappingnode.vector_type = 'TEXTURE'
        texcoordnode = spawner.create_generic_node("ShaderNodeTexCoord", (-2150, -200))
        spawner.connect_nodes(mappingnode, texcoordnode, "Vector", "UV")

    def create_texture_node(map_type: str, pos: tuple, colorspace: str = "Non-Color", connect_to=None,
                            connect_at: str = ""):
        texnode = spawner.create_generic_node('ShaderNodeTexImage', pos)
        texnode.image = loaded_images[map_type]
        texnode.show_texture = True
        texnode.image.colorspace_settings.name = colorspace

        if map_type in ["albedo", "specular", "translucency"] and texnode.image.file_format == 'OPEN_EXR':
            texnode.image.colorspace_settings.name = "Linear"

        if connect_to:
            spawner.connect_nodes(connect_to, texnode, connect_at, 0)

        if mdata.type not in ["3d", "3dplant"]:
            spawner.connect_nodes(texnode, mappingnode, "Vector", "Vector")

        return texnode

    def create_texture_multiply_node(a_map_type: str, b_map_type: str, pos: tuple, a_pos: tuple, b_pos: tuple,
                                     a_colorspace: str = "Non-Color", b_colorspace: str = "Non-Color", connect_to=None,
                                     connect_at: str = None):
        multnode = spawner.create_generic_node('ShaderNodeMixRGB', pos)
        multnode.blend_type = 'MULTIPLY'
        texnodeb = create_texture_node(a_map_type, a_pos, a_colorspace, multnode, "Color1")
        texnodea = create_texture_node(b_map_type, b_pos, b_colorspace, multnode, "Color2")

        if connect_to:
            spawner.connect_nodes(connect_to, multnode, connect_at)

        return multnode

    parentnodename = "Principled BSDF"
    outputnodename = "Material Output"
    parentnode = nodes.get(parentnodename)
    # outnodename = "Material Output"

    # nodes[parentName].distribution = 'MULTI_GGX'
    # nodes[parentName].inputs["Metallic"].default_value
    # nodes[.parentName].inputs["IOR"].default_value
    # nodes[parentName].inputs["Specular"].default_value
    # nodes[parentName].inputs["Clearcoat"].default_value

    # ["sRGB", "Non-Color", "Linear"]

    # albedo is last so the correct texture is selected

    if "metalness" in loaded_images:
        create_texture_node("metalness", (-1150, 200), "Non-Color", parentnode, "Metallic")

    if "roughness" in loaded_images:
        create_texture_node("roughness", (-1150, -60), "Non-Color", parentnode, "Roughness")
    elif "gloss" in loaded_images:
        glossnode = create_texture_node("gloss", (-1150, -60))
        invnode = spawner.create_generic_node("ShaderNodeInvert", (-250, 60))

        spawner.connect_nodes(invnode, glossnode, "Color", "Color")
        spawner.connect_nodes(parentnode, invnode, "Roughness")

    if "opacity" in loaded_images:
        create_texture_node("opacity", (-1550, -160), "Non-Color", parentnode, "Alpha")
        material.blend_method = 'HASHED'

    if "translucency" in loaded_images:
        create_texture_node("translucency", (-1550, -420), "sRGB", parentnode, "Transmission")
    elif "transmission" in loaded_images:
        create_texture_node("transmission", (-1550, -420), "Non-Color", parentnode, "Transmission")

    # avoid bump if is high poly - not implemented
    if "normal" in loaded_images and "bump" in loaded_images:
        bumpnode = spawner.create_generic_node("ShaderNodeBump", (-250, -170))
        bumpnode.inputs["Strength"].default_value = 0.1

        normalnode = spawner.create_generic_node("ShaderNodeNormalMap", (-640, -400))

        texnormnode = create_texture_node("normal", (-1150, -580), connect_to=normalnode, connect_at="Color")
        texbumpnode = create_texture_node("bump", (-640, -130), connect_to=bumpnode, connect_at="Height")

        spawner.connect_nodes(bumpnode, normalnode, "Normal", "Normal")

        spawner.connect_nodes(parentnode, bumpnode, "Normal")

    elif "normal" in loaded_images:
        normalnode = spawner.create_generic_node("ShaderNodeNormalMap", (-250, -170))

        texnormnode = create_texture_node("normal", (-640, -207), connect_to=normalnode, connect_at="Color")

        spawner.connect_nodes(parentnode, normalnode, "Normal")

    elif "bump" in loaded_images:
        bumpnode = spawner.create_generic_node("ShaderNodeBump", (-250, -170))
        bumpnode.inputs["Strength"].default_value = 0.1

        texbumbnode = create_texture_node("bump", (-640, -207), connect_to=bumpnode, connect_at="Height")

        spawner.connect_nodes(parentnode, bumpnode, "Normal")

    # avoid displacement if is high poly - not implemented
    if "displacement" in loaded_images:
        if bpy.context.scene.cycles.feature_set == 'EXPERIMENTAL':
            dispnode = spawner.create_generic_node("ShaderNodeDisplacement", (10, -400))
            dispnode.inputs["Scale"].default_value = 0.1
            dispnode.inputs["Midlevel"].default_value = 0

            splitnode = spawner.create_generic_node("ShaderNodeSeparateRGB", (-250, -499))
            # Import normal map and normal map node setup.
            dispmap = create_texture_node("displacement", (-640, -740))

            spawner.connect_nodes(splitnode, dispmap, "Image", "Color")
            spawner.connect_nodes(dispnode, splitnode, "Height", "R")

            spawner.connect_nodes(nodes.get(outputnodename), dispnode, "Displacement", "Displacement")
            material.cycles.displacement_method = 'BOTH'
        else:
            pass

    # albedo map as last so the selected texture is correct
    if "albedo" in loaded_images:
        if "ao" in loaded_images:
            create_texture_multiply_node("albedo", "ao", (-250, 320),
                                              (-640, 460), (-640, 200),
                                              "sRGB", "Non-Color",
                                              parentnode, "Base Color")
        else:
            create_texture_node("albedo", (-640, 420), "sRGB", parentnode, "Base Color")

    if mark_asset:
        add_asset(material, mdata, use_tags=use_tags, generate_previews=True)

    return {"material": material, "images": loaded_images}


def load_brush(mdata: MegascanData,
               filepath: str,
               use_filetype_maps: str,
               pack_maps: bool,
               name_template_map: str = None,
               name_template_brush: str = None):

    log.debug("loading brush")

    def load_if_exists(map_type):
        if map_type in mdata.maps:
            mmap = mdata.maps[map_type]
            image = load_map(mmap,
                                   filepath,
                                   use_filetype_maps=use_filetype_maps,
                                   pack_maps=pack_maps)
            image.name = string.Template(name_template_map).safe_substitute(name=mdata.name, id=mdata.id, type=mmap.type)
            return image
        return None

    texture_name = string.Template(name_template_brush).safe_substitute(name=mdata.name, id=mdata.id)

    texture = None
    if brush_image := load_if_exists("brush"):
        texture = bpy.data.textures.new(texture_name, type='IMAGE')
        texture.image = brush_image
    else:
        albedo_image = load_if_exists("albedo")
        opacity_image = load_if_exists("opacity")

        assert albedo_image and opacity_image

        texture = bpy.data.textures.new(texture_name, type='NONE')
        texture.use_nodes = True

        log.debug("quick lazy fix ahead")
        texture.node_tree.nodes.remove(texture.node_tree.nodes["Checker"])

        spawner = NodeSpawner(texture.node_tree)

        nodecombine = spawner.create_generic_node("TextureNodeCombineColor", (-240, 0))
        nodeseparate = spawner.create_generic_node("TextureNodeSeparateColor", (-480, 0))

        spawner.connect_nodes(texture.node_tree.nodes["Output"], nodecombine, "Color")

        spawner.connect_nodes(nodecombine, nodeseparate, "Red", "Red")
        spawner.connect_nodes(nodecombine, nodeseparate, "Green", "Green")
        spawner.connect_nodes(nodecombine, nodeseparate, "Blue", "Blue")

        nodealbedo = spawner.create_generic_node("TextureNodeImage", (-720, 0))
        nodealbedo.image = albedo_image
        nodeopacity = spawner.create_generic_node("TextureNodeImage", (-720, -120))
        nodeopacity.image = opacity_image

        spawner.connect_nodes(nodeseparate, nodealbedo, "Color", "Image")
        spawner.connect_nodes(nodecombine, nodeopacity, "Alpha", "Image")


    return {"texture": texture}


def load_map(mmap: MegascanMap,
             filepath: str,
             use_filetype_maps: str,
             pack_maps: bool):
    log.debug(f"loading map {mmap.type}")

    varianttype = None
    match use_filetype_maps:
        case 'PREFER_EXR':
            varianttype = 'image/x-exr' if 'image/x-exr' in mmap.lods[0] else 'image/jpeg'
        case 'EXR':
            varianttype = 'image/x-exr'
        case 'JPEG':
            varianttype = 'image/jpeg'
        case _:
            assert False
    assert varianttype
    #                                                                                eyo the pep limit is right here -->                      but mine is here -->
    if varianttype in mmap.lods[0]:
        image = bpy.data.images.load(
            parser.ensure_file(filepath, mmap.lods[0][varianttype].filepath))
        if pack_maps:
            image.pack()
        return image
    return None


def load_library(mdataarr: list[MegascanData],
                 group_by_model: bool,
                 group_by_lod: bool,
                 use_filetype_lods: str,
                 use_filetype_maps: str,
                 use_lods: list[int] | tuple[int] | set[int],
                 use_maps: list[str] | tuple[str] | set[str],
                 include_assets: list[str] | tuple[str] | set[str],
                 include_surfaces: list[str] | tuple[str] | set[str],
                 split_models: bool,
                 use_collections: bool,
                 generate_previews: bool,
                 apply_transform: bool = False,
                 use_tags: bool = False,
                 semantic_tags_categories: list[str] = [],
                 name_template_material: str = None,
                 name_template_map: str = None,
                 name_template_model: str = None,
                 name_template_group_asset: str = None,
                 name_template_group_model: str = None):

    # initialize progress bar
    wm = bpy.context.window_manager
    progress = 0
    wm.progress_begin(progress, len(mdataarr))

    for mdata in [d for d in mdataarr if
                  d.type in include_assets]:
        dirpath = os.path.dirname(mdata.path)

        ret = load_model(
            mdata=mdata,
            filepath=dirpath,
            group_by_model=group_by_model,
            group_by_lod=group_by_lod,
            use_filetype_lods=use_filetype_lods,
            use_filetype_maps=use_filetype_maps,
            use_lods=use_lods,
            use_maps=use_maps,
            pack_maps=False,  # this would let your lovely blender pc explode
            apply_transform=apply_transform,
            name_template_model=name_template_model,
            name_template_group_asset=name_template_group_asset,
            name_template_group_model=name_template_group_model)

        # decide the way to split models
        if split_models:
            if use_collections and ret["model_collections"]:
                [add_asset(c, mdata, use_tags=use_tags, generate_previews=generate_previews, semantic_tags_categories=semantic_tags_categories) for c in ret["model_collections"]]
            else:
                [add_asset(o, mdata, use_tags=use_tags, generate_previews=generate_previews, semantic_tags_categories=semantic_tags_categories) for o in ret["objects"]]
        else:
            if use_collections and ret["collection"]:
                add_asset(ret["collection"], mdata, use_tags=use_tags, generate_previews=generate_previews, semantic_tags_categories=semantic_tags_categories)
            else:
                [add_asset(o, mdata, use_tags=use_tags, generate_previews=generate_previews, semantic_tags_categories=semantic_tags_categories) for o in ret["objects"]]

        # hide
        hidden = False
        if ret["collection"]:
            ret["collection"].hide_viewport = True
            hidden = True
        if ret["model_collections"] and not hidden:
            for c in ret["model_collections"]:
                c.hide_viewport = True
            hidden = True
        if not hidden:
            for o in ret["objects"]:
                o.hide_viewport = True
            hidden = True

        # update progress
        progress += 1
        wm.progress_update(progress)

    for mdata in [d for d in mdataarr if
                  d.type in include_surfaces]:
        dirpath = os.path.dirname(mdata.path)

        ret = load_material(
            mdata=mdata,
            filepath=dirpath,
            use_filetype_maps=use_filetype_maps,
            use_maps=use_maps,
            pack_maps=False,
            name_template_material=name_template_material,
            name_template_map=name_template_map)

        add_asset(ret["material"], mdata, use_tags=use_tags, generate_previews=generate_previews, semantic_tags_categories=semantic_tags_categories)

        # update progress
        progress += 1
        wm.progress_update(progress)

    # finish progress
    wm.progress_end()

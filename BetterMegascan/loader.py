"""
yes, it is a bit messy
"""

import bpy

import os

from . import parser
from . import spawn_logger

log = spawn_logger(__name__)


def load_asset(mdata: parser.structures.MegascanData,
               filepath: str,
               group_by_model: bool,
               group_by_lod: bool,
               use_filetype_lods: str,
               use_filetype_maps: str,
               use_lods: list[int] | tuple[int] | set[int],
               use_maps: list[str] | tuple[str] | set[str],
               pack_maps: bool,
               apply_transform: bool = False):
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

            loaded_objects.extend(bpy.context.selected_objects)

    def load_models(mdata):
        cols = [] if len(mdata.models) else None
        for keymodel in mdata.models:
            # create new collection for model and change collection context
            prevmodelcol = None
            if group_by_lod:
                col = add_collection(keymodel)
                prevmodelcol = activate_collection(col)
                cols.append(col)

            load_model(mdata.models[keymodel])

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
        prevcol = activate_collection(newcol)

    mod_ret = load_models(mdata)

    # change back collection context
    if group_by_model:
        activate_collection(prevcol)

    mat_ret = load_material(mdata, filepath,
                             use_filetype_maps=use_filetype_maps,
                             use_maps=use_maps,
                             pack_maps=pack_maps)

    for o in loaded_objects:
        while len(o.data.materials):
            bpy.data.materials.remove(o.data.materials.pop())
        o.data.materials.append(mat_ret["material"])

    ret = {
        "objects": loaded_objects,
        "collection": newcol,
    }
    ret.update(mod_ret)
    ret.update(mat_ret)
    return ret


def load_material(mdata: parser.structures.MegascanData,
                  filepath: str,
                  use_filetype_maps: str,
                  use_maps: list[str] | tuple[str] | set[str],
                  pack_maps: bool):

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
                loaded_images[mmap.type] = image

    load_maps(mdata)

    log.debug("creating material")
    material = bpy.data.materials.new(f"{mdata.name}_{mdata.id}")
    material.use_nodes = True
    nodes = material.node_tree.nodes

    def create_generic_node(type, pos: tuple = None):
        node = material.node_tree.nodes.new(type=type)
        if pos:
            node.location = pos

        return node

    # order is from node input receiver to input provider node
    def connect_nodes(node_a, node_b, in_a: int | str = 0, out_b: int | str = 0):
        material.node_tree.links.new(node_a.inputs[in_a], node_b.outputs[out_b])

    def create_texture_node(map_type: str, pos: tuple, colorspace: str = "Non-Color", connect_to=None,
                            connect_at: str = ""):
        texnode = create_generic_node('ShaderNodeTexImage', pos)
        texnode.image = loaded_images[map_type]
        texnode.show_texture = True
        texnode.image.colorspace_settings.name = colorspace

        if map_type in ["albedo", "specular", "translucency"] and texnode.image.file_format == 'OPEN_EXR':
            texnode.image.colorspace_settings.name = "Linear"

        if connect_to:
            connect_nodes(connect_to, texnode, connect_at, 0)

        # if is_cycles and mdata.type not in ["3d", "3dplant"]:
        #    .mat.node_tree.links.new(textureNode.inputs["Vector"], .mappingNode.outputs["Vector"])

        return texnode

    def create_texture_multiply_node(a_map_type: str, b_map_type: str, pos: tuple, a_pos: tuple, b_pos: tuple,
                                     a_colorspace: str = "Non-Color", b_colorspace: str = "Non-Color", connect_to=None,
                                     connect_at: str = None):
        multnode = create_generic_node('ShaderNodeMixRGB', pos)
        multnode.blend_type = 'MULTIPLY'
        texnodeb = create_texture_node(a_map_type, a_pos, a_colorspace, multnode, "Color1")
        texnodea = create_texture_node(b_map_type, b_pos, b_colorspace, multnode, "Color2")

        if connect_to:
            connect_nodes(connect_to, multnode, connect_at)

        return multnode

    parentnodename = "Principled BSDF"
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
        invnode = create_generic_node("ShaderNodeInvert", (-250, 60))

        connect_nodes(invnode, glossnode, "Color", "Color")
        connect_nodes(parentnode, invnode, "Roughness")

    if "opacity" in loaded_images:
        create_texture_node("opacity", (-1550, -160), "Non-Color", parentnode, "Alpha")
        material.blend_method = 'HASHED'

    if "translucency" in loaded_images:
        create_texture_node("translucency", (-1550, -420), "sRGB", parentnode, "Transmission")
    elif "transmission" in loaded_images:
        create_texture_node("transmission", (-1550, -420), "Non-Color", parentnode, "Transmission")

    # avoid bump if is high poly - not implemented
    if "normal" in loaded_images and "bump" in loaded_images:
        bumpnode = create_generic_node("ShaderNodeBump", (-250, -170))
        bumpnode.inputs["Strength"].default_value = 0.1

        normalnode = create_generic_node("ShaderNodeNormalMap", (-640, -400))

        texnormnode = create_texture_node("normal", (-1150, -580), connect_to=normalnode, connect_at="Color")
        texbumpnode = create_texture_node("bump", (-640, -130), connect_to=bumpnode, connect_at="Height")

        connect_nodes(bumpnode, normalnode, "Normal", "Normal")

        connect_nodes(parentnode, bumpnode, "Normal")

    elif "normal" in loaded_images:
        normalnode = create_generic_node("ShaderNodeNormalMap", (-250, -170))

        texnormnode = create_texture_node("normal", (-640, -207), connect_to=normalnode, connect_at="Color")

        connect_nodes(parentnode, normalnode, "Normal")

    elif "bump" in loaded_images:
        bumpnode = create_generic_node("ShaderNodeBump", (-250, -170))
        bumpnode.inputs["Strength"].default_value = 0.1

        texbumbnode = create_texture_node("bump", (-640, -207), connect_to=bumpnode, connect_at="Height")

        connect_nodes(parentnode, bumpnode, "Normal")

    # if "displacement" in .loaded_images and is not high poly:
    #    .create_displacement_setup(True)

    if "albedo" in loaded_images:
        if "ao" in loaded_images:
            create_texture_multiply_node("albedo", "ao", (-250, 320),
                                              (-640, 460), (-640, 200),
                                              "sRGB", "Non-Color",
                                              parentnode, "Base Color")
        else:
            create_texture_node("albedo", (-640, 420), "sRGB", parentnode, "Base Color")

    return {"material": material, "images": loaded_images}


def load_brush(mdata: parser.structures.MegascanData,
               filepath: str,
               use_filetype_maps: str,
               pack_maps: bool):

    log.debug("loading brush")

    key = None
    if "brush" in mdata.maps:
        key = "brush"
    elif "opacity" in mdata.maps:
        key = "opacity"

    texture = None
    if key is not None:
        image = load_map(mdata.maps[key],
                         filepath,
                         use_filetype_maps=use_filetype_maps,
                         pack_maps=pack_maps)
        if image is not None:
            texture = bpy.data.textures.new(f"Brush_{mdata.name}_{mdata.id}", type='IMAGE')
            texture.image = image
        else:
            log.debug("map for brush was not found")

    return {"texture": texture}


def load_map(mmap: parser.structures.MegascanMap,
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
            raise Exception
    assert varianttype

    if varianttype in mmap.lods[0]:                                                # eyo the pep limit is right here -->                      but mine is here -->
        image = bpy.data.images.load(
            parser.ensure_file(filepath, mmap.lods[0][varianttype].filepath))
        if pack_maps:
            image.pack()
        return image
    return None


def load_library(mdataarr: list[parser.structures.MegascanData],
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
                 use_tags: bool = False):
    # utility function
    def add_asset(asset, mdata):
        # add
        asset.asset_mark()

        # optional
        if generate_previews:
            asset.asset_generate_preview()
        if use_tags:
            for tag in mdata.tags:
                asset.asset_data.tags.new(tag)

    for mdata in [d for d in mdataarr if
                  d.type in include_assets]:
        dirpath = os.path.dirname(mdata.path)

        ret = load_asset(
            mdata=mdata,
            filepath=dirpath,
            group_by_model=group_by_model,
            group_by_lod=group_by_lod,
            use_filetype_lods=use_filetype_lods,
            use_filetype_maps=use_filetype_maps,
            use_lods=use_lods,
            use_maps=use_maps,
            pack_maps=False,  # this would let your lovely blender pc explode
            apply_transform=apply_transform)

        # decide the way to split models
        if split_models:
            if use_collections and ret["model_collections"]:
                [add_asset(c, mdata) for c in ret["model_collections"]]
            else:
                [add_asset(o, mdata) for o in ret["objects"]]
        else:
            if use_collections and ret["collection"]:
                add_asset(ret["collection"], mdata)
            else:
                [add_asset(o, mdata) for o in ret["objects"]]

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

    for mdata in [d for d in mdataarr if
                  d.type in include_surfaces]:
        dirpath = os.path.dirname(mdata.path)

        ret = load_material(
            mdata=mdata,
            filepath=dirpath,
            use_filetype_maps=use_filetype_maps,
            use_maps=use_maps,
            pack_maps=False)

        add_asset(ret["material"], mdata)
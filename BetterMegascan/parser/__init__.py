import json
import os
from zipfile import ZipFile, Path as ZipPath
from pathlib import Path
import re
from pprint import pprint, pformat
import logging

# idk how to do it
if __name__ == '__main__':
    from exceptions import *
    from structures import *
else:
    from .exceptions import *
    from .structures import *

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

tmp_dir: str | None = None

def log_call(func):
    def wrapper(*args, **kwargs):
        log.debug(f"{func.__name__}")
        return func(*args, **kwargs)
    return wrapper

def _search_texture_file(filepath: str, dirfiles: list[str], tex_id, tex_type):
    ext = os.path.splitext(os.path.basename(filepath))[1].lstrip(".")
    pattern = rf".*{re.escape(tex_id)}_(raw|high|mid|low)_[1248]k_{re.escape(tex_type)}\.{re.escape(ext)}$"
    #print(pattern)
    #print(filepath)
    found = [e for e in dirfiles if
             re.match(pattern,
                      os.path.basename(e),
                      re.IGNORECASE)]
    assert len(found) <= 1, "found multiple:\n" + pformat(found)
    if found:
        return found[0]
    return None

def _search_geometry_file(filepath: str, dirfiles: list[str], geo_id):
    ext = os.path.splitext(os.path.basename(filepath))[1].lstrip(".")
    pattern = rf".*{re.escape(geo_id)}_(raw|high|mid|low)\.{re.escape(ext)}$"
    #print(pattern)
    #print(filepath)
    found = [e for e in dirfiles if
             re.match(pattern,
                      os.path.basename(e),
                      re.IGNORECASE)]
    assert len(found) <= 1, "found multiple:\n" + pformat(found)
    if found:
        return found[0]
    return None

@log_call
def _parse_json_models(mdata: MegascanData, jel, dirfiles: list[str]):
    for jmodel in jel:
        # filter available
        filepath = jmodel["uri"]
        if filepath not in dirfiles and not (filepath := _search_geometry_file(filepath, dirfiles,
                                                                               geo_id=mdata.id)):
            log.debug(f"file {jmodel['uri']} missing") # keep original uri here so it's not as confusing
            continue

        # create lod
        mmodlod = MegascanModelLod()
        mmodlod.filepath = filepath
        mmodlod.filetype = jmodel["mimeType"]
        mmodlod.level = jmodel.get("lod")
        if mmodlod.level is None: # 0 is valid
            mmodlod.level = jmodel["tier"]

        log.debug(f"found lod:\n{pformat(mmodlod)}")

        # get or add the model
        mmodel = mdata.get_or_create_model(re.split(r"/|\\", filepath)[0])

        # add to collection
        if mmodlod.level not in mmodel.lods:
            mmodel.lods[mmodlod.level] = {mmodlod.filetype: mmodlod}
        else:
            assert mmodlod.filetype not in mmodel.lods[mmodlod.level]
            mmodel.lods[mmodlod.level][mmodlod.filetype] = mmodlod

@log_call
def _parse_json_meshes(mdata: MegascanData, jel, dirfiles: list[str]):
    for jmesh in jel:
        for juri in jmesh["uris"]:
            # filter available
            filepath = juri["uri"]
            if filepath not in dirfiles and not (filepath := _search_geometry_file(filepath, dirfiles,
                                                                                   geo_id=mdata.id)):
                log.debug(f"file {juri['uri']} missing") # keep original uri here so it's not as confusing
                continue
            # mesh type check
            assert jmesh["type"] == "lod"

            # create lod
            mmodlod = MegascanModelLod()
            mmodlod.filepath = filepath
            mmodlod.filetype = juri["mimeType"]
            foundlod = re.findall(r"LOD\d+", filepath)
            mmodlod.level = int(foundlod[0].replace("LOD", "")) if len(foundlod) > 0 else 0

            log.debug(f"found mesh:\n{pformat(mmodlod)}")

            # get or add the model, asset name as fallback
            mmodel = mdata.get_or_create_model(mdata.name)

            # add to collection
            if mmodlod.level not in mmodel.lods:
                mmodel.lods[mmodlod.level] = {mmodlod.filetype: mmodlod}
            else:
                assert mmodlod.filetype not in mmodel.lods[mmodlod.level]
                mmodel.lods[mmodlod.level][mmodlod.filetype] = mmodlod

@log_call
def _parse_json_maps(mdata: MegascanData, jel, dirfiles: list[str]):
    for jmap in jel:
        tex_type = jmap["type"]

        # filter available
        filepath = jmap["uri"]
        # monkey proofing
        if tex_type not in filepath.lower():
            log.warning("monkey moment, hold tight this might not work")
            tex_type = re.search(r"(?s:.*)_(.*)\.", filepath).group(1).lower()
        if filepath not in dirfiles and not (filepath := _search_texture_file(filepath, dirfiles,
                                                                              tex_id=mdata.id,
                                                                              tex_type=tex_type)):
            log.debug(f"file {jmap['uri']} missing") # keep original uri here so it's not as confusing
            continue

        # create map
        mmaplod = MegascanMapLod()
        mmaplod.filepath = filepath
        mmaplod.filetype = jmap["mimeType"]
        mmaplod.level = 0

        log.debug(f"found map:\n{pformat(mmaplod)}")

        # get or add the map
        mmap = mdata.get_or_create_map(tex_type)

        # add to collection
        if mmaplod.level not in mmap.lods:
            mmap.lods[mmaplod.level] = {mmaplod.filetype: mmaplod}
        else:
            if mmaplod.filetype in mmap.lods[mmaplod.level]:
                assert mmap.lods[mmaplod.level][mmaplod.filetype] == mmaplod
            mmap.lods[mmaplod.level][mmaplod.filetype] = mmaplod

@log_call
def _parse_json_components(mdata: MegascanData, jel, dirfiles: list[str]):
    for jcomponent in jel:
        for juris in jcomponent["uris"]:
            for jresolution in juris["resolutions"]:
                for juri in jresolution["formats"]:
                    tex_type = jcomponent["type"]

                    # filter available
                    filepath = juri["uri"]
                    if filepath not in dirfiles and not (filepath := _search_texture_file(filepath, dirfiles,
                                                                                          tex_id=mdata.id,
                                                                                          tex_type=tex_type)):
                        log.debug(f"file {juri['uri']} missing") # keep original uri here so it's not as confusing
                        continue

                    # create map
                    mmaplod = MegascanMapLod()
                    mmaplod.filepath = filepath
                    mmaplod.filetype = juri["mimeType"]
                    foundlod = re.findall(r"LOD\d+", filepath)
                    mmaplod.level = int(foundlod[0].replace("LOD", "")) if len(foundlod) > 0 else 0

                    log.debug(f"found component:\n{pformat(mmaplod)}")

                    # get or add the map
                    mmap = mdata.get_or_create_map(tex_type)

                    # add to collection
                    if mmaplod.level not in mmap.lods:
                        mmap.lods[mmaplod.level] = {mmaplod.filetype: mmaplod}
                    else:
                        assert mmaplod.filetype not in mmap.lods[mmaplod.level]
                        mmap.lods[mmaplod.level][mmaplod.filetype] = mmaplod

@log_call
def _parse_json_metadata(mdata: MegascanData, jroot):
    mdata.tags = jroot["tags"]

    ## lowering tags included
    # mdata.semanticTags = {k: [i.lower() for i in jroot["semanticTags"][k]] for k in jroot["semanticTags"] if isinstance(jroot["semanticTags"][k], list)}

    jcategories = jroot["assetCategories"]

    jcurrentNode: dict = jcategories
    path = ""
    while len(jcurrentNode) == 1:
        key = list(jcurrentNode.keys())[0]
        path = path + '/' + key
        jcurrentNode = jcurrentNode[key]
    path = path.lstrip('/')

    mdata.categoryPath = path

@log_call
def _parse_json_3d(mdata: MegascanData, jroot, dirfiles: list[str]):
    if "meshes" in jroot and "components" in jroot: # might be 3D asset
        assert "models" not in jroot and "maps" not in jroot
        _parse_json_meshes(mdata, jroot["meshes"], dirfiles)
        _parse_json_components(mdata, jroot["components"], dirfiles)
        return

    if "models" in jroot and "maps" in jroot: # might be 3D plant
        assert "meshes" not in jroot and "components" not in jroot
        _parse_json_models(mdata, jroot["models"], dirfiles)
        _parse_json_maps(mdata, jroot["maps"], dirfiles)
        return

    raise InvalidStructureError("unexpected 3D asset format")

@log_call
def _parse_json_megascan(mdata: MegascanData, jroot, dirfiles: list[str]):
    log.debug(pformat(dirfiles))
    try:
        mdata.type = jroot["semanticTags"]["asset_type"]
        mdata.name = jroot.get("name") or jroot["semanticTags"]["name"]
        mdata.id = jroot["id"]

        _parse_json_metadata(mdata, jroot)

        match mdata.type:
            case "3D asset" | "3D plant":
                _parse_json_3d(mdata, jroot, dirfiles)
            case "surface" | "decal" | "brush" | "imperfection":
                _parse_json_maps(mdata, jroot["maps"], dirfiles)
            case "atlas":
                _parse_json_components(mdata, jroot["components"], dirfiles)
            case _:
                raise InvalidStructureError(f"unknown asset type '{mdata.type}'")
    except (KeyError, TypeError) as e:
        log.error(e)
        raise InvalidStructureError("json seems to be invalid") from e


def _find_json(path):
    # find metadata json
    metajson = None
    for p in path.iterdir():
        if not p.is_file():
            continue
        if p.name.endswith(".json"):
            metajson = p.name
            break
    if metajson is None:
        raise InvalidStructureError("no json ")

    log.debug(f"metadata json: {metajson}")
    return metajson

def parse(filepath: str) -> MegascanData:
    dirpath = os.path.dirname(filepath)
    dirfiles = []
    for root, _, files in os.walk(dirpath):
        for file in files:
            relativefilepath = os.path.relpath(os.path.join(root, file), dirpath).replace('\\', '/')
            dirfiles.append(relativefilepath)

    mdata = MegascanData()
    mdata.path = filepath

    # json parsing
    with open(filepath, mode='r') as jsonfile:
        jroot = json.loads(jsonfile.read())
        _parse_json_megascan(mdata, jroot, dirfiles)

    return mdata


def parse_zip(path: str) -> MegascanData:
    log.debug(f"reading zip {path}")

    with ZipFile(path) as arch:
        archfiles = [p.filename.replace('\\', '/') for p in arch.filelist]

        metajson = _find_json(ZipPath(arch))

        mdata = MegascanData()
        # json parsing
        with arch.open(metajson, mode='r') as jsonfile:
            jroot = json.load(jsonfile)
            _parse_json_megascan(mdata, jroot, archfiles)

        return mdata


def parse_dir(path: str) -> MegascanData:
    log.debug(f"reading dir {path}")

    metajson = os.path.join(path, _find_json(Path(path)))
    return parse(metajson)


def parse_library(filepath: str) -> list[MegascanData]:
    log.debug(f"reading library {filepath}")

    dirname = os.path.dirname(filepath)
    mdataarr: list[MegascanData] = []
    # json parsing
    with open(filepath, mode='r') as jsonfile:
        jroot = json.load(jsonfile)
        try:
            for jmegascan in jroot:
                mspath = os.path.join(dirname, *jmegascan["jsonPath"])
                mdataarr.append(parse(mspath))
        except (KeyError, TypeError) as e:
            raise InvalidStructureError("json seems to be invalid") from e

    return mdataarr

def extract_from_zip(source: str, path_in_zip: str, destination: str) -> str:
    with ZipFile(source) as arch:
        member = arch.getinfo(path_in_zip)
        arch.extract(member, path=destination)
    return os.path.join(destination, path_in_zip)


def ensure_file(source: str, path: str) -> str:
    if os.path.isfile(source):
        if not tmp_dir:
            assert False
        return extract_from_zip(source, path, tmp_dir)

    return os.path.join(source, path)


# my lazy-ass testing
if __name__ == '__main__':
    from pprint import pprint

    mdata = parse(r"F:\Megascans Library\Downloaded\3dplant\plants _3d_sbslY\sbslY.json")
    pprint(mdata)
    mdataarr = parse_library(r"F:\Megascans Library\Downloaded\assetsData.json")
    pprint(mdataarr)
    mdata = parse_zip(r"test-zip-file-here")
    pprint(mdata)
    mdata = parse_dir(r"test-directory-here")
    pprint(mdata)

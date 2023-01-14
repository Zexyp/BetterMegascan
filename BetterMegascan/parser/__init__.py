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

log: logging.Logger = None
try:
    from .. import spawn_logger
    log = spawn_logger(__name__)
except ImportError:
    log = logging.Logger(__name__)
    log.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(asctime)s][%(name)s][%(levelname)s]: %(message)s", "%H:%M:%S"))
    log.addHandler(handler)

tmp_dir: str = None

def _parse_json_models(mdata: MegascanData, jel, dirfiles: list[str]):
    for jmodel in jel:
        # filter available
        if jmodel["uri"] not in dirfiles:
            continue

        # create lod
        mmodlod = MegascanModelLOD()
        mmodlod.filepath = jmodel["uri"]
        mmodlod.filetype = jmodel["mimeType"]
        mmodlod.level = jmodel["lod"]

        log.debug(f"found lod:\n{pformat(mmodlod)}")

        # get or add the model
        mmodel = mdata.get_or_create_model(re.split(r"/|\\", jmodel["uri"])[0])

        # add to collection
        if mmodlod.level not in mmodel.lods:
            mmodel.lods[mmodlod.level] = {mmodlod.filetype: mmodlod}
        else:
            assert mmodlod.filetype not in mmodel.lods[mmodlod.level]
            mmodel.lods[mmodlod.level][mmodlod.filetype] = mmodlod


def _parse_json_meshes(mdata: MegascanData, jel, dirfiles: list[str]):
    for jmesh in jel:
        for juri in jmesh["uris"]:
            # filter available
            if juri["uri"] not in dirfiles:
                continue
            # mesh type check
            assert jmesh["type"] == "lod"

            # create lod
            mmodlod = MegascanModelLOD()
            mmodlod.filepath = juri["uri"]
            mmodlod.filetype = juri["mimeType"]
            foundlod = re.findall(r"LOD\d+", (juri["uri"]))
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


def _parse_json_maps(mdata: MegascanData, jel, dirfiles: list[str]):
    for jmap in jel:
        # filter available
        if jmap["uri"] not in dirfiles:
            continue

        # create map
        mmaplod = MegascanMapLOD()
        mmaplod.filepath = jmap["uri"]
        mmaplod.filetype = jmap["mimeType"]
        mmaplod.level = 0

        log.debug(f"found map:\n{pformat(mmaplod)}")

        # get or add the map
        mmap = mdata.get_or_create_map(jmap["type"])

        # add to collection
        if mmaplod.level not in mmap.lods:
            mmap.lods[mmaplod.level] = {mmaplod.filetype: mmaplod}
        else:
            assert mmaplod.filetype not in mmap.lods[mmaplod.level]
            mmap.lods[mmaplod.level][mmaplod.filetype] = mmaplod


def _parse_json_components(mdata: MegascanData, jel, dirfiles: list[str]):
    for jcomponent in jel:
        for juris in jcomponent["uris"]:
            for jresolution in juris["resolutions"]:
                for juri in jresolution["formats"]:
                    # filter available
                    if juri["uri"] not in dirfiles:
                        continue

                    # create map
                    mmaplod = MegascanMapLOD()
                    mmaplod.filepath = juri["uri"]
                    mmaplod.filetype = juri["mimeType"]
                    foundlod = re.findall(r"LOD\d+", (juri["uri"]))
                    mmaplod.level = int(foundlod[0].replace("LOD", "")) if len(foundlod) > 0 else 0

                    log.debug(f"found component:\n{pformat(mmaplod)}")

                    # get or add the map
                    mmap = mdata.get_or_create_map(jcomponent["type"])

                    # add to collection
                    if mmaplod.level not in mmap.lods:
                        mmap.lods[mmaplod.level] = {mmaplod.filetype: mmaplod}
                    else:
                        assert mmaplod.filetype not in mmap.lods[mmaplod.level]
                        mmap.lods[mmaplod.level][mmaplod.filetype] = mmaplod


def _parse_json(mdata: MegascanData, jsondata, dirfiles: list[str]):
    jroot = json.loads(jsondata)

    try:
        mdata.type = jroot["semanticTags"]["asset_type"]
        mdata.name = jroot["name"]
        mdata.id = jroot["id"]

        match mdata.type:
            case "3D asset":
                _parse_json_meshes(mdata, jroot["meshes"], dirfiles)
                _parse_json_components(mdata, jroot["components"], dirfiles)
            case "3D plant":
                _parse_json_models(mdata, jroot["models"], dirfiles)
                _parse_json_maps(mdata, jroot["maps"], dirfiles)
            case "surface" | "decal" | "brush":
                _parse_json_maps(mdata, jroot["maps"], dirfiles)
            case "atlas":
                _parse_json_components(mdata, jroot["components"], dirfiles)
            case _:
                raise InvalidStructureError("unknown asset type")
    except KeyError as ke:
        raise InvalidStructureError("json seems to be invalid") from ke


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


def parse_zip(path: str) -> MegascanData:
    log.debug(f"reading zip {path}")

    with ZipFile(path) as arch:
        archfiles = [p.filename.replace('\\', '/') for p in arch.filelist]

        metajson = _find_json(ZipPath(arch))

        mdata = MegascanData()
        # json parsing
        with arch.open(metajson, mode='r') as jsonfile:
            _parse_json(mdata, jsonfile.read(), archfiles)

        return mdata


def parse(path: str) -> MegascanData:
    log.debug(f"reading {path}")

    dirfiles = []
    for root, _, files in os.walk(path):
        for file in files:
            relativefilepath = os.path.relpath(os.path.join(root, file), path).replace('\\', '/')
            dirfiles.append(relativefilepath)

    metajson = os.path.join(path, _find_json(Path(path)))

    mdata = MegascanData()
    # json parsing
    with open(metajson, mode='r') as jsonfile:
        _parse_json(mdata, jsonfile.read(), dirfiles)

    return mdata


def extract_from_zip(source: str, path_in_zip: str, destination: str) -> str:
    with ZipFile(source) as arch:
        member = arch.getinfo(path_in_zip)
        arch.extract(member, path=destination)
    return os.path.join(destination, path_in_zip)


def ensure_file(source: str, path: str) -> str:
    if os.path.isfile(source):
        if not tmp_dir:
            raise Exception
        return extract_from_zip(source, path, tmp_dir)

    return os.path.join(source, path)


if __name__ == '__main__':
    from pprint import pprint

    mdata = parse_zip(r"test-file-here")
    pprint(mdata)
    mdata = parse(r"test-directory-here")
    pprint(mdata)

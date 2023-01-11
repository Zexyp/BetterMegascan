from dataclasses import dataclass, field


@dataclass
class MegascanFileInfo:
    filepath: str = None
    filetype: str = None


@dataclass
class MegascanModelLOD(MegascanFileInfo):
    level: int = None


@dataclass
class MegascanMapLOD(MegascanFileInfo):
    level: int = None


@dataclass
class MegascanModel:
    name: str = None
    #          level     mime
    lods: dict[int, dict[str, MegascanModelLOD]] = field(default_factory=lambda: {})


@dataclass
class MegascanMap:
    type: str = None
    #          level     mime
    lods: dict[int, dict[str, MegascanMapLOD]] = field(default_factory=lambda: {})

@dataclass
class MegascanData:
    type: str = None
    id: str = None
    name: str = None

    models: dict[str, MegascanModel] = field(default_factory=lambda: {})
    #          type
    maps: dict[str, MegascanMap] = field(default_factory=lambda: {})

    def get_or_create_model(self, name: str) -> MegascanModel:
        if name not in self.models:
            mmodel = MegascanModel()
            mmodel.name = name
            self.models[name] = mmodel

        return self.models[name]

    def get_or_create_map(self, type: str) -> MegascanMap:
        if type not in self.maps:
            mmap = MegascanMap()
            mmap.type = type
            self.maps[type] = mmap

        return self.maps[type]

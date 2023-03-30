import json
import pprint
from scene.Light import LightType

from scene.Scene import EnvironmentType

class Config:
    def __init__(self,filepath) -> None:
        self._config = None
        with open(filepath, 'r') as fd:
            fixed_json = ''.join(line for line in fd if (not line.startswith('//')))
            self._config = json.loads(fixed_json)
        self._validate()

    def __repr__(self) -> str:
        rep = "======== INIT CONFIG ========\n"
        rep += pprint.pformat(self._config, indent=4)
        rep += "\n======== END CONFIG  ========\n"
        return rep
    
    def __str__(self) -> str:
        rep = "======== INIT CONFIG ========\n"
        rep += pprint.pformat(self._config, indent=4)
        rep += "\n======== END CONFIG  ========\n"
        return rep

    def get(self, key: str=None):
        if key in self._config:
            return self._config[key]
        else:
            return None

    def _validate(self):
        if self._config["environment_type"] == "TEXTURE_ENVIRONMENT_BLURRED":
            self._config["environment_type"] = EnvironmentType.TEXTURE_ENVIRONMENT_BLURRED
        elif self._config["environment_type"] == "TEXTURE_ENVIRONMENT":
            self._config["environment_type"] = EnvironmentType.TEXTURE_ENVIRONMENT
        elif self._config["environment_type"] == "SPHERE":
            self._config["environment_type"] = EnvironmentType.SPHERE
        elif self._config["environment_type"] == "SKY":
            self._config["environment_type"] = EnvironmentType.SKY


        if self._config["light_disposition"] == "SINGLE":
            self._config["light_disposition"] = LightType.SINGLE
        elif self._config["light_disposition"] == "TRIANGLE":
            self._config["light_disposition"] = LightType.TRIANGLE
        elif self._config["light_disposition"] == "SQUARE":
            self._config["light_disposition"] = LightType.SQUARE
        
        default_materials = dict()
        for m in self._config["materials"]:
            default_materials[m["name"]] = m
        self._config["materials"] = default_materials       
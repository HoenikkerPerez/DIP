import bpy
import math
import logging
from scene import Scene

logger = logging.getLogger(__name__)

class LightType:
    TRIANGLE = "TriangleDisposition"
    SQUARE = "SquareDisposition"
    SINGLE = "Single"


class Light:
    def __init__(self, light_type: LightType, track_to_mesh) -> None:
        self._D = bpy.data
        self._C = bpy.context
        self._light_type = light_type
        self._track_to_mesh = track_to_mesh
        self._env_collection = Scene.get_collection()
        self.add_light()


    def add_light(self):
        logger.info(f"Adding light disposition of type: {self._light_type}")
        if self._light_type == LightType.SINGLE:
            lamp_data = self._D.lights.new('Lamp', type='SUN')
            lamp = self._D.objects.new('Lamp', lamp_data)
            self._C.collection.objects.link(lamp)
            lamp.data.energy = 10  # 10 is the max value for energy
            lamp.data.distance = 100
            lamp.location = (5, 0, 5)

        elif self._light_type == LightType.TRIANGLE:
            R = 5
            H = 5
            locations = [(0, R, H), (-R*math.sqrt(3)/2, -R/2, H), (R*math.sqrt(3)/2, -R/2, H)] 
            for i, loc in enumerate(locations):
                name = "LAMP_"+ str(i)
                lamp_data = self._D.lights.new(name=name, type="AREA") 
                lamp_object = self._D.objects.new(name=name, object_data=lamp_data)
                self._env_collection.objects.link(lamp_object)
                lamp_object.location = loc
                lamp_object.color = (1,1,1,1)
                lamp_data.energy = 150 
                # track obj
                if self._track_to_mesh is not None:
                    track_to_constraint = lamp_object.constraints.new(type='TRACK_TO')
                    track_to_constraint.target = self._track_to_mesh

        elif self._light_type == LightType.SQUARE:
            locations = [(5, 5, 5), (5, -5, 5), (-5, -5, 5), (-5, 5, 5)] 
            for i, loc in enumerate(locations):
                name = "LAMP_"+ str(i)
                lamp_data = self._D.lights.new(name=name, type="AREA") 
                lamp_object = self._D.objects.new(name=name, object_data=lamp_data)   # new lamp object
                self._env_collection.objects.link(lamp_object)
                lamp_object.location = loc
                lamp_object.color = (1,1,1,1)
                lamp_data.energy = 150
                # track obj
                if self._track_to_mesh is not None:
                    track_to_constraint = lamp_object.constraints.new(type='TRACK_TO')
                    track_to_constraint.target = self._track_to_mesh
        return lamp_object
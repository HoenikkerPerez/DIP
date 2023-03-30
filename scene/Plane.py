import bpy
from material.Material import Materials

class Plane:
    def __init__(self, materials: Materials=None) -> None:
        self._D = bpy.data
        self._materials = materials
        self._plate_obj = self.add_plane()
        self._set_material()
        
    def add_plane(self):
        if "Plane" in self._D.objects:
            return self._D.objects["Plane"]

        # add plane 
        bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0))
        return bpy.context.active_object
        
    def _set_material(self):
        if self._materials:
            self._materials.set_materials(self._plate_obj, "black_plane", "one")
            # self._plate_obj.data.materials.append(self._materials.)
            # self._plate_obj.data.materials.append(self._material)
        # else:
        #     D = bpy.data


    def get_bpy_obj(self):
        return self._plate_obj

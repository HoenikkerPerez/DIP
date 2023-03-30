import bpy
import math
import os 
import json
import random
import logging

from mathutils import Euler
from scene import Scene

logger = logging.getLogger(__name__)

class MainMesh:
    def __init__(self, mesh_file) -> None:
        self._D = bpy.data
        self._C = bpy.context
        self._env_collection = Scene.get_collection()
        self._mesh_file = mesh_file
        self._bpy_obj = self.add_mesh()


    def add_mesh(self):  
        bpy.ops.wm.obj_import(filepath= self._mesh_file)
        my_mesh = self._C.active_object
        
        bpy.ops.object.mode_set( mode = 'OBJECT' ) # Make sure we're in object mode
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')
        bpy.ops.object.location_clear() # Clear location - set location to (0,0,0)
        my_mesh.name = "MyMesh"   
        
        # if info file exists, load best rotation
        info_file_path = os.path.splitext(self._mesh_file)[0] + ".json"
        try:
            with open(info_file_path) as jf:
                info = json.load(jf)
                my_mesh.name = info["name"]
                rotation_euler = info["euler_rotation"]
                if rotation_euler[0] == 0 and rotation_euler[1] == 0 and rotation_euler[2] == 0:
                    logger.info("Not rotated")
                    return my_mesh
                logger.info(rotation_euler)
                # In order to rotate around world's axis but moved towards the object's
                # origin, either temporarily set object's origin to 0 (so move it to the
                # axis), or create a matrix without the location data, which I do below,
                # by only using rotation data to create the matrix:
                mat = my_mesh.rotation_euler.to_matrix().to_4x4()
                # code operates on radians, so convert the 90 degrees value to radians
                rot_values = (math.radians(rotation_euler[0]), math.radians(rotation_euler[1]), math.radians(rotation_euler[2]))  # convert degrees to radians
                y_rot = Euler(rot_values)  # default order is XYZ
                # use transformation matrix
                y_mat = y_rot.to_matrix().to_4x4()
                mat = y_mat @ mat
                # convert the resulting matrix back to an euler value
                # new_euler = mat.to_euler()
                # update object's euler:
                my_mesh.rotation_euler = mat.to_euler()
        except Exception as e:
            logger.info(str(e))
            logger.info(f"Info file not found: {info_file_path}")
        return my_mesh

    def move_object_to_origin(self):
        ob = self._bpy_obj
        minZ = self.get_min_z_vertex()
        # Move mesh to Z=0
        logger.info(f"Mesh moved to origin: {ob.name} > {ob.location[2]} --> {minZ}")
        ob.location[2] = -minZ#np.sign(minZ)*minZ
        self._C.view_layer.update()

    def get_min_z_vertex(self):
        mw =  self._bpy_obj.matrix_world
        glob_vertex_coordinates = [ mw @ v.co for v in  self._bpy_obj.data.vertices ] # Global coordinates of vertices
        # Find the lowest Z value amongst the object's verts
        return min( [ co.z for co in glob_vertex_coordinates ] ) 

    def get_max_z_vertex(self):
        mw =  self._bpy_obj.matrix_world
        glob_vertex_coordinates = [ mw @ v.co for v in  self._bpy_obj.data.vertices ] # Global coordinates of vertices
        # Find the lowest Z value amongst the object's verts
        return max( [ co.z for co in glob_vertex_coordinates ] ) 


    def scale_objects(self, box_dim = .9):
        C = bpy.context
        ob = self._bpy_obj
        x_obj,y_obj,z_obj = ob.dimensions
        x_ratio = x_obj#/1
        y_ratio = y_obj#/2
        z_ratio = z_obj
        box_dim = .9
        if x_ratio >= box_dim or y_ratio >= box_dim or z_ratio >= box_dim:
            scale_factor = box_dim/max(x_ratio, y_ratio, z_ratio)
            ob.scale = (scale_factor, scale_factor, scale_factor)
            logger.info(f"SCALE FACTOR: {scale_factor}")
            # need to update the scene, world matrix is computed async
            # https://blender.stackexchange.com/questions/27667/incorrect-matrix-world-after-transformation
            C.view_layer.update()

    def get_bpy_mesh(self):
        return self._bpy_obj
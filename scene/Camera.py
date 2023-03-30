import bpy
import math
import numpy as np 
from utils import rotate
from utils.Utils import get_collection

class CameraDispositionType:
    CYLINDER_AND_FIBO = "CylinderAndFibonacci"
    FIBO = "Fibonacci"
    CYLINDER = "Cylinder"
    CYL_AND_SPHERE = "CylAndSphere"
    SPHERE = "Sphere"

        
class Camera:
    def __init__(self, location=(0,0,0), track_to=None, name="lp_camera", debug=False) -> None:
        self._D = bpy.data
        self._C = bpy.context
        self._location = location
        self._track_to = track_to
        self.track_to_location = None
        self._cam_data = None
        self._cam_obj = None
        self._track_to_constraint = None
        self._name = name
        self._model = None
        if not debug:
            self._add_camera()
        else:
            self._add_debug_camera()
        if track_to:
            self.track_to(track_to)


    def dump_camera(self, filename):
        # in meshroom:
        # https://github.com/alicevision/meshroom/issues/655
        with open(filename, "a") as fd:
            fd.write(f"{self._name} ") 
            fd.write(f"{self._location [0]:.3f} {self._location [1]:.3f} {self._location [2]:.3f} ")
            fd.write(f"{self.track_to_location [0]:.3f} {self.track_to_location [1]:.3f} {self.track_to_location [2]:.3f}\n")


    def set_up_lens(self, sens_width, sens_lenght, lens):
        self._cam_data.lens = lens
        self._cam_data.sensor_fit = 'HORIZONTAL'
        self._cam_data.sensor_width = sens_width
        self._cam_data.sensor_height = sens_lenght

        
    def set_camera_model(self, model:str):
        """
        https://github.com/zalmoxes-laran/BlenderLandscape/blob/master/PhotogrTool.py
        """
        if model == "Canon6D35":
            # https://www.digicamdb.com/specs/canon_eos-6d/
            self.set_up_lens(35.8,23.9,35)
        elif model == "Canon6D24":
            self.set_up_lens(35.8,23.9,24)
        elif model == "Canon6D14":
            self.set_up_lens(35.8,23.9,14.46)
        elif model == "Canon6D_MARKII_35":
            # https://www.digicamdb.com/specs/canon_eos-6d-mark-ii/
            self._brand_name = "Canon"
            self._model_name = "Canon EOS 6D Mark II"
            self.set_up_lens(35.9, 24, 35)
    
    def get_model_name(self):
        return self._model_name
    
    def get_brand_name(self):
        return self._brand_name

    def _add_camera(self):
        self._cam_data = self._D.cameras.new(self._name)
        self._cam_obj = self._D.objects.new(self._name, self._cam_data)
        self._C.collection.objects.link(self._cam_obj)
        self._cam_obj.location = self._location
        self._cam_data.lens = 35
        # if self._track_to:
        #     track_to_constraint = self._cam_obj.constraints.new(type='TRACK_TO')
        #     track_to_constraint.target = self._track_to
        

    def _add_debug_camera(self):
        debug_collection = get_collection("Debug")
        self._cam_data = self._D.cameras.new(self._name)
        self._cam_obj = self._D.objects.new(self._name, self._cam_data)
        debug_collection.objects.link(self._cam_obj)
        self._cam_obj.location = self._location
        self._cam_data.lens = 35
        self._cam_data.display_size = .1

        # if self._track_to:
        #     self.track_to()
        #     track_to_constraint = self._cam_obj.constraints.new(type='TRACK_TO')
        #     track_to_constraint.target = self._track_to
    

    def _fibonacci_pt(self, R: float, i:int, n:int):
        Phi = math.sqrt(5)*.5 + .5
        # Phi = math.sqrt(5)*.5*R + .5
        phi = 2.0*math.pi * (i/Phi - math.floor(i/Phi))
        cosTheta = 1.0 - (2*i + 1.0)/n
        sinTheta = 1 - cosTheta*cosTheta
        sinTheta = math.sqrt(min(1,max(0,sinTheta)))
        return (math.cos(phi)*sinTheta *R , math.sin(phi)*sinTheta*R , cosTheta*R )

    def get_bpy_obj(self):
        return self._cam_obj

    def get_cam_data(self):
        return self._cam_data

    def set_render_cam(self):
        bpy.context.scene.camera = self._cam_obj

    def track_to(self, mesh):
        self.track_to_location = mesh.location
        if self._track_to_constraint is None:
            self._track_to_constraint = self._cam_obj.constraints.new(type='TRACK_TO')
        self._track_to_constraint.target = mesh
        return self._track_to_constraint

    def get_tracked_obj(self):
        return self._track_to_constraint.target

    def get_cam_locations(self, object_high, sampling_type="Fibonacci", N=0):
        
        # Fibonacci: fibonacci sampling [meshlab]
        ## Implementation of the Spherical Fibonacci Point Sets
        ## according to the description of
        ## Spherical Fibonacci Mapping
        ## Benjamin Keinert, Matthias Innmann, Michael Sanger, Marc Stamminger
        ## TOG 2015

        # CylAndSphere: Cylinder and HemiSphere
        
        if sampling_type == "CylinderAndFibonacci":
            if N == 0:
                raise ValueError("N cannot be 0 in Fibonacci sampling")
            cam_locations = []
            # z_step = (object_high+(.1*object_high))/3.
            # # z_position computed using high of the tracked object (3 circles on obj z axis)
            # z_positions = [z_step]
            # ANGLE_STEP = 20 # 20
            # angle_steps = int(360/ANGLE_STEP)
            # cam_location = np.array([1,0,z_positions[0]])
            # for z_pos in z_positions:
            #     cam_location = np.array([cam_location[0], cam_location[1], z_pos])
            #     for idx_axis, axis in enumerate([(0,0,1)]):
            #         for i in range(1, angle_steps+1):
            #             cam_location = rotate(cam_location, ANGLE_STEP, axis=axis)
            #             cam_locations.append(("cylinder", np.round(cam_location,2)))

            for i in range(N):
                fib_loc_i = [sampling_type, self._fibonacci_pt(1.2,i, N)]
                if fib_loc_i[1][2] > 0:
                    fib_loc_i[1] = (fib_loc_i[1][0], fib_loc_i[1][1], fib_loc_i[1][2])
                    cam_locations.append(fib_loc_i)
                
            cam_locations =  [cam_location for cam_location in cam_locations if cam_location[1][2]>0]

        if sampling_type == CameraDispositionType.FIBO:
            if N == 0:
                raise ValueError("N cannot be 0 in Fibonacci sampling")
            cam_locations = []
            for i in range(N):
                cam_locations.append((sampling_type, self._fibonacci_pt(object_high,i, N)))
            cam_locations =  [cam_location for cam_location in cam_locations if cam_location[1][2]>0]

        elif sampling_type == CameraDispositionType.CYL_AND_SPHERE:
            z_step = (object_high+(.1*object_high))/3.
            # z_position computed using high of the tracked object (3 circles on obj z axis)
            z_positions = [ z_step, 2*z_step, 3*z_step]
            # rotation on diagonal axis    
            cam_locations = []

            ANGLE_STEP = 10
            angle_steps = int(360/ANGLE_STEP)
            cam_location = np.array([1.5,0,0])
            for i in range(angle_steps):
                cam_locations.append(("sphere", np.round(cam_location,2)))
                cam_location = rotate(cam_location, ANGLE_STEP, axis=(0,1,0))

            cam_location = np.array([0,1.5,0])
            for i in range(angle_steps):
                cam_locations.append(("sphere", np.round(cam_location,2)))
                cam_location = rotate(cam_location, ANGLE_STEP, axis=(1,0,0))
            
            # Cylinder disposition
            ANGLE_STEP = 20 # 20
            angle_steps = int(360/ANGLE_STEP)
            cam_location = np.array([1,0,z_positions[0]])
            for z_pos in z_positions:
                cam_location = np.array([cam_location[0], cam_location[1], z_pos])
                for idx_axis, axis in enumerate([(0,0,1)]):
                    for i in range(1, angle_steps+1):
                        cam_location = rotate(cam_location, ANGLE_STEP, axis=axis)
                        cam_locations.append(("cylinder", np.round(cam_location,2)))
    

            # return only positive z camera positions
            cam_locations =  [cam_location for cam_location in cam_locations if cam_location[1][2]>0]
        return cam_locations


    def set_location(self, location):
        self._location = location
        self._cam_obj.location = location
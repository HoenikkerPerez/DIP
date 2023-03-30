import bpy
import os
from material.Material import Materials
import numpy as np 
import logging
from scene.Scene import Scene, EnvironmentType
from scene.Camera import Camera, CameraDispositionType
from scene.Plane import Plane
from scene.MainMesh import MainMesh
from scene.Light import Light, LightType
from utils import get_collection
from utils.Utils import update_exif_metadata

logger = logging.getLogger(__name__)


class Render:
    def __init__(self, engine="CYCLES") -> None:
        # self._engine = engine

        C = bpy.context
        scn= C.scene
        # engine = self._engine
        scn.render.engine = engine
        scn.render.image_settings.file_format='PNG'
        if engine == "CYCLES":
            scn.cycles.adaptive_threshold = 0.01
            scn.cycles.samples = 100
            scn.cycles.use_denoising = True
            # Set the device_type
            C.preferences.addons["cycles"].preferences.compute_device_type = "CUDA" # or "OPENCL"
            # Set the device and feature set
            scn.cycles.device = "GPU"

            # get_devices() to let Blender detects GPU device
            C.preferences.addons["cycles"].preferences.get_devices()
            logger.info(C.preferences.addons["cycles"].preferences.compute_device_type)
            for d in C.preferences.addons["cycles"].preferences.devices:
                d["use"] = 1 # Using all devices, include GPU and CPU
                logger.info(str(d["name"]) + " " +  str(d["use"]))
        scn.render.resolution_x = 3120
        scn.render.resolution_y = 2080

        # scn.render.resolution_x = 1620
        # scn.render.resolution_y = 1080


        logger.info("RENDER ENGINE: " + scn.render.engine)

    
    def render_multiview_single_scene(self, mesh_file, 
                                            filename, 
                                            material, 
                                            color,
                                            debug=False, 
                                            light_disposition: LightType ="SquareDisposition", 
                                            materials_path="", 
                                            background_type=None,
                                            background_image_path=None,
                                            output_render_dir="",
                                            exiftool_filepath="",
                                            camera_model="Canon6D_MARKII_35",
                                            default_materials = None):

        logger.info(f"Render: {background_type}, {filename}, {material}")
        C = bpy.context
        D = bpy.data
        
        materials = Materials(materials_path, default_materials)
        # Create Scene with background 
        scene = Scene(background_type=background_type,
                    background_image_path= background_image_path,
                    materials = materials,
                    debug=debug)
                    
        # plane = Plane(material)
        
        
        # import external obj
        my_mesh = MainMesh(mesh_file)
        my_mesh.scale_objects()
        my_mesh.move_object_to_origin()
        

        light = Light(light_disposition, my_mesh.get_bpy_mesh())

        materials.set_materials(my_mesh.get_bpy_mesh(), material, "one")        

        # CAMERA
        cam = Camera()
        cam.set_camera_model(camera_model)
        cam.set_render_cam()
        # cam = camera.get_bpy_obj()
        cam.track_to(my_mesh.get_bpy_mesh())
        


        output_dir = os.path.join(output_render_dir, filename)
        try:
            os.mkdir(output_dir)
        except:
            pass
        
        output_dir = os.path.join(output_dir, material)
        try:
            os.mkdir(output_dir)
        except:
            pass
        
        # output_dir = os.path.join(output_dir, material_type)
        # try:
        #     os.mkdir(output_dir)
        # except:
        #     pass

        counter = 0
        object_high = my_mesh.get_max_z_vertex()

        cam_locations = cam.get_cam_locations(object_high, sampling_type=CameraDispositionType.CYLINDER_AND_FIBO,  N=200)

        track_to_cubes = []
        z_step = object_high/3.
        track_to_zs = [1*z_step, 2*z_step, 3*z_step - .075]
        for tz in track_to_zs:                
            bpy.ops.mesh.primitive_cube_add(size=.01, enter_editmode=False, align='WORLD', location=(0,0,tz))
            track_to_cube = C.active_object
            track_to_cube.hide_render = True
            debug_collection = get_collection("Debug")
            debug_collection.objects.link(track_to_cube)
            C.collection.objects.unlink(track_to_cube)
            track_to_cubes.append(track_to_cube)

        for type, cam_location in cam_locations:
            # if cilinder look at mesh center, otherwise fix z axis of the camera and look at a non redered square
            if type == CameraDispositionType.CYLINDER:
                debug_collection = get_collection("Debug")
                bpy.ops.mesh.primitive_cube_add(size=.01, enter_editmode=False, align='WORLD', location=(0,0,cam_location[2]))
                camera_cube = C.active_object
                debug_collection.objects.link(camera_cube)
                C.collection.objects.unlink(camera_cube)
            #     #### 
                cube = C.active_object
                # track_to_constraint = cam.constraints.new(type='TRACK_TO')
                cam.track_to(cube)
            elif type == CameraDispositionType.SPHERE:
                cam.track_to(my_mesh)
            elif type == CameraDispositionType.FIBO:
                
                cam.track_to(my_mesh)
            elif type == CameraDispositionType.CYLINDER_AND_FIBO:
                #remove
                debug_collection = get_collection("Debug")
                bpy.ops.mesh.primitive_cube_add(size=.01, enter_editmode=False, align='WORLD', location=cam_location)
                camera_cube = C.active_object
                debug_collection.objects.link(camera_cube)
                #evomer
                possible_tzs = [tz for tz in track_to_zs if cam_location[2] > tz]
                if possible_tzs:
                    idx_track_to_z = np.argmax(possible_tzs)        
                    cam.track_to(track_to_cubes[idx_track_to_z])
                else:
                    cam.track_to(track_to_cubes[0])
            else:
                raise ValueError
            

            image_name = f"{str(counter).zfill(3)}"
            if debug:
                print("HERE")
                camera_cube = Camera(cam_location, track_to=cam.get_tracked_obj(), debug=True)
                
            else:            
                cam.set_location(cam_location)
                filepath = f"{output_dir}\\{image_name}.png"
                if not os.path.exists(filepath):
                    logger.info(f"Rendering: {filepath}")
                    C.scene.render.filepath = filepath
                    bpy.ops.render.render(write_still=1)
                    # TODO rimettere
                    # C.scene.render.resolution_x = 5472
                    # C.scene.render.resolution_y = 3648

                    #convert_to_tiff()
                    # update_exif_metadata(exiftool_path=exiftool_filepath,
                    #                     filepath=filepath,
                    #                     res_x=C.scene.render.resolution_x,
                    #                     res_y=C.scene.render.resolution_y,
                    #                     camera=cam
                    #                     )
                
                # dump camera locations and other infos
                cam.dump_camera(os.path.join(output_dir, "metainfo.txt"))
                # with open(os.path.join(output_dir, "metainfo.txt"), "a+") as mf:
                #     mf.write(f"{image_name} {cam_location[0]:.3f} {cam_location[1]:.3f} {cam_location[2]:.3f}\n")

            counter = counter+1
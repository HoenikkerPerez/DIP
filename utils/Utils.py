import bpy
import math
import logging
import numpy as np
from subprocess import TimeoutExpired, run


logger = logging.getLogger(__name__)

@staticmethod
def get_collection(name: str = "lp_collection") -> bpy.types.Collection:

    recon_collection = bpy.data.collections.get(name)
    if not recon_collection:
        recon_collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(recon_collection)
        logger.info(f"Created collection {name}")
    return recon_collection

def translate(point, xt, yt, zt):
    return np.array([point[0] + xt, point[1] + xt, point[2] + zt])


def rotate(point, angle_degrees, axis=(0,1,0)):
    theta_degrees = angle_degrees
    theta_radians = math.radians(theta_degrees)

    rotated_point =  np.dot(rotation_matrix(axis, theta_radians), point)
    
    return rotated_point


def rotation_matrix(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.
    """
    axis = np.asarray(axis)
    axis = axis / math.sqrt(np.dot(axis, axis))
    a = math.cos(theta / 2.0)
    b, c, d = -axis * math.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                    [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                    [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])


def convert_to_tiff(imagemagick_path, filepath):
    # https://github.com/alicevision/meshroom/issues/1558
    # & 'C:\Program Files\ImageMagick-7.1.0-Q16-HDRI\magick.exe' mogrify -format tiff "C:\Users\Luca\OneDrive - University of Pisa\Documents\Uni
    # \tesi magistrale\datasets\renders\FullBody_Decimated\concrete_rough\000.png" 
    logger.info("Converting PNG to TIFF")
    imagemagick_cmd = [
        imagemagick_path,
        "mogrify -format tiff",
        {filepath}
    ]

def update_exif_metadata(exiftool_path, filepath, res_x, res_y, camera):
    # --- update EXIF metadata
    logger.info("Updating EXIF metadata")
    camera_data = camera.get_cam_data()

    # compute 35mm focal length
    # https://en.wikipedia.org/wiki/35_mm_equivalent_focal_length
    # f35 = 36*f/w [mm]
    f = camera_data.lens
    w = camera_data.sensor_width 
    fl35 = 36.0 * f / w
    logger.info(f"Equivalent Focal Length: {fl35}")
    # resolution EOS MARK2 72x72
    exiftool_cmd = [
        exiftool_path,
        f"-exif:Make=Canon",
        f"-exif:Model={camera.get_model_name()}",
        f"-exif:FocalLength={f} mm",
        f"-exif:FocalLengthIn35mmFormat={int(fl35)}",
        "-exif:FocalPlaneXResolution={}".format(res_x / camera_data.sensor_width),
        "-exif:FocalPlaneYResolution={}".format(res_y / camera_data.sensor_height),
        "-exif:FocalPlaneResolutionUnit#=4",
        "-exif:ExifImageWidth={}".format(res_x),
        "-exif:ExifImageHeight={}".format(res_y),
        "-exif:ExifVersion=0230", 
        "-overwrite_original",
        filepath
    ]
    print(exiftool_cmd)
    #
    # "C:\\Users\\Luca\\Downloads\\exiftool.exe"
    #
    #

    # run exiftool
    try:
        exit_code = run(exiftool_cmd, timeout=5, check=False).returncode
        print("exit code:", exit_code)
    except Exception as e:  # pylint: disable=broad-except
        logger.info("Exiftool execution exception: %s)", e)
    finally:
        if exit_code != 0:
            logger.info("EXIFTOOL ERROR")
        else:
            logger.info("Metadata correctly set: {filepath}")  



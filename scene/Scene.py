import bpy
import logging
from mathutils import Euler, Vector
from scene.Plane import Plane

from utils.Utils import get_collection

logger = logging.getLogger(__name__)

class EnvironmentType:
    TEXTURE_ENVIRONMENT = "Texture Environment"
    TEXTURE_ENVIRONMENT_BLURRED = "Texture Environment Blurred"
    SPHERE = "Sphere"
    SKY = "Sky"

    
class Scene:

    def __init__(self, background_type: EnvironmentType, background_image_path=None, materials=None, debug=False) -> None:
        self._C = bpy.context
        self._D = bpy.data
        self._background_type = background_type
        self._background_image_path = background_image_path
        self._materials = materials

        self.clean_scene()
        self.add_background()
        self.add_sky()
        self.add_plane()

    def clean_scene(self):
        # remove all previous objs
        for obj in self._D.objects:
            if obj.name != "Plane":
                self._D.objects.remove(obj, do_unlink=True)


    def add_background(self):
        logger.info(f"Adding background: {self._background_type}, {self._background_image_path}")
        type = self._background_type
        image_path = self._background_image_path
        # possible_types = [EnvironmentType.TEXTURE_ENVIRONMENT,EnvironmentType.TEXTURE_ENVIRONMENT_BLURRED,EnvironmentType.SPHERE]
        # if (type == EnvironmentType.TEXTURE_ENVIRONMENT or type == EnvironmentType.TEXTURE_ENVIRONMENT_BLURRED) and image_path is None:
        #     raise ValueError
        # elif type not in possible_types:
        #     raise ValueError


        scn = self._C.scene
        scn.world.use_nodes = True

        #select world node tree
        wd = scn.world
        node_tree = wd.node_tree
        if type == EnvironmentType.TEXTURE_ENVIRONMENT:
            # Environment texture node
            env_tex_node = node_tree.nodes.new(type="ShaderNodeTexEnvironment")
            env_tex_node.image = self._D.images.load(image_path)
            node_tree.links.new(env_tex_node.outputs['Color'], node_tree.nodes['Background'].inputs['Color'])
            node_tree.nodes["Background"].inputs[1].default_value = 0.1 # "Strenght"

        elif type == EnvironmentType.TEXTURE_ENVIRONMENT_BLURRED:
            # Environment texture node
            env_tex_node = node_tree.nodes.new(type="ShaderNodeTexEnvironment")
            env_tex_node.image = self._D.images.load(image_path)
            node_tree.links.new(env_tex_node.outputs['Color'], node_tree.nodes['Background'].inputs['Color'])
        
            # Linear Light (MixRGB)
            mixrgb_node = node_tree.nodes.new(type="ShaderNodeMixRGB")
            mixrgb_node.blend_type = 'LINEAR_LIGHT'
            mixrgb_node.inputs[0].default_value = 0.1
            node_tree.links.new(mixrgb_node.outputs['Color'], env_tex_node.inputs['Vector'])

            # White Noise
            white_noise_node = node_tree.nodes.new(type="ShaderNodeTexWhiteNoise")
            node_tree.links.new(white_noise_node.outputs['Color'], mixrgb_node.inputs['Color2'])

            # Texture Cohordinate
            tex_coordinates_node = node_tree.nodes.new(type="ShaderNodeTexCoord")
            node_tree.links.new(tex_coordinates_node.outputs['Generated'], white_noise_node.inputs['Vector'])
            node_tree.links.new(tex_coordinates_node.outputs['Generated'], mixrgb_node.inputs['Color1'])
            
            node_tree.nodes["Background"].inputs[1].default_value = 0.1 # "Strenght"

        elif type == EnvironmentType.SPHERE:
            self.add_hemisphere(10)

        elif type == EnvironmentType.SKY:
            self.add_sky()

    def add_plane(self):
        # add plane 
        p = Plane(self._materials)
        p.add_plane()


    def add_sky(self) -> None:
        """Setup a procedural sky.
        Inspired by https://blenderartists.org/t/procedural-sky-texture/594259/11

        Arguments:
            context {bpy.types.Context} -- current context
        """

        scene = self._C.scene
        node_tree = scene.world.node_tree
        nodes = node_tree.nodes
        links = node_tree.links
        if not scene.world.node_tree.get("SKY_OUTPUT_NODE"):
            logger.info(f"{__name__}: Sky Environment already exists.")
            return
        nodes.clear()   # clear existing
        #
        # --- output chain
        output = nodes.new("ShaderNodeOutputWorld")
        output.location = Vector((2450, 0))
        output.name = "SKY_OUTPUT_NODE"
        add_shader = nodes.new("ShaderNodeAddShader")
        add_shader.location = Vector((2300, 0))
        links.new(add_shader.outputs[0], output.inputs['Surface'])
        #
        # --- input chain
        tex_coord = nodes.new("ShaderNodeTexCoord")
        tex_coord.location = Vector((0, 0))
        normal = nodes.new("ShaderNodeNormal")
        normal.location = Vector((200, 0))
        normal.outputs[0].default_value = Vector((0.0, 0.0, 1.0))
        links.new(tex_coord.outputs['Generated'], normal.inputs['Normal'])
        #
        # --- sun glare
        # normal
        sg_01 = nodes.new("ShaderNodeNormal")
        sg_01.location = Vector((600, -300))
        links.new(tex_coord.outputs['Generated'], sg_01.inputs['Normal'])
        # color ramp
        sg_02 = nodes.new("ShaderNodeValToRGB")
        sg_02.location = Vector((750, -300))
        sg_02.color_ramp.interpolation = 'B_SPLINE'
        c = sg_02.color_ramp.elements[0]
        c.position = 0.95
        c.color = Vector((0, 0, 0, 1))
        c = sg_02.color_ramp.elements[1]
        c.position = 0.995
        c.color = Vector((0, 0, 0, 1))
        sg_02.color_ramp.elements.new(1.0)
        c = sg_02.color_ramp.elements[2]
        c.color = Vector((1, 1, 1, 1))
        links.new(sg_01.outputs['Dot'], sg_02.inputs['Fac'])
        # mix
        sg_03a = nodes.new("ShaderNodeMixRGB")
        sg_03a.location = Vector((1000, -300))
        sg_03a.inputs['Color1'].default_value = Vector((0., 0., 0., 1.))
        sg_03a.inputs['Color2'].default_value = Vector((1., 0.6, 0.07, 1.))
        links.new(sg_02.outputs['Color'], sg_03a.inputs['Fac'])
        # color ramp
        sg_03b = nodes.new("ShaderNodeValToRGB")
        sg_03b.location = Vector((1000, -550))
        sg_03b.color_ramp.interpolation = 'EASE'
        c = sg_03b.color_ramp.elements[0]
        c.position = 0.0
        c.color = Vector((0, 0, 0, 1))
        c = sg_03b.color_ramp.elements[1]
        c.position = 0.05
        c.color = Vector((1, 1, 1, 1))
        links.new(normal.outputs['Dot'], sg_03b.inputs['Fac'])
        # multiply
        sg_04 = nodes.new("ShaderNodeMixRGB")
        sg_04.location = Vector((1250, -300))
        sg_04.blend_type = 'MULTIPLY'
        sg_04.inputs['Fac'].default_value = 1.0
        links.new(sg_03a.outputs['Color'], sg_04.inputs['Color1'])
        links.new(sg_03b.outputs['Color'], sg_04.inputs['Color2'])
        # background
        sg_05 = nodes.new("ShaderNodeBackground")
        sg_05.location = Vector((1400, -300))
        sg_05.inputs['Strength'].default_value = 1.5
        links.new(sg_04.outputs['Color'], sg_05.inputs['Color'])
        # to out
        links.new(sg_05.outputs['Background'], add_shader.inputs[1])
        #
        # --- clouds chain
        # mapping
        cl_01a = nodes.new("ShaderNodeMapping")
        cl_01a.location = Vector((600, 300))
        cl_01a.vector_type = 'POINT'
        pi_2 = 2 * pi
        location = Vector((random() - 0.5, random() - 0.5, random() - 0.5))
        rotation = Vector((random() * pi_2, random() * pi_2, random() * pi_2))
        scale = Vector((1 + random(), 1 + random(), 1 + random()))
        cl_01a.inputs['Location'].default_value = location
        cl_01a.inputs['Rotation'].default_value = rotation
        cl_01a.inputs['Scale'].default_value = scale

        links.new(tex_coord.outputs['Generated'], cl_01a.inputs['Vector'])
        # color ramp
        cl_01b = nodes.new("ShaderNodeValToRGB")
        cl_01b.location = Vector((600, 0))
        cl_01b.color_ramp.interpolation = 'B_SPLINE'
        c = cl_01b.color_ramp.elements[0]
        c.position = 0.0
        c.color = Vector((0.6, 0.6, 0.6, 1))
        c = cl_01b.color_ramp.elements[1]
        c.position = 0.33
        c.color = Vector((0.3, 0.3, 0.3, 1))
        cl_01b.color_ramp.elements.new(1.0)
        c = cl_01b.color_ramp.elements[2]
        c.color = Vector((0.1, 0.1, 0.1, 1))
        links.new(normal.outputs['Dot'], cl_01b.inputs['Fac'])
        # multiply
        cl_02 = nodes.new("ShaderNodeMath")
        cl_02.operation = 'MULTIPLY'
        cl_02.location = Vector((950, 0))
        cl_02.inputs[1].default_value = 15.0
        links.new(cl_01b.outputs['Color'], cl_02.inputs[0])
        # noise texture
        cl_03 = nodes.new("ShaderNodeTexNoise")
        cl_03.location = Vector((1100, 150))
        cl_03.inputs['Detail'].default_value = 16.0
        cl_03.inputs['Distortion'].default_value = 0.0
        links.new(cl_01a.outputs['Vector'], cl_03.inputs['Vector'])
        links.new(cl_02.outputs['Value'], cl_03.inputs['Scale'])
        # color ramp
        cl_04a = nodes.new("ShaderNodeValToRGB")
        cl_04a.location = Vector((1250, 450))
        cl_04a.color_ramp.interpolation = 'LINEAR'
        c = cl_04a.color_ramp.elements[0]
        c.position = 0.0
        c.color = Vector((0, 0, 0, 1))
        c = cl_04a.color_ramp.elements[1]
        c.position = 0.1
        c.color = Vector((1, 1, 1, 1))
        links.new(normal.outputs['Dot'], cl_04a.inputs['Fac'])
        # color ramp
        cl_04b = nodes.new("ShaderNodeValToRGB")
        cl_04b.location = Vector((1250, 150))
        cl_04b.color_ramp.interpolation = 'B_SPLINE'
        c = cl_04b.color_ramp.elements[0]
        c.position = 0.0
        c.color = Vector((0, 0, 0, 1))
        c = cl_04b.color_ramp.elements[1]
        c.position = 0.45
        c.color = Vector((0.01, 0.01, 0.01, 1))
        cl_04b.color_ramp.elements.new(1.0)
        c = cl_04b.color_ramp.elements[2]
        c.position = 0.55
        c.color = Vector((0.2, 0.2, 0.2, 1))
        cl_04b.color_ramp.elements.new(1.0)
        c = cl_04b.color_ramp.elements[3]
        c.position = 0.7
        c.color = Vector((0.45, 0.45, 0.45, 1))
        cl_04b.color_ramp.elements.new(1.0)
        c = cl_04b.color_ramp.elements[4]
        c.position = 0.85
        c.color = Vector((1, 1, 1, 1))
        links.new(cl_03.outputs['Color'], cl_04b.inputs['Fac'])
        # multiply color
        sg_05 = nodes.new("ShaderNodeMixRGB")
        sg_05.location = Vector((1500, 250))
        sg_05.blend_type = 'MULTIPLY'
        sg_05.inputs['Fac'].default_value = 1.0
        links.new(cl_04a.outputs['Color'], sg_05.inputs['Color1'])
        links.new(cl_04b.outputs['Color'], sg_05.inputs['Color2'])
        #
        # --- Sky chain
        # sky texture
        sky_tex = nodes.new("ShaderNodeTexSky")
        sky_tex.location = Vector((1650, 50))
        sky_tex.sky_type = 'HOSEK_WILKIE'   # TODO switch to the new NISHITA in 2.90+ ?
        sky_tex.turbidity = 2.0
        sky_tex.ground_albedo = 0.5
        # mix color
        sc_01 = nodes.new("ShaderNodeMixRGB")
        sc_01.location = Vector((1850, 200))
        sc_01.blend_type = 'MIX'
        sc_01.inputs['Color2'].default_value = Vector((0.490, 0.405, 0.319, 1))
        links.new(sky_tex.outputs['Color'], sc_01.inputs['Color1'])
        links.new(sg_05.outputs['Color'], sc_01.inputs['Fac'])
        # background
        sc_02 = nodes.new("ShaderNodeBackground")
        sc_02.location = Vector((2000, 200))
        sc_02.inputs['Strength'].default_value = 1.5
        links.new(sc_01.outputs['Color'], sc_02.inputs['Color'])
        # to out
        links.new(sc_02.outputs['Background'], add_shader.inputs[0])
        
    def add_hemisphere(self, walls_radius: float) -> None:
        
        # create scene walls
        bpy.ops.mesh.primitive_uv_sphere_add(location=(0,0,0), radius=walls_radius)
        sphere = self._C.active_object
        sphere.name = "Hemisphere"
        environment_collection = get_collection()
        environment_collection.objects.link(sphere)
        bpy.context.collection.objects.unlink(sphere)
        
        # give the sphere a flat "floor"
        offset = 0.01
        for vertex in sphere.data.vertices:
            v_world = sphere.matrix_world @ vertex.co 
            if v_world.z <= 0:
                v_world.z = 0 - offset
            vertex.co = sphere.matrix_world.inverted() @ v_world  # move back to obj space
        sphere.data.flip_normals()
        
        # setup wall material
        material = self._D.materials.new("SphereMaterial")
        material.use_nodes = True
        diffuse = material.node_tree.nodes.get("Principled BSDF")
        diffuse.inputs['Base Color'].default_value = (1.0, 1.0, 1.0, 1.0)
        diffuse.inputs['Roughness'].default_value = 0.0
        diffuse.inputs['Specular'].default_value = 0.0
        sphere.active_material = material

        # add subdivision surface
        sphere.modifiers.new(name="SfM_WallSubSurf", type='SUBSURF')
        bpy.ops.object.shade_smooth()

        print("Hemisphere Added")


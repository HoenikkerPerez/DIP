import bpy
import random
import logging

logger = logging.getLogger(__name__)


class Materials:
    def __init__(self, materials_path, default_materials) -> None:
        self._materials = dict()
        self._material_path = materials_path
        self._default_materials = default_materials

    # def get_material(self, material_k, rgb_color):
    #     D = bpy.data
    #     if material_k not in self._materials:
    #         mat = D.materials.new(name="MyMaterial")
    #         mat.use_nodes = True
    #     else:
    #         mat = self._materials[material_k]
        

    #     if material_k == "photorealistic":
    #         principled_node = mat.node_tree.nodes.get('Principled BSDF')
    #         principled_node.inputs["Base Color"].default_value = rgb_color # (0.65, 0.4, 0.08, 1) # random color!
    #         principled_node.inputs["Metallic"].default_value = 0
    #         principled_node.inputs["Roughness"].default_value = .9
    #         principled_node.inputs["Specular"].default_value = .1
    #     elif material_k == "metallic":
    #         principled_node = mat.node_tree.nodes.get('Principled BSDF')
    #         principled_node.inputs["Base Color"].default_value = rgb_color # (0.65, 0.4, 0.08, 1)
    #         principled_node.inputs["Metallic"].default_value = 1
    #         principled_node.inputs["Roughness"].default_value = .1
    #         principled_node.inputs["Specular"].default_value = .9
        
    #     return mat
        

    def set_materials(self, mesh, material_k, quant_materials="all"):
        D = bpy.data
        # change each material of the mesh, create a new material if it does not exist
        if len(mesh.data.materials) != 0:
            if quant_materials == "all":
                materials_to_mod = mesh.data.materials
            elif quant_materials == "one":
                materials_to_mod = [random.choice(mesh.data.materials)]
        else:
            logger.info(f"New Material: {material_k}")
            mat = D.materials.new(name="MyMaterial")
            mat.use_nodes = True
            # print(materials_to_mod)
            mesh.data.materials.append(mat)
            materials_to_mod = [mat]

        for mat in materials_to_mod:

            # if material_k in self._default_materials:
            #     default_mat = self._default_materials[material_k][material_type]
                # # new version
                # principled_node = mat.node_tree.nodes.get('Principled BSDF')
                # principled_node.inputs["Base Color"].default_value =  default_mat["BaseColor"]
                # principled_node.inputs["Metallic"].default_value = default_mat["Metallic"]
                # principled_node.inputs["Roughness"].default_value = default_mat["Roughness"]
                # principled_node.inputs["Specular"].default_value = default_mat["Specular"]
                # return


            principled_node = mat.node_tree.nodes.get('Principled BSDF')
            texture_coordinate_node = mat.node_tree.nodes.new("ShaderNodeTexCoord")
            mapping_node = mat.node_tree.nodes.new("ShaderNodeMapping")

            if material_k == "photorealistic":
        #        principled_node.inputs["Base Color"].default_value = rgb_color # (0.65, 0.4, 0.08, 1) # random color!
                principled_node.inputs["Metallic"].default_value = 0
                principled_node.inputs["Roughness"].default_value = .9
                principled_node.inputs["Specular"].default_value = .1
                
            elif material_k == "metallic":
        #        principled_node.inputs["Base Color"].default_value = rgb_color # (0.65, 0.4, 0.08, 1)
                principled_node.inputs["Metallic"].default_value = 1
                principled_node.inputs["Roughness"].default_value = .1
                principled_node.inputs["Specular"].default_value = .9

            elif material_k == "metal-bare":
                mat.node_tree.links.new(texture_coordinate_node.outputs['Normal'], mapping_node.inputs["Vector"])
                # Albedo
                tex_image_albedo_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                albedo_path = self._material_path + '\\Metal_Bare_se2abbvc_4K_surface_ms\\se2abbvc_4K_Albedo.jpg'
                tex_image_albedo_node.image = D.images.load(albedo_path)
                mat.node_tree.links.new(tex_image_albedo_node.outputs['Color'], principled_node.inputs[0])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_albedo_node.inputs["Vector"])
                # Roughness
                # tex_image_roughness_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                # roughness_path = self._material_path + '\\Metal_Bare_se2abbvc_4K_surface_ms\\se2abbvc_4K_Roughness.jpg'
                # tex_image_roughness_node.image = D.images.load(roughness_path)
                # mat.node_tree.links.new(tex_image_roughness_node.outputs['Color'], principled_node.inputs[9])
                # mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_roughness_node.inputs["Vector"])
                principled_node.inputs["Roughness"].default_value = .1

                # Metallic
                tex_image_metalness_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                metalness_path = self._material_path + '\\Metal_Bare_se2abbvc_4K_surface_ms\\se2abbvc_4K_Metalness.jpg'
                tex_image_metalness_node.image = D.images.load(metalness_path)
                mat.node_tree.links.new(tex_image_metalness_node.outputs['Color'], principled_node.inputs[6])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_metalness_node.inputs["Vector"])
                # Normal
                # tex_image_normal_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                # normal_path = self._material_path + '\\Metal_Bare_se2abbvc_4K_surface_ms\\se2abbvc_4K_Normal.jpg'
                # tex_image_normal_node.image = D.images.load(normal_path)
                # tex_image_normalmap_node = mat.node_tree.nodes.new(type="ShaderNodeNormalMap")
                # mat.node_tree.links.new(tex_image_normal_node.outputs['Color'], tex_image_normalmap_node.inputs["Color"])
                # mat.node_tree.links.new(tex_image_normalmap_node.outputs['Normal'], principled_node.inputs[22])

            elif material_k == "metal-bare-photogrammable":
                mat.node_tree.links.new(texture_coordinate_node.outputs['Normal'], mapping_node.inputs["Vector"])

                # Albedo
                tex_image_albedo_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                albedo_path = self._material_path + '\\Metal_Bare_se2abbvc_4K_surface_ms\\se2abbvc_4K_Albedo.jpg'
                tex_image_albedo_node.image = D.images.load(albedo_path)
                mat.node_tree.links.new(tex_image_albedo_node.outputs['Color'], principled_node.inputs[0])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_albedo_node.inputs["Vector"])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_albedo_node.inputs["Vector"])

                # Roughness
                # tex_image_roughness_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                # roughness_path = self._material_path + '\\Metal_Bare_se2abbvc_4K_surface_ms\\se2abbvc_4K_Roughness.jpg'
                # tex_image_roughness_node.image = D.images.load(roughness_path)
                # mat.node_tree.links.new(tex_image_roughness_node.outputs['Color'], principled_node.inputs[9])
                # mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_roughness_node.inputs["Vector"])
                principled_node.inputs["Roughness"].default_value = 1

                # Metallic
                tex_image_metalness_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                metalness_path = self._material_path + '\\Metal_Bare_se2abbvc_4K_surface_ms\\se2abbvc_4K_Metalness.jpg'
                tex_image_metalness_node.image = D.images.load(metalness_path)
                mat.node_tree.links.new(tex_image_metalness_node.outputs['Color'], principled_node.inputs[6])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_metalness_node.inputs["Vector"])
                # Normal
                # tex_image_normal_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                # normal_path = self._material_path + '\\Metal_Bare_se2abbvc_4K_surface_ms\\se2abbvc_4K_Normal.jpg'
                # tex_image_normal_node.image = D.images.load(normal_path)
                # tex_image_normalmap_node = mat.node_tree.nodes.new(type="ShaderNodeNormalMap")
                # mat.node_tree.links.new(tex_image_normal_node.outputs['Color'], tex_image_normalmap_node.inputs["Color"])
                # mat.node_tree.links.new(tex_image_normalmap_node.outputs['Normal'], principled_node.inputs[22])

            elif material_k == "marblewhitebetter":
                mapping_node.inputs[2].default_value[1] = 0.785398
                mat.node_tree.links.new(texture_coordinate_node.outputs['Generated'], mapping_node.inputs["Vector"])

                # Albedo
                tex_image_albedo_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                albedo_path = self._material_path + '\\Marble_white_better\\Marble 1_baseColor.jpeg'
                tex_image_albedo_node.image = D.images.load(albedo_path)
                mat.node_tree.links.new(tex_image_albedo_node.outputs['Color'], principled_node.inputs[0])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_albedo_node.inputs["Vector"])
                # Specular
                principled_node.inputs["Specular"].default_value = .5
                # Roughness
                principled_node.inputs["Roughness"].default_value = .3

                # Metallic
                tex_image_metalness_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                metalness_path = self._material_path + '\\Marble_white_better\\Marble 1_metallic.jpeg'
                tex_image_metalness_node.image = D.images.load(metalness_path)
                mat.node_tree.links.new(tex_image_metalness_node.outputs['Color'], principled_node.inputs[6])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_metalness_node.inputs["Vector"])

            elif material_k == "marblewhitebetter-photogrammable":
                mapping_node.inputs[2].default_value[1] = 0.785398
                mat.node_tree.links.new(texture_coordinate_node.outputs['Generated'], mapping_node.inputs["Vector"])
                # Albedo
                tex_image_albedo_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                albedo_path = self._material_path + '\\Marble_white_better\\Marble 1_baseColor.jpeg'
                tex_image_albedo_node.image = D.images.load(albedo_path)
                mat.node_tree.links.new(tex_image_albedo_node.outputs['Color'], principled_node.inputs[0])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_albedo_node.inputs["Vector"])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_albedo_node.inputs["Vector"])
                # Specular
                principled_node.inputs["Specular"].default_value = .5
                # Roughness
                principled_node.inputs["Roughness"].default_value = 1

                # Metallic
                tex_image_metalness_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                metalness_path = self._material_path + '\\Marble_white_better\\Marble 1_metallic.jpeg'
                tex_image_metalness_node.image = D.images.load(metalness_path)
                mat.node_tree.links.new(tex_image_metalness_node.outputs['Color'], principled_node.inputs[6])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_metalness_node.inputs["Vector"])

            elif material_k == "marblewhite":
                mat.node_tree.links.new(texture_coordinate_node.outputs['Normal'], mapping_node.inputs["Vector"])

                # Albedo
                tex_image_albedo_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                albedo_path = self._material_path + '\\Marble_white\\Marble 5_BaseColor.jpg'
                tex_image_albedo_node.image = D.images.load(albedo_path)
                mat.node_tree.links.new(tex_image_albedo_node.outputs['Color'], principled_node.inputs[0])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_albedo_node.inputs["Vector"])
                # Roughness
                # tex_image_roughness_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                # roughness_path = self._material_path + '\\Marble_white\\se2abbvc_4K_Roughness.jpg'
                # tex_image_roughness_node.image = D.images.load(roughness_path)
                # mat.node_tree.links.new(tex_image_roughness_node.outputs['Color'], principled_node.inputs[9])
                # mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_roughness_node.inputs["Vector"])
                principled_node.inputs["Roughness"].default_value = .3

                # Metallic
                tex_image_metalness_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                metalness_path = self._material_path + '\\Marble_white\\Marble 5_OcclusionRoughnessMetallic.jpg'
                tex_image_metalness_node.image = D.images.load(metalness_path)
                mat.node_tree.links.new(tex_image_metalness_node.outputs['Color'], principled_node.inputs[6])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_metalness_node.inputs["Vector"])
                
            elif material_k == "marblewhite-photogrammable":
                mat.node_tree.links.new(texture_coordinate_node.outputs['Normal'], mapping_node.inputs["Vector"])
                # Albedo
                tex_image_albedo_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                albedo_path = self._material_path + '\\Marble_white\\Marble 5_BaseColor.jpg'
                tex_image_albedo_node.image = D.images.load(albedo_path)
                mat.node_tree.links.new(tex_image_albedo_node.outputs['Color'], principled_node.inputs[0])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_albedo_node.inputs["Vector"])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_albedo_node.inputs["Vector"])

                # Roughness
                principled_node.inputs["Roughness"].default_value = 1

                # Metallic
                tex_image_metalness_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                metalness_path = self._material_path + '\\Marble_white\\Marble 5_OcclusionRoughnessMetallic.jpg'
                tex_image_metalness_node.image = D.images.load(metalness_path)
                mat.node_tree.links.new(tex_image_metalness_node.outputs['Color'], principled_node.inputs[6])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_metalness_node.inputs["Vector"])

            elif material_k == "marblebrown":
                mapping_node.inputs[2].default_value[1] = 1.5708 # pi/2
                mat.node_tree.links.new(texture_coordinate_node.outputs['Generated'], mapping_node.inputs["Vector"])
                # Albedo
                tex_image_albedo_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                albedo_path = self._material_path + '\\Marble_brown\\Marble 15_baseColor.jpeg'
                tex_image_albedo_node.image = D.images.load(albedo_path)
                mat.node_tree.links.new(tex_image_albedo_node.outputs['Color'], principled_node.inputs[0])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_albedo_node.inputs["Vector"])
                
                # Specular
                principled_node.inputs["Specular"].default_value = .3


                # Roughness
                principled_node.inputs["Roughness"].default_value = .2

                # Metallic
                tex_image_metalness_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                metalness_path = self._material_path + '\\Marble_brown\\Marble 15_metallic.jpeg'
                tex_image_metalness_node.image = D.images.load(metalness_path)
                mat.node_tree.links.new(tex_image_metalness_node.outputs['Color'], principled_node.inputs[6])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_metalness_node.inputs["Vector"])

            elif material_k == "marblebrown-photogrammable":
                mapping_node.inputs[2].default_value[1] = 1.5708 # pi/2
                mat.node_tree.links.new(texture_coordinate_node.outputs['Generated'], mapping_node.inputs["Vector"])

                # Albedo
                tex_image_albedo_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                albedo_path = self._material_path + '\\Marble_brown\\Marble 15_baseColor.jpeg'
                tex_image_albedo_node.image = D.images.load(albedo_path)
                mat.node_tree.links.new(tex_image_albedo_node.outputs['Color'], principled_node.inputs[0])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_albedo_node.inputs["Vector"])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_albedo_node.inputs["Vector"])

                # Specular
                principled_node.inputs["Specular"].default_value = .3

                # Roughness
                principled_node.inputs["Roughness"].default_value = 1

                # Metallic
                tex_image_metalness_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                metalness_path = self._material_path + '\\Marble_brown\\Marble 15_metallic.jpeg'
                tex_image_metalness_node.image = D.images.load(metalness_path)
                mat.node_tree.links.new(tex_image_metalness_node.outputs['Color'], principled_node.inputs[6])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_metalness_node.inputs["Vector"])

            elif material_k == "rusty-iron":
                # mapping_node.inputs[2].default_value = 1.5708 # pi/2
                mat.node_tree.links.new(texture_coordinate_node.outputs['Normal'], mapping_node.inputs["Vector"])

                # Albedo
                tex_image_albedo_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                albedo_path = self._material_path + '\\Rusty_iron\\Metal iron 4_baseColor.jpeg'
                tex_image_albedo_node.image = D.images.load(albedo_path)
                mat.node_tree.links.new(tex_image_albedo_node.outputs['Color'], principled_node.inputs[0])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_albedo_node.inputs["Vector"])
                # Roughness
                # tex_image_roughness_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                # roughness_path = self._material_path + '\\Rusty_iron\\se2abbvc_4K_Roughness.jpg'
                # tex_image_roughness_node.image = D.images.load(roughness_path)
                # mat.node_tree.links.new(tex_image_roughness_node.outputs['Color'], principled_node.inputs[9])
                # mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_roughness_node.inputs["Vector"])
                principled_node.inputs["Roughness"].default_value = .3
                # Specular
                principled_node.inputs["Specular"].default_value = 0
                # Metallic
                tex_image_metalness_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                metalness_path = self._material_path + '\\Rusty_iron\\Metal iron 4_metallic.jpeg'
                tex_image_metalness_node.image = D.images.load(metalness_path)
                mat.node_tree.links.new(tex_image_metalness_node.outputs['Color'], principled_node.inputs[6])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_metalness_node.inputs["Vector"])
               
            elif material_k == "rusty-iron-photogrammable":
                mat.node_tree.links.new(texture_coordinate_node.outputs['Normal'], mapping_node.inputs["Vector"])
                # Albedo
                tex_image_albedo_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                albedo_path = self._material_path + '\\Rusty_iron\\Metal iron 4_baseColor.jpeg'
                tex_image_albedo_node.image = D.images.load(albedo_path)
                mat.node_tree.links.new(tex_image_albedo_node.outputs['Color'], principled_node.inputs[0])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_albedo_node.inputs["Vector"])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_albedo_node.inputs["Vector"])
               
                # Specular
                principled_node.inputs["Specular"].default_value = 0

                # Roughness
                principled_node.inputs["Roughness"].default_value = 1

                # Metallic
                tex_image_metalness_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                metalness_path = self._material_path + '\\Rusty_iron\\Metal iron 4_metallic.jpeg'
                tex_image_metalness_node.image = D.images.load(metalness_path)
                mat.node_tree.links.new(tex_image_metalness_node.outputs['Color'], principled_node.inputs[6])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_metalness_node.inputs["Vector"])
        


            elif material_k == "gold":
                mat.node_tree.links.new(texture_coordinate_node.outputs['Normal'], mapping_node.inputs["Vector"])
                mat.node_tree.links.new(texture_coordinate_node.outputs['Generated'], mapping_node.inputs["Location"])

                # Albedo
                tex_image_albedo_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                albedo_path = self._material_path + '\\gold\\Gold material 17_BaseColor.jpg'
                tex_image_albedo_node.image = D.images.load(albedo_path)
                mat.node_tree.links.new(tex_image_albedo_node.outputs['Color'], principled_node.inputs[0])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_albedo_node.inputs["Vector"])
                # Roughness
                principled_node.inputs["Roughness"].default_value = .3
                # Specular
                principled_node.inputs["Specular"].default_value = 0
                # Metallic
                tex_image_metalness_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                metalness_path = self._material_path + '\\gold\\Gold material 17_Metallic.jpg'
                tex_image_metalness_node.image = D.images.load(metalness_path)
                mat.node_tree.links.new(tex_image_metalness_node.outputs['Color'], principled_node.inputs[6])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_metalness_node.inputs["Vector"])
               
            elif material_k == "gold-photogrammable":
                mat.node_tree.links.new(texture_coordinate_node.outputs['Normal'], mapping_node.inputs["Vector"])
                mat.node_tree.links.new(texture_coordinate_node.outputs['Generated'], mapping_node.inputs["Location"])
                # Albedo
                tex_image_albedo_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                albedo_path = self._material_path + '\\gold\\Gold material 17_BaseColor.jpg'
                tex_image_albedo_node.image = D.images.load(albedo_path)
                mat.node_tree.links.new(tex_image_albedo_node.outputs['Color'], principled_node.inputs[0])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_albedo_node.inputs["Vector"])
                # Specular
                principled_node.inputs["Specular"].default_value = 0
                # Roughness
                principled_node.inputs["Roughness"].default_value = 1
                # Metallic
                tex_image_metalness_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                metalness_path = self._material_path + '\\gold\\Gold material 17_Metallic.jpg'
                tex_image_metalness_node.image = D.images.load(metalness_path)
                mat.node_tree.links.new(tex_image_metalness_node.outputs['Color'], principled_node.inputs[6])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_metalness_node.inputs["Vector"])


            elif material_k == "goldold":  # NO
                # Albedo
                tex_image_albedo_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                albedo_path = self._material_path + '\\gold_5\\gold raw_baseColor.jpg'
                tex_image_albedo_node.image = D.images.load(albedo_path)
                mat.node_tree.links.new(tex_image_albedo_node.outputs['Color'], principled_node.inputs[0])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_albedo_node.inputs["Vector"])
                # Roughness
                # tex_image_roughness_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                # roughness_path = self._material_path + '\\gold_5\\se2abbvc_4K_Roughness.jpg'
                # tex_image_roughness_node.image = D.images.load(roughness_path)
                # mat.node_tree.links.new(tex_image_roughness_node.outputs['Color'], principled_node.inputs[9])
                # mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_roughness_node.inputs["Vector"])
                principled_node.inputs["Roughness"].default_value = .1

                # Metallic
                tex_image_metalness_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                metalness_path = self._material_path + '\\gold_5\\gold raw_metallic.jpg'
                tex_image_metalness_node.image = D.images.load(metalness_path)
                mat.node_tree.links.new(tex_image_metalness_node.outputs['Color'], principled_node.inputs[6])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_metalness_node.inputs["Vector"])

            elif material_k == "goldold-photogrammable":  # NO
                # Albedo
                tex_image_albedo_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                albedo_path = self._material_path + '\\gold_5\\gold raw_baseColor.jpg'
                tex_image_albedo_node.image = D.images.load(albedo_path)
                mat.node_tree.links.new(tex_image_albedo_node.outputs['Color'], principled_node.inputs[0])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_albedo_node.inputs["Vector"])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_albedo_node.inputs["Vector"])

                # Roughness
                # tex_image_roughness_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                # roughness_path = self._material_path + '\\gold_5\\se2abbvc_4K_Roughness.jpg'
                # tex_image_roughness_node.image = D.images.load(roughness_path)
                # mat.node_tree.links.new(tex_image_roughness_node.outputs['Color'], principled_node.inputs[9])
                # mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_roughness_node.inputs["Vector"])
                principled_node.inputs["Roughness"].default_value = 1

                # Metallic
                tex_image_metalness_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                metalness_path = self._material_path + '\\gold_5\\gold raw_metallic.jpg'
                tex_image_metalness_node.image = D.images.load(metalness_path)
                mat.node_tree.links.new(tex_image_metalness_node.outputs['Color'], principled_node.inputs[6])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_metalness_node.inputs["Vector"])

            elif material_k == "imperfections":
                # Roughness
                tex_image_roughness_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                roughness_path = self._material_path + '\\Imperfections_rmmodbdp_4K_surface_ms\\rmmodbdp_4K_Roughness.jpg'
                tex_image_roughness_node.image = D.images.load(roughness_path)
                mat.node_tree.links.new(tex_image_roughness_node.outputs['Color'], principled_node.inputs[9])

            elif material_k == "sand-fine":
                mat.node_tree.links.new(texture_coordinate_node.outputs['Normal'], mapping_node.inputs["Vector"])

                # Albedo
                tex_image_albedo_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                albedo_path = self._material_path + '\\Sand_Fine_sjzkfega_4K_surface_ms\\sjzkfega_4K_Albedo.jpg'
                tex_image_albedo_node.image = D.images.load(albedo_path)
                mat.node_tree.links.new(tex_image_albedo_node.outputs['Color'], principled_node.inputs[0])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_albedo_node.inputs["Vector"])

                # Roughness
                # tex_image_roughness_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                # roughness_path = self._material_path + '\\Sand_Fine_sjzkfega_4K_surface_ms\\sjzkfega_4K_Roughness.jpg'
                # tex_image_roughness_node.image = D.images.load(roughness_path)
                # mat.node_tree.links.new(tex_image_roughness_node.outputs['Color'], principled_node.inputs[9])
                # mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_roughness_node.inputs["Vector"])
                principled_node.inputs["Roughness"].default_value = .1
                # Normal
                tex_image_normal_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                normal_path = self._material_path + '\\Sand_Fine_sjzkfega_4K_surface_ms\\sjzkfega_4K_Normal.jpg'
                tex_image_normal_node.image = D.images.load(normal_path)
                normalmap_node = mat.node_tree.nodes.new(type="ShaderNodeNormalMap")
                mat.node_tree.links.new(tex_image_normal_node.outputs['Color'], normalmap_node.inputs["Color"])
                mat.node_tree.links.new(normalmap_node.outputs['Normal'], principled_node.inputs[22])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_normal_node.inputs["Vector"])

                # Displacement
                tex_image_displacement_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                displacement_path = self._material_path + '\\Sand_Fine_sjzkfega_4K_surface_ms\\sjzkfega_4K_Displacement.exr'
                tex_image_displacement_node.image = D.images.load(displacement_path)
                displacement_node = mat.node_tree.nodes.new(type="ShaderNodeDisplacement")
                output_node = mat.node_tree.nodes.get("Material Output")
                mat.node_tree.links.new(tex_image_displacement_node.outputs['Color'], displacement_node.inputs["Height"])
                mat.node_tree.links.new(displacement_node.outputs['Displacement'], output_node.inputs["Displacement"])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_displacement_node.inputs["Vector"])

            elif material_k == "sand-fine-photogrammable":
                mat.node_tree.links.new(texture_coordinate_node.outputs['Normal'], mapping_node.inputs["Vector"])

                # Albedo
                tex_image_albedo_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                albedo_path = self._material_path + '\\Sand_Fine_sjzkfega_4K_surface_ms\\sjzkfega_4K_Albedo.jpg'
                tex_image_albedo_node.image = D.images.load(albedo_path)
                mat.node_tree.links.new(tex_image_albedo_node.outputs['Color'], principled_node.inputs[0])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_albedo_node.inputs["Vector"])

                # Roughness
                principled_node.inputs["Roughness"].default_value = 1
                # Normal
                tex_image_normal_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                normal_path = self._material_path + '\\Sand_Fine_sjzkfega_4K_surface_ms\\sjzkfega_4K_Normal.jpg'
                tex_image_normal_node.image = D.images.load(normal_path)
                normalmap_node = mat.node_tree.nodes.new(type="ShaderNodeNormalMap")
                mat.node_tree.links.new(tex_image_normal_node.outputs['Color'], normalmap_node.inputs["Color"])
                mat.node_tree.links.new(normalmap_node.outputs['Normal'], principled_node.inputs[22])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_normal_node.inputs["Vector"])

                # Displacement
                tex_image_displacement_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                displacement_path = self._material_path + '\\Sand_Fine_sjzkfega_4K_surface_ms\\sjzkfega_4K_Displacement.exr'
                tex_image_displacement_node.image = D.images.load(displacement_path)
                displacement_node = mat.node_tree.nodes.new(type="ShaderNodeDisplacement")
                output_node = mat.node_tree.nodes.get("Material Output")
                mat.node_tree.links.new(tex_image_displacement_node.outputs['Color'], displacement_node.inputs["Height"])
                mat.node_tree.links.new(displacement_node.outputs['Displacement'], output_node.inputs["Displacement"])
                mat.node_tree.links.new(mapping_node.outputs['Vector'], tex_image_displacement_node.inputs["Vector"])



            elif material_k == "plane-material":
                # Albedo
                tex_image_albedo_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                albedo_path = self._material_path + '\\Concrete_Rough_sdijbcwb_4K_surface_ms\\sdijbcwb_4K_Albedo.jpg'
                tex_image_albedo_node.image = D.images.load(albedo_path)
                mat.node_tree.links.new(tex_image_albedo_node.outputs['Color'], principled_node.inputs[0])
                # Roughness
                tex_image_roughness_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                roughness_path = self._material_path + '\\Concrete_Rough_sdijbcwb_4K_surface_ms\\sdijbcwb_4K_Roughness.jpg'
                tex_image_roughness_node.image = D.images.load(roughness_path)
                mat.node_tree.links.new(tex_image_roughness_node.outputs['Color'], principled_node.inputs[9])
                # Normal
                tex_image_normal_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                normal_path = self._material_path + '\\Concrete_Rough_sdijbcwb_4K_surface_ms\\sdijbcwb_4K_Normal.jpg'
                tex_image_normal_node.image = D.images.load(normal_path)
                normalmap_node = mat.node_tree.nodes.new(type="ShaderNodeNormalMap")
                mat.node_tree.links.new(tex_image_normal_node.outputs['Color'], normalmap_node.inputs["Color"])
                mat.node_tree.links.new(normalmap_node.outputs['Normal'], principled_node.inputs[22])
                # Displacement
                tex_image_displacement_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                displacement_path = self._material_path + '\\Concrete_Rough_sdijbcwb_4K_surface_ms\\sdijbcwb_4K_Displacement.exr'
                tex_image_displacement_node.image = D.images.load(displacement_path)
                displacement_node = mat.node_tree.nodes.new(type="ShaderNodeDisplacement")
                output_node = mat.node_tree.nodes.get("Material Output")
                mat.node_tree.links.new(tex_image_displacement_node.outputs['Color'], displacement_node.inputs["Height"])
                mat.node_tree.links.new(displacement_node.outputs['Displacement'], output_node.inputs["Displacement"])

            elif material_k == "black_plane":
                # Albedo
                principled_node.inputs[0].default_value = (0,0,0,1)
                principled_node.inputs[7].default_value = 0.02

                # tex_image_albedo_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                # albedo_path = self._material_path + '\\Asphalt_Cracked_sivodcfa_4K_surface_ms\\sivodcfa_4K_Albedo.jpg'
                # tex_image_albedo_node.image = D.images.load(albedo_path)
                # mat.node_tree.links.new(tex_image_albedo_node.outputs['Color'], principled_node.inputs[0])
                # Roughness
                tex_image_roughness_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                roughness_path = self._material_path + '\\Asphalt_Cracked_sivodcfa_4K_surface_ms\\sivodcfa_4K_Roughness.jpg'
                tex_image_roughness_node.image = D.images.load(roughness_path)
                mat.node_tree.links.new(tex_image_roughness_node.outputs['Color'], principled_node.inputs[9])
                # # Normal
                # tex_image_normal_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                # normal_path = self._material_path + '\\Asphalt_Cracked_sivodcfa_4K_surface_ms\\sivodcfa_4K_Normal.jpg'
                # tex_image_normal_node.image = D.images.load(normal_path)
                # normalmap_node = mat.node_tree.nodes.new(type="ShaderNodeNormalMap")
                # mat.node_tree.links.new(tex_image_normal_node.outputs['Color'], normalmap_node.inputs["Color"])
                # mat.node_tree.links.new(normalmap_node.outputs['Normal'], principled_node.inputs[22])
                # # Displacement
                # tex_image_displacement_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                # displacement_path = self._material_path + '\\Asphalt_Cracked_sivodcfa_4K_surface_ms\\sivodcfa_4K_Displacement.exr'
                # tex_image_displacement_node.image = D.images.load(displacement_path)
                # displacement_node = mat.node_tree.nodes.new(type="ShaderNodeDisplacement")
                # output_node = mat.node_tree.nodes.get("Material Output")
                # mat.node_tree.links.new(tex_image_displacement_node.outputs['Color'], displacement_node.inputs["Height"])
                # mat.node_tree.links.new(displacement_node.outputs['Displacement'], output_node.inputs["Displacement"])

            elif material_k == "asphalt_2":
                # Albedo
                tex_image_albedo_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                albedo_path = self._material_path + '\\Asphalt_Cracked_sivodcfa_4K_surface_ms\\sivodcfa_4K_Albedo.jpg'
                tex_image_albedo_node.image = D.images.load(albedo_path)
                mat.node_tree.links.new(tex_image_albedo_node.outputs['Color'], principled_node.inputs[0])
                # Roughness
                tex_image_roughness_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                roughness_path = self._material_path + '\\Asphalt_Cracked_sivodcfa_4K_surface_ms\\sivodcfa_4K_Roughness.jpg'
                tex_image_roughness_node.image = D.images.load(roughness_path)
                mat.node_tree.links.new(tex_image_roughness_node.outputs['Color'], principled_node.inputs[9])
                # Normal
                tex_image_normal_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                normal_path = self._material_path + '\\Asphalt_Cracked_sivodcfa_4K_surface_ms\\sivodcfa_4K_Normal.jpg'
                tex_image_normal_node.image = D.images.load(normal_path)
                normalmap_node = mat.node_tree.nodes.new(type="ShaderNodeNormalMap")
                mat.node_tree.links.new(tex_image_normal_node.outputs['Color'], normalmap_node.inputs["Color"])
                mat.node_tree.links.new(normalmap_node.outputs['Normal'], principled_node.inputs[22])
                # Displacement
                tex_image_displacement_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                displacement_path = self._material_path + '\\Asphalt_Cracked_sivodcfa_4K_surface_ms\\sivodcfa_4K_Displacement.exr'
                tex_image_displacement_node.image = D.images.load(displacement_path)
                displacement_node = mat.node_tree.nodes.new(type="ShaderNodeDisplacement")
                output_node = mat.node_tree.nodes.get("Material Output")
                mat.node_tree.links.new(tex_image_displacement_node.outputs['Color'], displacement_node.inputs["Height"])
                mat.node_tree.links.new(displacement_node.outputs['Displacement'], output_node.inputs["Displacement"])


            elif material_k == "concrete_rough":
                # Albedo
                tex_image_albedo_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                albedo_path = self._material_path + '\\Concrete_Rough_sdijbcwb_4K_surface_ms\\sdijbcwb_4K_Albedo.jpg'
                tex_image_albedo_node.image = D.images.load(albedo_path)
                mat.node_tree.links.new(tex_image_albedo_node.outputs['Color'], principled_node.inputs[0])
                # Roughness
                tex_image_roughness_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                roughness_path = self._material_path + '\\Concrete_Rough_sdijbcwb_4K_surface_ms\\sdijbcwb_4K_Roughness.jpg'
                tex_image_roughness_node.image = D.images.load(roughness_path)
                mat.node_tree.links.new(tex_image_roughness_node.outputs['Color'], principled_node.inputs[9])
                # Normal
                tex_image_normal_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                normal_path = self._material_path + '\\Concrete_Rough_sdijbcwb_4K_surface_ms\\sdijbcwb_4K_Normal.jpg'
                tex_image_normal_node.image = D.images.load(normal_path)
                normalmap_node = mat.node_tree.nodes.new(type="ShaderNodeNormalMap")
                mat.node_tree.links.new(tex_image_normal_node.outputs['Color'], normalmap_node.inputs["Color"])
                mat.node_tree.links.new(normalmap_node.outputs['Normal'], principled_node.inputs[22])
                # Displacement
                tex_image_displacement_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                displacement_path = self._material_path + '\\Concrete_Rough_sdijbcwb_4K_surface_ms\\sdijbcwb_4K_Displacement.exr'
                tex_image_displacement_node.image = D.images.load(displacement_path)
                displacement_node = mat.node_tree.nodes.new(type="ShaderNodeDisplacement")
                output_node = mat.node_tree.nodes.get("Material Output")
                mat.node_tree.links.new(tex_image_displacement_node.outputs['Color'], displacement_node.inputs["Height"])
                mat.node_tree.links.new(displacement_node.outputs['Displacement'], output_node.inputs["Displacement"])
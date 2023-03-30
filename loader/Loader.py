import logging
import os

logger = logging.getLogger("Loader")

class Loader():

    @staticmethod
    def get_shapenet_meshes(shapenet_dir):
        meshes = []
        for root, dirnames, filenames in os.walk(shapenet_dir):
            for f in filenames:
                if f.endswith('.obj'):
                    model_name = root.split('\\')[3] + "_" + root.split('\\')[4]
                    # select only model that have texture, which are inside model_dir/../images
                    absolute_path = os.path.join(root, f)
                    if os.path.isdir(os.path.normpath(os.path.join(root, '..//images'))):
                        meshes.append((absolute_path, model_name))
        logger.info(f"SHAPENET\t{len(meshes)}")
        return meshes

    @staticmethod
    def get_custom_models_meshes(custom_model_dir):
        meshes = []
        for root, dirnames, filenames in os.walk(custom_model_dir):
            for f in filenames:
                if f.endswith('.obj'):
                    model_name = f.split(".")[0]
                    absolute_path = os.path.join(root, f)
                    meshes.append((absolute_path, model_name))
        logger.info(f"CUSTOM\t\t{len(meshes)}")
        return meshes

    @staticmethod
    def get_meshes(datasets):
        meshes = []
        logger.info("DATASET\t\tCOUNT")
        for dataset in datasets:
            dataset_name = dataset["name"]
            dataset_path = dataset["path"]
            
            logger.info(f"{dataset_name}\t\t{dataset_path}")
            if dataset_name == "shapenet":                
                meshes = meshes + Loader.get_shapenet_meshes(dataset_path)
            elif dataset_name == "custom_models":
                meshes = meshes + Loader.get_custom_models_meshes(dataset_path)
        logger.info(f"---------------------")
        logger.info(f"TOTAL\t\t{len(meshes)}")
        return meshes
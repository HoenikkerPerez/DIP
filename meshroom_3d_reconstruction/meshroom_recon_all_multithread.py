import math
import shutil
import os
import argparse
from queue import Queue
from timerClock import TimerClock
from threading import Thread

MESHROOM_BINDIR = 'Meshroom-2021.1.0-win64\\Meshroom-2021.1.0\\aliceVision\\bin'
VERBOSELEVEL = 'error'
    


def SilentMkdir(theDir):
    try:
        os.mkdir(theDir)
    except FileExistsError:
        return False
    return True

def consumer(queue, i):
    print('Consumer: Running')
    while True:
        item = queue.get()
        if item is None:
            break
        MESHROOM_CACHE_TMP, image_path, output_path,  model_dir, material = item
        main(MESHROOM_CACHE_TMP, image_path, output_path,  model_dir, material)
        print(f'>consumer got {item}')
    print(f'Consumer {i}: Done')

def Node_00_CameraInit(baseDir, srcImageDir):
    SilentMkdir(baseDir + "/00_CameraInit")

    binName = MESHROOM_BINDIR + "\\aliceVision_cameraInit.exe"
    dstDir = baseDir + "/00_CameraInit/"
    cmdLine = binName
    cmdLine = cmdLine + f' --defaultFieldOfView 45.0 --verboseLevel {VERBOSELEVEL} --sensorDatabase "{MESHROOM_BINDIR}\\..\\share\\aliceVision\\cameraSensors.db" --allowSingleView 1'
    cmdLine = cmdLine + f' --imageFolder "{srcImageDir}"'
    cmdLine = cmdLine + f' --output "{dstDir}\\cameraInit.sfm"'
    print(cmdLine)
    os.system(cmdLine)

    return 0


def Node_01_FeatureExtraction(baseDir, numImages, groupSize):
    SilentMkdir(baseDir + "/01_FeatureExtraction")

    srcSfm = baseDir + "/00_CameraInit/cameraInit.sfm"

    binName = MESHROOM_BINDIR + "\\aliceVision_featureExtraction.exe"

    dstDir = baseDir + "/01_FeatureExtraction/"

    numGroups = math.ceil(numImages / groupSize)

    for groupIter in range(numGroups):
        gStart = groupSize * groupIter
        gSize = min(groupSize, numImages - gStart)
        print("DepthMap Group %d/%d: %d, %d" % (groupIter, numGroups, gStart, gSize))
        exec_cmd = f'''{binName} \
                    --describerTypes sift \
                    --forceCpuExtraction False \
                    --verboseLevel {VERBOSELEVEL} \
                    --describerPreset normal \
                    --rangeStart {gStart} \
                    --rangeSize {gSize} \
                    --input "{srcSfm}" \
                    --output "{dstDir}"
                    '''

        print(exec_cmd)
        os.system(exec_cmd)

    return 0


def Node_02_ImageMatching(baseDir):
    SilentMkdir(baseDir + "/02_ImageMatching")

    srcSfm = baseDir + "/00_CameraInit/cameraInit.sfm"
    srcFeatures = baseDir + "/01_FeatureExtraction/"
    dstMatches = baseDir + "/02_ImageMatching/imageMatches.txt"

    binName = MESHROOM_BINDIR + "\\aliceVision_imageMatching.exe"

    cmdLine = binName
    cmdLine = cmdLine + " --minNbImages 200 --tree "" --maxDescriptors 500 --verboseLevel " + VERBOSELEVEL + " --weights "" --nbMatches 50"
    cmdLine = cmdLine + " --input \"" + srcSfm + "\""
    cmdLine = cmdLine + " --featuresFolder \"" + srcFeatures + "\""
    cmdLine = cmdLine + " --output \"" + dstMatches + "\""

    print(cmdLine)
    os.system(cmdLine)

    return 0


def Node_03_FeatureMatching(baseDir, numImages, groupSize):
    SilentMkdir(baseDir + "/03_FeatureMatching")

    srcSfm = baseDir + "/00_CameraInit/cameraInit.sfm"
    srcFeatures = baseDir + "/01_FeatureExtraction/"
    srcImageMatches = baseDir + "/02_ImageMatching/imageMatches.txt"
    dstMatches = baseDir + "/03_FeatureMatching"

    binName = MESHROOM_BINDIR + "\\aliceVision_featureMatching.exe"

    numGroups = math.ceil(numImages / groupSize)

    # for groupIter in range(numGroups):
        # gStart = groupSize * groupIter
        # gSize = min(groupSize, numImages - gStart)
        # print("DepthMap Group %d/%d: %d, %d" % (groupIter, numGroups, gStart, gSize))

    exec_cmd = f'''{binName} \
            --verboseLevel {VERBOSELEVEL} \
            --describerTypes sift \
            --maxMatches 0 \
            --exportDebugFiles False \
            --savePutativeMatches False \
            --guidedMatching False \
            --geometricEstimator acransac \
            --geometricFilterType fundamental_matrix \
            --maxIteration 2048 \
            --distanceRatio 0.8 \
            --photometricMatchingMethod ANN_L2 \
            --imagePairsList "{srcImageMatches}" \
            --input "{srcSfm}" \
            --featuresFolders "{srcFeatures}" \
            --output "{dstMatches}"
            '''

    print(exec_cmd)
    os.system(exec_cmd)
    return 0


def Node_04_StructureFromMotion(baseDir):
    SilentMkdir(baseDir + "/04_StructureFromMotion")

    srcSfm = baseDir + "/00_CameraInit/cameraInit.sfm"
    srcFeatures = baseDir + "/01_FeatureExtraction/"
    srcImageMatches = baseDir + "/02_ImageMatching/imageMatches.txt"
    srcMatches = baseDir + "/03_FeatureMatching"
    dstDir = baseDir + "/04_StructureFromMotion"

    binName = MESHROOM_BINDIR + "\\aliceVision_incrementalSfm.exe"

    exec_cmd = f'''{binName} \
                   --minAngleForLandmark 2.0 \
                   --minNumberOfObservationsForTriangulation 2 \
                   --maxAngleInitialPair 40.0 \
                   --maxNumberOfMatches 0 \
                   --localizerEstimator acransac \
                   --describerTypes sift \
                   --lockScenePreviouslyReconstructed False \
                   --localBAGraphDistance 1 \
                   --initialPairA "" \
                   --initialPairB "" \
                   --interFileExtension .abc \
                   --useLocalBA True \
                   --minInputTrackLength 2 \
                   --useOnlyMatchesFromInputFolder False \
                   --verboseLevel {VERBOSELEVEL} \
                   --minAngleForTriangulation 3.0 \
                   --maxReprojectionError 4.0 \
                   --minAngleInitialPair 5.0 \
                   --input "{srcSfm}" \
                   --featuresFolders "{srcFeatures}" \
                   --matchesFolders "{srcMatches}" \
                   --outputViewsAndPoses "{dstDir}/cameras.sfm" \
                   --extraInfoFolder "{dstDir}" \
                   --output "{dstDir}/sfm.abc"
                '''
    print(exec_cmd)
    if os.system(exec_cmd) != 0:
        print(f"ERROR: {__name__}")
        return -1
    return 0


def Node_04b_ConvertSfMFormat(baseDir):
    SilentMkdir(baseDir + "/04b_ConvertSfMFormat")
    srcViewAndPosesSfm = baseDir + "/04b_ConvertSfMFormat/sfm.json"
    srcSfm = baseDir + "/04_StructureFromMotion/cameras.sfm"
    binName = MESHROOM_BINDIR + "\\aliceVision_convertSfMFormat.exe"

    exec_cmd = f'''{binName} \
                       --input "{srcSfm}" \
                       --output "{srcViewAndPosesSfm}" \
                       --describerTypes sift \
                       --views True \
                       --intrinsics True \
                       --extrinsics True \
                       --structure True \
                       --observations True \
                       --verboseLevel {VERBOSELEVEL}
                    '''
    print(exec_cmd)
    if os.system(exec_cmd) != 0:
        print(f"ERROR: {__name__}")
        return -1
    return 0


def Node_05_PrepareDenseScene(baseDir):
    SilentMkdir(baseDir + "/05_PrepareDenseScene")

    # srcSfm = baseDir + "/04_StructureFromMotion/cameras.sfm"
    srcSfm = baseDir + "/04_StructureFromMotion/sfm.abc"
    dstDir = baseDir + "/05_PrepareDenseScene"

    binName = MESHROOM_BINDIR + "\\aliceVision_prepareDenseScene.exe"
    exec_cmd = f'''{binName} \
                   --input "{srcSfm}" \
                   --output "{dstDir}" \
                   --verboseLevel {VERBOSELEVEL}
                '''
    print(exec_cmd)
    if os.system(exec_cmd) != 0:
        print(f"ERROR: {__name__}")
        return -1
    return 0


def Node_07_DepthMap(baseDir, numImages, groupSize):
    SilentMkdir(baseDir + "/07_DepthMap")

    # numGroups = (numImages + (groupSize - 1)) / groupSize
    numGroups = math.ceil(numImages / groupSize)
    imagesFolder = baseDir + "/05_PrepareDenseScene"
    srcIni = baseDir + "/04_StructureFromMotion/sfm.abc"
    binName = MESHROOM_BINDIR + "\\aliceVision_depthMapEstimation.exe"
    dstDir = baseDir + "/07_DepthMap"

    for groupIter in range(numGroups):
        gStart = groupSize * groupIter
        # gSize = min(groupSize, numImages - groupStart)
        gSize = min(groupSize, numImages - gStart)
        print("DepthMap Group %d/%d: %d, %d" % (groupIter, numGroups, gStart, gSize))
        exec_cmd = f'''{binName} \
                    --sgmGammaC 5.5 \
                    --sgmWSH 4 \
                    --refineGammaP 8.0 \
                    --refineSigma 15 \
                    --refineNSamplesHalf 150 \
                    --sgmMaxTCams 10 \
                    --refineWSH 3 \
                    --downscale 2 \
                    --refineMaxTCams 6 \
                    --refineGammaC 15.5 \
                    --sgmGammaP 8.0 \
                    --refineNiters 100 \
                    --refineNDepthsToRefine 31 \
                    --refineUseTcOrRcPixSize False \
                    --imagesFolder "{imagesFolder}" \
                    --input "{srcIni}" \
                    --output "{dstDir}" \
                    --rangeStart {gStart} \
                    --rangeSize {gSize} \
                    --verboseLevel {VERBOSELEVEL}
                    '''
        # --imagesFolder {}
        print(exec_cmd)
        if os.system(exec_cmd) != 0:
            print(f"ERROR: {__name__}")
            return -1

    # cmd = "aliceVision_depthMapEstimation  --sgmGammaC 5.5 --sgmWSH 4 --refineGammaP 8.0 --refineSigma 15 --refineNSamplesHalf 150 --sgmMaxTCams 10 --refineWSH 3 --downscale 2 --refineMaxTCams 6 --verboseLevel info --refineGammaC 15.5 --sgmGammaP 8.0 --ini \"c:/users/geforce/appdata/local/temp/MeshroomCache/PrepareDenseScene/4f0d6d9f9d072ed05337fd7c670811b1daa00e62/mvs.ini\" --refineNiters 100 --refineNDepthsToRefine 31 --refineUseTcOrRcPixSize False --output \"c:/users/geforce/appdata/local/temp/MeshroomCache/DepthMap/18f3bd0a90931bd749b5eda20c8bf9f6dab63af9\" --rangeStart 0 --rangeSize 3"
    # cmd = binName + " --sgmGammaC 5.5 --sgmWSH 4 --refineGammaP 8.0 --refineSigma 15 --refineNSamplesHalf 150 --sgmMaxTCams 10 --refineWSH 3 --downscale 2 --refineMaxTCams 6 --verboseLevel info --refineGammaC 15.5 --sgmGammaP 8.0 --ini \"c:/users/geforce/appdata/local/temp/MeshroomCache/PrepareDenseScene/4f0d6d9f9d072ed05337fd7c670811b1daa00e62/mvs.ini\" --refineNiters 100 --refineNDepthsToRefine 31 --refineUseTcOrRcPixSize False --output \"build_files/07_DepthMap/\" --rangeStart 0 --rangeSize 3"
    # cmd = binName + " --sgmGammaC 5.5 --sgmWSH 4 --refineGammaP 8.0 --refineSigma 15 --refineNSamplesHalf 150 --sgmMaxTCams 10 --refineWSH 3 --downscale 2 --refineMaxTCams 6 --verboseLevel info --refineGammaC 15.5 --sgmGammaP 8.0 --ini \"" + srcIni + "\" --refineNiters 100 --refineNDepthsToRefine 31 --refineUseTcOrRcPixSize False --output \"build_files/07_DepthMap/\" --rangeStart 0 --rangeSize 3"
    # print(cmd)
    # os.system(cmd)

    return 0


def Node_08_DepthMapFilter(baseDir, numImages, groupSize):
    SilentMkdir(baseDir + "/08_DepthMapFilter")

    binName = MESHROOM_BINDIR + "\\aliceVision_depthMapFiltering.exe"
    dstDir = baseDir + "/08_DepthMapFilter"
    srcDepthDir = baseDir + "/07_DepthMap"
    srcIni = baseDir + "/04_StructureFromMotion/sfm.abc"

    numGroups = math.ceil(numImages / groupSize)

    for groupIter in range(numGroups):
        gStart = groupSize * groupIter
        gSize = min(groupSize, numImages - gStart)
        print("DepthMap Group %d/%d: %d, %d" % (groupIter, numGroups, gStart, gSize))

        exec_cmd = f'''{binName} \
                --minNumOfConsistentCamsWithLowSimilarity 4 \
                --minNumOfConsistentCams 3 \
                --pixSizeBall 0 \
                --pixSizeBallWithLowSimilarity 0 \
                --nNearestCams 10 \
                --input "{srcIni}" \
                --depthMapsFolder "{srcDepthDir}" \
                --output "{dstDir}" \
                --verboseLevel {VERBOSELEVEL}'''
        print(exec_cmd)
        if os.system(exec_cmd) != 0:
            print(f"ERROR: {__name__}")
            return -1
    return 0


def Node_09_Meshing(baseDir):
    SilentMkdir(baseDir + "/09_Meshing")

    binName = MESHROOM_BINDIR + "\\aliceVision_meshing.exe"
    srcIni = baseDir + "/04_StructureFromMotion/sfm.abc"
    srcDepthFilterDir = baseDir + "/08_DepthMapFilter"
    srcDepthMapDir = baseDir + "/07_DepthMap"

    dstDir = baseDir + "/09_Meshing"

    exec_cmd = f'''{binName} \
--simGaussianSizeInit 10.0 \
--maxInputPoints 50000000 \
--repartition multiResolution \
--simGaussianSize 10.0 \
--simFactor 15.0 \
--voteMarginFactor 4.0 \
--contributeMarginFactor 2.0 \
--minStep 2 \
--pixSizeMarginFinalCoef 4.0 \
--maxPoints 5000000 \
--maxPointsPerVoxel 1000000 \
--angleFactor 15.0 \
--partitioning singleBlock \
--minAngleThreshold 1.0 \
--pixSizeMarginInitCoef 2.0 \
--refineFuse True \
--saveRawDensePointCloud True \
--seed 0 \
--input "{srcIni}" \
--depthMapsFolder "{srcDepthFilterDir}" \
--output "{dstDir}/densePointCloud.abc" \
--outputMesh "{dstDir}/mesh.obj" \
--verboseLevel {VERBOSELEVEL}'''
    # --depthMapsFilterFolder "{srcDepthFilterDir}" \

    print(exec_cmd)
    if os.system(exec_cmd) != 0:
        print(f"ERROR: {__name__}")
        return -1
    return 0


def Node_09b_ConvertSfMFormat_2(baseDir):
    SilentMkdir(baseDir + "/09b_ConvertSfMFormat_2")
    srcRawPointCloud = baseDir + "/09_Meshing/densePointCloud.abc"
    outConvertedRawPointCLoud = baseDir + "/09b_ConvertSfMFormat_2/densePointCloud.ply"
    binName = MESHROOM_BINDIR + "\\aliceVision_convertSfMFormat.exe"

    exec_cmd = f'''{binName} \
                       --input "{srcRawPointCloud}" \
                       --output "{outConvertedRawPointCLoud}" \
                       --describerTypes unknown \
                       --views False \
                       --intrinsics False \
                       --extrinsics False \
                       --structure True \
                       --observations False \
                       --verboseLevel {VERBOSELEVEL}
                    '''
    print(exec_cmd)
    if os.system(exec_cmd) != 0:
        print(f"ERROR: {__name__}")
        return -1
    return 0


def Node_10_MeshFiltering(baseDir):
    """
    Lapacian Filtering
    :param baseDir:
    :return:
    """
    SilentMkdir(baseDir + "/10_MeshFiltering")

    binName = MESHROOM_BINDIR + "\\aliceVision_meshFiltering.exe"

    srcMesh = baseDir + "/09_Meshing/mesh.obj"
    dstMesh = baseDir + "/10_MeshFiltering/mesh.obj"

    exec_cmd = f'''{binName} \
--filterLargeTrianglesFactor 60.0 \
--filteringIterations 1 \
--smoothingIterations 5 \
--keepLargestMeshOnly 0 \
--input "{srcMesh}" \
--output "{dstMesh}" \
--verboseLevel {VERBOSELEVEL}'''

    # TODO try: --filteringIterations 5
    # TODO try: --keepLargestMeshOnly True
    print(exec_cmd)
    if os.system(exec_cmd) != 0:
        print(f"ERROR: {__name__}")
        return -1

    return 0


def Node_11_Texturing(baseDir):
    SilentMkdir(baseDir + "/11_Texturing")

    binName = MESHROOM_BINDIR + "\\aliceVision_texturing.exe"

    srcMesh = baseDir + "/10_MeshFiltering/mesh.obj"
    # srcRecon = baseDir + "/09_Meshing/denseReconstruction.bin"
    # srcIni = baseDir + "/05_PrepareDenseScene/mvs.ini"
    srcIni = baseDir + "/09_Meshing/densePointCloud.abc"
    dstDir = baseDir + "/11_Texturing"
    imagesFolder = baseDir + "/05_PrepareDenseScene"
    # --textureSide 8192 \
    # --downscale 2 \
    # --padding 15 \
    # --inputDenseReconstruction "{srcRecon}" \ depr
    exec_cmd = f'''{binName} \
--unwrapMethod Basic \
--outputTextureFileType png \
--flipNormals False \
--fillHoles False \
--inputMesh "{srcMesh}" \
--input "{srcIni}" \
--imagesFolder "{imagesFolder}" \
--output "{dstDir}" \
--verboseLevel {VERBOSELEVEL}'''

    print(exec_cmd)
    if os.system(exec_cmd) != 0:
        print(f"ERROR: {__name__}")
        return -1

    return 0


def Export_Results(baseDir, dstDir):
    """
    Export camera pose, pointcloud and mesh
    :param baseDir:
    :return:
    """
    srcViewAndPosesSfm = baseDir + "/04b_ConvertSfMFormat/sfm.json"
    dstViewAndPosesSfm = dstDir + "/sfm.json"
    
    srcRawDensePointCloud = baseDir + "/09b_ConvertSfMFormat_2/densePointCloud.ply"
    dstRawDensePointCloud = dstDir + "/densePointCloud.ply"
    
    srcMesh = baseDir + "/09_Meshing/mesh.obj"
    dstMesh = dstDir + "/mesh.obj"

    try:
        shutil.copyfile(srcViewAndPosesSfm, dstViewAndPosesSfm)
        shutil.copyfile(srcRawDensePointCloud, dstRawDensePointCloud)
        shutil.copyfile(srcMesh, dstMesh)
        return 0
    except:
        return -1


def is_results_exported(dstDir):
    dstViewAndPosesSfm = dstDir + "/sfm.json"
    dstRawDensePointCloud = dstDir + "/densePointCloud.ply"
    dstMesh = dstDir + "/mesh.obj"
    
    if os.path.exists(dstViewAndPosesSfm) and os.path.exists(dstRawDensePointCloud) and os.path.exists(dstMesh):
        return True
    else:
        return False

def main(cacheDir, srcImageDir, dstModelDir, model_name, material_name):
    """
    baseDir: root directory of intermediate node results
    srcImageDir: Input images

    """
    print()
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ")
    print("Bin dir    : %s" % MESHROOM_BINDIR)
    print("Cache dir   : %s" % cacheDir)
    print("Image dirs : %s" % srcImageDir)
    print("Model      : %s" % model_name)
    print("Material   : %s" % material_name)
    
    if not os.path.isdir(cacheDir):
        os.makedirs(cacheDir)
    
    # if already computed return
    if is_results_exported(dstModelDir):
        print(f"Already exported: {dstModelDir}")
        return 1
    
    with TimerClock(f"RUN_{model_name}_material_name"):
        numImages = len([x for x in os.listdir(srcImageDir)])
  
        # PHOTOGRAMMETRY PIPELINE
        print(f"\n\n\n\n[Node_00_CameraInit] - {srcImageDir}")
        if Node_00_CameraInit(cacheDir, srcImageDir) != 0:
            return -1
        print(f"\n\n\n\n[Node_01_FeatureExtraction - {srcImageDir}]")
        if Node_01_FeatureExtraction(cacheDir, numImages, 40) != 0:
            return -1
        print(f"\n\n\n\n[Node_02_ImageMatching - {srcImageDir}]")
        if Node_02_ImageMatching(cacheDir) != 0:
            return -1
        print(f"\n\n\n\n[Node_03_FeatureMatching - {srcImageDir}]")
        if Node_03_FeatureMatching(cacheDir, numImages, 20) != 0:
            return -1
        print(f"\n\n\n\n[Node_04_StructureFromMotion - {srcImageDir}]")
        if Node_04_StructureFromMotion(cacheDir) != 0:
            return -1
        print(f"\n\n\n\n[Node_04b_ConvertSfMFormat - {srcImageDir}]")
        if Node_04b_ConvertSfMFormat(cacheDir) != 0:
            return -1
        print(f"\n\n\n\n[Node_05_PrepareDenseScene - {srcImageDir}]")
        if Node_05_PrepareDenseScene(cacheDir) != 0:
            return -1
        print(f"\n\n\n\n[Node_07_DepthMap - {srcImageDir}]")
        # Node_07_DepthMap(cacheDir, numImages, 200)
        if Node_07_DepthMap(cacheDir, numImages, 3) != 0:
            return -1
        print(f"\n\n\n\n[Node_08_DepthMapFilter - {srcImageDir}]")
        # Node_08_DepthMapFilter(cacheDir, numImages, 200)
        if Node_08_DepthMapFilter(cacheDir, numImages, 10) != 0:
            return -1
        print(f"\n\n\n\n[Node_09_Meshing - {srcImageDir}]")
        if Node_09_Meshing(cacheDir) != 0:
            return -1
        print(f"\n\n\n\n[Node_09b_ConvertSfMFormat_2 - {srcImageDir}]")
        if Node_09b_ConvertSfMFormat_2(cacheDir) != 0:
            return -1
        print(f"\n\n\n\n[Export_Results - {srcImageDir}, {dstModelDir}]")
        if Export_Results(cacheDir, dstModelDir) != 0:
            return -1
        
        # Clean cacheDir
        shutil.rmtree(cacheDir)
        
    return 0


if __name__ == "__main__":
    """
    python meshroom_recon_all.py --rootRenderDirs 
     - renderDirs
          - model1
                  - material1
                          - images
                                  - img1.png
                                  - img2.png
                                  - ...
                  - material2
                  - ...
          - model2
          - ...

    """
    CLI = argparse.ArgumentParser()

    CLI.add_argument(
        "-r",
        "--rootRenderDirs",
        dest='rootRenderDirs',
        help='Root directory of rendered images intermediate node results',
        type=str,
        required=True
    )
    
    CLI.add_argument(
        "-e",
        "--excludedMaterial",
        dest='excludedMaterial',
        help='Name of material to exclude',
        nargs='+',
        type=str,
        default=[]
    )
    args = CLI.parse_args()
    
    MESHROOM_CACHE_TMP = 'temp'
    
    queue = Queue()
    rootDir = os.path.normpath(args.rootRenderDirs)
    for model_dir in os.listdir(rootDir):
    
        for material in os.listdir(os.path.join(rootDir, model_dir)):
            material_path = os.path.join(os.path.join(rootDir, model_dir), material)
            if not os.path.isdir(material_path):
                continue
            if material in args.excludedMaterial:
                continue
            
            output_path = os.path.join(material_path, "eval")
            SilentMkdir(output_path)            
            image_path = os.path.join(material_path, "images")
            print(image_path, output_path)
            
            queue.put((MESHROOM_CACHE_TMP, image_path, output_path,  model_dir, material))
            
    queue.put(None)
    consumers = [Thread(target=consumer, args=(queue,i)) for i in range(8)]
    for consumer in consumers:
        consumer.start()
    for consumer in consumers:
        consumer.join()


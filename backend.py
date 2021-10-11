# From Python
# It requires OpenCV installed for Python
import sys
import cv2
import os
from sys import platform
import argparse
import time

def score(corner1, corner2, coordinates):
    # corner1 upper left point, corner2 down right point
    value = False

    if coordinates[0] != 0 and coordinates[1] != 0:
        if coordinates[0]> corner1[0] and coordinates[0]< corner2[0]:
            if coordinates[1]> corner1[1] and coordinates[1]< corner2[1]:
                value = True

    return value

finalScore = 0
lasttimeSwitch = False

try:
    # Import Openpose (Windows/Ubuntu/OSX)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    try:
        # Windows Import
        if platform == "win32":
            # Change these variables to point to the correct folder (Release/x64 etc.)
            sys.path.append(dir_path + '/../../python/openpose/Release');
            os.environ['PATH']  = os.environ['PATH'] + ';' + dir_path + '/../../x64/Release;' +  dir_path + '/../../bin;'
            import pyopenpose as op
        else:
            # Change these variables to point to the correct folder (Release/x64 etc.)
            sys.path.append('../../python');
            # If you run `make install` (default path is `/usr/local/python` for Ubuntu), you can also access the OpenPose/python module from there. This will install OpenPose and the python library at your desired installation path. Ensure that this is in your python path in order to use it.
            # sys.path.append('/usr/local/python')
            from openpose import pyopenpose as op
    except ImportError as e:
        print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
        raise e

    # Flags
    parser = argparse.ArgumentParser()
    parser.add_argument("--image_dir", default="../../../examples/media/", help="Process a directory of images. Read all standard formats (jpg, png, bmp, etc.).")
    parser.add_argument("--no_display", default=False, help="Enable to disable the visual display.")
    args = parser.parse_known_args()

    # Custom Params (refer to include/openpose/flags.hpp for more parameters)
    params = dict()
    params["model_folder"] = "../../../models/"

    # Add others in path?
    for i in range(0, len(args[1])):
        curr_item = args[1][i]
        if i != len(args[1])-1: next_item = args[1][i+1]
        else: next_item = "1"
        if "--" in curr_item and "--" in next_item:
            key = curr_item.replace('-','')
            if key not in params:  params[key] = "1"
        elif "--" in curr_item and "--" not in next_item:
            key = curr_item.replace('-','')
            if key not in params: params[key] = next_item

    # Construct it from system arguments
    # op.init_argv(args[1])
    # oppython = op.OpenposePython()

    # Starting OpenPose
    opWrapper = op.WrapperPython()
    opWrapper.configure(params)
    opWrapper.start()

    # Read frames on directory
    imagePaths = op.get_images_on_directory(args[0].image_dir)

    vid = cv2.VideoCapture(0)

    while(True):
      
        # Capture the video frame
        # by frame
        ret, frame = vid.read()
        datum = op.Datum()

        datum.cvInputData = frame
        opWrapper.emplaceAndPop(op.VectorDatum([datum]))

        try:

            # print("Body keypoints: \n" + str(datum.poseKeypoints))
            print("Left Hand: " + str(datum.poseKeypoints[0][4]))
            print("Right Hand: " + str(datum.poseKeypoints[0][7]))

            leftHand = [int(datum.poseKeypoints[0][4][0]), int(datum.poseKeypoints[0][4][1])]

            result = datum.cvOutputData

            corner1 = [100,10]
            corner2 = [200,200]

            if score(corner1, corner2, leftHand) and lasttimeSwitch == False:
                finalScore = finalScore + 1
                lasttimeSwitch = True
                cv2.rectangle(result, corner1, corner2, (0, 255, 0), 2)
            elif score(corner1, corner2, leftHand) and lasttimeSwitch == True:
                cv2.rectangle(result, corner1, corner2, (0, 255, 0), 2)
            else:
                lasttimeSwitch = False
                cv2.rectangle(result, corner1, corner2, (255, 255, 255), 2)

            cv2.putText(result, 'Your score is: '+str(finalScore), (10,450), cv2.FONT_HERSHEY_SIMPLEX, 
                    1, (255,255,255), 2, cv2.LINE_AA)
            # Display the resulting frame
            cv2.imshow('frame', result)

            print(lasttimeSwitch)
       
        except:
            print('No players detected!')

        # the 'q' button is set as the
        # quitting button you may use any
        # desired button of your choice
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # After the loop release the cap object
    vid.release()
    # Destroy all the windows
    cv2.destroyAllWindows()

except Exception as e:
    print(e)
    sys.exit(-1)

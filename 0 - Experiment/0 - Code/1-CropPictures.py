import os
import cvlib as cv
import cv2
import json
from PIL import Image

def detect(fileName):
    im = cv2.imread(fileName)
    bbox, label, conf = cv.detect_common_objects(im)

    return(bbox, label, conf)

def cropPicture(ImagesPath, entry):
    # Collect data from the detector
    ImagePath = os.path.join(ImagesPath, entry)
    data = detect(ImagePath)

    # Save data to a json file
    json_obj = json.dumps(data)
    jsonFile = open(ImagePath[:-4] + '.json','w')
    json.dump(json_obj, jsonFile)
    jsonFile.close()
    print("     Detection finished")

    # Crop picture for each book found
    numberOfBooks = 0
    for i in range(len(data[1])):   
        if (data[1][i] == "book"): 
            numberOfBooks = numberOfBooks +1
            # Getting the coordinates
            x0 = float(data[0][i][0])
            y0 = float(data[0][i][1])
            x1 = float(data[0][i][2])
            y1 = float(data[0][i][3])
            # print("          - Bounding box: (" + str(x0) + ", " + str(y0) + ") , (" + str(x1) + ", "  +str(y1) + ")")

            # Cropping image
            im = Image.open(ImagePath)
            im = im.crop((x0, y0, x1, y1))
            cropName = os.path.join(ImagesPath + "Cropped\\" + entry[:-4] + "Crop" + str(i) + ".png")
            # print("            Name of the cropped file: " + cropName)
            im = im.save(cropName)
    print("     " + str(numberOfBooks) + " books detected")
    print("     Cropping finished")


########################################################
# Creating folder for cropped pictures
ImagesPath = "C:\\PepperRecordings\\Part 2\\"
croppedFiles = os.path.join(ImagesPath, "Cropped")
os.mkdir(croppedFiles)


########################################################
# List all files and use detector to crop books
for entry in os.listdir(ImagesPath):
    fullPath = os.path.join(ImagesPath, entry)
    if os.path.isfile(fullPath):
        print(entry)
        cropPicture(ImagesPath, entry)
print("Detection finished, pictures cropped")
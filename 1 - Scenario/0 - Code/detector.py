import cv2
import cvlib as cv
import argparse
import json

def detect(fileName):
    im = cv2.imread(fileName)
    bbox, label, conf = cv.detect_common_objects(im)

    return(bbox, label, conf)


def main(fileName):
    #Collect data from the detector
    data = detect(fileName)

    #Save data to a json file
    json_obj = json.dumps(data)
    jsonFile = open(fileName + '.json','w')
    json.dump(json_obj, jsonFile)
    jsonFile.close()
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, help="Name of the picture to use the detector on")
    
    args = parser.parse_args()

    # print("args: ", args)

    main(args.file)

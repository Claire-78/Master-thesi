import sys
import argparse
import qi
import paramiko
import os
import subprocess
import time
import json
from PIL import Image

def main(app, args):
    
        
    photoCapture = app.session.service("ALPhotoCapture")
    tabletService = app.session.service("ALTabletService")
    tts = app.session.service("ALTextToSpeech")


    ######################################################## 
    # Taking Picture
    PepperPath = "/home/nao/recordings/cameras/library/"
    ComputerPath = "C:\\PepperRecordings\\"
    pictureName = "image"
    pictureFormat = "jpg"
    resolution = 3
    
    photoCapture.setCameraID(0)
    photoCapture.setResolution(resolution)
    photoCapture.setPictureFormat(pictureFormat)

    motionService = app.session.service("ALMotion")

    JointNamesH = ["HeadPitch", "HeadYaw"] # range ([-1,1],[-0.5,0.5]) // HeadPitch :{(-)up,(+)down} , HeadYaw :{(-)left,(+)right}
    pFractionMaxSpeed = 0.1
    HeadA = [0.17,0.07]
    motionService.angleInterpolationWithSpeed(JointNamesH, HeadA, pFractionMaxSpeed)

    print(photoCapture.takePicture(PepperPath, pictureName))
    print("Picture taken!")    


    ########################################################
    # Transfering picture to computer
    t = paramiko.Transport(args.ip, args.port)
    t.connect(username="nao", password="edutech123")
    sftp = paramiko.SFTPClient.from_transport(t)
    files = sftp.listdir(PepperPath)
    # print("Files on Pepper in folder " + PepperPath + ": ")
    # print(files)

    f = pictureName + "." + pictureFormat
    print('Transfering ' + f + '...')
    sftp.get(os.path.join(PepperPath, f),os.path.join(ComputerPath, f))
    print("File transfered.")
    sftp.remove(PepperPath+f)         # This deletes the file from Pepper once it has been transfered to the computer.
    
    tts.say("Picture taken and transfered. Now looking for books in the image.")

    ########################################################
    # Object detection
    imagePath = os.path.join(ComputerPath, f)
    detection_command = ['python3',"detector.py", "--file" , imagePath]
    # print("Python command: "+ detection_command)
    startTime = time.time()
    process = subprocess.call(detection_command)
    elapsedTime = time.time() - startTime
    print("Detection finished in %.2f seconds" % elapsedTime)


    ########################################################
    # Counting books found
    f = open(imagePath + '.json',)
    print("JSON File Name: " + imagePath[:-4] + '.json')
    data = json.load(f)
    data = json.loads(data)
    booksFound = 0
    booksCoordinates = []

    for i in range(len(data[1])):
        if (data[1][i] =="book"):
            booksFound += 1
            booksCoordinates.append(data[0][i])
    print("%s books found" % booksFound)
    tts.say("I have found " + str(booksFound) + " books")


    ########################################################
    # Creating cropped pictures and using OCR to read
    if (booksFound >0):
        textToDisplay = ""
        OCR_command = ['python3',"OCR.py", "--list"]
        for i in range(booksFound):   
            im = Image.open(imagePath) 
            # Getting the coordinates
            x0 = float(booksCoordinates[i][0])
            y0 = float(booksCoordinates[i][1])
            x1 = float(booksCoordinates[i][2])
            y1 = float(booksCoordinates[i][3])
            print("Bounding box: (" + str(x0) + ", " + str(y0) + ") , (" + str(x1) + ", "  +str(y1) + ")")

            # Cropping image
            im = im.crop((x0, y0, x1, y1))
            cropName = os.path.join(imagePath[:-4] + "Crop" + str(i) + ".jpg")
            print("Name of the cropped file: " + cropName)
            im = im.save(cropName)
            # im.close()
            OCR_command.append(cropName)

        tts.say("Using OCR to read the titles.")
        # Using OCR on cropped pictures
        # print("OCR command: " + OCR_command)
        startTime = time.time()
        OCRprocess = subprocess.call(OCR_command)
        elapsedTime = time.time() - startTime
        print("OCR subprocess finished in %.2f seconds" % elapsedTime)
 
        for i in range(booksFound):   
            textFileName = os.path.join(imagePath[:-4] + "Crop" + str(i)+'.txt')
            with open(textFileName, "r") as f:
                textToDisplay += "\n <h1>Book " + str(i) + ": " + f.read() + "</h1>\n"


        #Have Pepper show the text read
        tts.say("Here is what I have read on the spine of the books.")
        tabletService.showWebview("data:text/html," + textToDisplay)
        time.sleep(10)
        tabletService.hideWebview()

   
    
                
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="192.168.137.175",
                        help="Robot IP address. On robot or Local Naoqi: use \
                        '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")
    
    args = parser.parse_args()

    # Initialize qi framework.
    connection_url = "tcp://" + args.ip + ":" + str(args.port)
    app = qi.Application(["Detector",
                          "--qi-url=" + connection_url])
    # Connection
    try:
        app.start()
        main(app, args)
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " +
                str(args.port) + ".\n")

        sys.exit(1)
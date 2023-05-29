import sys
import argparse
import qi
import paramiko
import os

def main(app):
        
    photoCapture = app.session.service("ALPhotoCapture")
    # motionService = app.session.service("ALMotion")


    # JointNamesH = ["HeadPitch", "HeadYaw"] # range ([-1,1],[-0.5,0.5]) // HeadPitch :{(-)up,(+)down} , HeadYaw :{(-)left,(+)right}
    # pFractionMaxSpeed = 0.1
    # HeadA = [0.17,0]
    # motionService.angleInterpolationWithSpeed(JointNamesH, HeadA, pFractionMaxSpeed)


    # Taking Picture
    PepperPath = "/home/nao/recordings/cameras/library/"
    pictureFormat = "png"
    distance = 45
    iteration = 5
    resolutions = [3,6]
    
    photoCapture.setCameraID(0)
    photoCapture.setPictureFormat(pictureFormat)

    for resolution in resolutions:
        photoCapture.setResolution(resolution)
        pictureName = "image_" + str(resolution) + "_" + str(distance) + "_" + str(iteration)
        photoCapture.takePicture(PepperPath, pictureName)
        print("Picture taken!")    


    ########################################################
    # Transfering picture to computer
    ComputerPath = "C:\\PepperRecordings\\Part 1\\"
    t = paramiko.Transport(args.ip, args.port)
    t.connect(username="nao", password="edutech123")
    sftp = paramiko.SFTPClient.from_transport(t)
    files = sftp.listdir(PepperPath)
    print("Files on Pepper in folder" + PepperPath + ": ")
    print(files)

    for resolution in resolutions:
        pictureName = "image_" + str(resolution) + "_" + str(distance) + "_" + str(iteration)
        f = pictureName + "." + pictureFormat
        print('Transfering ' + f + '...')
        sftp.get(os.path.join(PepperPath, f),os.path.join(ComputerPath, f))
        print("File transfered.")
        sftp.remove(PepperPath+f)         # This deletes the file from Pepper once it has been transfered to the computer.

    
                
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="192.168.137.233",
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
        main(app)
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " +
                str(args.port) + ".\n")

        sys.exit(1)
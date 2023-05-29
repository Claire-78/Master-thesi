import argparse
import easyocr
import time

reader = easyocr.Reader(['no'])#,'en'


def main(filesList):
    #Use OCR algorithm
    # print(fileName)
    startTime = time.time()
    for fileName in filesList:
        # print(fileName)
        data = reader.readtext(fileName)
        # print("Text recognized: ")
        # print(data)

        #Save data to a txt file
        # print('Name of txt file: ' + fileName[:-4]+'.txt')
        with open(fileName[:-4]+'.txt', 'w') as f:
            for i in range (len(data)):
                f.write(data[i][1])
    elapsedTime = time.time() - startTime
    print("OCR finished in %.2f seconds" % elapsedTime)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", nargs="+", help="Names of the pictures to use")
    
    args = parser.parse_args()
    main(args.list)
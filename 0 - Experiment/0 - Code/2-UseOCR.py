import os
import pytesseract
import easyocr
import keras_ocr
import math
 
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract'
reader = easyocr.Reader(['en'])
pipeline = keras_ocr.pipeline.Pipeline()

croppedFiles = "C:\\PepperRecordings\\Part 2\\Cropped\\"

def pytess(fileName):
    #Use OCR algorithm
    data = pytesseract.image_to_string(fileName, lang='eng')
    # print("Text recognized: ")
    # print(data)

    #Save data to a txt file
    print('     Name of txt file: ' + fileName[:-4] + 'Pytess.txt')
    with open(fileName+'.txt', 'w') as f:
        f.write(data)

def easyOCR(fileName):
    #Use OCR algorithm
    data = reader.readtext(fileName)
    # print("Text recognized: ")
    # print(data)

    #Save data to a txt file  (only recognized text)
    print('     Name of txt file: ' + fileName[:-4] + 'EasyOCR.txt')
    with open(fileName+'EasyOCR.txt', 'w') as f:
        for i in range (len(data)):
            f.write(data[i][1])
            f.write(" ")

def get_distance(predictions):
    """
    Function returns dictionary with (key,value):
        * text : detected text in image
        * center_x : center of bounding box (x)
        * center_y : center of bounding box (y)
        * distance_from_origin : hypotenuse
        * distance_y : distance between y and origin (0,0)
    """
    
    # Point of origin
    x0, y0 = 0, 0    # Generate dictionary
    detections = []
    for group in predictions:
        # Get center point of bounding box
        top_left_x, top_left_y = group[1][0]
        bottom_right_x, bottom_right_y = group[1][1]
        center_x = (top_left_x + bottom_right_x) / 2
        center_y = (top_left_y + bottom_right_y) / 2    # Use the Pythagorean Theorem to solve for distance from origin
        distance_from_origin = math.dist([x0,y0], [center_x, center_y])    # Calculate difference between y and origin to get unique rows
        distance_y = center_y - y0    # Append all results
        detections.append({
                        'text':group[0],
                        'center_x':center_x,
                        'center_y':center_y,
                        'distance_from_origin':distance_from_origin,
                        'distance_y':distance_y
                    })
    return detections

def distinguish_rows(lst, thresh=15):
    """Function to help distinguish unique rows"""
    sublists = [] 
    for i in range(0, len(lst)-1):
        if lst[i+1]['distance_y'] - lst[i]['distance_y'] <= thresh:
            if lst[i] not in sublists:
                sublists.append(lst[i])
            sublists.append(lst[i+1])
        else:
            yield sublists
            sublists = [lst[i+1]]
    yield sublists

def sorting(predictions, thresh=15, order='yes'):
    """
    Function returns predictions in human readable order 
    from left to right & top to bottom
    """
    predictions2 = get_distance(predictions)
    predictions2 = list(distinguish_rows(predictions2, thresh))    # Remove all empty rows
    predictions2 = list(filter(lambda x:x!=[], predictions2))    # Order text detections in human readable format
    ordered_preds = []
    ylst = ['yes', 'y']
    for pr in predictions2:
        if order in ylst: 
            row = sorted(pr, key=lambda x:x['distance_from_origin'])
            for each in row: 
                ordered_preds.append(each['text'])
    return ordered_preds

def kerasOCR(fileName):
    image = keras_ocr.tools.read(fileName)
    data = pipeline.recognize([image])
    # print("Text recognized: ")
    # print(data)
    text = sorting(data[0])
    # print(text)


    #Save data to a txt file (only recognized text)
    print('     Name of txt file: ' + fileName[:-4] + 'KerasOCR.txt')
    with open(fileName+'KerasOCR.txt', 'w') as f:
        for item in text:
            f.write(item + " ")


########################################################
# For each cropped file, use all 3 OCR algorithms and store data in txt files.
# List all files and use OCR on all
for entry in os.listdir(croppedFiles):
    fullPath = os.path.join(croppedFiles, entry)
    if os.path.isfile(fullPath):
        print(fullPath)
        pytess(fullPath)
        print("     Pytesseract OCR done")
        easyOCR(fullPath)
        print("     EasyOCR done")
        kerasOCR(fullPath)
        print("     KerasOCR done")

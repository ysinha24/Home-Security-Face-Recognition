from PIL import Image
from imutils import paths
import face_recognition
import pickle
import cv2
import os

# iterate through directory of images
imagePaths = list(paths.list_images(r'/home/yash/Development/Arduino Projects/Images'))

knownEncodings = []
knownNames = []

for (i, imagePath) in enumerate(imagePaths):
    # extract the person name from the image path
    name = imagePath.split(os.path.sep)[-2]
    print("[Photo %s/%s] Running on %s" % (str(i+1), len(imagePaths), name))

    # load image to start encoding
    image = cv2.imread(imagePath)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    face_to_process = face_recognition.face_locations(rgb_image, model='hog')
    encodings = face_recognition.face_encodings(rgb_image, face_to_process)

    # check boxes on faces
    save_face_boxes(image, face_to_process)

    # iterate and store facial encodings
    for encoding in encodings:
        knownEncodings.append(encoding)
        knownNames.append(name)

print(knownNames)
print(knownEncodings)

# create pickle serialization
data = {"encodings":knownEncodings, "names":knownNames}
pickle_out = open("encodings.pickle", "wb")
pickle.dump(data, pickle_out)
pickle_out.close()

def save_face_boxes(image, boxes):
    for((top, right, bottom, left), name) in zip(boxes, names):
        cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
        y = top - 15 if top - 15 > 15 else top + 15
        cv2.putText(image, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
            0.75, (0, 255, 0), 2)

    cv2.imshow("Image", image)
    cv2.waitKey(0)

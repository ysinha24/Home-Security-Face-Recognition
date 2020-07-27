from PIL import ImageStat
from PIL import Image
import urllib.request
import mysql.connector
import requests
import face_recognition
from datetime import datetime
import pickle
import sshtunnel
import cv2
from io import BytesIO
import base64
import numpy as np


# get encodings
pickle_in = open("encodings.pickle", "rb")
data = pickle.load(pickle_in)
pickle_in.close()

# database configuration
config = {
  'user': 'yash',
  'password': 'ysinha11',
  'host': 'localhost',
  'database': 'face_recognition',
  'port': 3306,
  'raise_on_warnings': True,
  'charset': "utf8mb4"
}

def main():
    # get detection result of ping sensor from URI
    try:
        response = requests.get("http://192.168.1.29/detect")
        detection = response.text
    except:
        return

    if detection == '1':
        # get image from capture
        try:
            response = requests.get("http://192.168.1.29/capture")
            img = Image.open(BytesIO(response.content))
            img.save("Capture.jpg")
        except:
            return

        # initialize list of names found
        names = []

        # load images and get encodings
        print(brightness("Capture.jpg"))
        image = gamma_correction(cv2.imread("Capture.jpg"))
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


        # find and encode faces
        face_to_process = face_recognition.face_locations(rgb_image, model='hog')
        encodings = face_recognition.face_encodings(rgb_image, face_to_process)

        for encoding in encodings:
            # get results
            results = face_recognition.compare_faces(data["encodings"], encoding)
            name = "Unknown"

            if True in results:
                # put indexes of success in the list
                matchedIdxs = [i for (i, b) in enumerate(results) if b]
                counts = {}

                # count successes of each name
                for i in matchedIdxs:
                	name = data["names"][i]
                	counts[name] = counts.get(name, 0) + 1

                # return the name with highest counts
                name = max(counts, key = counts.get)

            # update the list of names
            names.append(name)


        for ((top, right, bottom, left), name) in zip(face_to_process, names):
            # draw the predicted face name on the image
            cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(image, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

        # write image to disk
        cv2.imwrite("Capture.jpg", image)

        # check output
        print(names)


        # change post request payload based on results
        # no face detected
        if len(names) == 0:
            str_name = 'nobody_or_unclear '

        # known or unknown face detected
        else:
            str_name = ''
            for name in names:
                str_name += (name + ' ')

        # post request payload
        post_data = {"result":str_name[0:-1]}

        # post request back to the ESP32 module
        try:
            requests.post("http://192.168.1.29/person", data = post_data, timeout = 10 )
        except Exception as err:
            raise SystemExit(err)

        # call function to insert into database
        if(str_name != 'nobody_or_unclear'):
            store_on_database(str_name[0:-1])

def store_on_database(names):
    # have to use mysql_native_password or older version since
    # mysql.connector is not compatible with new versions

    # with sshtunnel.SSHTunnelForwarder(
    #     ('localhost', 2222),
    #     ssh_username='yash',
    #     ssh_password='ysinha11',
    #     remote_bind_address=('127.0.0.1', 3306)
    # ) as tunnel:


    # setup connection to db and point to last row
    db = mysql.connector.connect(**config)
    cursor = db.cursor()

    # get data
    time = datetime.now()
    bytes = open('Capture.jpg', 'rb').read()
    blob_val =  base64.b64encode(bytes)


    # mySQL query
    add_image = ("INSERT INTO iot1 "
                "(time, image, names) "
                "VALUES (%s, %s, %s)")

    # tuple of results
    image_details = (time, blob_val, names)

    # insert and commit data
    cursor.execute(add_image, image_details)
    db.commit()

    # close connection
    cursor.close()
    db.close()


def get_image_from_db():
    # connect to database
    db = mysql.connector.connect(**config)
    cursor = db.cursor()

    # run query to get information
    cursor.execute('SELECT image FROM iot1')
    data = cursor.fetchall()

    # decode BLOB to bytes
    utf8_data = base64.b64decode(data[0][0])
    bytes = BytesIO(utf8_data)
    img = Image.open(bytes)

    img.save("DB.jpg")

    # close connection
    cursor.close()
    db.close()

def brightness( im_file ):
   im = Image.open(im_file).convert('L')
   stat = ImageStat.Stat(im)
   return stat.mean[0]

def gamma_correction(image, gamma = 1.75):
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
        for i in np.arange(0, 256)]).astype("uint8")
    # apply gamma correction using the lookup table
    return cv2.LUT(image, table)

# run endlessly
while True:
    main()


### test database
# store_on_database("Yash")
# get_image_from_db()

### test image correction
# image = cv2.imread("Yash.jpg")
# cv2.imwrite("Test.jpg",gamma_correction(image))

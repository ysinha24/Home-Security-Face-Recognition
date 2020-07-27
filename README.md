# Home Security with Face Recognition

<p align="center">
  <img src="https://github.com/ysinha24/Home-Security-Face-Recognition/blob/master/DoorRecognitionIOT.jpg?raw=true" width="350">
</p>
This Project uses multiple ESP32-CAM microcontrollers as an IOT device that detects an individual, takes a picture, and stores the images on a local MySQL database using APIs. These images are further processed using AWS Lambda cloud computing to detect known faces using OpenCV and premade machine learning architectures. The system also sends a real-time SMS text for any unauthorized people, and also analyzes who enters at each time and provides a weekly overview of occurrences.


<p align="center">
  <img src="https://github.com/ysinha24/Home-Security-Face-Recognition/blob/master/ESP32-Recognition%20network.jpg?raw=true" width="600">
</p>

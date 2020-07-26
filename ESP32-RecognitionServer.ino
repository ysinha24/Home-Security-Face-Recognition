#include "esp_camera.h"
#include <WiFi.h>
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"

//
// WARNING!!! Make sure that you have either selected ESP32 Wrover Module,
//            or another board which has PSRAM enabled
//


const int pingPin     = 13;
const int echoPin     = 12;
const int greenLight  = 14;
const int redLight    = 2;
const int pResistor   = 15;
const int flashPin    = 4;

// camera model
#define CAMERA_MODEL_AI_THINKER

#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27

#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

const char* ssid =     "NETGEAR71";
const char* password = "manicprairie768";

void startCameraServer();
void setDetectionBool(bool);
bool getFaceDetection();
bool hasReceivedPostRequest();

void setup() {
  pinMode(pingPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(greenLight, OUTPUT);
  pinMode(redLight, OUTPUT);
  pinMode(pResistor, INPUT);
  pinMode(flashPin, OUTPUT);

  digitalWrite(greenLight, HIGH);
  digitalWrite(redLight, HIGH);

  // resolves brownout issues
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG,0);
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  
  //init with high specs to pre-allocate larger buffers
  if(psramFound()){
    config.frame_size = FRAMESIZE_UXGA;
    config.jpeg_quality = 10;
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_SVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }

  // camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  sensor_t * s = esp_camera_sensor_get();
  s->set_framesize(s, FRAMESIZE_UXGA);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");

  startCameraServer();

  Serial.print("Connected: http://");
  Serial.println(WiFi.localIP());
}

bool found = false;


long getPing() {
  long duration, inches;
  
  digitalWrite(pingPin, LOW);
  delayMicroseconds(2);
  digitalWrite(pingPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(pingPin, LOW);
  delayMicroseconds(2);
  
  duration = pulseIn(echoPin, HIGH);
  inches = microsecondsToInches(duration);

  return inches;
}

long microsecondsToInches(long microsecs) {
  return microsecs / 74 / 2;  
}

int getLightValue() {
  return analogRead(pResistor);
}

void loop() {
  if(getPing() <= 35){
    delay(1000);
    
    // get photoresistor value and flash
//    int x = getLightValue();
//    Serial.println(x);
//    if(getLightValue() > 4000)
//      digitalWrite(flashPin, HIGH);       // turn on flash
      
    found = true;
    Serial.println("Waiting for Script");
    setDetectionBool(found);
    
    // wait until post request
    int count = 0;
    while(!hasReceivedPostRequest()){
      delay(100);
      count++;
      if(count >= 100)
        break;
    }
    digitalWrite(flashPin, LOW);          // turn off flash
    
    // timeout counter reached
    if(count >= 100)
      return;
    
    // display results
    bool faceFound = getFaceDetection();
    // found face
    if(faceFound){
      digitalWrite(greenLight, LOW);
     digitalWrite(redLight, LOW);
      Serial.println("Flash GreenLight");
      digitalWrite(greenLight, HIGH);
      delay(10000);
    }
    // did not find face
    else {
      digitalWrite(greenLight, LOW);
      digitalWrite(redLight, LOW);
      Serial.println("Flash RedLight");
      digitalWrite(redLight, HIGH);
      delay(1000);
    }
    Serial.println();
  }
  else{
    // turn off both lights
    digitalWrite(greenLight, LOW);
    digitalWrite(redLight, LOW);
  }
  found = false;
}

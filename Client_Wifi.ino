/*********
  Rui Santos
  Complete project details at https://randomnerdtutorials.com  
*********/

// Load Wi-Fi library
#include <WiFi.h>
#include <HTTPClient.h>

// Replace with your network credentials
const char* ssid     = "ESP32-Access-Point";
const char* password = "123456789";

const char* serverUrl = "http://192.168.4.4:8000/esp32"; // 

void setup() {
  Serial.begin(115200);

  // Connetti l'ESP32 al Wi-Fi
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("Connessione al Wi-Fi in corso...");
}

void loop(){
  // Assicuriamoci che l'ESP32 sia connesso alla rete Wi-Fi come Client
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    // Effettua una richiesta GET al server FastAPI
    http.begin(serverUrl);
    int httpResponseCode = http.GET();

    if (httpResponseCode > 0) {
      // Se la richiesta è andata a buon fine, stampa la risposta
      String payload = http.getString();
      Serial.println("Risposta ricevuta dal server:");
      Serial.println(payload);
    } else {
      Serial.print("Errore nella richiesta HTTP: ");
      Serial.println(httpResponseCode);
    }

    http.end(); // Chiude la connessione HTTP
  } else {
    Serial.println("Client non connesso al Wi-Fi.");
  }

  delay(10000); // Ripeti ogni 10 secondi
  
}
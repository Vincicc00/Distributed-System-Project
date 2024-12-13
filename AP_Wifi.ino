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


void setup() {
  Serial.begin(115200);
  
  // Connect to Wi-Fi network with SSID and password
  Serial.print("Setting AP (Access Point)…");
  // Remove the password parameter, if you want the AP (Access Point) to be open
  WiFi.softAP(ssid, password);

  IPAddress IP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(IP);
  
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
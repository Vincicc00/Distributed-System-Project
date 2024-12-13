#include <Wire.h>
#include <SPI.h>
#include <Adafruit_PN532.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <WiFi.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

#define PN532_IRQ   (2)
#define PN532_RESET (3)  // Not connected by default on the NFC Shield


// Or use this line for a breakout or shield with an I2C connection: 
//sdaPin GPIO21.
//sclPin GPIO22
Adafruit_PN532 nfc(PN532_IRQ, PN532_RESET);

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
#define OLED_RESET     -1 // Reset pin # (or -1 if sharing Arduino reset pin)
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);


int vect[2] = {0,0};
int points = 100;
int squadre_passate = 0;

const char* ssid     = "ESP32-Access-Point";
const char* password = "123456789";

const char* serverUrl = "http://192.168.4.2:8000";

void inizializza_Oled(void){
  // Initialize the display
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { 
    Serial.println(F("SSD1306 allocation failed"));
    for (;;); // Don't proceed, loop forever
  }

  // Clear the display buffer
  display.clearDisplay();

  // Set text properties
  display.setTextSize(1);      // Text size
  display.setTextColor(WHITE); // Text color
}

void inizializza_Nfc(void){
  nfc.begin();

  uint32_t versiondata = nfc.getFirmwareVersion();
  if (! versiondata) {
    Serial.print("Didn't find PN53x board");
    while (1); // halt
  }
  // Got ok data, print it out!
  Serial.print("Found chip PN5"); Serial.println((versiondata>>24) & 0xFF, HEX);
  Serial.print("Firmware ver. "); Serial.print((versiondata>>16) & 0xFF, DEC);
  Serial.print('.'); Serial.println((versiondata>>8) & 0xFF, DEC);

  Serial.println("Waiting for an ISO14443A Card ...");
  
}

void inizializza_WiFi(void){
    // Connessione Wi-Fi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
      delay(1000);
      Serial.println("Connessione al Wi-Fi...");
    }
    Serial.println("Connesso al Wi-Fi!");
}

void displayTesto(const char* testo)
{
  display.clearDisplay();
  display.setCursor(0, 0);     // Start at top-left corner
  display.println(F(testo));
}

void displayPunteggio(int punteggio)
{
    display.setCursor(0,32);
    display.println(F("Punteggio:"));
    display.println(punteggio,DEC);
    display.display();
    delay(3000);
    display.clearDisplay();
    display.display();
}

int openTransaction(void) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String url = String(serverUrl) + "/open_transaction";
    http.begin(url);

    int httpResponseCode = http.GET();

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Risposta del server:");
      Serial.println(response);

      // Parsing della risposta JSON
      StaticJsonDocument<200> doc;
      DeserializationError error = deserializeJson(doc, response);

      if (!error) {
        int tid = doc["TID"]; // Leggi il valore di TID
        http.end();
        return tid;
      } else {
        Serial.println("Errore nel parsing JSON");
      }
    } else {
      Serial.print("Errore nella richiesta HTTP: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  } else {
    Serial.println("Wi-Fi non connesso");
  }
  return -1; // Restituisci un valore di errore se qualcosa va storto
}

void sendLock(int id_squadra, int trans_id, String lock_type) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String url = String(serverUrl) + "/lock";
    http.begin(url);
    http.addHeader("Content-Type","application/json");
    String payload;
    DynamicJsonDocument doc(2048);
    doc["id_squadra"] = id_squadra;
    doc["trans_id"] = trans_id;
    doc["lock_type"] = lock_type;

    serializeJson(doc, payload); 
    Serial.println(payload);

    int httpResponseCode = http.POST(payload);

    if (httpResponseCode > 0) {
      Serial.println("Lock inviato con successo");
    } else {
      Serial.println("Errore nella richiesta Lock");
    }
    http.end();
  }

}

bool UnlockClose(int trans_id) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String url = String(serverUrl) + "/unlockClose";
    http.begin(url);
    http.addHeader("Content-Type", "application/json");

    String payload = String("{\"trans_id\":") + trans_id + "}";
    int httpResponseCode = http.POST(payload);

     if (httpResponseCode > 0) {
      Serial.println("Transazione chiusa:");
      String response=http.getString();
	  // Parsing della risposta JSON
      StaticJsonDocument<200> doc;
      DeserializationError error = deserializeJson(doc, response);

      if (!error) {
        bool commit = doc["Commit"]; 
        http.end();
        return commit;
      } else {
        Serial.println("Errore nel parsing JSON");
      }
      
      } else {
      Serial.println("Errore nella chiusura della transazione");
    }
    http.end();
  }
}

/*bool closeTransaction(int trans_id) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String url = String(serverUrl) + "/close_transaction?trans_id=" + trans_id;
    http.begin(url);

    int httpResponseCode = http.GET();

    if (httpResponseCode > 0) {
      Serial.println("Transazione chiusa:");
      String response=http.getString();
	  // Parsing della risposta JSON
      StaticJsonDocument<200> doc;
      DeserializationError error = deserializeJson(doc, response);

      if (!error) {
        bool commit = doc["Commit"]; 
        http.end();
        return commit;
      } else {
        Serial.println("Errore nel parsing JSON");
      }
      
      } else {
      Serial.println("Errore nella chiusura della transazione");
    }
    http.end();
  }
}*/

int retrievePoints(int id_squadra, int trans_id) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String url = String(serverUrl) + "/retrieve_point?id_squadra=" + id_squadra + "&trans_id=" + trans_id;
    http.begin(url);

    int httpResponseCode = http.GET();

    if (httpResponseCode > 0) {
	  String response = http.getString();
      Serial.println("Punti recuperati:");
	  
      // Parsing della risposta JSON
      StaticJsonDocument<200> doc;
      DeserializationError error = deserializeJson(doc, response);

      if (!error) {
        int punteggio = doc["Punteggio"]; // Leggi il valore di TID
        Serial.println(punteggio);
        http.end();
        return punteggio;
      } else {
        Serial.println("Errore nel parsing JSON");
      }
    } else {
      Serial.println("Errore nel recupero dei punti");
    }
    http.end();
  }
}

void updatePoints(int id_squadra, int amount, int trans_id) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String url = String(serverUrl) + "/update_points"; // URL per la route POST

    http.begin(url); // Inizializza la connessione
    http.addHeader("Content-Type", "application/json"); // Aggiunge l'intestazione per il tipo di contenuto

    // Crea il payload JSON con i parametri
    String payload = String("{\"id_squadra\":") + id_squadra + 
                     ",\"amount\":" + amount + 
                     ",\"trans_id\":" + trans_id + "}";
    

    Serial.println("Payload inviato: " + payload); // Debug del payload

    // Invia la richiesta POST con il payload JSON
    int httpResponseCode = http.POST(payload);
    String response = http.getString();
          // Parsing della risposta JSON
      StaticJsonDocument<200> doc;
      DeserializationError error = deserializeJson(doc, response);
      int punteggio = doc["Punteggio"]; // Leggi il valore di TID
      Serial.println(punteggio);
    // Gestisce la risposta
    if (httpResponseCode > 0) {
      Serial.println("Punti aggiornati con successo");
    } else {
      Serial.println("Errore nell'aggiornamento dei punti");
    }

    http.end(); // Termina la connessione HTTP
  } else {
    Serial.println("Connessione WiFi non disponibile");
  }


}

int OttieniPunteggio(int id_squadra)
{
  bool commit = false;
  int punteggio = 0;
  do{
  int trans_id = openTransaction();
  sendLock(id_squadra, trans_id, "r");
  punteggio = retrievePoints(id_squadra, trans_id);
  commit = UnlockClose(trans_id);
  }while(commit == false);
  return punteggio;
}

int AggiornaPunteggio(int id_squadra, int punti)
{
  int punteggio = 0;
  bool commit = false;
  do{
  int trans_id = openTransaction();
  sendLock(id_squadra, trans_id, "w");
  punteggio = retrievePoints(id_squadra, trans_id);
  punteggio += punti;

  updatePoints(id_squadra, punteggio,trans_id);
  commit = UnlockClose(trans_id);
  }while(commit == false);
  return punteggio;
}

void setup(void) {
  Serial.begin(115200);
  inizializza_Nfc();
  inizializza_Oled(); 
  inizializza_WiFi(); 
}


void loop(void) 
{
  uint8_t success;
  uint8_t uid[] = { 0, 0, 0, 0, 0, 0, 0 };  // Buffer to store the returned UID
  uint8_t uidLength;                        // Length of the UID (4 or 7 bytes depending on ISO14443A card type)

  success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength);

  if (success) //ho letto una scheda
  {	
  // Display some basic information about the card
    Serial.println("Found an ISO14443A card");
    Serial.print("  UID Length: ");Serial.print(uidLength, DEC);Serial.println(" bytes");
    Serial.print("  UID Value: ");
    nfc.PrintHex(uid, uidLength);
    Serial.println("");

    uint8_t keya[6] = { 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF };

    success = nfc.mifareclassic_AuthenticateBlock(uid, uidLength, 4, 0, keya);

     if (success)     //ho autenticato il blocco
     {
        Serial.println("Sector 1 (Blocks 4..7) has been authenticated");
        uint8_t data[16];
        
        success = nfc.mifareclassic_ReadDataBlock(4, data);

        if (success)  //ho letto il blocco
        {
          // Data seems to have been read ... spit it out
          Serial.println("Reading Block 4:");
          nfc.PrintHexChar(data, 16);
          Serial.println("");

          int id_squadra = data[0];
          Serial.print(id_squadra,DEC);
          int punteggio = 0;
          if(vect[id_squadra] == 1){
            //Serial.println("Your squad is already passed!!!");
            //chiamate verso server per fare transazioni. 
            displayTesto("Your squad is already passed!!!");
            punteggio = OttieniPunteggio(id_squadra);
           }else{
            vect[id_squadra] = 1; // se è il primo a passare
            //Serial.println("Sei il primo della tua squadra a passare, inizio transazione....  ");
            //Chiamate verso server per fare transazioni.
            displayTesto("Sei il primo della tua squadra a passare, inizio transazione....");
            squadre_passate += 1;
            punteggio = AggiornaPunteggio(id_squadra,points/squadre_passate);
          }
          displayPunteggio(punteggio);
        }
	    else
	  	{
		  Serial.println("Ooops ... unable to read the requested block.  Try another key?");
	  	}
	   }	
	}	
 }




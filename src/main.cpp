#include <Arduino.h>
#include <map>

#if defined(ESP8266)
  #include <ESP8266WiFi.h>
  #include <WiFiManager.h>
  #include <LittleFS.h>
  #include <ESP8266WebServer.h>
  ESP8266WebServer server(80);
  #define FSYS LittleFS
#elif defined(ESP32)
  #include <WiFi.h>
  #include <WiFiManager.h>
  #include <FS.h>
  #include <LITTLEFS.h>
  #include <WebServer.h>
  WebServer server(80);
  #define FSYS LITTLEFS
#else
  #error "Define ESP8266 or ESP32 via -DESP8266 or -DESP32"
#endif

#ifndef WIFI_TIMEOUT
  #define WIFI_TIMEOUT 20
#endif

// ------------------------------------------------------------
// Globals
// ------------------------------------------------------------
int gpioPin = 2;          // default D4 / GPIO2
bool inverted = false;    // default normaal
int dotDuration = 200;    // ms (frontend bepaalt tempo; hier alleen voor consistentie)

// ------------------------------------------------------------
// Morse tabel
// ------------------------------------------------------------
std::map<char, String> morseMap =
{
  {'A', ".-"},    {'B', "-..."},  {'C', "-.-."}, {'D', "-.."},
  {'E', "."},     {'F', "..-."},  {'G', "--."},  {'H', "...."},
  {'I', ".."},    {'J', ".---"},  {'K', "-.-"},  {'L', ".-.."},
  {'M', "--"},    {'N', "-."},    {'O', "---"},  {'P', ".--."},
  {'Q', "--.-"},  {'R', ".-."},   {'S', "..."},  {'T', "-"},
  {'U', "..-"},   {'V', "...-"},  {'W', ".--"},  {'X', "-..-"},
  {'Y', "-.--"},  {'Z', "--.."},
  {'1', ".----"}, {'2', "..---"}, {'3', "...--"}, {'4', "....-"},
  {'5', "....."}, {'6', "-...."}, {'7', "--..."}, {'8', "---.."},
  {'9', "----."}, {'0', "-----"},
  {' ', " / "}
};

// ------------------------------------------------------------
// Helpers
// ------------------------------------------------------------
String textToMorse(const String &text)
{
    String morse = "";

    for (unsigned int i = 0; i < text.length(); i++)
    {
        char c = toupper(text[i]);

        if (c == ' ')
        {
            // Vier spaties tussen woorden
            morse += "    ";
        }
        else if (morseMap.count(c))
        {
            // Voeg twee spaties na elke letter toe
            morse += morseMap[c] + "  ";
        }
    }

    return morse;
}

// Laatste 4 MAC-bytes (ww:xx:yy:zz)
String macSuffixWwXxYyZz()
{
  String mac = WiFi.macAddress();               // "AA:BB:CC:DD:EE:FF"
  int c5 = mac.lastIndexOf(':');                // tussen EE en FF
  int c4 = mac.lastIndexOf(':', c5 - 1);        // tussen DD en EE
  int c3 = mac.lastIndexOf(':', c4 - 1);        // tussen CC en DD
  int c2 = mac.lastIndexOf(':', c3 - 1);        // tussen BB en CC
  if (c2 < 0) return mac;
  // substring vanaf na c2 tot vóór c5 (inclusief de :): "CC:DD:EE"
  // we willen "CC:DD:EE:FF"
  return mac.substring(c2 + 1);
}

bool askYesNo(const char *prompt, bool defaultYes, uint32_t timeoutMs)
{
  Serial.printf("%s (%c/%c) [Enter = %s]  (timeout %lus)\n",
                prompt,
                defaultYes ? 'Y' : 'y',
                defaultYes ? 'n' : 'N',
                defaultYes ? "Yes" : "No",
                (unsigned long)(timeoutMs / 1000));

  unsigned long start = millis();
  while (millis() - start < timeoutMs)
  {
    if (Serial.available())
    {
      char c = Serial.read();
      if (c == '\r' || c == '\n')
      {
        return defaultYes; // Enter
      }
      if (c == 'y' || c == 'Y') return true;
      if (c == 'n' || c == 'N') return false;
    }
    delay(10);
  }
  return defaultYes; // timeout
}

bool connectWithSaved(uint32_t timeoutSec)
{
  String ssid = WiFi.SSID();
  String psk  = WiFi.psk();    // (kan leeg zijn als niet eerder ingesteld)

  Serial.println("— Probeert opgeslagen WiFi —");
  Serial.printf("  SSID: %s\n", ssid.c_str());
  Serial.printf("  PSK : %s\n", psk.c_str());

  if (ssid.length() == 0)
  {
    Serial.println("  (Geen opgeslagen SSID)");
    return false;
  }

  WiFi.mode(WIFI_STA);
  WiFi.begin(); // gebruikt opgeslagen creds
  unsigned long t0 = millis();
  while (WiFi.status() != WL_CONNECTED && (millis() - t0) < timeoutSec * 1000UL)
  {
    delay(250);
    Serial.print('.');
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED)
  {
    Serial.println("✅ Verbonden met opgeslagen WiFi");
    Serial.printf("📶 SSID: %s\n", WiFi.SSID().c_str());
    Serial.printf("🌐 IP  : %s\n", WiFi.localIP().toString().c_str());
    return true;
  }

  Serial.printf("❌ Verbinden met opgeslagen WiFi mislukt (status=%d)\n", WiFi.status());
  return false;
}

bool startPortalAndReconnect(const String &apName)
{
    WiFiManager wm;
    wm.setDebugOutput(true);
    wm.setTimeout(WIFI_TIMEOUT); // sluit automatisch na timeout

    Serial.println("🧭 Start WiFiManager portal...");
    bool connected = wm.startConfigPortal(apName.c_str()); // blokkeert

    // Toon resultaat en ingevoerde data
    String ssid = WiFi.SSID();
    String psk  = WiFi.psk();

    Serial.println("💾 Terug uit portal — credentials nu:");
    Serial.printf("  SSID: %s\n", ssid.c_str());
    Serial.printf("  PSK : %s\n", psk.c_str());

    if (!connected)
    {
        Serial.println("⚠️  Portal afgebroken of timeout.");
    }

    // Extra verbindingspoging met de nieuwe credentials
    if (ssid.length())
    {
        WiFi.begin(ssid.c_str(), psk.c_str());
        unsigned long t0 = millis();
        while (WiFi.status() != WL_CONNECTED && (millis() - t0) < WIFI_TIMEOUT * 1000UL)
        {
            delay(250);
            Serial.print('.');
        }
        Serial.println();
    }

    if (WiFi.status() == WL_CONNECTED)
    {
        Serial.println("✅ Verbonden met nieuwe credentials");
        Serial.printf("📶 SSID: %s\n", WiFi.SSID().c_str());
        Serial.printf("🌐 IP  : %s\n", WiFi.localIP().toString().c_str());
        return true;
    }

    Serial.printf("❌ Verbinden met nieuwe credentials mislukt (status=%d)\n", WiFi.status());
    WiFi.mode(WIFI_STA);   // Verlaat AP-modus van WiFiManager
    delay(100);
    return false;
}

void startAp(const String &apName)
{
  WiFi.disconnect(true);
  delay(100);
  WiFi.mode(WIFI_AP);
  delay(100);

  bool apOk = WiFi.softAP(apName.c_str());
  if (!apOk)
  {
    Serial.println("❌ Kon AP niet starten!");
    return;
  }

  IPAddress ip = WiFi.softAPIP();
  Serial.println("🌐 AP-modus actief");
  Serial.printf("   Naam: %s\n", apName.c_str());
  Serial.printf("   IP  : %s\n", ip.toString().c_str());
  Serial.println("===========================");
}

// ------------------------------------------------------------
// Web Handlers
// ------------------------------------------------------------
void handleRoot()
{
  File f = FSYS.open("/index.html", "r");
  if (!f)
  {
    server.send(200, "text/plain", "index.html ontbreekt in LittleFS");
    return;
  }
  server.streamFile(f, "text/html");
  f.close();
}

void handleStyle()
{
  File f = FSYS.open("/style.css", "r");
  if (!f)
  {
    server.send(404, "text/plain", "style.css ontbreekt");
    return;
  }
  server.streamFile(f, "text/css");
  f.close();
}

void handleScript()
{
  File f = FSYS.open("/script.js", "r");
  if (!f)
  {
    server.send(404, "text/plain", "script.js ontbreekt");
    return;
  }
  server.streamFile(f, "application/javascript");
  f.close();
}

// Geeft de volledige Morse terug voor de frontend
// /morse?text=...
void handleMorse()
{
  String text = server.arg("text");
  text.trim();
  String morse = textToMorse(text);
  server.send(200, "text/plain", morse);
}

// Zet fysieke GPIO hoog/laag met inversie
// /gpio?state=0/1&gpio=2&inv=true/false
void handleGpio()
{
  if (server.hasArg("gpio"))
  {
    gpioPin = server.arg("gpio").toInt();
  }
  if (server.hasArg("inv"))
  {
    String invStr = server.arg("inv");
    inverted = (invStr == "1" || invStr == "true" || invStr == "True");
  }

  pinMode(gpioPin, OUTPUT);

  int state = 0;
  if (server.hasArg("state"))
  {
    state = server.arg("state").toInt();
  }

  digitalWrite(gpioPin, inverted ? !state : state);
  server.send(200, "text/plain", "OK");
}

// Seriële logging synchroon met frontend:
// /serial?start=Tekst
// /serial?symbol=.,-,SPACE,WORD
// /serial?end=1
void handleSerialLog()
{
  if (server.hasArg("start"))
  {
    String t = server.arg("start");
    Serial.printf("📝 Tekst: %s\n", t.c_str());
    server.send(200, "text/plain", "OK");
    return;
  }

  if (server.hasArg("symbol"))
  {
    String s = server.arg("symbol");
    if (s == "SPACE" || s == "WORD")
    {
      Serial.print(' ');
    }
    else if (s.length())
    {
      Serial.print(s.charAt(0)); // '.' of '-'
    }
    server.send(200, "text/plain", "OK");
    return;
  }

  if (server.hasArg("end"))
  {
    Serial.println();
    server.send(200, "text/plain", "OK");
    return;
  }

  server.send(400, "text/plain", "Bad Request");
}

// ------------------------------------------------------------
// WiFi start
// ------------------------------------------------------------
void startWifi()
{
    String apName = "espMorseMachine-" + macSuffixWwXxYyZz();

    Serial.println("=== WiFi Initialisatie ===");
    Serial.printf("📛 AP/Systeemnaam: %s\n", apName.c_str());

    // Stap 1: probeer opgeslagen netwerk
    if (connectWithSaved(WIFI_TIMEOUT))
    {
        return;
    }

    // Stap 2: vraag of portal moet starten
    bool usePortal = askYesNo("Portal starten (Y/n)", true, 20000UL);
    bool connected = false;

    if (usePortal)
    {
        connected = startPortalAndReconnect(apName);
    }

    if (connected)
    {
        return; // klaar
    }

    // Stap 3: nog steeds geen verbinding, vraag AP
    Serial.println("⚠️  Geen verbinding na portal.");
    bool asAp = askYesNo("Starten als AP? (y/N)", false, 20000UL);

    if (asAp)
    {
        startAp(apName);
    }
    else
    {
        Serial.println("🔁 Geen AP gewenst, herstart...");
        delay(200);
        ESP.restart();
    }
}

// ------------------------------------------------------------
// Setup / Loop
// ------------------------------------------------------------
void setup()
{
  Serial.begin(115200);
  delay(300);
  Serial.println();
  Serial.println("=== ESP Morse Machine ===");

  if (!FSYS.begin())
  {
    Serial.println("❌ Filesystem mount failed!");
  }

  startWifi();

  // Web routes
  server.on("/",           handleRoot);
  server.on("/style.css",  handleStyle);
  server.on("/script.js",  handleScript);
  server.on("/morse",      handleMorse);
  server.on("/gpio",       handleGpio);
  server.on("/serial",     handleSerialLog);

  server.begin();
  Serial.println("✅ Webserver gestart.");
}

void loop()
{
  server.handleClient();
}

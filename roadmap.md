# Projectspecificatie: ESP Morse Machine

## Naam:
ESP Morse Machine

## Hardware:
	•	ESP8266 (NodeMCU of Wemos D1 Mini) en ESP32 (via compiler option)
	•	4MB flash, 2MB LittleFS
	•	Optioneel LED of buzzer aangesloten op configureerbare GPIO-pin

## Coding
- allman coding style - ook voor script.js en style.css
- lowerCamelCase naming
- extensieve logging op Serial
- Voorkeur voor Serial.printf()
- snprintf()

## Let op!
***platformio*** commando via volledige path:
```
~/.platformio/penv/bin/platformio
```
idem voor ***pio***:
```
~/.platformio/penv/bin/pio
```

⸻
## WiFi gedrag
	1.	ESP probeert verbinding te maken met opgeslagen SSID + wachtwoord.
      - toon het SSID en Wachtwoord dat gebruikt wordt
      - timeout 20 seconden (via compiler option)
	2.	Als dit mislukt, start hij WiFiManager in AP-modus:
	    -	SSID = espMorseMachine-ww:xx:yy:zz
	    -	Geen wachtwoord
	    -	Laatste 4 bytes van MAC-adres in de naam
      - Toon SSID en Wachtwoord dat door het Captive portal wordt terug gegeven
	3.	Voordat AP start, vraagt het systeem via Serial:
      > “Start as AP? (y/N)”
	      -	30 seconden timeout
	      -	Default = “Yes”
	      -	“No” → ESP.restart()

⸻

# Webinterface
## Bestanden in /data (LittleFS):
	•	index.html
	•	style.css
	•	script.js

## Functionaliteit:
	•	Tekstinvoer (om te vertalen naar Morse)
	•	Knipperend gele “lamp”
	•	Console-venster (zoals Arduino IDE monitor)
	•	Realtime Morse-uitvoer: symbolen verschijnen één voor één op één regel
	•	Slider: snelheid van “dot” instellen (base unit, bepaalt timing)
	•	Invoerveld voor GPIO-pin
	•	Radio-knoppen:
	   - “Normal” of “Inversed” GPIO-actie
	   - Webserver reageert op /morse?text=... en /gpio?...

## Layout:
	•	Lichte stijl, wit venster 70–80 % breed/hoog
	•	Koptekst “ESP Morse Machine” linksboven buiten het venster
	•	Ruimte onder het invoerveld

⸻
## Backend (main.cpp)
	•	Framework: Arduino (ESP8266 of ESP32)
	•	Filesystem: LittleFS
	•	Webserver: standaard ESP8266WebServer (geen async) of de webserver voor de ESP32
	•	WiFiManager fallback
	•	Diagnostiek via Serial.printf

## Morse-functionaliteit:
	•	Tekst → Morse via std::map<char, String>
	•	ESP knippert gekozen GPIO synchroon met frontend en Serial
	•	Morse timing:
	•	Dot = base time
	•	Dash = 3× dot
	•	Letter gap = 3× dot
	•	Word gap = 7× dot

## Flow van de Morse-transmissie
	1.	De gebruiker klikt op [Zenden]
        → invoerveld + knop worden gedeactiveerd
	2.	De tekst wordt:
	  -	naar de Serial Monitor gestuurd (📝 Tekst:)
	  -	naar de browserconsole in het frontend gestuurd
	3.	Daarna wordt elke morse-puls (dot/dash/spatie):
	  -	tegelijkertijd uitgezonden op de GPIO,
	  -	getoond in het frontend op één regel,
	  -	geprint op Serial (. en -)
	4.	Bij het einde:
	  -	een \n naar Serial,
	  -	een lege regel in de webconsole,
	  -	invoerveld + knop worden weer actief.

## Logging:
	•	Serial.printf voor systeemstatus
	•	Tijdens Morse-uitvoer: elke punt/streep live naar Serial

⸻
## Build System & Flash Configuratie

### PlatformIO Custom Build Script (scripts/custom_build.py)

Het project gebruikt een custom build script dat automatisch flash configuraties genereert voor verschillende ESP platforms.

#### ESP32 - Dynamische Flash Configuratie via idedata.json:
	1.	Pre-build:
	    - Kopieert custom partitions.csv naar project directory (indien gespecificeerd)
	    - Kopieert boot_app0.bin uit framework
	2.	Post-build:
	    - Genereert idedata.json via PlatformIO
	    - Leest flash_images array met offsets voor:
	        * bootloader.bin
	        * partitions.bin  
	        * boot_app0.bin
	    - Leest application_offset voor firmware.bin
	    - Kopieert alle bestanden met correcte offsets
	    - Genereert flash.json met complete flash configuratie
	3.	Post-buildfs:
	    - Kopieert littlefs.bin of spiffs.bin
	    - Leest filesystem offset uit partitions.csv
	    - Update flash.json met filesystem image

#### ESP8266 - Statische Flash Configuratie:
	1.	Pre-build:
	    - Geen actie (ESP8266 heeft geen partitions)
	2.	Post-build:
	    - Kopieert firmware.bin met offset 0x0
	    - Genereert flash.json
	3.	Post-buildfs:
	    - Kopieert littlefs.bin of spiffs.bin
	    - Gebruikt standaard offset 0x300000
	    - Update flash.json met filesystem image

#### Output per project:
Elk project krijgt een directory: `projects/morseMachine/{board}/{version}/`
Bevat:
	•	flash.json - Complete flash configuratie met offsets
	•	firmware.bin - Application binary
	•	littlefs.bin of spiffs.bin - Filesystem image
	•	ESP32 specifiek:
	    - bootloader.bin
	    - partitions.bin
	    - boot_app0.bin
	    - partitions.csv (human readable)

#### Voordelen:
	•	Automatisch correcte flash offsets per platform
	•	Ondersteuning voor custom partition schemes
	•	Ready-to-flash configuratie voor productie
	•	Geen handmatige offset berekeningen nodig

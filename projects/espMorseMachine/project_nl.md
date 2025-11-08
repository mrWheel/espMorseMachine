# ESP Morse Machine

## Projectbeschrijving

De ESP Morse Machine is een IoT-apparaat dat tekst omzet naar morsecode en deze uitzendt via een knipperende LED of buzzer. Het project biedt een moderne webinterface voor controle en monitoring, en ondersteunt een breed scala aan ESP8266 en ESP32 hardware platforms.

## Hoofdfunctionaliteit

### Hardware
- **Platform ondersteuning**: Alle ESP8266 en ESP32 varianten
- **Filesystem**: LittleFS voor web-files
- **GPIO output**: Configureerbare pin voor LED of buzzer (normaal/geïnverteerd)

### WiFi Gedrag
1. **Automatische verbinding**: Probeert eerst verbinding te maken met opgeslagen WiFi credentials (20 seconden timeout)
2. **WiFiManager fallback**: Start bij falen een captive portal in AP-modus:
   - SSID: `espMorseMachine-ww:xx:yy:zz` (laatste 4 bytes van MAC-adres)
   - Geen wachtwoord

### Webinterface

Het project levert een complete webapplicatie (HTML/CSS/JavaScript) met:

- **Tekstinvoer**: Invoerveld voor te vertalen tekst
- **Visuele feedback**: Knipperende gele "lamp" die synchroon loopt met de fysieke GPIO
- **Live console**: Real-time display van morsecode output
- **Snelheidsregeling**: Slider voor aanpassen van de dot-duration (base timing unit)
- **GPIO configuratie**: Invoerveld voor pin-nummer en toggle voor normal/inverted mode
- **Responsive design**: Lichte stijl met wit venster (70-80% schermformaat)

### Morsecode Implementatie

- **Complete karakter set**: Alle letters (A-Z), cijfers (0-9) en spatie
- **Correcte timing**:
  - Dot = base time (verstelbaar via slider)
  - Dash = 3× dot
  - Letter gap = 3× dot  
  - Word gap = 7× dot
- **Triple sync**: GPIO, webinterface en Serial Monitor werken synchroon
- **Extensieve logging**: Real-time output naar Serial Monitor met emoji's voor status indicatie

## Licentie & Ontwikkeling

Dit is een PlatformIO project ontwikkeld voor educatieve en experimentele doeleinden met morsecode.

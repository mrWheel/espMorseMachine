# PlatformIO Custom Build Script Documentatie

## Overzicht

Het `scripts/custom_build.py` script automatiseert het genereren van flash configuraties voor ESP microcontrollers. Het script werkt platform-onafhankelijk voor alle ESP32 varianten (ESP32, ESP32-S3, ESP32-C3, ESP32-S2, ESP32-WROOM, ESP32-WROVER, etc.) en ESP8266.

## Doel

Het script genereert voor elk project automatisch:
- Flash configuratie met correcte offsets per platform
- Complete set flash images (bootloader, partitions, firmware, filesystem)
- JSON bestand met flash instructies voor productie

## Configuratie

### Environment Naming Conventie

Environment namen in `platformio.ini` MOETEN de volgende structuur hebben:

```
[env:{board}-v{major}_{minor}_{patch}]
```

**Voorbeelden:**
- `esp32dev-v1_0_0`
- `esp32-s3-v2_1_5`
- `esp12e-v3_3_3`
- `esp32-WROVER-v1_2_0`

**Componenten:**
- `{board}`: Board identifier uit PlatformIO (bijv. `esp32dev`, `esp32-s3`, `esp12e`)
- `v{major}_{minor}_{patch}`: Versienummer met underscores (wordt omgezet naar `v1.0.0` format)

### Project Directory Structuur

Het script detecteert automatisch de project naam uit de `projects/` directory:

```
projects/
└── {project_name}/           # Bijv. "morseMachine"
    ├── {board}/              # Bijv. "esp32dev", "esp32-s3", "esp12e"
    │   └── {version}/        # Bijv. "v1.0.0"
    │       ├── flash.json
    │       ├── firmware.bin
    │       ├── littlefs.bin (of spiffs.bin)
    │       └── ESP32 specifiek:
    │           ├── bootloader.bin
    │           ├── partitions.bin
    │           ├── boot_app0.bin
    │           └── partitions.csv
```

## Platform Detectie

Het script detecteert automatisch het platform type:

### ESP32 Familie (alle varianten)
Detectie: `"32"` in platform name (case-insensitive)
- ESP32 (esp32dev)
- ESP32-S2
- ESP32-S3
- ESP32-C3
- ESP32-C6
- ESP32-WROOM
- ESP32-WROVER
- Alle toekomstige ESP32 varianten

### ESP8266
Detectie: `"8266"` in platform name (case-insensitive)
- ESP12E
- ESP12F
- NodeMCU
- Wemos D1 Mini
- Alle ESP8266 varianten

## Workflow

### Pre-Build Fase

**Timing:** Voor `buildprog` target

#### ESP32 Platforms
1. **Partitions CSV**
   - Controleert `board_build.partitions` in platformio.ini
   - Als gespecificeerd: kopieert custom partitions file
   - Anders: gebruikt `default.csv` uit framework
   - Doel: `projects/{project}/{board}/{version}/partitions.csv`

2. **Boot App Binary**
   - Zoekt `boot_app0.bin` in framework directory
   - Kopieert naar project directory
   - Nodig voor OTA updates

#### ESP8266 Platforms
- Geen actie (ESP8266 heeft geen separate partition table)

### Post-Build Fase

**Timing:** Na `buildprog` target

#### ESP32 Platforms - Dynamische Configuratie

1. **Genereer idedata.json**
   ```python
   platformio run -e {environment} -t idedata
   ```

2. **Parse Flash Images**
   Leest uit `idedata.json`:
   ```json
   {
     "extra": {
       "flash_images": [
         {"offset": "0x1000", "path": "/path/to/bootloader.bin"},
         {"offset": "0x8000", "path": "/path/to/partitions.bin"},
         {"offset": "0xe000", "path": "/path/to/boot_app0.bin"}
       ],
       "application_offset": "0x10000"
     }
   }
   ```

3. **Kopieer Binaries**
   - bootloader.bin → `{offset}` uit idedata
   - partitions.bin → `{offset}` uit idedata
   - boot_app0.bin → `{offset}` uit idedata
   - firmware.bin → `{application_offset}` uit idedata

4. **Genereer flash.json**
   ```json
   {
     "board": "esp32dev",
     "version": "v1.0.0",
     "flash_files": [
       {"offset": "0x1000", "file": "bootloader.bin"},
       {"offset": "0x8000", "file": "partitions.bin"},
       {"offset": "0xe000", "file": "boot_app0.bin"},
       {"offset": "0x10000", "file": "firmware.bin"}
     ]
   }
   ```

#### ESP32 Fallback Mode
Als idedata.json niet beschikbaar of parsing faalt:
- Gebruikt standaard ESP32 offsets:
  - 0x1000: bootloader.bin
  - 0x8000: partitions.bin
  - 0xe000: boot_app0.bin
  - 0x10000: firmware.bin

#### ESP8266 Platforms - Statische Configuratie

1. **Kopieer Firmware**
   - firmware.bin → offset 0x0

2. **Genereer flash.json**
   ```json
   {
     "board": "esp12e",
     "version": "v3.3.3",
     "flash_files": [
       {"offset": "0x0", "file": "firmware.bin"}
     ]
   }
   ```

### Post-BuildFS Fase

**Timing:** Na `buildfs` target

#### Alle Platforms

1. **Detecteer Filesystem Image**
   - Zoekt `littlefs.bin` of `spiffs.bin` in build directory

2. **Kopieer Filesystem Image**

3. **Bepaal Filesystem Offset**
   
   **Methode 1 - Uit partitions.csv (ESP32):**
   ```csv
   # Name,   Type, SubType, Offset,  Size
   spiffs,   data, spiffs,  0x290000, 0x170000
   ```
   
   **Methode 2 - Standaard offsets:**
   - ESP32: 0x290000
   - ESP8266: 0x300000

4. **Update flash.json**
   Voegt filesystem image toe aan flash_files array

## Output: flash.json

### Structuur

```json
{
  "board": "string",        // Board identifier
  "version": "string",      // Versie in v1.2.3 formaat
  "flash_files": [          // Array van flash images
    {
      "offset": "hex_string",  // Flash offset in hex
      "file": "filename"       // Relatieve bestandsnaam
    }
  ]
}
```

### ESP32 Voorbeeld (met custom partitions)

```json
{
  "board": "esp32dev",
  "version": "v2.2.2",
  "flash_files": [
    {"offset": "0x1000", "file": "bootloader.bin"},
    {"offset": "0x8000", "file": "partitions.bin"},
    {"offset": "0xe000", "file": "boot_app0.bin"},
    {"offset": "0x10000", "file": "firmware.bin"},
    {"offset": "0x290000", "file": "littlefs.bin"}
  ]
}
```

### ESP8266 Voorbeeld

```json
{
  "board": "esp12e",
  "version": "v3.3.3",
  "flash_files": [
    {"offset": "0x0", "file": "firmware.bin"},
    {"offset": "0x300000", "file": "littlefs.bin"}
  ]
}
```

## Gebruik in platformio.ini

### Basis Configuratie

```ini
[env:esp32dev-v1_0_0]
platform = espressif32
board = esp32dev
extra_scripts = scripts/custom_build.py
```

### Met Custom Partitions

```ini
[env:esp32dev-v2_0_0]
platform = espressif32
board = esp32dev
extra_scripts = scripts/custom_build.py
board_build.partitions = projects/myProject/esp32dev/v2.0.0/custom.csv
```

### ESP8266 Configuratie

```ini
[env:esp12e-v3_0_0]
platform = espressif8266
board = esp12e
extra_scripts = scripts/custom_build.py
```

### ESP32-S3 Voorbeeld

```ini
[env:esp32-s3-v1_5_0]
platform = espressif32
board = esp32-s3-devkitc-1
extra_scripts = scripts/custom_build.py
board_build.partitions = projects/myProject/esp32-s3/v1.5.0/huge_app.csv
```

## Build Commands

### Volledige Build
```bash
platformio run -e esp32dev-v1_0_0
platformio run -e esp32dev-v1_0_0 -t buildfs
```

### Clean Build
```bash
platformio run -e esp32dev-v1_0_0 -t clean
platformio run -e esp32dev-v1_0_0
platformio run -e esp32dev-v1_0_0 -t buildfs
```

## Console Output

### ESP32 Build
```
>>> [PRE-BUILD] Voor myProject/esp32dev/v1.0.0
  Aangepaste partitions file gevonden: custom.csv
  ✓ custom.csv → projects/myProject/esp32dev/v1.0.0/partitions.csv
  boot_app0.bin uit framework kopiëren...
  ✓ boot_app0.bin → projects/myProject/esp32dev/v1.0.0/boot_app0.bin
>>> [PRE-BUILD] Klaar.

>>> [POST-BUILD] Voor myProject/esp32dev/v1.0.0
  ESP32 gedetecteerd - genereer idedata.json...
  Kopieer flash images met offsets uit idedata.json:
  ✓ bootloader.bin → projects/myProject/esp32dev/v1.0.0/bootloader.bin
  ✓ partitions.bin → projects/myProject/esp32dev/v1.0.0/partitions.bin
  ✓ boot_app0.bin → projects/myProject/esp32dev/v1.0.0/boot_app0.bin
  Kopieer firmware met offset 0x10000:
  ✓ firmware.bin → projects/myProject/esp32dev/v1.0.0/firmware.bin
  Zoek naar filesystem image...
  ✓ flash.json aangemaakt: projects/myProject/esp32dev/v1.0.0/flash.json

  Flash configuratie:
    0x1000 → bootloader.bin
    0x8000 → partitions.bin
    0xe000 → boot_app0.bin
    0x10000 → firmware.bin
>>> [POST-BUILD] Klaar.

>>> [POST-BUILDFS] Voor myProject/esp32dev/v1.0.0
  Zoek naar filesystem image...
  Kopieer filesystem image: littlefs.bin
  ✓ littlefs.bin → projects/myProject/esp32dev/v1.0.0/littlefs.bin
  ℹ️  Filesystem offset gevonden in partitions.csv: 0x290000
  ✓ flash.json bijgewerkt met littlefs.bin
>>> [POST-BUILDFS] Klaar.
```

### ESP8266 Build
```
>>> [PRE-BUILD] Voor myProject/esp12e/v3.3.3
  ESP8266 detecteerd — geen partitions.csv of boot_app0.bin nodig
>>> [PRE-BUILD] Klaar.

>>> [POST-BUILD] Voor myProject/esp12e/v3.3.3
  ESP8266 gedetecteerd - kopieer firmware...
  ✓ firmware.bin → projects/myProject/esp12e/v3.3.3/firmware.bin
  Zoek naar filesystem image...
  ✓ flash.json aangemaakt: projects/myProject/esp12e/v3.3.3/flash.json

  Flash configuratie:
    0x0 → firmware.bin
>>> [POST-BUILD] Klaar.

>>> [POST-BUILDFS] Voor myProject/esp12e/v3.3.3
  Zoek naar filesystem image...
  Kopieer filesystem image: littlefs.bin
  ✓ littlefs.bin → projects/myProject/esp12e/v3.3.3/littlefs.bin
  ℹ️  ESP8266: gebruik standaard filesystem offset 0x300000
  ✓ flash.json bijgewerkt met littlefs.bin
>>> [POST-BUILDFS] Klaar.
```

## Error Handling

### Fallback Mechanismen

1. **idedata.json niet beschikbaar**
   - Script gebruikt hardcoded ESP32 offsets
   - Waarschuwing in console
   - Build continues

2. **Framework path niet gevonden**
   - Waarschuwing in console
   - Geen boot_app0.bin gekopieerd
   - Build continues (bestanden kunnen handmatig toegevoegd)

3. **Partitions file niet gevonden**
   - Gebruikt default.csv uit framework
   - Waarschuwing in console

4. **Filesystem offset niet in partitions.csv**
   - Gebruikt platform-specifieke standaard offset
   - Info message in console

## Platform Specificaties

### ESP32 Familie

**Ondersteunde Boards:**
- esp32dev
- esp32-s2
- esp32-s3-devkitc-1
- esp32-c3-devkitm-1
- esp32-c6-devkitc-1
- esp32-wrover
- esp32-wroom-32
- Alle andere ESP32 varianten

**Flash Layout:**
```
0x1000    - Bootloader
0x8000    - Partition Table
0xe000    - Boot App0 (voor OTA)
0x10000   - Application (firmware)
0x290000+ - Filesystem (variabel)
```

**Partition Schemes:**
- default.csv (standaard)
- huge_app.csv
- minimal.csv
- no_ota.csv
- custom (eigen schema)

### ESP8266

**Ondersteunde Boards:**
- esp12e
- esp12f
- nodemcuv2
- d1_mini
- Alle ESP8266 varianten

**Flash Layout:**
```
0x0       - Application (firmware)
0x300000  - Filesystem (standaard)
```

**Note:** ESP8266 heeft geen separate partition table

## Productie Gebruik

### Flash Commando's

**ESP32:**
```bash
esptool.py --chip esp32 \
  --before default_reset --after hard_reset write_flash \
  0x1000 bootloader.bin \
  0x8000 partitions.bin \
  0xe000 boot_app0.bin \
  0x10000 firmware.bin \
  0x290000 littlefs.bin
```

**ESP8266:**
```bash
esptool.py --chip esp8266 \
  --before default_reset --after hard_reset write_flash \
  0x0 firmware.bin \
  0x300000 littlefs.bin
```

### Automatisch uit flash.json

Python script om flash.json te parseren:
```python
import json

with open('flash.json', 'r') as f:
    config = json.load(f)

cmd = f"esptool.py --chip {get_chip(config['board'])} write_flash"
for item in config['flash_files']:
    cmd += f" {item['offset']} {item['file']}"

print(cmd)
```

## Troubleshooting

### "Source not found" Error
**Probleem:** Custom partitions file niet gevonden
**Oplossing:** Zorg dat het pad in `board_build.partitions` correct is en het bestand bestaat

### "idedata.json niet gevonden"
**Probleem:** idedata.json wordt niet gegenereerd
**Oplossing:** Script gebruikt automatisch fallback offsets, geen actie nodig

### Verkeerde Flash Offsets
**Probleem:** flash.json bevat verkeerde offsets
**Oplossing:** 
1. Check of idedata.json correct wordt gegenereerd
2. Verwijder `.pio/build/{env}/idedata.json` en rebuild
3. Check custom partitions file voor correcte offsets

### Bestanden niet gekopieerd
**Probleem:** Bestanden niet in project directory
**Oplossing:**
1. Run clean build: `pio run -e {env} -t clean`
2. Check console output voor error messages
3. Verifieer dat `extra_scripts` correct is ingesteld

## Voordelen

1. **Platform Onafhankelijk**
   - Werkt met alle ESP32 varianten
   - Werkt met ESP8266
   - Automatische detectie

2. **Versie Management**
   - Meerdere versies naast elkaar
   - Duidelijke versie nummering
   - Per versie complete flash image set

3. **Productie Ready**
   - Complete flash configuratie
   - Alle benodigde binaries
   - Direct flashbaar

4. **Geen Handmatig Werk**
   - Automatische offset detectie
   - Automatisch bestand kopiëren
   - Automatische flash.json generatie

5. **Flexibel**
   - Custom partition schemes
   - Verschillende filesystems (LittleFS/SPIFFS)
   - Platform-specifieke optimalisaties

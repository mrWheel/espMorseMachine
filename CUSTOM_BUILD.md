# PlatformIO Custom Build Script Documentatie

## Overzicht

Het `scripts/custom_build.py` script automatiseert het genereren van flash configuraties voor ESP microcontrollers. Het script werkt platform-onafhankelijk voor alle ESP32 varianten (ESP32, ESP32-S3, ESP32-C3, ESP32-S2, ESP32-WROOM, ESP32-WROVER, etc.) en ESP8266.

## Doel

Het script genereert voor elk project automatisch:
- Flash configuratie met correcte offsets per platform
- Complete set flash images (bootloader, partitions, firmware, filesystem)
- JSON bestand met flash instructies voor productie
- `build_log.md` met alle (fout)meldingen van het `custom_build.py` script

## Configuratie

### Environment Naming Conventie

Environment namen in `platformio.ini` KUNNEN de volgende structuur hebben:

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

Maar als deze NIET deze structuur hebben, zoek dan in de `build_flags` of in idedata.json naar "VERSION" en gebruik deze met dezelfde structuur: `v{major}.{minor}.{patch}`

### Project Directory Structuur

Het script detecteert automatisch de project naam uit de `projects/` directory:

```
projects/
└── {project_name}/           # Bijv. "morseMachine"
    ├── {board}/              # Bijv. "esp32dev", "esp32-s3", "esp12e"
    │   └── {version}/        # Bijv. "v1.0.0"
    │       ├── flash.json    # Gegenereerd uit idedata.json (voor esp32)
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

## Auto-Sync Functionaliteit

Het script bevat een intelligente auto-sync functie die automatisch detecteert wanneer project files bijgewerkt moeten worden, ook bij cached builds in VSCode of via CLI.

### Hoe werkt Auto-Sync?

1. **Timestamp Checking**
   - Vergelijkt timestamps van build output met project directory
   - Detecteert of firmware.bin nieuwer is dan gekopieerde versie
   - Detecteert of filesystem images bestaan maar nog niet gekopieerd zijn

2. **Automatische Sync**
   - Bij cached builds waar bestanden wel gebouwd maar niet gekopieerd zijn
   - Na buildfs → buildprog volgorde (filesystem eerst, dan firmware)
   - Bij incremental builds in VSCode

3. **Efficiëntie**
   - Alleen sync wanneer nodig
   - Geen onnodige file operations bij volledig cached builds
   - Minimale overhead (timestamp vergelijking)

### Voordelen Auto-Sync

✅ **Geen handmatige clean meer nodig** - VSCode Build knop werkt altijd correct  
✅ **Flexibele build volgorde** - buildfs dan buildprog, of omgekeerd  
✅ **Cached builds ondersteuning** - Snelle rebuilds met correcte output  
✅ **VSCode UI compatible** - Werkt met standaard PlatformIO knoppen  

## Workflow

### Pre-Build Fase

**Timing:** Voor `buildprog` target

#### ESP32 Platforms
1. **Partitions CSV**
   - Controleert `board_build.partitions` in platformio.ini
   - Als gespecificeerd: kopieert custom partitions file naar: 
     - Doel: `projects/{project}/{board}/{version}/partitions.csv`
   - Anders: gebruikt `default.csv` uit framework en kopieer deze naar:
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

1. **Lees en interpreteer idedata.json**

2. **Parse Flash Images**
   Leest uit `idedata.json`:
   ```json
   {
     "extra": {
       "flash_images": [
         {"offset": "0x?????", "path": "/path/to/bootloader.bin"},
         {"offset": "0x?????", "path": "/path/to/partitions.bin"},
         {"offset": "0x?????", "path": "/path/to/boot_app0.bin"},
         {"offset": "0x?????", "path": "/path/to/??????.bin"}
       ],
       "application_offset": "0x?????"
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
       {"offset": "0x?????", "file": "bootloader.bin"},
       {"offset": "0x?????", "file": "partitions.bin"},
       {"offset": "0x?????", "file": "boot_app0.bin"},
       {"offset": "0x?????", "file": "firmware.bin"}
     ]
   }
   ```

#### ESP32 Fallback Mode
Als `idedata.json` niet beschikbaar of parsing faalt:
- Gebruikt offsets uit `partitions.csv`:
  - 0x????: bootloader.bin
  - 0x????: partitions.bin
  - 0x????: boot_app0.bin
  - 0x?????: firmware.bin

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
       {"offset": "0x????", "file": "spiffs.bin"}
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

   **Methode 1 - Uit idedata.json (ESP32):**
   
   **Methode 2 - Uit partitions.csv (ESP32):**
   - Leest partitions.csv uit project directory
   - Check zowel `Name` als `SubType` kolommen
   - Ondersteunt: spiffs, littlefs, fatfs, ffat
   - Voorbeeld:
   ```csv
   # Name,   Type, SubType, Offset,  Size
   spiffs,   data, spiffs,  0x790000, 0x70000
   ```
   
   **Methode 3 - Standaard offsets:**
   - ESP32: 0x290000  -> display foutmelding
   - ESP8266: 0x300000  -> display foutmelding

4. **Update flash.json**
   Voegt filesystem image toe aan flash_files array

### Auto-Sync Fase

**Timing:** Na `firmware.elf` build (cached builds)

1. **Check Firmware Status**
   - Vergelijkt timestamp van firmware.bin in build dir vs project dir
   - Triggert post_build_action bij wijzigingen

2. **Check Filesystem Status**
   - Detecteert of filesystem image bestaat in build dir
   - Controleert of deze al gekopieerd is naar project dir
   - Triggert post_build_action als filesystem ontbreekt

3. **Slim Gedrag**
   - Geen actie bij volledig cached builds (alles up-to-date)
   - Sync alleen wat nodig is
   - Werkt onafhankelijk van build volgorde

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
[env:esp32dev]
platform = espressif32
board = esp32dev
extra_scripts = scripts/custom_build.py
board_build.partitions = projects/myProject/esp32dev/v2.0.0/custom.csv
build_flags = -DVERSION="v1.0.1"
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

### Volledige Build (Automatisch)
```bash
# Via CLI
~/.platformio/penv/bin/platformio run -e esp32dev-v1_0_0
~/.platformio/penv/bin/platformio run -e esp32dev-v1_0_0 -t buildfs

# Of combined
~/.platformio/penv/bin/platformio run -e esp32dev-v1_0_0 && platformio run -e esp32dev-v1_0_0 -t buildfs
```

### VSCode Build Knoppen
Het script werkt automatisch met VSCode PlatformIO UI:
- ✅ **Build** knop - Werkt direct (auto-sync bij cached builds)
- ✅ **Upload** knop - Build + upload in één actie
- ✅ **Build Filesystem Image** knop - Maakt en kopieert filesystem
- ℹ️ **Clean** knop - Optioneel, niet meer nodig voor correcte sync

### Clean Build (Optioneel)
Alleen nodig bij problemen of complete rebuild:
```bash
~/.platformio/penv/bin/platformio run -e esp32dev-v1_0_0 -t clean
~/.platformio/penv/bin/platformio run -e esp32dev-v1_0_0
~/.platformio/penv/bin/platformio run -e esp32dev-v1_0_0 -t buildfs
```

## Console Output

### ESP32 Build (Clean)
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
  ℹ️  Filesystem offset gevonden in partitions.csv: 0x270000
  ✓ flash.json bijgewerkt met littlefs.bin
>>> [POST-BUILDFS] Klaar.
```

### ESP32 Cached Build met Auto-Sync
```
>>> Auto-sync: Detected changes, updating project files...

>>> [POST-BUILD] Voor myProject/esp32dev/v1.0.0
  ESP32 gedetecteerd - genereer idedata.json...
  Kopieer flash images met offsets uit idedata.json:
  ✓ bootloader.bin → projects/myProject/esp32dev/v1.0.0/bootloader.bin
  ✓ partitions.bin → projects/myProject/esp32dev/v1.0.0/partitions.bin
  ✓ boot_app0.bin → projects/myProject/esp32dev/v1.0.0/boot_app0.bin
  Kopieer firmware met offset 0x10000:
  ✓ firmware.bin → projects/myProject/esp32dev/v1.0.0/firmware.bin
  Zoek naar filesystem image...
  Kopieer filesystem image: littlefs.bin
  ✓ littlefs.bin → projects/myProject/esp32dev/v1.0.0/littlefs.bin
  ℹ️  Filesystem offset gevonden in partitions.csv: 0x790000
  ✓ flash.json aangemaakt
>>> [POST-BUILD] Klaar.
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

### Bestanden niet gekopieerd na cached build
**Probleem:** Na een cached build in VSCode staan bestanden niet in project directory  
**Oplossing:** Dit wordt nu automatisch opgelost door auto-sync. Indien toch problemen:
1. Check console output voor "Auto-sync" berichten
2. Verifieer dat timestamps correct zijn (geen clock skew)
3. Als persistent: run clean build

### Build werkt in CLI maar niet in VSCode
**Probleem:** Script werkt via terminal maar niet met VSCode UI knoppen  
**Oplossing:** Dit is opgelost met auto-sync functionaliteit. VSCode gebruikt cached builds, die nu automatisch gedetecteerd en gesync'd worden.

### Filesystem gebouwd voor firmware
**Probleem:** Buildfs uitgevoerd, daarna buildprog, bestanden niet gekopieerd  
**Oplossing:** Auto-sync detecteert dit automatisch en kopieert alle benodigde bestanden bij de buildprog actie.

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

6. **Intelligent Auto-Sync**
   - Werkt met cached builds
   - Geen handmatige clean nodig
   - VSCode UI compatible
   - Flexibele build volgorde (buildfs eerst of buildprog eerst)
   - Efficiënt (sync alleen bij wijzigingen)

## Technische Details

### Filesystem Offset Detectie

De `get_filesystem_offset()` functie gebruikt een robuuste aanpak:

1. **Primary Method - partitions.csv parsing:**
   ```python
   # Check zowel Name als SubType kolommen
   if 'spiffs' in name or 'spiffs' in subtype:
       return offset
   if 'littlefs' in name or 'littlefs' in subtype:
       return offset
   # Ook: fatfs, ffat
   ```

2. **Hex Offset Conversie:**
   - Accepteert hex (0x790000) en decimal formaten
   - Normaliseert naar hex string
   - Fallback bij parse errors

3. **Standaard Offsets:**
   - ESP32: 0x290000 (2.625 MB)
   - ESP8266: 0x300000 (3 MB)

### Board Build Partitions

Het script leest `board_build.partitions` correct via:
```python
custom_partitions = env.GetProjectOption("board_build.partitions", None)
```

Dit zorgt voor correcte detectie van custom partition files in platformio.ini, zoals:
```ini
board_build.partitions = partitions/default_8MB.csv
board_build.partitions = partitions/bigProgSmallSpiffs.csv
```

### Build Event Hooks

Het script registreert meerdere build hooks:
```python
env.AddPreAction("buildprog", pre_build_action)
env.AddPostAction("buildprog", post_build_action)
env.AddPostAction("$BUILD_DIR/firmware.elf", check_and_sync)
env.AddPostAction("buildfs", post_buildfs_action)
```

De `check_and_sync` hook op firmware.elf zorgt voor auto-sync bij cached builds.

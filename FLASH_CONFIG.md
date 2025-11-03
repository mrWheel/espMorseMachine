# Flash Configuration Documentation

## Overzicht

Het `scripts/custom_build.py` script is aangepast om automatisch alle benodigde flash bestanden te kopiëren en een `flash.json` configuratie bestand te genereren.

## Wat doet het script nu?

### 1. Leest idedata.json
Het script leest tijdens de post-build fase het `idedata.json` bestand uit de build directory. Dit bestand bevat:
- `extra.flash_images`: Array met bootloader, partitions en boot_app0 bestanden inclusief hun flash offsets
- `extra.application_offset`: De offset waar firmware.bin geflashed moet worden

### 2. Kopieert alle benodigde bestanden
Het script kopieert nu de exacte bestanden die gebruikt worden tijdens het flashen:

#### Voor ESP32:
- `bootloader.bin` (offset: 0x1000) - uit idedata.json
- `partitions.bin` (offset: 0x8000) - uit idedata.json  
- `boot_app0.bin` (offset: 0xe000) - uit idedata.json
- `firmware.bin` (offset: 0x10000) - de gecompileerde applicatie
- `spiffs.bin` of `littlefs.bin` - filesystem image (offset wordt bepaald uit partitions.csv)
- `partitions.csv` - de gebruikte partitie tabel

#### Voor ESP8266:
- `firmware.bin` - de gecompileerde applicatie
- `littlefs.bin` of `spiffs.bin` - filesystem image

### 3. Genereert flash.json
Het script creëert een `flash.json` bestand in de project directory met:
- Board type
- Versie nummer
- Array van alle flash bestanden met hun offset adressen

## Voorbeeld flash.json

```json
{
  "board": "esp32dev",
  "version": "v2.2.2",
  "flash_files": [
    {
      "offset": "0x1000",
      "file": "bootloader.bin"
    },
    {
      "offset": "0x8000",
      "file": "partitions.bin"
    },
    {
      "offset": "0xe000",
      "file": "boot_app0.bin"
    },
    {
      "offset": "0x10000",
      "file": "firmware.bin"
    },
    {
      "offset": "0x290000",
      "file": "spiffs.bin"
    }
  ]
}
```

## Gebruik van flash.json

Dit bestand kan gebruikt worden om:
1. De ESP32/ESP8266 te flashen met esptool.py:
```bash
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 \
  write_flash 0x1000 bootloader.bin \
               0x8000 partitions.bin \
               0xe000 boot_app0.bin \
               0x10000 firmware.bin \
               0x290000 spiffs.bin
```

2. Automatische flash scripts te genereren
3. Web-based flash tools te configureren (zoals ESP Web Tools)

## Filesystem Offset Detectie

Het script bepaalt de filesystem offset op de volgende manier:

1. **Eerst**: Leest `partitions.csv` en zoekt naar een partitie met 'spiffs', 'littlefs' of 'fatfs' in de naam
2. **Fallback voor ESP32**: Gebruikt standaard offset 0x290000
3. **Fallback voor ESP8266**: Gebruikt standaard offset 0x300000

## Directory Structuur

Na een succesvolle build worden bestanden gekopieerd naar:
```
projects/
└── morseMachine/
    ├── esp32dev/
    │   └── v2.2.2/
    │       ├── bootloader.bin
    │       ├── partitions.bin
    │       ├── boot_app0.bin
    │       ├── firmware.bin
    │       ├── spiffs.bin
    │       ├── partitions.csv
    │       └── flash.json
    └── esp12e/
        └── v3.3.3/
            ├── firmware.bin
            ├── littlefs.bin
            └── flash.json
```

## Logging

Het script toont tijdens de build gedetailleerde informatie over:
- Welke bestanden worden gekopieerd
- Waar ze vandaan komen
- De flash offsets
- Eventuele fouten of waarschuwingen

## Troubleshooting

### Geen idedata.json gevonden
Als `idedata.json` niet bestaat, gebruikt het script een fallback mechanisme en kopieert alle .bin bestanden uit de build directory.

### Filesystem offset niet gevonden
Als het offset niet kan worden bepaald uit `partitions.csv`, wordt er een standaard offset gebruikt gebaseerd op het platform (ESP32 of ESP8266).

### Boot_app0.bin niet gevonden
Dit bestand wordt gezocht in het Arduino framework. Als het niet gevonden wordt, toont het script een waarschuwing maar gaat wel door met de rest van de build.

Versie gevonden in build_flags: v1.0.0

# Project morseMachine

```
Build Log - 2025-11-04 13:47:12
Board: esp32-s3-devkitc-1
Version: v1.0.0
Environment: esp32-s3
```
## Framework-pad:
/Users/WillemA/.platformio/packages/framework-arduinoespressif32


### [PRE-BUILD]

Aangepaste partitions file gevonden: partitions/default_8MB.csv

✓ default_8MB.csv → projects/morseMachine/esp32-s3-devkitc-1/v1.0.0/partitions.csv


boot_app0.bin uit framework kopiëren...

✓ boot_app0.bin → projects/morseMachine/esp32-s3-devkitc-1/v1.0.0/boot_app0.bin



### [POST-BUILD]

ESP32 gedetecteerd - genereer idedata.json...

Kopieer flash images met offsets uit idedata.json:

✓ bootloader.bin → projects/morseMachine/esp32-s3-devkitc-1/v1.0.0/bootloader.bin

✓ partitions.bin → projects/morseMachine/esp32-s3-devkitc-1/v1.0.0/partitions.bin

✓ boot_app0.bin → projects/morseMachine/esp32-s3-devkitc-1/v1.0.0/boot_app0.bin


Kopieer firmware met offset 0x10000:

✓ firmware.bin → projects/morseMachine/esp32-s3-devkitc-1/v1.0.0/firmware.bin


Zoek naar filesystem image...

Bestaande filesystem image gevonden: **littlefs.bin**

  ℹ️  Filesystem offset gevonden in partitions.csv: 0x790000
✓ littlefs.bin toegevoegd aan flash.json met offset 0x790000

✓ flash.json aangemaakt: projects/morseMachine/esp32-s3-devkitc-1/v1.0.0/flash.json


### Flash Configuratie:

- `0x0000` → **bootloader.bin**

- `0x8000` → **partitions.bin**

- `0xe000` → **boot_app0.bin**

- `0x10000` → **firmware.bin**

- `0x790000` → **littlefs.bin**


### Partitions.csv Inhoud:

```
# Name,   Type, SubType, Offset,  Size, Flags
nvs,      data, nvs,     0x9000,  0x5000,
otadata,  data, ota,     0xe000,  0x2000,
app0,     app,  ota_0,   0x10000, 0x3C0000,
app1,     app,  ota_1,   0x3D0000,0x3C0000,
spiffs,   data, spiffs,  0x790000,0x70000,
```

### [POST-BUILDFS]

Zoek naar filesystem image...

Kopieer filesystem image: **littlefs.bin**

✓ littlefs.bin → projects/morseMachine/esp32-s3-devkitc-1/v1.0.0/littlefs.bin



Versie gevonden in environment naam: v1.0.1

# Project UnnamedProject

```
Build Log - 2025-11-08 10:21:36
Board: esp32-s3-devkitc-1
Version: v1.0.1
Environment: esp32-s3-v1_0_1
```
## Framework-pad:
/Users/WillemA/.platformio/packages/framework-arduinoespressif32


### [PRE-BUILD]

Aangepaste partitions file gevonden: partitions/bigSpiffs.csv

✓ bigSpiffs.csv → projects/UnnamedProject/esp32-s3-devkitc-1/v1.0.1/partitions.csv


boot_app0.bin uit framework kopiëren...

✓ boot_app0.bin → projects/UnnamedProject/esp32-s3-devkitc-1/v1.0.1/boot_app0.bin



### [POST-BUILD]

ESP32 gedetecteerd - genereer idedata.json...

Kopieer flash images met offsets uit idedata.json:

✓ bootloader.bin → projects/UnnamedProject/esp32-s3-devkitc-1/v1.0.1/bootloader.bin

✓ partitions.bin → projects/UnnamedProject/esp32-s3-devkitc-1/v1.0.1/partitions.bin

✓ boot_app0.bin → projects/UnnamedProject/esp32-s3-devkitc-1/v1.0.1/boot_app0.bin


Kopieer firmware met offset 0x10000:

✓ firmware.bin → projects/UnnamedProject/esp32-s3-devkitc-1/v1.0.1/firmware.bin


Zoek naar filesystem image...

✓ flash.json aangemaakt: projects/UnnamedProject/esp32-s3-devkitc-1/v1.0.1/flash.json


### Flash Configuratie:

- `0x0000` → **bootloader.bin**

- `0x8000` → **partitions.bin**

- `0xe000` → **boot_app0.bin**

- `0x10000` → **firmware.bin**


### Partitions.csv Inhoud:

```
# Name,   Type, SubType, Offset,   Size,      Flags
nvs,      data, nvs,     0x9000,   0x5000,
otadata,  data, ota,     0xE000,   0x2000,
app0,     app,  ota_0,   0x10000,  0x300000,
app1,     app,  ota_1,   0x310000, 0x300000,
spiffs,   data, spiffs,  0x610000, 0x1EF000,
```

### [POST-BUILDFS]

Zoek naar filesystem image...

Kopieer filesystem image: **littlefs.bin**

✓ littlefs.bin → projects/UnnamedProject/esp32-s3-devkitc-1/v1.0.1/littlefs.bin


  ℹ️  Filesystem offset gevonden in partitions.csv: 0x610000
✓ flash.json bijgewerkt met littlefs.bin


### [PRE-BUILD]

Aangepaste partitions file gevonden: partitions/bigSpiffs.csv

✓ bigSpiffs.csv → projects/espMorseMachine/esp32-s3-devkitc-1/v1.0.1/partitions.csv


boot_app0.bin uit framework kopiëren...

✓ boot_app0.bin → projects/espMorseMachine/esp32-s3-devkitc-1/v1.0.1/boot_app0.bin



### [POST-BUILD]

ESP32 gedetecteerd - genereer idedata.json...

Kopieer flash images met offsets uit idedata.json:

✓ bootloader.bin → projects/espMorseMachine/esp32-s3-devkitc-1/v1.0.1/bootloader.bin

✓ partitions.bin → projects/espMorseMachine/esp32-s3-devkitc-1/v1.0.1/partitions.bin

✓ boot_app0.bin → projects/espMorseMachine/esp32-s3-devkitc-1/v1.0.1/boot_app0.bin


Kopieer firmware met offset 0x10000:

✓ firmware.bin → projects/espMorseMachine/esp32-s3-devkitc-1/v1.0.1/firmware.bin


Zoek naar filesystem image...

Kopieer filesystem image: **littlefs.bin**

✓ littlefs.bin → projects/espMorseMachine/esp32-s3-devkitc-1/v1.0.1/littlefs.bin


  ℹ️  Filesystem offset gevonden in partitions.csv: 0x610000
✓ flash.json aangemaakt: projects/espMorseMachine/esp32-s3-devkitc-1/v1.0.1/flash.json


### Flash Configuratie:

- `0x0000` → **bootloader.bin**

- `0x8000` → **partitions.bin**

- `0xe000` → **boot_app0.bin**

- `0x10000` → **firmware.bin**

- `0x610000` → **littlefs.bin**


### Partitions.csv Inhoud:

```
# Name,   Type, SubType, Offset,   Size,      Flags
nvs,      data, nvs,     0x9000,   0x5000,
otadata,  data, ota,     0xE000,   0x2000,
app0,     app,  ota_0,   0x10000,  0x300000,
app1,     app,  ota_1,   0x310000, 0x300000,
spiffs,   data, spiffs,  0x610000, 0x1EF000,
```

### [POST-BUILDFS]

Zoek naar filesystem image...

Kopieer filesystem image: **littlefs.bin**

✓ littlefs.bin → projects/espMorseMachine/esp32-s3-devkitc-1/v1.0.1/littlefs.bin



### [PRE-BUILD]

Aangepaste partitions file gevonden: partitions/bigSpiffs.csv

✓ bigSpiffs.csv → projects/espMorseMachine/esp32-s3-devkitc-1/v1.0.1/partitions.csv


boot_app0.bin uit framework kopiëren...

✓ boot_app0.bin → projects/espMorseMachine/esp32-s3-devkitc-1/v1.0.1/boot_app0.bin



### [POST-BUILD]

ESP32 gedetecteerd - genereer idedata.json...

Kopieer flash images met offsets uit idedata.json:

✓ bootloader.bin → projects/espMorseMachine/esp32-s3-devkitc-1/v1.0.1/bootloader.bin

✓ partitions.bin → projects/espMorseMachine/esp32-s3-devkitc-1/v1.0.1/partitions.bin

✓ boot_app0.bin → projects/espMorseMachine/esp32-s3-devkitc-1/v1.0.1/boot_app0.bin


Kopieer firmware met offset 0x10000:

✓ firmware.bin → projects/espMorseMachine/esp32-s3-devkitc-1/v1.0.1/firmware.bin


Zoek naar filesystem image...

Kopieer filesystem image: **littlefs.bin**

✓ littlefs.bin → projects/espMorseMachine/esp32-s3-devkitc-1/v1.0.1/littlefs.bin


  ℹ️  Filesystem offset gevonden in partitions.csv: 0x610000
✓ flash.json aangemaakt: projects/espMorseMachine/esp32-s3-devkitc-1/v1.0.1/flash.json


### Flash Configuratie:

- `0x0000` → **bootloader.bin**

- `0x8000` → **partitions.bin**

- `0xe000` → **boot_app0.bin**

- `0x10000` → **firmware.bin**

- `0x610000` → **littlefs.bin**


### Partitions.csv Inhoud:

```
# Name,   Type, SubType, Offset,   Size,      Flags
nvs,      data, nvs,     0x9000,   0x5000,
otadata,  data, ota,     0xE000,   0x2000,
app0,     app,  ota_0,   0x10000,  0x300000,
app1,     app,  ota_1,   0x310000, 0x300000,
spiffs,   data, spiffs,  0x610000, 0x1EF000,
```

### [POST-BUILDFS]

Zoek naar filesystem image...

Kopieer filesystem image: **littlefs.bin**

✓ littlefs.bin → projects/espMorseMachine/esp32-s3-devkitc-1/v1.0.1/littlefs.bin



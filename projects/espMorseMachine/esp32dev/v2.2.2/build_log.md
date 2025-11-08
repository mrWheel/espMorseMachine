Versie gevonden in environment naam: v2.2.2

# Project UnnamedProject

```
Build Log - 2025-11-08 10:21:20
Board: esp32dev
Version: v2.2.2
Environment: esp32dev-v2_2_2
```
## Framework-pad:
/Users/WillemA/.platformio/packages/framework-arduinoespressif32


### [PRE-BUILD]

Aangepaste partitions file gevonden: partitions/bigProgPartitions.csv

✓ bigProgPartitions.csv → projects/UnnamedProject/esp32dev/v2.2.2/partitions.csv


boot_app0.bin uit framework kopiëren...

✓ boot_app0.bin → projects/UnnamedProject/esp32dev/v2.2.2/boot_app0.bin



### [POST-BUILD]

ESP32 gedetecteerd - genereer idedata.json...

Kopieer flash images met offsets uit idedata.json:

✓ bootloader.bin → projects/UnnamedProject/esp32dev/v2.2.2/bootloader.bin

✓ partitions.bin → projects/UnnamedProject/esp32dev/v2.2.2/partitions.bin

✓ boot_app0.bin → projects/UnnamedProject/esp32dev/v2.2.2/boot_app0.bin


Kopieer firmware met offset 0x10000:

✓ firmware.bin → projects/UnnamedProject/esp32dev/v2.2.2/firmware.bin


Zoek naar filesystem image...

✓ flash.json aangemaakt: projects/UnnamedProject/esp32dev/v2.2.2/flash.json


### Flash Configuratie:

- `0x1000` → **bootloader.bin**

- `0x8000` → **partitions.bin**

- `0xe000` → **boot_app0.bin**

- `0x10000` → **firmware.bin**


### Partitions.csv Inhoud:

```
# Name,   Type, SubType, Offset,  Size, Flags
nvs,      data, nvs,     0x9000,  0x5000,
otadata,  data, ota,     0xe000,  0x2000,
app0,     app,  ota_0,   0x10000, 0x1E0000,
app1,     app,  ota_1,   0x1F0000,0x1E0000,
spiffs,   data, spiffs,  0x3D0000,0x30000,
```

### [POST-BUILDFS]

Zoek naar filesystem image...

Kopieer filesystem image: **littlefs.bin**

✓ littlefs.bin → projects/UnnamedProject/esp32dev/v2.2.2/littlefs.bin


  ℹ️  Filesystem offset gevonden in partitions.csv: 0x3D0000
✓ flash.json bijgewerkt met littlefs.bin


### [PRE-BUILD]

Aangepaste partitions file gevonden: partitions/bigProgPartitions.csv

✓ bigProgPartitions.csv → projects/espMorseMachine/esp32dev/v2.2.2/partitions.csv


boot_app0.bin uit framework kopiëren...

✓ boot_app0.bin → projects/espMorseMachine/esp32dev/v2.2.2/boot_app0.bin



### [POST-BUILD]

ESP32 gedetecteerd - genereer idedata.json...

Kopieer flash images met offsets uit idedata.json:

✓ bootloader.bin → projects/espMorseMachine/esp32dev/v2.2.2/bootloader.bin

✓ partitions.bin → projects/espMorseMachine/esp32dev/v2.2.2/partitions.bin

✓ boot_app0.bin → projects/espMorseMachine/esp32dev/v2.2.2/boot_app0.bin


Kopieer firmware met offset 0x10000:

✓ firmware.bin → projects/espMorseMachine/esp32dev/v2.2.2/firmware.bin


Zoek naar filesystem image...

Kopieer filesystem image: **littlefs.bin**

✓ littlefs.bin → projects/espMorseMachine/esp32dev/v2.2.2/littlefs.bin


  ℹ️  Filesystem offset gevonden in partitions.csv: 0x3D0000
✓ flash.json aangemaakt: projects/espMorseMachine/esp32dev/v2.2.2/flash.json


### Flash Configuratie:

- `0x1000` → **bootloader.bin**

- `0x8000` → **partitions.bin**

- `0xe000` → **boot_app0.bin**

- `0x10000` → **firmware.bin**

- `0x3D0000` → **littlefs.bin**


### Partitions.csv Inhoud:

```
# Name,   Type, SubType, Offset,  Size, Flags
nvs,      data, nvs,     0x9000,  0x5000,
otadata,  data, ota,     0xe000,  0x2000,
app0,     app,  ota_0,   0x10000, 0x1E0000,
app1,     app,  ota_1,   0x1F0000,0x1E0000,
spiffs,   data, spiffs,  0x3D0000,0x30000,
```

### [POST-BUILDFS]

Zoek naar filesystem image...

Kopieer filesystem image: **littlefs.bin**

✓ littlefs.bin → projects/espMorseMachine/esp32dev/v2.2.2/littlefs.bin



### [PRE-BUILD]

Aangepaste partitions file gevonden: partitions/bigProgPartitions.csv

✓ bigProgPartitions.csv → projects/espMorseMachine/esp32dev/v2.2.2/partitions.csv


boot_app0.bin uit framework kopiëren...

✓ boot_app0.bin → projects/espMorseMachine/esp32dev/v2.2.2/boot_app0.bin



### [POST-BUILD]

ESP32 gedetecteerd - genereer idedata.json...

Kopieer flash images met offsets uit idedata.json:

✓ bootloader.bin → projects/espMorseMachine/esp32dev/v2.2.2/bootloader.bin

✓ partitions.bin → projects/espMorseMachine/esp32dev/v2.2.2/partitions.bin

✓ boot_app0.bin → projects/espMorseMachine/esp32dev/v2.2.2/boot_app0.bin


Kopieer firmware met offset 0x10000:

✓ firmware.bin → projects/espMorseMachine/esp32dev/v2.2.2/firmware.bin


Zoek naar filesystem image...

Kopieer filesystem image: **littlefs.bin**

✓ littlefs.bin → projects/espMorseMachine/esp32dev/v2.2.2/littlefs.bin


  ℹ️  Filesystem offset gevonden in partitions.csv: 0x3D0000
✓ flash.json aangemaakt: projects/espMorseMachine/esp32dev/v2.2.2/flash.json


### Flash Configuratie:

- `0x1000` → **bootloader.bin**

- `0x8000` → **partitions.bin**

- `0xe000` → **boot_app0.bin**

- `0x10000` → **firmware.bin**

- `0x3D0000` → **littlefs.bin**


### Partitions.csv Inhoud:

```
# Name,   Type, SubType, Offset,  Size, Flags
nvs,      data, nvs,     0x9000,  0x5000,
otadata,  data, ota,     0xe000,  0x2000,
app0,     app,  ota_0,   0x10000, 0x1E0000,
app1,     app,  ota_1,   0x1F0000,0x1E0000,
spiffs,   data, spiffs,  0x3D0000,0x30000,
```

### [POST-BUILDFS]

Zoek naar filesystem image...

Kopieer filesystem image: **littlefs.bin**

✓ littlefs.bin → projects/espMorseMachine/esp32dev/v2.2.2/littlefs.bin



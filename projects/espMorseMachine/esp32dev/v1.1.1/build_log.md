Versie gevonden in environment naam: v1.1.1

# Project UnnamedProject

```
Build Log - 2025-11-08 10:21:12
Board: esp32dev
Version: v1.1.1
Environment: esp32dev-v1_1_1
```
## Framework-pad:
/Users/WillemA/.platformio/packages/framework-arduinoespressif32


### [PRE-BUILD]

Geen board_build.partitions — gebruik default.csv uit framework

✓ default.csv → projects/UnnamedProject/esp32dev/v1.1.1/partitions.csv


boot_app0.bin uit framework kopiëren...

✓ boot_app0.bin → projects/UnnamedProject/esp32dev/v1.1.1/boot_app0.bin



### [POST-BUILD]

ESP32 gedetecteerd - genereer idedata.json...

Kopieer flash images met offsets uit idedata.json:

✓ bootloader.bin → projects/UnnamedProject/esp32dev/v1.1.1/bootloader.bin

✓ partitions.bin → projects/UnnamedProject/esp32dev/v1.1.1/partitions.bin

✓ boot_app0.bin → projects/UnnamedProject/esp32dev/v1.1.1/boot_app0.bin


Kopieer firmware met offset 0x10000:

✓ firmware.bin → projects/UnnamedProject/esp32dev/v1.1.1/firmware.bin


Zoek naar filesystem image...

✓ flash.json aangemaakt: projects/UnnamedProject/esp32dev/v1.1.1/flash.json


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
app0,     app,  ota_0,   0x10000, 0x140000,
app1,     app,  ota_1,   0x150000,0x140000,
spiffs,   data, spiffs,  0x290000,0x160000,
coredump, data, coredump,0x3F0000,0x10000,
```

### [POST-BUILDFS]

Zoek naar filesystem image...

Kopieer filesystem image: **littlefs.bin**

✓ littlefs.bin → projects/UnnamedProject/esp32dev/v1.1.1/littlefs.bin


  ℹ️  Filesystem offset gevonden in partitions.csv: 0x290000
✓ flash.json bijgewerkt met littlefs.bin


### [PRE-BUILD]

Geen board_build.partitions — gebruik default.csv uit framework

✓ default.csv → projects/espMorseMachine/esp32dev/v1.1.1/partitions.csv


boot_app0.bin uit framework kopiëren...

✓ boot_app0.bin → projects/espMorseMachine/esp32dev/v1.1.1/boot_app0.bin



### [POST-BUILD]

ESP32 gedetecteerd - genereer idedata.json...

Kopieer flash images met offsets uit idedata.json:

✓ bootloader.bin → projects/espMorseMachine/esp32dev/v1.1.1/bootloader.bin

✓ partitions.bin → projects/espMorseMachine/esp32dev/v1.1.1/partitions.bin

✓ boot_app0.bin → projects/espMorseMachine/esp32dev/v1.1.1/boot_app0.bin


Kopieer firmware met offset 0x10000:

✓ firmware.bin → projects/espMorseMachine/esp32dev/v1.1.1/firmware.bin


Zoek naar filesystem image...

Kopieer filesystem image: **littlefs.bin**

✓ littlefs.bin → projects/espMorseMachine/esp32dev/v1.1.1/littlefs.bin


  ℹ️  Filesystem offset gevonden in partitions.csv: 0x290000
✓ flash.json aangemaakt: projects/espMorseMachine/esp32dev/v1.1.1/flash.json


### Flash Configuratie:

- `0x1000` → **bootloader.bin**

- `0x8000` → **partitions.bin**

- `0xe000` → **boot_app0.bin**

- `0x10000` → **firmware.bin**

- `0x290000` → **littlefs.bin**


### Partitions.csv Inhoud:

```
# Name,   Type, SubType, Offset,  Size, Flags
nvs,      data, nvs,     0x9000,  0x5000,
otadata,  data, ota,     0xe000,  0x2000,
app0,     app,  ota_0,   0x10000, 0x140000,
app1,     app,  ota_1,   0x150000,0x140000,
spiffs,   data, spiffs,  0x290000,0x160000,
coredump, data, coredump,0x3F0000,0x10000,
```

### [POST-BUILDFS]

Zoek naar filesystem image...

Kopieer filesystem image: **littlefs.bin**

✓ littlefs.bin → projects/espMorseMachine/esp32dev/v1.1.1/littlefs.bin



### [PRE-BUILD]

Geen board_build.partitions — gebruik default.csv uit framework

✓ default.csv → projects/espMorseMachine/esp32dev/v1.1.1/partitions.csv


boot_app0.bin uit framework kopiëren...

✓ boot_app0.bin → projects/espMorseMachine/esp32dev/v1.1.1/boot_app0.bin



### [POST-BUILD]

ESP32 gedetecteerd - genereer idedata.json...

Kopieer flash images met offsets uit idedata.json:

✓ bootloader.bin → projects/espMorseMachine/esp32dev/v1.1.1/bootloader.bin

✓ partitions.bin → projects/espMorseMachine/esp32dev/v1.1.1/partitions.bin

✓ boot_app0.bin → projects/espMorseMachine/esp32dev/v1.1.1/boot_app0.bin


Kopieer firmware met offset 0x10000:

✓ firmware.bin → projects/espMorseMachine/esp32dev/v1.1.1/firmware.bin


Zoek naar filesystem image...

Kopieer filesystem image: **littlefs.bin**

✓ littlefs.bin → projects/espMorseMachine/esp32dev/v1.1.1/littlefs.bin


  ℹ️  Filesystem offset gevonden in partitions.csv: 0x290000
✓ flash.json aangemaakt: projects/espMorseMachine/esp32dev/v1.1.1/flash.json


### Flash Configuratie:

- `0x1000` → **bootloader.bin**

- `0x8000` → **partitions.bin**

- `0xe000` → **boot_app0.bin**

- `0x10000` → **firmware.bin**

- `0x290000` → **littlefs.bin**


### Partitions.csv Inhoud:

```
# Name,   Type, SubType, Offset,  Size, Flags
nvs,      data, nvs,     0x9000,  0x5000,
otadata,  data, ota,     0xe000,  0x2000,
app0,     app,  ota_0,   0x10000, 0x140000,
app1,     app,  ota_1,   0x150000,0x140000,
spiffs,   data, spiffs,  0x290000,0x160000,
coredump, data, coredump,0x3F0000,0x10000,
```

### [POST-BUILDFS]

Zoek naar filesystem image...

Kopieer filesystem image: **littlefs.bin**

✓ littlefs.bin → projects/espMorseMachine/esp32dev/v1.1.1/littlefs.bin



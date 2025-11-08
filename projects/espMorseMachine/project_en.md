# ESP Morse Machine

## Project Description

The ESP Morse Machine is an IoT device that converts text to Morse code and transmits it via a blinking LED or buzzer. The project offers a modern web interface for control and monitoring, and supports a wide range of ESP8266 and ESP32 hardware platforms.

## Main Functionality

### Hardware
- **Platform support**: All ESP8266 and ESP32 variants
- **Filesystem**: LittleFS for the web files
- **GPIO output**: Configurable pin for LED or buzzer (normal/inverted)

### WiFi Behavior
1. **Automatic connection**: First attempts to connect with saved WiFi credentials (20 second timeout)
2. **WiFiManager fallback**: Starts a captive portal in AP mode on failure:
   - SSID: `espMorseMachine-ww:xx:yy:zz` (last 4 bytes of MAC address)
   - No password

### Web Interface

The project provides a complete web application (HTML/CSS/JavaScript) with:

- **Text input**: Input field for text to be translated
- **Visual feedback**: Blinking yellow "lamp" that runs synchronously with the physical GPIO
- **Live console**: Real-time display of Morse code output
- **Speed control**: Slider to adjust the dot-duration (base timing unit)
- **GPIO configuration**: Input field for pin number and toggle for normal/inverted mode
- **Responsive design**: Light style with white window (70-80% screen size)

### Morse Code Implementation

- **Complete character set**: All letters (A-Z), digits (0-9) and space
- **Correct timing**:
  - Dot = base time (adjustable via slider)
  - Dash = 3× dot
  - Letter gap = 3× dot  
  - Word gap = 7× dot
- **Triple sync**: GPIO, web interface and Serial Monitor work synchronously
- **Extensive logging**: Real-time output to Serial Monitor with emojis for status indication


## License & Development

This is a PlatformIO project developed for educational and experimental purposes with Morse code.

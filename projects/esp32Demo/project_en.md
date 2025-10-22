# espMorseMachine

This is a demo project for the ESP32.

It connects to a WiFi AP, but if that fails an AP is started where you can enter the credentials for your WiFi network.

A web server serves a frontend where you can enter text that is then converted to Morse code.

The text is shown in the frontend as dots and dashes, and also with a "LED". It is also possible to output the Morse code via a GPIO pin to a buzzer or an external LED.

The project is intended to test the **flasher.aandewiel.nl** website.
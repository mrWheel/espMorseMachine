// -----------------------------------------------------
// ESP Morse Machine - Frontend script
// lowerCamelCase + Allman style
// Volledige synchronisatie: frontend + Serial + GPIO
// -----------------------------------------------------

let dotDuration = 200;
let inverted = false;
let gpioPin = 2;

const consoleDiv      = document.getElementById("console");
const textInput       = document.getElementById("textInput");
const sendButton      = document.getElementById("sendButton");
const dotSlider       = document.getElementById("dotSlider");
const dotValue        = document.getElementById("dotValue");
const gpioInput       = document.getElementById("gpioInput");
const invertNormal    = document.getElementById("invertNormal");
const invertInversed  = document.getElementById("invertInversed");
const lamp            = document.getElementById("lamp");
const versionDiv      = document.getElementById("version");

// -------------------- helpers ------------------------

function sleep(ms)
{
  return new Promise(resolve => setTimeout(resolve, ms));
}

function logLine(text, color = "#1b1e27")
{
  const p = document.createElement("p");
  p.textContent = text;
  p.style.color = color;
  p.style.margin = "0 0 6px 0";
  consoleDiv.appendChild(p);
  consoleDiv.scrollTop = consoleDiv.scrollHeight;
  return p;
}

function newMorseLine()
{
  const line = document.createElement("p");
  line.className = "morseLine";
  line.style.margin = "0 0 10px 0";
  line.style.fontFamily = "monospace";
  line.style.whiteSpace = "pre-wrap"; // behoud spaties
  consoleDiv.appendChild(line);
  consoleDiv.scrollTop = consoleDiv.scrollHeight;
  return line;
}

function appendSymbol(lineElem, symbol, color = "#0a7a32")
{
  const span = document.createElement("span");
  span.style.color = color;

  if (symbol === " ")
  {
    span.innerHTML = "&nbsp;";
  }
  else
  {
    span.textContent = symbol;
  }

  lineElem.appendChild(span);
  consoleDiv.scrollTop = consoleDiv.scrollHeight;
}

function lampOn()
{
  lamp.style.backgroundColor = "#ffcf33";
  lamp.style.boxShadow = "0 0 16px rgba(255,207,51,.8), inset 0 1px 2px rgba(0,0,0,.2)";
}

function lampOff()
{
  lamp.style.backgroundColor = "#c7cedd";
  lamp.style.boxShadow = "inset 0 1px 2px rgba(0,0,0,.15)";
}

async function gpioWrite(state)
{
  try
  {
    await fetch(`/gpio?state=${state ? 1 : 0}&gpio=${gpioPin}&inv=${inverted ? 1 : 0}`);
  }
  catch (e)
  {
    // negeer fetchfouten
  }
}

async function serialStart(originalText)
{
  try { await fetch(`/serial?start=${encodeURIComponent(originalText)}`); } catch (e) {}
}

async function serialSymbol(token)
{
  try { await fetch(`/serial?symbol=${encodeURIComponent(token)}`); } catch (e) {}
}

async function serialEnd()
{
  try { await fetch(`/serial?end=1`); } catch (e) {}
}

function setUiEnabled(enabled)
{
  textInput.disabled = !enabled;
  sendButton.disabled = !enabled;

  gpioInput.disabled = false;
  invertNormal.disabled = false;
  invertInversed.disabled = false;
  dotSlider.disabled = false;
}

// -------------------- UI bindings --------------------

dotSlider.addEventListener("input", () =>
{
  dotDuration = parseInt(dotSlider.value);
  dotValue.textContent = `${dotDuration} ms`;
});

gpioInput.addEventListener("change", () =>
{
  const v = parseInt(gpioInput.value);
  if (Number.isFinite(v)) { gpioPin = v; }
  logLine(`GPIO ingesteld op ${gpioPin}`, "#445066");
});

invertNormal.addEventListener("change", () =>
{
  inverted = false;
  logLine("GPIO-actie: normaal", "#445066");
});

invertInversed.addEventListener("change", () =>
{
  inverted = true;
  logLine("GPIO-actie: inversed", "#445066");
});

textInput.addEventListener("keydown", (e) =>
{
  if (e.key === "Enter")
  {
    e.preventDefault();
    sendButton.click();
  }
});

// -------------------- hoofdactie --------------------

sendButton.addEventListener("click", async () =>
{
  const text = textInput.value.trim();
  if (text === "") return;

  setUiEnabled(false);

  // 1) Toon originele tekst
  logLine(`> ${text}`, "#0a66ff");

  // 2) Meld start aan Serial
  await serialStart(text);

  // 3) Morse map voor conversie
  const morseMap = {
    'A': '.-',    'B': '-...',  'C': '-.-.',  'D': '-..',
    'E': '.',     'F': '..-.',  'G': '--.',   'H': '....',
    'I': '..',    'J': '.---',  'K': '-.-',   'L': '.-..',
    'M': '--',    'N': '-.',    'O': '---',   'P': '.--.',
    'Q': '--.-',  'R': '.-.',   'S': '...',   'T': '-',
    'U': '..-',   'V': '...-',  'W': '.--',   'X': '-..-',
    'Y': '-.--',  'Z': '--..',
    '1': '.----', '2': '..---', '3': '...--', '4': '....-',
    '5': '.....', '6': '-....', '7': '--...', '8': '---..',
    '9': '----.', '0': '-----'
  };

  // 4) Nieuwe regel voor Morse
  const morseLine = newMorseLine();

  // 5) Timing
  const dash = dotDuration * 3;
  const letterGap = dotDuration * 3;
  const wordGap = dotDuration * 7;

  // 6) Verwerk tekst character per character
  const upperText = text.toUpperCase();
  
  for (let charIdx = 0; charIdx < upperText.length; charIdx++)
  {
    const char = upperText[charIdx];
    
    if (char === ' ')
    {
      //-- Woordspatie
      appendSymbol(morseLine, '    ', '#888888');
      serialSymbol("WORD");
      await sleep(wordGap);
    }
    else if (morseMap[char])
    {
      //-- Toon (LETTER) vóór morse patroon
      const letterLabel = `(${char})`;
      appendSymbol(morseLine, letterLabel, '#0066cc');
      
      //-- Stuur letter label ook naar Serial
      try 
      {
        await fetch(`/serial?label=${encodeURIComponent(letterLabel)}`);
      } 
      catch (e) {}
      
      const morsePattern = morseMap[char];
      
      //-- Speel morse patroon af
      for (let i = 0; i < morsePattern.length; i++)
      {
        const symbol = morsePattern[i];
        const duration = (symbol === '.') ? dotDuration : dash;
        
        lampOn();
        gpioWrite(true);
        serialSymbol(symbol);
        appendSymbol(morseLine, symbol);
        
        await sleep(duration);
        
        lampOff();
        gpioWrite(false);
        
        await sleep(dotDuration);
      }
      
      //-- Letterspatie (na morse patroon, tussen letters)
      if (charIdx < upperText.length - 1 && upperText[charIdx + 1] !== ' ')
      {
        appendSymbol(morseLine, '  ', '#888888');
        serialSymbol("SPACE");
        await sleep(letterGap);
      }
    }
  }

  // 7) Einde transmissie
  await serialEnd();
  textInput.value = "";
  setUiEnabled(true);
});

// -------------------- versie ophalen ------------------

async function fetchVersion()
{
  try
  {
    const res = await fetch("/version");
    if (res.ok)
    {
      const version = await res.text();
      versionDiv.textContent = version;
    }
  }
  catch (e)
  {
    // negeer fetchfouten
  }
}

fetchVersion();

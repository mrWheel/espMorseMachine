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

  // 3) Haal Morse op
  let morse = "";
  try
  {
    const res = await fetch(`/morse?text=${encodeURIComponent(text)}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    morse = await res.text();
  }
  catch (err)
  {
    logLine(`Fout bij /morse: ${String(err)}`, "#cc1122");
    setUiEnabled(true);
    return;
  }

  // 4) Nieuwe regel voor Morse
  const morseLine = newMorseLine();

  // 5) Timing
  const dash = dotDuration * 3;
  const letterGap = dotDuration * 3;
  const wordGap = dotDuration * 7;

  // 6) Speel Morse synchroon af
  for (let i = 0; i < morse.length; i++)
  {
    const symbol = morse[i];

    if (symbol === '.' || symbol === '-')
    {
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
    else if (symbol === ' ')
    {
      // Tel aantal spaties om te onderscheiden tussen letters/woorden
      let spaceCount = 1;
      while (i + spaceCount < morse.length && morse[i + spaceCount] === ' ')
      {
        spaceCount++;
      }

      appendSymbol(morseLine, ' '.repeat(spaceCount));

      if (spaceCount >= 4)
      {
        serialSymbol("WORD");
        await sleep(wordGap);
      }
      else
      {
        serialSymbol("SPACE");
        await sleep(letterGap);
      }

      i += (spaceCount - 1);
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

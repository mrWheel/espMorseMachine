Import("env")
import os
import shutil
import glob
import json
from datetime import datetime

# ---------------- LOGGING ----------------
build_log_file = None
build_log_buffer = []

def log_message(message, to_console=True):
  """
  Log een bericht naar console en build_log.txt.
  Buffer berichten tot we weten waar de log file moet komen.
  """
  global build_log_buffer
  
  if to_console:
    print(message)
  
  #-- Buffer het bericht
  build_log_buffer.append(message)
  
  #-- Als we al een log file hebben, schrijf direct
  if build_log_file and os.path.exists(os.path.dirname(build_log_file)):
    try:
      with open(build_log_file, 'a', encoding='utf-8') as f:
        f.write(message + '\n')
    except Exception as e:
      print(f"!!! Fout bij schrijven naar build_log.txt: {e}")

def flush_log_buffer(mode='a'):
  """
  Schrijf alle gebufferde berichten naar de log file.
  
  Parameters:
    mode: 'w' om te overschrijven, 'a' om toe te voegen (default='a')
  """
  global build_log_buffer, build_log_file
  
  if build_log_file and build_log_buffer:
    try:
      os.makedirs(os.path.dirname(build_log_file), exist_ok=True)
      with open(build_log_file, mode, encoding='utf-8') as f:
        f.write('\n'.join(build_log_buffer) + '\n')
      build_log_buffer = []
    except Exception as e:
      print(f"!!! Fout bij schrijven build_log.md: {e}")

# ---------------- HULPFUNCTIES ----------------
def copy_file(src, dst):
  """Veilig bestand kopiëren met logging."""
  try:
    if not os.path.exists(src):
      log_message(f"⚠️ Bestand niet gevonden: {src}\n")
      return False
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy(src, dst)
    log_message(f"✓ {os.path.basename(src)} → {os.path.relpath(dst, env.subst('$PROJECT_DIR'))}\n")
    return True
  except Exception as e:
    log_message(f"⚠️ Fout bij kopiëren {src}: {e}\n")
    return False

def read_idedata(build_dir):
  """Lees idedata.json en retourneer de data."""
  idedata_path = os.path.join(build_dir, "idedata.json")
  if not os.path.exists(idedata_path):
    log_message(f"  ⚠️  idedata.json niet gevonden: {idedata_path}")
    return None
  
  try:
    with open(idedata_path, 'r') as f:
      data = json.load(f)
    return data
  except Exception as e:
    log_message(f"  ⚠️  Fout bij lezen idedata.json: {e}")
    return None

# ---------------- INITIALISATIE ----------------
project_config = env.GetProjectConfig()
platform = env.PioPlatform()
active_env = env["PIOENV"]

#-- Bepaal project_name uit de projects/ directory structuur
project_dir = env.subst("$PROJECT_DIR")
projects_path = os.path.join(project_dir, "projects")

project_name = "UnnamedProject"
if os.path.exists(projects_path):
  subdirs = [d for d in os.listdir(projects_path) 
             if os.path.isdir(os.path.join(projects_path, d)) and not d.startswith('.')]
  if subdirs:
    project_name = subdirs[0]

#-- Bepaal versie met fallback logica
def get_version_from_env():
  """
  Haal versie op met de volgende prioriteit:
  1. Uit environment naam (bijv. "esp32dev-v1_1_1" → "v1.1.1")
  2. Uit build_flags (-DVERSION="v1.0.0")
  3. Uit idedata.json
  4. Fallback naar "v0.0.0"
  """
  #-- 1. Probeer uit environment naam
  version_parts = active_env.split('-v')
  if len(version_parts) > 1:
    version = f"v{version_parts[1].replace('_', '.')}"
    log_message(f"Versie gevonden in environment naam: {version}")
    return version
  
  #-- 2. Probeer uit build_flags
  try:
    build_flags = env.get("BUILD_FLAGS", [])
    for flag in build_flags:
      if isinstance(flag, str) and "VERSION" in flag:
        #-- Zoek naar -DVERSION="v1.0.0" of -DVERSION=v1.0.0
        if "=" in flag:
          version_str = flag.split("=", 1)[1].strip('"').strip("'")
          if version_str:
            log_message(f"Versie gevonden in build_flags: {version_str}")
            return version_str
  except Exception as e:
    log_message(f"  ⚠️  Fout bij lezen build_flags: {e}")
  
  #-- 3. Probeer uit idedata.json (later in post_build beschikbaar)
  build_dir = env.subst("$BUILD_DIR")
  idedata_path = os.path.join(build_dir, "idedata.json")
  if os.path.exists(idedata_path):
    try:
      with open(idedata_path, 'r') as f:
        idedata = json.load(f)
      if "defines" in idedata:
        for define in idedata.get("defines", []):
          if "VERSION" in define:
            version_str = define.split("=", 1)[1].strip('"').strip("'") if "=" in define else None
            if version_str:
              log_message(f"Versie gevonden in idedata.json: {version_str}")
              return version_str
    except Exception as e:
      log_message(f"  ⚠️  Fout bij lezen idedata.json voor versie: {e}")
  
  #-- 4. Fallback
  log_message("  ⚠️  Geen versie gevonden, gebruik fallback v0.0.0")
  return "v0.0.0"

version = get_version_from_env()

board = env["BOARD"]

# Doelmap aanmaken
target_dir = os.path.join("projects", project_name, board, version)
os.makedirs(target_dir, exist_ok=True)

#-- Initialiseer build log file
build_log_file = os.path.join(target_dir, "build_log.md")

# ---------------- FRAMEWORK-DETECTIE ----------------
frameworks = env.get("PIOFRAMEWORK", [])
framework_path = None

if "arduino" in frameworks:
  platform_name = platform.name.lower()
  if "32" in platform_name:
    framework_key = "framework-arduinoespressif32"
  elif "8266" in platform_name:
    framework_key = "framework-arduinoespressif8266"
  else:
    # fallback voor toekomstige varianten
    framework_key = (
      platform.get_package_dir("framework-arduinoespressif32")
      or platform.get_package_dir("framework-arduinoespressif8266")
    )
  framework_path = (
    platform.get_package_dir(framework_key)
    if isinstance(framework_key, str)
    else framework_key
  )

# ---------------- PRE-BUILD ----------------
def pre_build_action(source, target, env):
  #-- Check of dit een nieuwe build is (buildprog start altijd met pre_build)
  #-- Als build_log.md NIET bestaat, maak dan header aan
  if not os.path.exists(build_log_file):
    log_message(f"\n# Project {project_name}\n")
    log_message(f"```")
    log_message(f"Build Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_message(f"Board: {board}")
    log_message(f"Version: {version}")
    log_message(f"Environment: {active_env}")
    log_message(f"```")
    #log_message(f"{'='*60}\n")
    if framework_path:
      log_message(f"## Framework-pad:\n{framework_path}\n")
    flush_log_buffer(mode='w')  # Nieuwe file, overschrijf
  
  log_message(f"\n### [PRE-BUILD]\n")

  platform_name = platform.name.lower()
  is_esp32 = "32" in platform_name
  is_esp8266 = "8266" in platform_name

  if is_esp32:
    #-- ESP32: Partitions en boot_app0.bin
    partitions_dest = os.path.join(target_dir, "partitions.csv")

    # 1️⃣ Controleer op custom partitions file
    custom_partitions = None
    try:
      custom_partitions = env.GetProjectOption("board_build.partitions", None)
    except Exception:
      pass

    if custom_partitions:
      custom_path = os.path.join(env.subst("$PROJECT_DIR"), custom_partitions)
      if os.path.exists(custom_path):
        log_message(f"Aangepaste partitions file gevonden: {custom_partitions}\n")
        copy_file(custom_path, partitions_dest)
        log_message("")  # Extra line break
      else:
        log_message(f"⚠️ board_build.partitions verwijst naar niet-bestaand bestand: {custom_partitions}\n")
        # Fallback naar default.csv
        if framework_path:
          default_csv_path = os.path.join(framework_path, "tools", "partitions", "default.csv")
          if os.path.exists(default_csv_path):
            log_message("Gebruik fallback: default.csv uit framework\n")
            copy_file(default_csv_path, partitions_dest)
            log_message("")  # Extra line break
    else:
      # Geen custom partitions file → gebruik default.csv uit framework
      if framework_path:
        default_csv_path = os.path.join(framework_path, "tools", "partitions", "default.csv")
        if os.path.exists(default_csv_path):
          log_message("Geen board_build.partitions — gebruik default.csv uit framework\n")
          copy_file(default_csv_path, partitions_dest)
          log_message("")  # Extra line break
        else:
          log_message("⚠️ Geen default.csv gevonden in framework.\n")
      else:
        log_message("⚠️ Frameworkpad onbekend, kan geen partitions.csv genereren.\n")

    # 2️⃣ boot_app0.bin uit framework kopiëren
    if framework_path:
      log_message("boot_app0.bin uit framework kopiëren...\n")
      boot_app0_found = False
      for root, _, files in os.walk(framework_path):
        if boot_app0_found:
          break
        for f in files:
          if f == "boot_app0.bin":
            src = os.path.join(root, f)
            dst = os.path.join(target_dir, f)
            copy_file(src, dst)
            boot_app0_found = True
            break
      if not boot_app0_found:
        log_message("⚠️ boot_app0.bin niet gevonden in framework.\n")
      log_message("")  # Extra line break
    else:
      log_message("⚠️ Geen frameworkpad beschikbaar, boot_app0.bin overgeslagen.\n")

  elif is_esp8266:
    log_message("ESP8266 detecteerd — geen partitions.csv of boot_app0.bin nodig\n")

# ---------------- POST-BUILD ----------------
def post_build_action(source, target, env):
  log_message(f"\n### [POST-BUILD]\n")

  build_dir = env.subst("$BUILD_DIR")
  if not os.path.exists(build_dir):
    log_message("⚠️ Build-map bestaat niet — build is mogelijk mislukt.\n")
    return

  platform_name = platform.name.lower()
  is_esp32 = "32" in platform_name
  is_esp8266 = "8266" in platform_name
  
  flash_config = []
  
  if is_esp32:
    log_message("ESP32 gedetecteerd - genereer idedata.json...\n")
    
    #-- Genereer idedata.json expliciet
    import subprocess
    try:
      idedata_cmd = [
        env.subst("$PYTHONEXE"),
        "-m", "platformio",
        "run", "-e", active_env, "-t", "idedata"
      ]
      result = subprocess.run(idedata_cmd, 
                            capture_output=True, 
                            text=True,
                            cwd=env.subst("$PROJECT_DIR"))
      
      #-- Zoek JSON output in stdout
      import re
      json_match = re.search(r'\{.*"extra".*\}', result.stdout, re.DOTALL)
      if json_match:
        idedata = json.loads(json_match.group())
        
        if "extra" in idedata:
          extra = idedata["extra"]
          
          #-- Kopieer flash_images met offsets uit idedata
          if "flash_images" in extra and extra["flash_images"]:
            log_message("Kopieer flash images met offsets uit idedata.json:\n")
            for image in extra["flash_images"]:
              src_path = image["path"]
              offset = image["offset"]
              filename = os.path.basename(src_path)
              dst_path = os.path.join(target_dir, filename)
              
              if copy_file(src_path, dst_path):
                flash_config.append({
                  "offset": offset,
                  "file": filename
                })
            log_message("")  # Extra line break
          
          #-- Kopieer firmware met offset uit idedata
          if "application_offset" in extra:
            app_offset = extra["application_offset"]
            firmware_src = os.path.join(build_dir, "firmware.bin")
            firmware_dst = os.path.join(target_dir, "firmware.bin")
            
            log_message(f"Kopieer firmware met offset {app_offset}:\n")
            if copy_file(firmware_src, firmware_dst):
              flash_config.append({
                "offset": app_offset,
                "file": "firmware.bin"
              })
            log_message("")  # Extra line break
      else:
        log_message("⚠️ Geen JSON gevonden in idedata output, gebruik fallback\n")
        use_esp32_fallback(build_dir, flash_config)
    except Exception as e:
      log_message(f"⚠️ Fout bij genereren idedata.json: {e}\n")
      log_message("Gebruik fallback offsets...\n")
      use_esp32_fallback(build_dir, flash_config)
    
  elif is_esp8266:
    log_message("ESP8266 gedetecteerd - kopieer firmware...\n")
    
    #-- Voor ESP8266: firmware begint op 0x0
    firmware_src = os.path.join(build_dir, "firmware.bin")
    if os.path.exists(firmware_src):
      firmware_dst = os.path.join(target_dir, "firmware.bin")
      if copy_file(firmware_src, firmware_dst):
        flash_config.append({
          "offset": "0x0",
          "file": "firmware.bin"
        })
      log_message("")  # Extra line break
    else:
      log_message("⚠️ firmware.bin niet gevonden in buildmap!\n")
  
  #-- Zoek naar filesystem image (littlefs.bin of spiffs.bin)
  log_message("Zoek naar filesystem image...\n")
  fs_images = ["littlefs.bin", "spiffs.bin"]
  for fs_img in fs_images:
    fs_src = os.path.join(build_dir, fs_img)
    if os.path.exists(fs_src):
      fs_dst = os.path.join(target_dir, fs_img)
      log_message(f"Kopieer filesystem image: **{fs_img}**\n")
      if copy_file(fs_src, fs_dst):
        log_message("")  # Extra line break
        #-- Probeer filesystem offset te vinden uit partitions
        fs_offset = get_filesystem_offset(build_dir, target_dir)
        if fs_offset:
          flash_config.append({
            "offset": fs_offset,
            "file": fs_img
          })
        else:
          log_message(f"ℹ️ Filesystem offset niet gevonden, {fs_img} toegevoegd zonder offset\n")
  
  #-- Sorteer flash_config op offset
  if flash_config:
    flash_config.sort(key=lambda x: int(x["offset"], 16))
    
    #-- Schrijf flash.json
    flash_json_path = os.path.join(target_dir, "flash.json")
    try:
      with open(flash_json_path, 'w') as f:
        json.dump({
          "board": board,
          "version": version,
          "flash_files": flash_config
        }, f, indent=2)
      log_message(f"✓ flash.json aangemaakt: {os.path.relpath(flash_json_path, env.subst('$PROJECT_DIR'))}\n")
      log_message("")  # Extra line break
      
      #-- Toon flash configuratie
      log_message("### Flash Configuratie:\n")
      for item in flash_config:
        log_message(f"- `{item['offset']}` → **{item['file']}**\n")
      log_message("")  # Extra line break
      
      #-- Toon partitions.csv inhoud als deze bestaat
      partitions_csv = os.path.join(target_dir, "partitions.csv")
      if os.path.exists(partitions_csv):
        log_message("### Partitions.csv Inhoud:\n")
        log_message("```")
        try:
          with open(partitions_csv, 'r') as f:
            log_message(f.read().strip())
        except Exception as e:
          log_message(f"Fout bij lezen partitions.csv: {e}")
        log_message("```")
    except Exception as e:
      log_message(f"⚠️ Fout bij schrijven flash.json: {e}\n")
  else:
    log_message("⚠️ Geen flash configuratie beschikbaar voor flash.json\n")

def use_esp32_fallback(build_dir, flash_config):
  """
  Fallback voor ESP32 wanneer idedata.json niet beschikbaar is.
  Probeert offsets te lezen uit partitions.csv, anders hardcoded offsets.
  """
  log_message("  Gebruik fallback: probeer offsets uit partitions.csv te lezen...")
  
  #-- Probeer offsets te lezen uit partitions.csv
  offsets = get_offsets_from_partitions_csv()
  
  #-- Standaard hardcoded offsets als fallback
  if not offsets:
    log_message("  ⚠️  Kan partitions.csv niet lezen, gebruik hardcoded offsets")
    offsets = {
      "bootloader": "0x1000",
      "partitions": "0x8000",
      "boot_app0": "0xe000",
      "app0": "0x10000"
    }
  else:
    log_message(f"  ✓ Offsets gelezen uit partitions.csv")
  
  #-- 1. Bootloader
  bootloader_src = os.path.join(build_dir, "bootloader.bin")
  if os.path.exists(bootloader_src):
    bootloader_dst = os.path.join(target_dir, "bootloader.bin")
    if copy_file(bootloader_src, bootloader_dst):
      flash_config.append({
        "offset": offsets.get("bootloader", "0x1000"),
        "file": "bootloader.bin"
      })
  
  #-- 2. Partitions
  partitions_src = os.path.join(build_dir, "partitions.bin")
  if os.path.exists(partitions_src):
    partitions_dst = os.path.join(target_dir, "partitions.bin")
    if copy_file(partitions_src, partitions_dst):
      flash_config.append({
        "offset": offsets.get("partitions", "0x8000"),
        "file": "partitions.bin"
      })
  
  #-- 3. boot_app0 is al gekopieerd in pre_build
  boot_app0_dst = os.path.join(target_dir, "boot_app0.bin")
  if os.path.exists(boot_app0_dst):
    flash_config.append({
      "offset": offsets.get("boot_app0", "0xe000"),
      "file": "boot_app0.bin"
    })
  
  #-- 4. Firmware (app0 partition)
  firmware_src = os.path.join(build_dir, "firmware.bin")
  if os.path.exists(firmware_src):
    firmware_dst = os.path.join(target_dir, "firmware.bin")
    if copy_file(firmware_src, firmware_dst):
      flash_config.append({
        "offset": offsets.get("app0", "0x10000"),
        "file": "firmware.bin"
      })

def get_offsets_from_partitions_csv():
  """
  Lees flash offsets uit partitions.csv voor bootloader, partitions, boot_app0 en app0.
  Retourneert dict met offsets of None bij falen.
  """
  partitions_csv = os.path.join(target_dir, "partitions.csv")
  if not os.path.exists(partitions_csv):
    return None
  
  offsets = {}
  
  try:
    with open(partitions_csv, 'r') as f:
      for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
          continue
        
        parts = [p.strip() for p in line.split(',')]
        if len(parts) >= 4:
          #-- Format: Name, Type, SubType, Offset, Size, Flags
          name = parts[0].lower()
          offset = parts[3].strip()
          
          #-- Zorg dat offset in hex format is
          if not offset.startswith('0x'):
            try:
              offset = hex(int(offset, 16))
            except:
              try:
                offset = hex(int(offset))
              except:
                continue
          
          #-- Zoek naar specifieke partities
          if 'factory' in name or 'app0' in name or name == 'app':
            offsets['app0'] = offset
          elif 'otadata' in name:
            offsets['boot_app0'] = offset
    
    #-- Als we een app0 offset gevonden hebben, kunnen we de andere afleiden
    if 'app0' in offsets:
      #-- Standaard ESP32 layout: bootloader @ 0x1000, partitions @ 0x8000
      #-- boot_app0 kan variëren, maar is meestal @ 0xe000
      if 'boot_app0' not in offsets:
        offsets['boot_app0'] = "0xe000"
      offsets['bootloader'] = "0x1000"
      offsets['partitions'] = "0x8000"
      return offsets
    
  except Exception as e:
    log_message(f"  ⚠️  Fout bij lezen partitions.csv voor offsets: {e}")
  
  return None

def get_filesystem_offset(build_dir, target_dir):
  """Probeer filesystem offset te vinden uit partitions.bin of partitions.csv."""
  
  #-- Probeer eerst uit partitions.csv
  partitions_csv = os.path.join(target_dir, "partitions.csv")
  if os.path.exists(partitions_csv):
    try:
      with open(partitions_csv, 'r') as f:
        for line in f:
          line = line.strip()
          if not line or line.startswith('#'):
            continue
          parts = [p.strip() for p in line.split(',')]
          if len(parts) >= 4:
            # Format: Name, Type, SubType, Offset, Size, Flags
            name = parts[0].lower()
            subtype = parts[2].lower() if len(parts) > 2 else ""
            
            # Check zowel name als subtype voor filesystem types
            if any(fs_type in name or fs_type in subtype 
                   for fs_type in ['spiffs', 'littlefs', 'fatfs', 'ffat']):
              offset = parts[3].strip()
              
              # Zorg dat offset in hex format is
              if not offset.startswith('0x'):
                try:
                  offset = hex(int(offset, 16))
                except:
                  try:
                    offset = hex(int(offset))
                  except:
                    log_message(f"  ⚠️  Kan offset niet parsen: {offset}")
                    continue
              
              log_message(f"  ℹ️  Filesystem offset gevonden in partitions.csv: {offset}")
              return offset
    except Exception as e:
      log_message(f"  ⚠️  Fout bij lezen partitions.csv: {e}")
  
  #-- Standaard offsets als fallback
  platform_name = platform.name.lower()
  if "8266" in platform_name:
    log_message(f"  ℹ️  ESP8266: gebruik standaard filesystem offset 0x300000")
    return "0x300000"
  elif "32" in platform_name:
    log_message(f"  ℹ️  ESP32: gebruik standaard filesystem offset 0x290000")
    return "0x290000"
  
  return None

# ---------------- POST-BUILDFS ----------------
def post_buildfs_action(source, target, env):
  log_message(f"\n### [POST-BUILDFS]\n")
  
  build_dir = env.subst("$BUILD_DIR")
  
  #-- Zoek naar filesystem image (littlefs.bin of spiffs.bin)
  log_message("Zoek naar filesystem image...\n")
  fs_images = ["littlefs.bin", "spiffs.bin"]
  for fs_img in fs_images:
    fs_src = os.path.join(build_dir, fs_img)
    if os.path.exists(fs_src):
      fs_dst = os.path.join(target_dir, fs_img)
      log_message(f"Kopieer filesystem image: **{fs_img}**\n")
      copy_file(fs_src, fs_dst)
      log_message("")  # Extra line break
      
      #-- Update flash.json als deze bestaat
      flash_json_path = os.path.join(target_dir, "flash.json")
      if os.path.exists(flash_json_path):
        try:
          with open(flash_json_path, 'r') as f:
            flash_data = json.load(f)
          
          #-- Controleer of filesystem image al in lijst staat
          fs_exists = any(item["file"] == fs_img for item in flash_data.get("flash_files", []))
          
          if not fs_exists:
            #-- Voeg filesystem image toe
            fs_offset = get_filesystem_offset(build_dir, target_dir)
            if fs_offset:
              flash_data["flash_files"].append({
                "offset": fs_offset,
                "file": fs_img
              })
              
              #-- Sorteer op offset
              flash_data["flash_files"].sort(key=lambda x: int(x["offset"], 16))
              
              #-- Schrijf terug
              with open(flash_json_path, 'w') as f:
                json.dump(flash_data, f, indent=2)
              log_message(f"✓ flash.json bijgewerkt met {fs_img}\n")
        except Exception as e:
          log_message(f"⚠️  Fout bij bijwerken flash.json: {e}\n")
  

# ---------------- ACTIES KOPPELEN ----------------
# Voor cached builds: check altijd of target bestanden up-to-date zijn
def check_and_sync(source, target, env):
  """Check of output bestanden up-to-date zijn, zo niet, sync."""
  build_dir = env.subst("$BUILD_DIR")
  
  # Check of firmware.bin bestaat en gekopieerd moet worden
  firmware_src = os.path.join(build_dir, "firmware.bin")
  firmware_dst = os.path.join(target_dir, "firmware.bin")
  
  needs_post_build = False
  
  if os.path.exists(firmware_src):
    # Als target niet bestaat of ouder is dan source, run post_build_action
    if not os.path.exists(firmware_dst) or \
       os.path.getmtime(firmware_src) > os.path.getmtime(firmware_dst):
      needs_post_build = True
  
  # Check filesystem image - dit moet ook gecheckt worden bij buildprog
  # voor het geval buildfs al eerder is uitgevoerd
  for fs_img in ["littlefs.bin", "spiffs.bin"]:
    fs_src = os.path.join(build_dir, fs_img)
    fs_dst = os.path.join(target_dir, fs_img)
    
    if os.path.exists(fs_src):
      if not os.path.exists(fs_dst):
        needs_post_build = True
        break
  
  if needs_post_build:
    log_message("\n>>> Auto-sync: Detected changes, updating project files...")
    post_build_action(source, target, env)

env.AddPreAction("buildprog", pre_build_action)
env.AddPostAction("buildprog", post_build_action)
env.AddPostAction("$BUILD_DIR/firmware.elf", check_and_sync)
env.AddPostAction("buildfs", post_buildfs_action)

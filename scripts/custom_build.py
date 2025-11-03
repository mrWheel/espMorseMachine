Import("env")
import os
import shutil
import glob
import json

# ---------------- HULPFUNCTIES ----------------
def copy_file(src, dst):
  """Veilig bestand kopiëren met logging."""
  try:
    if not os.path.exists(src):
      print(f"  ⚠️  Bestand niet gevonden: {src}")
      return False
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy(src, dst)
    print(f"  ✓ {os.path.basename(src)} → {os.path.relpath(dst, env.subst('$PROJECT_DIR'))}")
    return True
  except Exception as e:
    print(f"!!! Fout bij kopiëren {src}: {e}")
    return False

def read_idedata(build_dir):
  """Lees idedata.json en retourneer de data."""
  idedata_path = os.path.join(build_dir, "idedata.json")
  if not os.path.exists(idedata_path):
    print(f"  ⚠️  idedata.json niet gevonden: {idedata_path}")
    return None
  
  try:
    with open(idedata_path, 'r') as f:
      data = json.load(f)
    return data
  except Exception as e:
    print(f"  ⚠️  Fout bij lezen idedata.json: {e}")
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
    print(f"Project name gedetecteerd uit directory structuur: {project_name}")

# Haal versie uit environment naam (bijv. "esp32dev-v1_1_1" → "v1.1.1")
version_parts = active_env.split('-v')
if len(version_parts) > 1:
  version = f"v{version_parts[1].replace('_', '.')}"
else:
  version = "v0"

board = env["BOARD"]

# Doelmap aanmaken
target_dir = os.path.join("projects", project_name, board, version)
os.makedirs(target_dir, exist_ok=True)

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
else:
  print(f"!!! Environment '{active_env}' gebruikt geen Arduino framework — acties overgeslagen.")

if not framework_path:
  print(f"⚠️  Geen frameworkpad gevonden voor {active_env}. Bootloader-bestanden en default.csv niet beschikbaar.")
else:
  print(f"Framework-pad gedetecteerd: {framework_path}")

# ---------------- PRE-BUILD ----------------
def pre_build_action(source, target, env):
  print(f"\n>>> [PRE-BUILD] Voor {project_name}/{board}/{version}")

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
        print(f"  Aangepaste partitions file gevonden: {custom_partitions}")
        copy_file(custom_path, partitions_dest)
      else:
        print(f"  ⚠️  board_build.partitions verwijst naar niet-bestaand bestand: {custom_partitions}")
        # Fallback naar default.csv
        if framework_path:
          default_csv_path = os.path.join(framework_path, "tools", "partitions", "default.csv")
          if os.path.exists(default_csv_path):
            print("  Gebruik fallback: default.csv uit framework")
            copy_file(default_csv_path, partitions_dest)
    else:
      # Geen custom partitions file → gebruik default.csv uit framework
      if framework_path:
        default_csv_path = os.path.join(framework_path, "tools", "partitions", "default.csv")
        if os.path.exists(default_csv_path):
          print("  Geen board_build.partitions — gebruik default.csv uit framework")
          copy_file(default_csv_path, partitions_dest)
        else:
          print("  ⚠️  Geen default.csv gevonden in framework.")
      else:
        print("  ⚠️  Frameworkpad onbekend, kan geen partitions.csv genereren.")

    # 2️⃣ boot_app0.bin uit framework kopiëren
    if framework_path:
      print("  boot_app0.bin uit framework kopiëren...")
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
        print("  ⚠️  boot_app0.bin niet gevonden in framework.")
    else:
      print("  ⚠️  Geen frameworkpad beschikbaar, boot_app0.bin overgeslagen.")

  elif is_esp8266:
    print("  ESP8266 detecteerd — geen partitions.csv of boot_app0.bin nodig")

  print(">>> [PRE-BUILD] Klaar.\n")

# ---------------- POST-BUILD ----------------
def post_build_action(source, target, env):
  print(f"\n>>> [POST-BUILD] Voor {project_name}/{board}/{version}")

  build_dir = env.subst("$BUILD_DIR")
  if not os.path.exists(build_dir):
    print("!!! Build-map bestaat niet — build is mogelijk mislukt.")
    return

  platform_name = platform.name.lower()
  is_esp32 = "32" in platform_name
  is_esp8266 = "8266" in platform_name
  
  flash_config = []
  
  if is_esp32:
    print("  ESP32 gedetecteerd - genereer idedata.json...")
    
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
            print("  Kopieer flash images met offsets uit idedata.json:")
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
          
          #-- Kopieer firmware met offset uit idedata
          if "application_offset" in extra:
            app_offset = extra["application_offset"]
            firmware_src = os.path.join(build_dir, "firmware.bin")
            firmware_dst = os.path.join(target_dir, "firmware.bin")
            
            print(f"  Kopieer firmware met offset {app_offset}:")
            if copy_file(firmware_src, firmware_dst):
              flash_config.append({
                "offset": app_offset,
                "file": "firmware.bin"
              })
      else:
        print("  ⚠️  Geen JSON gevonden in idedata output, gebruik fallback")
        #-- Fallback: gebruik hardcoded offsets
        use_esp32_fallback(build_dir, flash_config)
    except Exception as e:
      print(f"  ⚠️  Fout bij genereren idedata.json: {e}")
      print("  Gebruik fallback offsets...")
      use_esp32_fallback(build_dir, flash_config)
    
  elif is_esp8266:
    print("  ESP8266 gedetecteerd - kopieer firmware...")
    
    #-- Voor ESP8266: firmware begint op 0x0
    firmware_src = os.path.join(build_dir, "firmware.bin")
    if os.path.exists(firmware_src):
      firmware_dst = os.path.join(target_dir, "firmware.bin")
      if copy_file(firmware_src, firmware_dst):
        flash_config.append({
          "offset": "0x0",
          "file": "firmware.bin"
        })
    else:
      print("  ⚠️  firmware.bin niet gevonden in buildmap!")
  
  #-- Zoek naar filesystem image (littlefs.bin of spiffs.bin)
  print("  Zoek naar filesystem image...")
  fs_images = ["littlefs.bin", "spiffs.bin"]
  for fs_img in fs_images:
    fs_src = os.path.join(build_dir, fs_img)
    if os.path.exists(fs_src):
      fs_dst = os.path.join(target_dir, fs_img)
      print(f"  Kopieer filesystem image: {fs_img}")
      if copy_file(fs_src, fs_dst):
        #-- Probeer filesystem offset te vinden uit partitions
        fs_offset = get_filesystem_offset(build_dir, target_dir)
        if fs_offset:
          flash_config.append({
            "offset": fs_offset,
            "file": fs_img
          })
        else:
          print(f"  ℹ️  Filesystem offset niet gevonden, {fs_img} toegevoegd zonder offset")
  
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
      print(f"  ✓ flash.json aangemaakt: {os.path.relpath(flash_json_path, env.subst('$PROJECT_DIR'))}")
      
      #-- Toon flash configuratie
      print("\n  Flash configuratie:")
      for item in flash_config:
        print(f"    {item['offset']} → {item['file']}")
    except Exception as e:
      print(f"  ⚠️  Fout bij schrijven flash.json: {e}")
  else:
    print("  ⚠️  Geen flash configuratie beschikbaar voor flash.json")

  print(">>> [POST-BUILD] Klaar.\n")

def use_esp32_fallback(build_dir, flash_config):
  """Fallback voor ESP32 wanneer idedata.json niet beschikbaar is."""
  print("  Gebruik hardcoded ESP32 offsets...")
  
  #-- 1. Bootloader (0x1000)
  bootloader_src = os.path.join(build_dir, "bootloader.bin")
  if os.path.exists(bootloader_src):
    bootloader_dst = os.path.join(target_dir, "bootloader.bin")
    if copy_file(bootloader_src, bootloader_dst):
      flash_config.append({
        "offset": "0x1000",
        "file": "bootloader.bin"
      })
  
  #-- 2. Partitions (0x8000)
  partitions_src = os.path.join(build_dir, "partitions.bin")
  if os.path.exists(partitions_src):
    partitions_dst = os.path.join(target_dir, "partitions.bin")
    if copy_file(partitions_src, partitions_dst):
      flash_config.append({
        "offset": "0x8000",
        "file": "partitions.bin"
      })
  
  #-- 3. boot_app0 is al gekopieerd in pre_build
  boot_app0_dst = os.path.join(target_dir, "boot_app0.bin")
  if os.path.exists(boot_app0_dst):
    flash_config.append({
      "offset": "0xe000",
      "file": "boot_app0.bin"
    })
  
  #-- 4. Firmware (0x10000)
  firmware_src = os.path.join(build_dir, "firmware.bin")
  if os.path.exists(firmware_src):
    firmware_dst = os.path.join(target_dir, "firmware.bin")
    if copy_file(firmware_src, firmware_dst):
      flash_config.append({
        "offset": "0x10000",
        "file": "firmware.bin"
      })

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
                    print(f"  ⚠️  Kan offset niet parsen: {offset}")
                    continue
              
              print(f"  ℹ️  Filesystem offset gevonden in partitions.csv: {offset}")
              return offset
    except Exception as e:
      print(f"  ⚠️  Fout bij lezen partitions.csv: {e}")
  
  #-- Standaard offsets als fallback
  platform_name = platform.name.lower()
  if "8266" in platform_name:
    print(f"  ℹ️  ESP8266: gebruik standaard filesystem offset 0x300000")
    return "0x300000"
  elif "32" in platform_name:
    print(f"  ℹ️  ESP32: gebruik standaard filesystem offset 0x290000")
    return "0x290000"
  
  return None

# ---------------- POST-BUILDFS ----------------
def post_buildfs_action(source, target, env):
  print(f"\n>>> [POST-BUILDFS] Voor {project_name}/{board}/{version}")
  
  build_dir = env.subst("$BUILD_DIR")
  
  #-- Zoek naar filesystem image (littlefs.bin of spiffs.bin)
  print("  Zoek naar filesystem image...")
  fs_images = ["littlefs.bin", "spiffs.bin"]
  for fs_img in fs_images:
    fs_src = os.path.join(build_dir, fs_img)
    if os.path.exists(fs_src):
      fs_dst = os.path.join(target_dir, fs_img)
      print(f"  Kopieer filesystem image: {fs_img}")
      copy_file(fs_src, fs_dst)
      
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
              print(f"  ✓ flash.json bijgewerkt met {fs_img}")
        except Exception as e:
          print(f"  ⚠️  Fout bij bijwerken flash.json: {e}")
  
  print(">>> [POST-BUILDFS] Klaar.\n")

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
    print("\n>>> Auto-sync: Detected changes, updating project files...")
    post_build_action(source, target, env)

env.AddPreAction("buildprog", pre_build_action)
env.AddPostAction("buildprog", post_build_action)
env.AddPostAction("$BUILD_DIR/firmware.elf", check_and_sync)
env.AddPostAction("buildfs", post_buildfs_action)

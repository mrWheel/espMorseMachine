Import("env")
import os
import shutil
import glob

# ---------------- HULPFUNCTIES ----------------
def copy_file(src, dst):
    """Veilig bestand kopiëren met logging."""
    try:
        if not os.path.exists(src):
            print(f"  ⚠️  Bestand niet gevonden: {src}")
            return
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(src, dst)
        print(f"  - {os.path.basename(src)} → {os.path.basename(dst)}")
    except Exception as e:
        print(f"!!! Fout bij kopiëren {src}: {e}")

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
            custom_partitions = project_config.get(f"env:{active_env}", "board_build.partitions", fallback=None)
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

    bin_files = glob.glob(os.path.join(build_dir, "*.bin"))
    if not bin_files:
        print("  ⚠️  Geen .bin bestanden gevonden in buildmap!")
        return

    print("  Kopieer build .bin bestanden...")
    for bin_file in bin_files:
        dst = os.path.join(target_dir, os.path.basename(bin_file))
        copy_file(bin_file, dst)

    print(">>> [POST-BUILD] Klaar.\n")

# ---------------- ACTIES KOPPELEN ----------------
env.AddPreAction("buildprog", pre_build_action)
env.AddPostAction("buildprog", post_build_action)

import os
import sys
import json

# Automatically generates .nif.json files by creating new variants from a base set of files, applying new names and affixes,
# replacing textures, and renaming NiTriShape nodes according to predefined rules
# 
# Usage:
# 1. Convert your NIF files to JSON with Sniff.exe from Zilav (https://www.nexusmods.com/newvegas/mods/67829)
# 2. Place this script to folder with your .NIF.JSON files 
# 3. Configure CONFIG section (also 'List of suffixes/affixes for .NIF name generation' + 'List of new textures for the first material' for more detailed setup)
# 4. Run script
# 5. Convert all .NIF.JSON files back to NIF with Sniff.exe

# Configuration settings
CONFIG = {
    "directory": ".",
    "base_name": "Snow01_BM",                            # Base .NIF file name
    "base_NTS_name": "Snow",                             # Base NiTriShape name of the first material
    "base_M1_affix": "_S2",                              # Base .NIF file affix of the first material
    "base_M1_texture": "textures\\\\tx_bm_Snow_02.dds",  # Base texture of the first material
    
    "log_file": "_TES3_autoretex_BM_snow_SM_log.txt"
}

# List of suffixes/affixes for .NIF name generation
suffixes = ["", "_m", "a", "a_m", "b", "b_m"]            # Base .NIF file suffix variations

new_M1_affixes = [                                       # New .NIF file affix variations
    "_S1", "_S2", "_S3", "_S4", "_S5",                   # for snow
    "_SI1",                                              # for snow_ice
    "_SR1"                                               # for snow_rock
]

# List of new textures for the first material
# The number of textures must be equal to the number of 'new_M1_affixes'
# Textures must be listed in the same order as 'new_M1_affixes'
def generate_textures():
    snow_textures = [f"textures\\\\tx_bm_snow_{i:02d}.dds" for i in range(1, 6)]
    snow_ice_textures = ["textures\\\\tx_bm_snow_ice_01.dds"]
    snow_rock_textures = ["textures\\\\tx_bm_snow_rock_01.dds"]

    # Combining textures into one list
    return (
        snow_textures +
        snow_ice_textures +
        snow_rock_textures
    )

# Function to log messages to log file and console
def log_message(message, is_input=False, log_to_file=True):
    log_file = CONFIG.get("log_file", "")

    if log_to_file and log_file:
        try:
            with open(log_file, "a", encoding="utf-8") as log:
                log.write(message + "\n")
        except OSError as e:
            print(f"ERROR - Failed to write to log file: {e}")

    if not is_input:
        print(message)
    else:
        return input(message)

# Generate a mapping of existing affixes to new affixes
def generate_affix_mapping(suffixes, new_M1_affixes, base_M1_affix):
    return {
        f"{base_M1_affix}{suffix}": [f"{new}{suffix}" for new in new_M1_affixes]
        for suffix in suffixes
    }

# Function to return a list of .NIF.JSON files from the current folder
def get_json_files(directory):
    return [
        f for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f)) and f.lower().endswith(".nif.json")
    ]

# Function to split filename into base_name and _affix
def get_base_name_and_affix(filename, base_name):
    if filename.startswith(base_name) and filename.endswith(".nif.json"):
        return base_name, filename[len(base_name):-len(".nif.json")]
    return None, None

# Function to check if there is a NiTriShape block with the name base_NTS_name
def has_base_nitrishape(content, base_NTS_name):
    for key, value in content.items():
        if "NiTriShape" in key and isinstance(value, dict) and value.get("Name") == base_NTS_name:
            return True
    return False

# Function to check if there is a base_M1_texture in NiSourceTexture
def has_base_texture(content, base_M1_texture):
    normalized_base_texture = os.path.normpath(base_M1_texture)
    for key, value in content.items():
        if "NiSourceTexture" in key and isinstance(value, dict):
            texture_path = os.path.normpath(value.get("File Name", ""))
            if texture_path == normalized_base_texture:
                return True
    return False

# Function to count NiTriShapes inside '0 NiNode'
def count_nitrishapes(children):
    return sum(1 for child in children if "NiTriShape" in child)

# Function to process files in directory
def process_files(config):
    directory = config["directory"]
    base_name = config["base_name"]
    base_NTS_name = config["base_NTS_name"] 
    base_M1_texture = config["base_M1_texture"]
    
    new_base_M1_texture = generate_textures()
    M1_affix_mapping = generate_affix_mapping(suffixes, new_M1_affixes, CONFIG["base_M1_affix"])
    
    files = get_json_files(directory)
    if not files:
        log_message("ERROR - No .nif.json files found in current folder. Conversion canceled.")
        log_message("\nThe ending of the words is ALMSIVI\n")
        input("Press Enter to continue...")
        return

    # Check for files with the required base_name and base_M1_affix
    valid_files = []
    invalid_base_name_files = []
    invalid_affix_files = []

    for filename in files:
        base, current_affix = get_base_name_and_affix(filename, base_name)
        if not base:
            invalid_base_name_files.append(filename)
            continue
        if current_affix not in M1_affix_mapping:
            invalid_affix_files.append(filename)
            continue
        valid_files.append(filename)

    if invalid_base_name_files:
        log_message("ERROR - Following files do not match the required base_name:")
        for file in invalid_base_name_files:
            log_message(f"  - {file}")

    if invalid_affix_files:
        log_message("ERROR - Following files do not match the required base_M1_affix:")
        for file in invalid_affix_files:
            log_message(f"  - {file}")

    if not valid_files:
        log_message("\nERROR - No valid files found. Conversion canceled.")
        log_message("\nThe ending of the words is ALMSIVI\n")
        input("Press Enter to continue...")
        return

    # Processing valid files
    for filename in valid_files:
        base, current_affix = get_base_name_and_affix(filename, base_name)
        if not base or current_affix not in M1_affix_mapping:
            continue
        
        original_path = os.path.join(directory, filename)

        try:
            with open(original_path, "r", encoding="utf-8") as f:
                content = json.load(f)
        except (OSError, IOError) as e:
            log_message(f"ERROR - Can't read {filename}: {e}. Skipping file.")
            continue

        if not has_base_nitrishape(content, base_NTS_name):
            log_message(f"WARNING - NiTriShape name '{base_NTS_name}' not found in {filename}. Skipping file.")
            continue

        if not has_base_texture(content, base_M1_texture):
            log_message(f"WARNING - Texture '{base_M1_texture}' not found in {filename}. Skipping file.")
            continue

        # Get the list of children from the 0 NiNode
        ni_node = content.get("0 NiNode", {})
        children = ni_node.get("Children", [])
        
        # Count the number of NiTriShape blocks
        nitrishape_count = count_nitrishapes(children)
        
        if nitrishape_count == 0:
            log_message(f"WARNING - No NiTriShape blocks found in {filename}. Skipping file.")
            continue

        for i, new_affix in enumerate(M1_affix_mapping[current_affix]):
            new_filename = f"{base_name}{new_affix}.nif.json"
            new_path = os.path.join(directory, new_filename)
            log_message(f"File created --------> {new_filename}")

            # Create a deep copy of the content to avoid modifying the original
            updated_content = json.loads(json.dumps(content))

            # Update the NiNode children and NiTriShape names
            for j, child in enumerate(updated_content["0 NiNode"]["Children"]):
                if "NiTriShape" in child:
                    old_name = child.split('"')[1]
                    new_name = f"Tri {base_name}{new_affix}:{j + 1}"
                    updated_content["0 NiNode"]["Children"][j] = child.replace(old_name, new_name)
                    nitrishape_key = child.split()[0]
                    if nitrishape_key in updated_content:
                        updated_content[nitrishape_key]["Name"] = new_name
                    log_message(f"Updating Children ---> {old_name} | {new_name}")

            # Update the Name field in NiTriShape blocks
            nitrishape_counter = 1
            for key, value in updated_content.items():
                if "NiTriShape" in key and isinstance(value, dict):
                    if value.get("Name") == base_NTS_name:
                        new_name = f"Tri {base_name}{new_affix}:{nitrishape_counter}"
                        updated_content[key]["Name"] = new_name
                        log_message(f"Renaming NiTriShape -> {base_NTS_name} | {new_name}")
                        nitrishape_counter += 1

            # Replace the base texture
            new_texture = new_base_M1_texture[i % len(new_base_M1_texture)]
            normalized_base_texture = os.path.normpath(base_M1_texture)
            normalized_new_texture = os.path.normpath(new_texture)

            for key, value in updated_content.items():
                if "NiSourceTexture" in key and isinstance(value, dict):
                    if value.get("File Name") == normalized_base_texture:
                        updated_content[key]["File Name"] = normalized_new_texture
                        log_message(f"Replacing texture ---> {normalized_base_texture} | {normalized_new_texture}")

            try:
                with open(new_path, "w", encoding="utf-8") as f:
                    json.dump(updated_content, f, indent=4)
            except (OSError, IOError) as e:
                log_message(f"ERROR - Can't write {new_filename}: {e}")

def main():
    with open(CONFIG["log_file"], "w", encoding="utf-8") as log:
        log.write("")

    print("\nTES3 Automatic Retexturing Script\nBloodmoon Snow | Single Material\n\nby Siberian Crab\nv1.0.3\n")
    
    try:
        process_files(CONFIG)
    except Exception as e:
        log_message(f"ERROR - Unexpected error: {e}")
    
    log_message("\nThe ending of the words is ALMSIVI\n")
    input("Press Enter to continue...")

if __name__ == "__main__":
    main()
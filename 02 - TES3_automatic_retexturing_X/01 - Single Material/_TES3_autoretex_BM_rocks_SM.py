import os
import sys

# Automatically generates .nif.json files by creating new variants from a base set of files, applying new names and affixes,
# replacing textures, and renaming NiTriShape nodes according to predefined rules
# 
# Usage:
# 1. Convert your NIF files to JSON with Sniff.exe from Zilav (https://www.nexusmods.com/newvegas/mods/67829)
# 2. Place this script to folder with your .NIF.JSON files 
# 3. Configure CONFIG section + List of suffixes/affixes for .NIF name generation + List of new textures for the first material
# 4. Run script
# 5. Convert all .NIF.JSON files back to NIF with Sniff.exe

# Configuration settings
CONFIG = {
    "directory": ".",                               	  # Current folder
    "base_name": "Rock27_BM",                       	  # Base .NIF file name
    "base_M1_affix": "_R2",                            	  # Base .NIF file affix of the first material
    "base_M1_texture": "textures\\\\tx_bm_rock_02.dds",   # Base texture of the first material
    
    "log_file": "_TES3_autoretex_BM_rocks_SM_log.txt"
}

# List of suffixes/affixes for .NIF name generation
suffixes = ["", "_m", "a", "a_m", "b", "b_m"]             # Base .NIF file suffix variations 
new_M1_affixes = [                                        # New .NIF file affix variations
    "_I1", "_I2", "_I3", "_I4", "_I5", "_I6",             # for ice
    "_R1", "_R2", "_R3",                                  # for rock
    "_RS1", "_RS2", "_RS3",                               # for rock_snow
    "_RSa1", "_RSa2",                                     # for rock_snow_a
    "_S1", "_S2", "_S3", "_S4", "_S5",                    # for snow
    "_SI1",                                               # for snow_ice
    "_SR1"                                                # for snow_rock
]

# List of new textures for the first material
# The number of textures must be equal to the number of 'new_M1_affixes'
# Textures must be listed in the same order as 'new_M1_affixes'
def generate_textures():
    ice_textures = [f"textures\\\\tx_bm_ice_{i:02d}.dds" for i in range(1, 7)]
    rock_textures = [f"textures\\\\tx_bm_rock_{i:02d}.dds" for i in range(1, 4)]
    rock_snow_textures = [f"textures\\\\tx_bm_rock_snow_{i:02d}.dds" for i in range(1, 4)]
    rock_snow_a_textures = [f"textures\\\\tx_bm_rock_snow_{i:02d}a.dds" for i in range(1, 3)]
    snow_textures = [f"textures\\\\tx_bm_snow_{i:02d}.dds" for i in range(1, 6)]
    snow_ice_textures = ["textures\\\\tx_bm_snow_ice_01.dds"]
    snow_rock_textures = ["textures\\\\tx_bm_snow_rock_01.dds"]

    # Combining textures into one list
    return (
        ice_textures +
        rock_textures +
        rock_snow_textures +
        rock_snow_a_textures +
        snow_textures +
        snow_ice_textures +
        snow_rock_textures
    )

# Function to log messages to log file and console
def log_message(message, is_input=False):
    with open(CONFIG["log_file"], "a", encoding="utf-8") as log:
        log.write(message + "\n")
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
        return base_name, filename[len(base_name):-9]  # Убираем .nif.json
    return None, None

# Function to process files in directory, copy them with new affixes, replace NiTriShape names and textures
def process_files(config):
    directory = config["directory"]
    base_name = config["base_name"]
    base_M1_texture = config["base_M1_texture"]
    
    new_base_M1_texture = generate_textures()
    M1_affix_mapping = generate_affix_mapping(suffixes, new_M1_affixes, CONFIG["base_M1_affix"])
    
    files = get_json_files(directory)
    if not files:
        log_message("ERROR - No .nif.json files found in current folder. Conversion canceled.")
        log_message("\nThe ending of the words is ALMSIVI\n")
        input("Press Enter to continue...")
        sys.exit(1)

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
        sys.exit(1)

    # Processing valid files
    for filename in valid_files:
        base, current_affix = get_base_name_and_affix(filename, base_name)
        if not base or current_affix not in M1_affix_mapping:
            continue
        
        original_path = os.path.join(directory, filename)

        try:
            with open(original_path, "r", encoding="utf-8") as f:
                content = f.read()
        except (OSError, IOError) as e:
            log_message(f"ERROR - Can't read {filename}: {e}. Skipping file.")
            continue
        
        if base_M1_texture not in content:
            log_message(f"WARNING - Texture {base_M1_texture} not found in {filename}. Skipping replacement.")
            continue

        for i, new_affix in enumerate(M1_affix_mapping[current_affix]):
            new_filename = f"{base_name}{new_affix}.nif.json"
            new_path = os.path.join(directory, new_filename)
            log_message(f"File created --------> {new_filename}")

            new_content = content.replace(f"{base_name}{current_affix}", f"{base_name}{new_affix}")
            log_message(f"Renaming NiTriShape -> {base_name}{current_affix} | {base_name}{new_affix}")
            
            new_texture = new_base_M1_texture[i % len(new_base_M1_texture)]
            new_content = new_content.replace(base_M1_texture, new_texture)
            log_message(f"Replacing texture ---> {base_M1_texture} | {new_texture}")

            try:
                with open(new_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
            except (OSError, IOError) as e:
                log_message(f"ERROR - Can't write {new_filename}: {e}")

def main():
    with open(CONFIG["log_file"], "w", encoding="utf-8") as log:
        log.write("")

    print("\nTES3 Automatic Retexturing Script\nBloodmoon Rocks | Single Material\n\nby Siberian Crab\nv1.0.0\n")
    
    try:
        process_files(CONFIG)
    except Exception as e:
        log_message(f"ERROR - Unexpected error: {e}")
    
    log_message("\nThe ending of the words is ALMSIVI\n")
    input("Press Enter to continue...")

if __name__ == "__main__":
    main()
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
    "base_name": "Ice{num_part}_BM",                     # Base .NIF file name
    "base_numbers": range(1, 9999),                      # Base .NIF file name numeration
    "base_NTS_name": "Ice",                              # Base NiTriShape name of the first material
    "base_M1_affix": "_I2",                              # Base .NIF file affix of the first material
    "base_M1_texture": "textures\\\\tx_bm_Ice_02.dds",   # Base texture of the first material
    
    "log_file": "_TES3_autoretex_BM_ice_SM.log"
}

# List of suffixes/affixes for .NIF name generation
suffixes = ["", "_m", "a", "a_m", "b", "b_m"]            # Base .NIF file suffix variations

new_M1_affixes = [                                       # New .NIF file affix variations
    "_I1", "_I2", "_I3", "_I4", "_I5", "_I6",            # for ice
]

# List of new textures for the first material
# The number of textures must be equal to the number of 'new_M1_affixes'
# Textures must be listed in the same order as 'new_M1_affixes'
def generate_textures():
    ice_textures = [f"textures\\\\tx_bm_ice_{i:02d}.dds" for i in range(1, 7)]

    # Combining textures into one list
    return (
        ice_textures
    )

# Function to log messages to log file and console
def log_message(message, log_to_file=True):
    print(message)

    if log_to_file and CONFIG["log_file"]:
        try:
            with open(CONFIG["log_file"], "a", encoding="utf-8") as log:
                log.write(message + "\n")
        except OSError as e:
            print(f"ERROR - Failed to write to log file: {e}")

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
    base_name_template = config["base_name"]
    base_numbers = config["base_numbers"]
    base_NTS_name = config["base_NTS_name"] 
    base_M1_texture = config["base_M1_texture"]

    new_base_M1_texture = generate_textures()
    M1_affix_mapping = generate_affix_mapping(suffixes, new_M1_affixes, CONFIG["base_M1_affix"])

    # Global check for any .nif.json files in the directory
    all_files = get_json_files(directory)
    if not all_files:
        log_message("No .nif.json files found in current folder. Conversion canceled.")
        log_message("\nThe ending of the words is ALMSIVI\n")
        input("Press Enter to continue...")
        return

    # Creating a set of unique base names (without affixes/suffixes)
    base_names = set()
    for filename in all_files:
        for number in base_numbers:
            num_part = f"{number:02d}" if number < 100 else (f"{number:03d}" if number < 1000 else f"{number:04d}")
            base_name = base_name_template.format(num_part=num_part)
            if filename.startswith(base_name):
                base_names.add(base_name)
                break

    # Sorting base names for sequential processing
    sorted_base_names = sorted(base_names)
    total_base_files = len(sorted_base_names)
    processed_base_files = 0
    files_created = 0
    files_skipped = 0

    log_message(f"Found {total_base_files} base files to process")

    for base_name in sorted_base_names:
        processed_base_files += 1
        log_message(f"\nProcessing base name: {base_name} (progress: {processed_base_files}/{total_base_files})")
        
        # Processing files matching the current base_name pattern
        files = [f for f in all_files if f.startswith(base_name) and f.endswith(".nif.json")]
        
        if not files:
            log_message(f"WARNING - No files found for {base_name}. Skipping.")
            continue

        valid_files = []
        invalid_affix_files = []

        for filename in files:
            _, current_affix = get_base_name_and_affix(filename, base_name)
            if current_affix not in M1_affix_mapping:
                invalid_affix_files.append(filename)
                continue
            valid_files.append(filename)

        if invalid_affix_files:
            log_message(f"WARNING - Following files do not match the required affixes for {base_name}:")
            for file in invalid_affix_files:
                log_message(f"  - {file}")

        if not valid_files:
            log_message(f"WARNING - No valid files found for {base_name}. Skipping.")
            continue

        # Processing valid files for current base_name
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
                files_skipped += 1
                continue

            if not has_base_nitrishape(content, base_NTS_name):
                log_message(f"WARNING - NiTriShape name '{base_NTS_name}' not found in {filename}. Skipping file.")
                files_skipped += 1
                continue

            if not has_base_texture(content, base_M1_texture):
                log_message(f"WARNING - Texture '{base_M1_texture}' not found in {filename}. Skipping file.")
                files_skipped += 1
                continue

            # Get the list of children from the 0 NiNode
            ni_node = content.get("0 NiNode", {})
            children = ni_node.get("Children", [])
            
            # Count the number of NiTriShape blocks
            nitrishape_count = count_nitrishapes(children)
            
            if nitrishape_count == 0:
                log_message(f"WARNING - No NiTriShape blocks found in {filename}. Skipping file.")
                files_skipped += 1
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
                    files_created += 1
                except (OSError, IOError) as e:
                    log_message(f"ERROR - Can't write {new_filename}: {e}")

    # Return the counters to the main function
    return processed_base_files, files_created, files_skipped

def main():
    try:
        with open(CONFIG["log_file"], "w", encoding="utf-8") as log:
            log.write("")
    except OSError as e:
        print(f"Failed to initialize log file: {e}")
        return

    print("\nTES3 Automatic Retexturing Script\nBloodmoon Ice  |  Single Material\n\nby Siberian Crab\nv1.0.4\n")
    
    try:
        processed_base_files, files_created, files_skipped = process_files(CONFIG)
    except Exception as e:
        log_message(f"ERROR - Unexpected error: {e}")
        processed_base_files, files_created, files_skipped = 0, 0, 0
    
    log_message(f"\nProcessing complete!")
    log_message(f"  - total files skipped: {files_skipped}")
    log_message(f"  - total files created: {files_created}")
    log_message("\nThe ending of the words is ALMSIVI\n")
    input("Press Enter to continue...")

if __name__ == "__main__":
    main()
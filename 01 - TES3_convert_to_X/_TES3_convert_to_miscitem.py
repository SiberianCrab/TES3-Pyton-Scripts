import os
import sys
import json

# Generates JSON fragments for MiscItem records from NIF files.
# Output format: comma-separated JSON objects for manual insertion into array.
# 
# Usage:
# 1. Convert your ESP or ESM file to JSON with tes3conv.exe from Greatness7 (https://github.com/Greatness7/tes3conv)
# 2. Place this script to folder with your NIF files
# 3. Configure CONFIG section
# 4. Run script
# 5. Copy contents of output_file into your JSON

# Configuration settings
CONFIG = {
    "s_flags": "",                     # PERSISTENT | BLOCKED
    "s_name": "",                      # Name for all records (max 31 characters)
    "s_script": "",
    "s_icon": "",                      # Path to icon inside 'Icons' folder (max 31 chars)
    "s_weight": 1.0,
    "s_value": 10,
    "prefix_id": "_RR_",               # Unique prefix for record IDs
    "prefix_mesh": "rr\\f\\",	       # Path to files inside 'Meshes' folder

    "max_length_id": 31,
    "max_length_name": 31,
    "max_length_mesh": 31,
    "max_length_icon": 31,

    "output_file": "_TES3_convert_to_miscitem_out.txt",
    "log_file": "_TES3_convert_to_miscitem.log"
}

# Function to return a list of NIF files from the current folder
def get_nif_files(ignored_files):
    return [
        f for f in os.listdir('.')
        if os.path.isfile(f) and f.lower().endswith(".nif") and f not in ignored_files
    ]

# Function to construct and validate record ID and Mesh Path
def validate_length(nif_name, config):
    full_id = f"{config['prefix_id']}{nif_name}"
    full_mesh = f"{config['prefix_mesh']}{nif_name}.nif"

    len_id = len(full_id)
    len_mesh = len(full_mesh)

    error_id = f"{nif_name} (current {len_id} chars)" if len_id > config['max_length_id'] else None
    error_mesh = f"{nif_name} (current {len_mesh} chars)" if len_mesh > config['max_length_mesh'] else None

    return full_id, full_mesh, error_id, error_mesh

# Function to validate user settings
def validate_settings(config):
    if len(config['s_name']) > config['max_length_name']:
        print(f"\nERROR - defined 's_name' is too long: max {config['max_length_name']} chars, current {len(config['s_name'])} chars")
        return False
    if len(config['s_icon']) > config['max_length_icon']:
        print(f"\nERROR - defined 's_icon' is too long: max {config['max_length_icon']} chars, current {len(config['s_icon'])} chars")
        return False
    return True

# Function to generate a dictionary corresponding to one JSON record
def generate_entry(full_id, full_mesh, config):
    return {
        "type": "MiscItem",
        "flags": config["s_flags"],
        "id": full_id,
        "name": config["s_name"],
        "script": config["s_script"],
        "mesh": full_mesh,
        "icon": config["s_icon"],
        "data": {
            "weight": config["s_weight"],
            "value": config["s_value"],
            "flags": ""
        }
    }

# Function to write content to file
def write_file(filepath, content, is_json=False):
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            if is_json:
                for entry in content:
                    json.dump(entry, f, ensure_ascii=False, indent=2)
                    f.write(",\n")
            else:
                f.write(content)
    except IOError as e:
        print(f"\nERROR - failed to write {filepath}: {e}")

# Function to process NIF files
def process_files(config, ignored_files):
    files = get_nif_files(ignored_files)
    if not files:
        print("\nNo .nif files found in current folder. Conversion canceled.")
        return

    entries = []
    errors = {"id": [], "mesh": []}

    for file in files:
        nif_name, _ = os.path.splitext(file)
        full_id, full_mesh, error_id, error_mesh = validate_length(nif_name, config)

        if error_id:
            errors["id"].append(error_id)
        if error_mesh:
            errors["mesh"].append(error_mesh)

        if not error_id and not error_mesh:
            entries.append(generate_entry(full_id, full_mesh, config))

    # Write valid records as a JSON array
    if entries:
        write_file(config["output_file"], entries, is_json=True)
        print(f"\nResult written to: {config['output_file']}")
    else:
        print("\nWARNING - no valid .nif files for conversion, skipping output file creation.")

    # Write error log if there are any errors
    if errors["id"] or errors["mesh"]:
        log_content = ""
        if errors["id"]:
            log_content += f"ERROR - record id is too long (max {config['max_length_id']} chars):\n" + "\n".join(errors["id"]) + "\n\n"
        if errors["mesh"]:
            log_content += f"ERROR - record mesh path is too long (max {config['max_length_mesh']} chars):\n" + "\n".join(errors["mesh"]) + "\n"
        write_file(config["log_file"], log_content)
        print(f"\nWARNING - incorrect records found, see: {config['log_file']}")

def main():
    print("\nTES3 Convert to MiscItem Script\nby Siberian Crab\nv1.0.2")

    ignored_files = {os.path.basename(sys.argv[0]), CONFIG["output_file"], CONFIG["log_file"]}

    if not validate_settings(CONFIG):
        print("\nThe ending of the words is ALMSIVI\n")
        input("Press Enter to continue...")
        return

    process_files(CONFIG, ignored_files)
    
    print("\nThe ending of the words is ALMSIVI\n")
    input("Press Enter to continue...")

if __name__ == "__main__":
    main()

import os
import sys
import textwrap

# Function to get .nif files from current folder
def get_nif_files(ignored_files):
    return [
        f for f in os.listdir('.')
        if os.path.isfile(f) and f.lower().endswith(".nif") and f not in ignored_files
    ]

# Function to validate record ID and mesh path length
def validate_records(nif_name, prefix_id, prefix_mesh, max_length_id, max_length_mesh):
    full_id = f"{prefix_id}{nif_name}"
    full_mesh = f"{prefix_mesh}{nif_name}.nif"
    
    length_id = len(full_id)
    length_mesh = len(full_mesh.replace('\\\\', '\\'))
    
    error_id = f"{nif_name} (current {length_id} chars)" if length_id > max_length_id else None
    error_mesh = f"{nif_name} (current {length_mesh} chars)" if length_mesh > max_length_mesh else None
    
    return full_id, full_mesh, error_id, error_mesh

# Function to validate user settings
def validate_settings(s_name, s_icon, max_length_name, max_length_icon):
    length_name = len(s_name)
    length_icon = len(s_icon.replace('\\\\', '\\'))
    
    if length_name > max_length_name:
        print(f'\nERROR - defined "s_name" is too long: max {max_length_name} chars, current {length_name} chars')
        return False
    if length_icon > max_length_icon:
        print(f'\nERROR - defined "s_icon" is too long: max {max_length_icon} chars, current {length_icon} chars')
        return False
    return True

# Function to define the format for each record in the .json structure
def generate_entry(full_id, full_mesh):
    return textwrap.dedent(f'''\
    {{
      "type": "MiscItem",
      "flags": "{s_flags}",
      "id": "{full_id}",
      "name": "{s_name}",
      "script": "{s_script}",
      "mesh": "{full_mesh}",
      "icon": "{s_icon}",
      "data": {{
        "weight": {s_weight},
        "value": {s_value},
        "flags": ""
      }}
    }},''')

# Function to write conversion result to output file
def write_output_file(entries, output_file):
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(entries))
        print(f"\nConversion result written to: {output_file}")
    except IOError as e:
        print(f"\nERROR - failed to write to {output_file}: {e}")

# Function to write errors to log file
def write_log_file(log_error_mesh, log_error_id, log_file, max_length_id, max_length_mesh):
    if log_error_mesh or log_error_id:
        try:
            with open(log_file, "w", encoding="utf-8") as log:
                if log_error_id:
                    log.write(f"ERROR - record id is too long (max {max_length_id} chars) for:\n" + "\n".join(log_error_id) + "\n\n")
                if log_error_mesh:
                    log.write(f"ERROR - record mesh path is too long (max {max_length_mesh} chars) for:\n" + "\n".join(log_error_mesh) + "\n")
            print(f"\nWARNING - incorrect records found, see: {log_file}")
        except IOError as e:
            print(f"\nERROR - failed to write {log_file}: {e}")

# Function to process input data to .json structure
def process_files():
    files = get_nif_files(ignored_files)
    
    if not files:
        print("\nERROR - no .nif files found in current folder. Conversion canceled...")
        # Wait for user input before exiting
        input("\nThe ending of the words is ALMSIVI\n\nPress Enter to continue...")
        sys.exit(1)
    
    entries = []
    log_error_mesh = []
    log_error_id = []
    
    for file in files:
        nif_name = os.path.splitext(file)[0]
        full_id, full_mesh, error_id, error_mesh = validate_records(nif_name, prefix_id, prefix_mesh, max_length_id, max_length_mesh)
        
        if error_id:
            log_error_id.append(error_id)
        if error_mesh:
            log_error_mesh.append(error_mesh)
        
        if not error_id and not error_mesh:
            entries.append(generate_entry(full_id, full_mesh))
        
    # Check if there is any data to write to output file
    if entries:
        write_output_file(entries, output_file)
    else:
        print("\nWARNING - there are no .nif files for conversion, skipping output file creation...")
    
    write_log_file(log_error_mesh, log_error_id, log_file, max_length_id, max_length_mesh)

if __name__ == "__main__":
    # Display script information
    print("\nTES3 Convert to MiscItem Script\nby Siberian Crab\nv1.0.0")
    
    # Settings
    s_flags = ""                    # PERSISTENT | BLOCKED
    s_name = ""                     # Defines a name for ALL records (should be <= 31 chars)
    s_script = ""
    s_icon = ""                     # Defines a path to icon inside 'Icons' folder (should be <= 31 chars) - a\\\\icon.dds
    s_weight = "1.0"
    s_value = "10"
    
    prefix_id = "_RR_"              # Defines a unique prefix for record IDs
    prefix_mesh = "rr\\\\f\\\\"     # Defines a path to files inside 'Meshes' folder
    
    max_length_id = 31
    max_length_name = 31
    max_length_mesh = 31
    max_length_icon = 31
    
    output_file = "_TES3_convert_to_miscitem.txt"
    log_file = "_TES3_convert_to_miscitem_log.txt"
    ignored_files = {os.path.basename(sys.argv[0]), output_file, log_file}
    
    # Validate user settings before processing
    if not validate_settings(s_name, s_icon, max_length_name, max_length_icon):
        # Wait for user input before exiting
        input("\nThe ending of the words is ALMSIVI\n\nPress Enter to continue...")
        sys.exit(1)
    
    # Process input data to .json structure
    process_files()
    
    # Wait for user input before exiting
    input("\nThe ending of the words is ALMSIVI\n\nPress Enter to continue...")

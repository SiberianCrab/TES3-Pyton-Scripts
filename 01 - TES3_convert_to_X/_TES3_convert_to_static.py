import os
import sys
import textwrap

# Function to get .nif files from current folder
def get_nif_files(ignored_files):
    return [
        f for f in os.listdir('.')
        if os.path.isfile(f) and f.lower().endswith(".nif") and f not in ignored_files
    ]

# Function to validate record ID and path length
def validate_records(nif_name, prefix_id, prefix_path, max_length_id, max_length_path):
    full_id = f"{prefix_id}{nif_name}"
    full_path = f"{prefix_path}{nif_name}.nif"
    
    length_id = len(full_id)
    length_path = len(full_path.replace('\\\\', '\\'))
    
    error_id = f"{nif_name} (current {length_id} chars)" if length_id > max_length_id else None
    error_path = f"{nif_name} (current {length_path} chars)" if length_path > max_length_path else None
    
    return full_id, full_path, error_id, error_path

# Function to define the format for each record in the .json structure
def generate_entry(full_id, full_path):
    return textwrap.dedent(f'''\
    {{
      "type": "Static",
      "flags": "{s_flags}",
      "id": "{full_id}",
      "mesh": "{full_path}"
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
def write_log_file(log_error_path, log_error_id, log_file, max_length_id, max_length_path):
    if log_error_path or log_error_id:
        try:
            with open(log_file, "w", encoding="utf-8") as log:
                if log_error_id:
                    log.write(f"ERROR - record id is too long (max {max_length_id} chars) for:\n" + "\n".join(log_error_id) + "\n\n")
                if log_error_path:
                    log.write(f"ERROR - record mesh path is too long (max {max_length_path} chars) for:\n" + "\n".join(log_error_path) + "\n")
            print(f"\nWARNING - incorrect records found, see: {log_file}")
        except IOError as e:
            print(f"\nERROR - failed to write {log_file}: {e}")

# Function to process files to the .json structure
def process_files():
    files = get_nif_files(ignored_files)
    
    if not files:
        print("\nERROR - no .nif files found in current folder. Conversion canceled...")
        # Wait for user input before exiting
        input("\nThe ending of the words is ALMSIVI\n\nPress Enter to continue...")
        sys.exit(1)
    
    entries = []
    log_error_path = []
    log_error_id = []
    
    for file in files:
        nif_name = os.path.splitext(file)[0]
        full_id, full_path, error_id, error_path = validate_records(nif_name, prefix_id, prefix_path, max_length_id, max_length_path)
        
        if error_id:
            log_error_id.append(error_id)
        if error_path:
            log_error_path.append(error_path)
        
        if not error_id and not error_path:
            entries.append(generate_entry(full_id, full_path))
    
    # Check if there is any data to write to output file
    if entries:
        write_output_file(entries, output_file)
    else:
        print("\nWARNING - there are no .nif files for conversion, skipping output file creation...")
    
    write_log_file(log_error_path, log_error_id, log_file, max_length_id, max_length_path)

if __name__ == "__main__":
    # Display script information
    print("\nTES3 Convert to Static Script\nby Siberian Crab\nv1.0.0")
    
    # Settings
    s_flags = ""                    # PERSISTENT | BLOCKED
    
    prefix_id = "_RR_"              # Defines a unique prefix for record IDs
    prefix_path = "rr\\\\f\\\\"     # Defines a path to files inside 'Meshes' folder
    
    max_length_id = 31
    max_length_path = 31
    
    output_file = "_TES3_convert_to_static.txt"
    log_file = "_TES3_convert_to_static_log.txt"
    ignored_files = {os.path.basename(sys.argv[0]), output_file, log_file}
    
    # Generate a JSON array chunk with records data
    process_files()
    
    # Wait for user input before exiting
    input("\nThe ending of the words is ALMSIVI\n\nPress Enter to continue...")

import os
import json

# Configuration settings
CONFIG = {
    "directory": ".",
    "x_suffix": "a",                     		# Suffix for X-UVW mirrored files
    "y_suffix": "b",                     		# Suffix for Y-UVW mirrored files
    "mirror_suffix": "_m",                      # NIF mirror suffix to check
    
    "log_file": "_TES3_automirror_UVW_X_Y.log"  # Log file name
}

# Function to log messages to log file and console
def log_message(message, log_to_file=True):
    print(message)
    
    if log_to_file and CONFIG["log_file"]:
        try:
            with open(CONFIG["log_file"], "a", encoding="utf-8") as log:
                log.write(message + "\n")
        except OSError as e:
            print(f"ERROR - Failed to write to log file: {e}")

# Function to mirror UVW coordinates along X/Y-axis
def mirror_uv(uv_coords: str, mirror_type: str) -> str:
    try:
        u, v = map(float, uv_coords.split())
        if mirror_type == 'x':
            return f"{1.0 - u} {v}"
        elif mirror_type == 'y':
            return f"{u} {1.0 - v}"
        else:
            log_message(f"Warning: Unknown mirror type '{mirror_type}' - returning original")
            return uv_coords
    except ValueError as e:
        log_message(f"Error mirroring UV coords '{uv_coords}': {e}")
        return uv_coords

# Function to process and mirror all model data components
def process_model_uv(model_data: dict, mirror_type: str) -> dict:
    for key in model_data:
        if "NiTriShapeData" in key:
            shape_data = model_data[key]
            
            if not isinstance(shape_data, dict):
                log_message(f"Warning: Unexpected data format in {key}, skipping")
                continue
            
            try:
                if "UV Sets" in shape_data and shape_data["UV Sets"]:
                    uv_set = shape_data["UV Sets"][0]
                    if uv_set and isinstance(uv_set, list):
                        shape_data["UV Sets"][0] = [mirror_uv(uv, mirror_type) for uv in uv_set]
            except Exception as e:
                log_message(f"Error processing UV data in {key}: {e}")
                continue
    
    return model_data

# Function to process a single input file and save its mirrored version
def process_single_file(input_path: str) -> bool:
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            model_json = json.load(f)
        
        filename = os.path.basename(input_path)
        base_name = filename.replace(".nif.json", "")
        
        if CONFIG["mirror_suffix"] in base_name:
            split_name = base_name.split(CONFIG["mirror_suffix"])
            output_base_x = f"{split_name[0]}{CONFIG['x_suffix']}{CONFIG['mirror_suffix']}{split_name[1]}"
            output_base_y = f"{split_name[0]}{CONFIG['y_suffix']}{CONFIG['mirror_suffix']}{split_name[1]}"
        else:
            output_base_x = f"{base_name}{CONFIG['x_suffix']}"
            output_base_y = f"{base_name}{CONFIG['y_suffix']}"
        
        output_filename_x = f"{output_base_x}.nif.json"
        output_path_x = os.path.join(CONFIG["directory"], output_filename_x)
        
        output_filename_y = f"{output_base_y}.nif.json"
        output_path_y = os.path.join(CONFIG["directory"], output_filename_y)
        
        # Create X-mirrored version
        mirrored_x = json.loads(json.dumps(model_json))
        mirrored_x = process_model_uv(mirrored_x, 'x')
        
        # Create Y-mirrored version
        mirrored_y = json.loads(json.dumps(model_json))
        mirrored_y = process_model_uv(mirrored_y, 'y')
        
        # Save both versions
        with open(output_path_x, 'w', encoding='utf-8') as f:
            json.dump(mirrored_x, f, indent=4, ensure_ascii=False)
        
        with open(output_path_y, 'w', encoding='utf-8') as f:
            json.dump(mirrored_y, f, indent=4, ensure_ascii=False)
        
        log_message(f"{filename.ljust(30)} -> {output_filename_x}")
        log_message(f"{' ' * 30} -> {output_filename_y}")
        return True
        
    except json.JSONDecodeError as e:
        log_message(f"Error parsing JSON in {os.path.basename(input_path)}: {e}")
    except Exception as e:
        log_message(f"Error processing {os.path.basename(input_path)}: {e}")
    return False

# Function to find all .nif.json files that haven't been mirrored yet
def find_json_files(folder_path: str) -> list:
    try:
        return [
            entry.name for entry in os.scandir(folder_path)
            if entry.is_file() 
            and entry.name.endswith(".nif.json") 
            and not entry.name.startswith("mirrored_") 
            and CONFIG["x_suffix"] not in entry.name
            and CONFIG["y_suffix"] not in entry.name
        ]
    except OSError as e:
        log_message(f"Error scanning directory {folder_path}: {e}")
        return []

def main():
    try:
        with open(CONFIG["log_file"], "w", encoding="utf-8") as log:
            log.write("")
    except OSError as e:
        print(f"Failed to initialize log file: {e}")
        return

    print("\nTES3 Automatic Mirroring Script\n        UVW | X/Y-axis\n\nby Siberian Crab\nv1.0.0\n")

    files_to_process = find_json_files(CONFIG["directory"])
    
    if not files_to_process:
        log_message("No .nif.json files found in current folder. Conversion canceled.")
        log_message("\nThe ending of the words is ALMSIVI\n")
        input("Press Enter to continue...")
        return
    
    max_filename_length = max(len(f) for f in files_to_process)
    column_width = min(max_filename_length, 64)  # Limit maximum width

    log_message(f"Found {len(files_to_process)} files to process:")

    success_count = 0
    for filename in files_to_process:
        input_path = os.path.join(CONFIG["directory"], filename)
        
        if process_single_file(input_path):
            success_count += 1
        else:
            log_message(f"[FAIL] {filename.ljust(30)}")

    log_message(f"\nProcessing complete. Success: {success_count}/{len(files_to_process)}")
    log_message("\nThe ending of the words is ALMSIVI\n")
    input("Press Enter to continue...")

if __name__ == "__main__":
    main()
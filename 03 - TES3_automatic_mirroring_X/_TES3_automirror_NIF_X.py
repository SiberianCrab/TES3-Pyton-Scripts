import os
import json

# Configuration settings
CONFIG = {
    "directory": ".",
    "mirror_suffix": "_m",                  # Suffix for mirrored files
    
    "log_file": "_TES3_automirror_NIF.log"   # Log file name
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

# Function to mirror coordinates along X-axis
def mirror_coordinates(coords: str) -> str:
    try:
        x, y, z = map(float, coords.split())
        return f"{-x} {y} {z}"
    except ValueError as e:
        log_message(f"Error mirroring coordinates '{coords}': {e}")
        return coords

# Function to process and mirror all model data components
def process_model_data(model_data: dict) -> dict:
    for key in model_data:
        if "NiTriShapeData" in key:
            shape_data = model_data[key]
            
            if not isinstance(shape_data, dict):
                log_message(f"Warning: Unexpected data format in {key}, skipping")
                continue
            
            # Mirroring
            try:
                if "Vertices" in shape_data:
                    shape_data["Vertices"] = [mirror_coordinates(v) for v in shape_data["Vertices"]]
                if "Normals" in shape_data:
                    shape_data["Normals"] = [mirror_coordinates(n) for n in shape_data["Normals"]]
                if "Center" in shape_data:
                    shape_data["Center"] = mirror_coordinates(shape_data["Center"])
                
                # Processing triangles if they exist and are in correct format
                if "Triangles" in shape_data:
                    triangles = shape_data["Triangles"]
                    
                    if all(isinstance(t, str) for t in triangles):
                        try:
                            split_triangles = [t.split() for t in triangles]
                            processed_triangles = [f"{t[2]} {t[1]} {t[0]}" for t in split_triangles if len(t) == 3]
                            shape_data["Triangles"] = processed_triangles
                        except IndexError as e:
                            log_message(f"Malformed triangle data in {key}: {triangles} - skipping. Error: {e}")
                    elif isinstance(triangles, list) and len(triangles) % 3 == 0:
                        triangles_copy = triangles.copy()
                        for i in range(0, len(triangles_copy), 3):
                            triangles_copy[i], triangles_copy[i+2] = triangles_copy[i+2], triangles_copy[i]
                        shape_data["Triangles"] = triangles_copy
                    else:
                        log_message(f"Warning: Unsupported triangle format in {key} - skipping triangle processing")
            except Exception as e:
                log_message(f"Error processing shape data in {key}: {e}")
                continue
    
    return model_data

# Function to process a single input file and save its mirrored version
def process_single_file(input_path: str, output_path: str) -> bool:
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            model_json = json.load(f)
        
        mirrored_model = process_model_data(model_json)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(mirrored_model, f, indent=4, ensure_ascii=False)
        
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
            and CONFIG["mirror_suffix"] not in entry.name
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

    print("\nTES3 Automatic Mirroring Script\n          NIF | X-axis\n\nby Siberian Crab\nv1.0.1\n")

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
        base_name = filename.replace(".nif.json", "")
        output_filename = f"{base_name}{CONFIG['mirror_suffix']}.nif.json"
        output_path = os.path.join(CONFIG["directory"], output_filename)
        
        if process_single_file(input_path, output_path):
            log_message(f"{filename.ljust(column_width, '.')} -> {output_filename}")
            success_count += 1
        else:
            log_message(f"[FAIL] {filename.ljust(column_width)} -> Failed")

    log_message(f"Processing complete. Success: {success_count}/{len(files_to_process)}")
    log_message("\nThe ending of the words is ALMSIVI\n")
    input("Press Enter to continue...")

if __name__ == "__main__":
    main()
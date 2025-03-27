import json
import os

# Configuration settings
CONFIG = {
    "directory": ".",
    "mirror_suffix": "_m",    					 # Suffix for mirrored files
    
    "log_file": "_TES3_automatic_mirroring.log"  # Log file name
}

# Function to log messages to log file and console
def log_message(message, log_to_file=True):
    log_file = CONFIG.get("log_file", "")
    if log_to_file and log_file:
        try:
            with open(log_file, "a", encoding="utf-8") as log:
                log.write(message + "\n")
        except OSError as e:
            print(f"ERROR - Failed to write to log file: {e}")
    print(message)

# Function to mirror vertex coordinates along X axis
def mirror_vertex(vertex: str) -> str:
    x, y, z = map(float, vertex.split())
    return f"{-x} {y} {z}"

# Function to mirror normal vector coordinates along X axis
def mirror_normal(normal: str) -> str:
    x, y, z = map(float, normal.split())
    return f"{-x} {y} {z}"

# Function to process and mirror all model data components
def process_model_data(model_data: dict) -> dict:
    for key in model_data:
        if "NiTriShapeData" in key:
            shape_data = model_data[key]
            
            # Mirror vertices
            if "Vertices" in shape_data:
                shape_data["Vertices"] = [mirror_vertex(v) for v in shape_data["Vertices"]]
            
            # Mirror normals
            if "Normals" in shape_data:
                shape_data["Normals"] = [mirror_normal(n) for n in shape_data["Normals"]]
            
            # Update center point
            if "Center" in shape_data:
                x, y, z = map(float, shape_data["Center"].split())
                shape_data["Center"] = f"{-x} {y} {z}"
            
            # Process triangles if they exist and are in correct format
            if "Triangles" in shape_data:
                triangles = shape_data["Triangles"]
                
                # Check if triangles is a list of strings (like ["0 1 2", "3 4 5"])
                if all(isinstance(t, str) for t in triangles):
                    try:
                        # Split each triangle string into components
                        split_triangles = [t.split() for t in triangles]
                        # Reverse winding order for each triangle
                        processed_triangles = [f"{t[2]} {t[1]} {t[0]}" for t in split_triangles]
                        shape_data["Triangles"] = processed_triangles
                    except IndexError:
                        log_message(f"Warning: Malformed triangle data in {key} - skipping triangle processing")
                
                # Or if triangles is a flat list of indices (like [0, 1, 2, 3, 4, 5])
                elif isinstance(triangles, list) and len(triangles) % 3 == 0:
                    # Reverse winding order by swapping first and last vertex of each triangle
                    for i in range(0, len(triangles), 3):
                        triangles[i], triangles[i+2] = triangles[i+2], triangles[i]
                else:
                    log_message(f"Warning: Unsupported triangle format in {key} - skipping triangle processing")
    
    return model_data

# Function to process a single input file and save its' mirrored version
def process_single_file(input_path: str, output_path: str) -> bool:
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            model_json = json.load(f)
        
        mirrored_model = process_model_data(model_json)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(mirrored_model, f, indent=4, ensure_ascii=False)
        
        return True
    except Exception as e:
        log_message(f"Error processing {os.path.basename(input_path)}: {str(e)}")
        return False

# Function to find all .nif.json files that haven't been mirrored yet
def find_json_files(folder_path: str) -> list:
    return [
        f for f in os.listdir(folder_path) 
        if f.endswith(".nif.json") and not f.startswith("mirrored_") and CONFIG["mirror_suffix"] not in f
    ]

def main():
    with open(CONFIG["log_file"], "w", encoding="utf-8") as log:
        log.write("")
    
    print("\nTES3 Automatic NIF Mirroring Script\n\nby Siberian Crab\nv1.0.0\n")

    files_to_process = find_json_files(CONFIG["directory"])
    
    if not files_to_process:
        log_message(f"No .nif.json files found")
        return
    
    # Calculating maximum filename length for alignment
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
            log_message(f"{filename.ljust(column_width)} -> {output_filename}")
            success_count += 1
        else:
            log_message(f"[FAIL] {filename.ljust(column_width)} -> Failed")

    log_message(f"Processing complete. Success: {success_count}/{len(files_to_process)}")
    log_message("\nThe ending of the words is ALMSIVI\n")
    input("Press Enter to continue...")

if __name__ == "__main__":
    main()
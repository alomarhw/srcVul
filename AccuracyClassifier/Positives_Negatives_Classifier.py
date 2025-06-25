import os
import re
import json
import shutil
import hashlib
from datetime import datetime
from collections import defaultdict
from compute_slicing_vector import compute_slicing_vector
from src_slicing import identify_vr_vars, srcSlice

# Paths
CVE_DIFFS_PATH = input("Enter path to CVE_Diffs directory: ").strip()
# Example: /Users/gyawalh/srcVul/CVE_Diffs

PATCH_METADATA_PATH = input("Enter path to patch_metadata directory: ").strip()
# Example: /Users/gyawalh/srcVul/patch_metadata

UNIQUE_PATCH_METADATA_PATH = input("Enter path to unique_patch_metadata directory: ").strip()
# Example: /Users/gyawalh/srcVul/unique_patch_metadata


# Initialize counters for evaluation metrics
tp, fp, tn, fn = 0, 0, 0, 0
tp_ids, fp_ids, fn_ids, tn_ids = [], [], [], []

# Helper function to parse dates from diff files
def get_commit_date(diff_content):
    match = re.search(r'(AuthorDate|CommitDate):\s+(.+)', diff_content)
    if match:
        date_str = match.group(2)
        return datetime.strptime(date_str, "%a %b %d %H:%M:%S %Y %z")
    return None

# Function to calculate hash of slicing vector
def hash_slicing_vector(slicing_vector):
    return hashlib.sha256(str(slicing_vector).encode()).hexdigest()

# Simulated srcVul function for detection based on the slicing vector similarity
def srcVul_detect(diff_path, vector_database):
    with open(diff_path, 'r') as file:
        diff_content = file.read()

    vr_vars = identify_vr_vars(diff_content)
    vr_statements = srcSlice(diff_content, vr_vars)
    module_size = len(re.findall(r'^\+[^+]', diff_content, re.MULTILINE)) + len(re.findall(r'^\-[^-]', diff_content, re.MULTILINE))

    slicing_vector = compute_slicing_vector(vr_statements, module_size)
    vector_hash = hash_slicing_vector(slicing_vector)

    for vector in vector_database:
        if vector_hash == vector["Vector_Hash"]:
            return True  # Vulnerability detected
    return False  # Vulnerability not detected

# Load all JSON files in the unique_patch_metadata directory as the known vulnerable vectors
vector_database = []
for filename in os.listdir(UNIQUE_PATCH_METADATA_PATH):
    if filename.endswith(".json"):
        file_path = os.path.join(UNIQUE_PATCH_METADATA_PATH, filename)
        with open(file_path, 'r') as file:
            data = json.load(file)
            data["Vector_Hash"] = hash_slicing_vector(data["Slicing_Vector"])
            vector_database.append(data)

# Step 1: Load and categorize diffs by project and date
project_diffs = defaultdict(list)

# Gather .diff files and categorize by project
for diff_filename in os.listdir(CVE_DIFFS_PATH):
    if diff_filename.endswith(".diff"):
        diff_path = os.path.join(CVE_DIFFS_PATH, diff_filename)
        with open(diff_path, 'r') as diff_file:
            diff_content = diff_file.read()
            date = get_commit_date(diff_content)
            if date:
                project_name = diff_filename.split('_')[0]
                project_diffs[project_name].append((date, diff_filename))

# Sort each project's diffs by date
for project in project_diffs:
    project_diffs[project].sort()

# Step 2: Process each version, running srcVul on the previous version (version i)
for project_name, versions in project_diffs.items():
    for i in range(len(versions) - 1):
        # Define current and previous versions
        prev_version_date, prev_diff_filename = versions[i]
        curr_version_date, curr_diff_filename = versions[i + 1]

        prev_diff_path = os.path.join(CVE_DIFFS_PATH, prev_diff_filename)
        curr_diff_path = os.path.join(CVE_DIFFS_PATH, curr_diff_filename)

        # Step 3: Check if the current version has an associated CVE JSON file
        cve_id = curr_diff_filename.split('_')[0]
        json_filename = f"{cve_id}_{curr_diff_filename.split('_')[1]}.json"
        json_path = os.path.join(PATCH_METADATA_PATH, json_filename)

        if os.path.exists(json_path):
            # Step 4: Temporarily remove the JSON file for testing
            tmp_path = os.path.join(UNIQUE_PATCH_METADATA_PATH, json_filename)
            if os.path.exists(json_path):
                shutil.move(json_path, tmp_path)

            # Step 5: Run srcVul on the previous version
            is_detected = srcVul_detect(prev_diff_path, vector_database)

            # Determine TP or FN
            if is_detected:
                tp += 1
                tp_ids.append(curr_diff_filename)   # record the ID
            else:
                fn += 1
                fn_ids.append(curr_diff_filename)

            # Restore JSON file after testing
            shutil.move(tmp_path, json_path)
        
        else:
            # Non-CVE diff: Run srcVul and check if it falsely detects vulnerability
            is_detected = srcVul_detect(prev_diff_path, vector_database)
            if is_detected:
                fp += 1
                fp_ids.append(curr_diff_filename)
            else:
                tn += 1
                tn_ids.append(curr_diff_filename)

# Step 6: Print results
print(f"True Positives (TP): {tp}")
print(f"False Negatives (FN): {fn}")
print(f"False Positives (FP): {fp}")
print(f"True Negatives (TN): {tn}")

# Total Results
print("\nFinal Counts:")
print(f"Total True Positives (TP): {tp}")
print("TP IDs:", tp_ids)

print(f"\nTotal False Negatives (FN): {fn}")
print("FN IDs:", fn_ids)

print(f"\nTotal False Positives (FP): {fp}")
print("FP IDs:", fp_ids)

print(f"\nTotal True Negatives (TN): {tn}")
print("TN IDs:", tn_ids)

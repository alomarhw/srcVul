import os
import json
from datasketch import MinHash, MinHashLSH

# Generalized paths
# Replace these with appropriate paths for your environment
PATCH_METADATA_PATH = "./patch_metadata"  # Path to the directory with JSON files
GROUPS_OUTPUT_PATH = "./clone_groups.txt"  # Path to save clone groups
PAIRS_OUTPUT_PATH = "./clone_pairs.txt"  # Path to save clone pairs

# Function to generate MinHash for a given slicing vector
def minhash_slicing_vector(slicing_vector):
    """
    Generate MinHash for a slicing vector.
    :param slicing_vector: Dictionary representing the slicing vector
    :return: MinHash object
    """
    m = MinHash(num_perm=128)
    # Convert the slicing vector dictionary into hashable strings
    for key, value in slicing_vector.items():
        m.update(f"{key}:{value}".encode('utf8'))
    return m

# Create an LSH index
lsh = MinHashLSH(threshold=0.8, num_perm=128)

# Dictionary to store MinHashes by CVE_ID for later comparison or retrieval
minhash_dict = {}

# Set to keep track of inserted CVE IDs and avoid duplicates
inserted_cves = set()

# Process each JSON file in the patch_metadata directory
for filename in os.listdir(PATCH_METADATA_PATH):
    if filename.endswith(".json"):
        file_path = os.path.join(PATCH_METADATA_PATH, filename)
        with open(file_path, 'r') as file:
            data = json.load(file)
            cve_id = data.get("CVE_ID")
            slicing_vector = data.get("Slicing_Vector")

            if slicing_vector and cve_id:
                # Skip if this CVE ID is already inserted
                if cve_id in inserted_cves:
                    print(f"Skipping duplicate CVE ID: {cve_id}")
                    continue
                
                # Generate MinHash for the slicing vector
                minhash = minhash_slicing_vector(slicing_vector)

                # Add MinHash to the LSH index and track the insertion
                lsh.insert(cve_id, minhash)
                inserted_cves.add(cve_id)

                # Store MinHash for reference
                minhash_dict[cve_id] = minhash

# To find clone groups and pairs
clone_groups = []
clone_pairs = set()  # Using a set to avoid duplicate pairs
visited = set()

for cve_id, minhash in minhash_dict.items():
    # Skip if already processed as part of a group
    if cve_id in visited:
        continue
    
    # Query the LSH index for similar vectors (forming a clone group)
    similar_cves = lsh.query(minhash)
    
    # Mark all similar CVEs as visited
    for sim_cve in similar_cves:
        visited.add(sim_cve)
        
        # Record clone pairs (unique pair without duplicates)
        if sim_cve != cve_id:
            pair = tuple(sorted([cve_id, sim_cve]))  # Sort to avoid duplicate pairs like (A, B) and (B, A)
            clone_pairs.add(pair)
    
    # Only add non-trivial groups (more than one member)
    if len(similar_cves) > 1:
        clone_groups.append(similar_cves)

# Output clone groups and pairs to files
with open(GROUPS_OUTPUT_PATH, 'w') as output_file:
    for group in clone_groups:
        output_file.write("Clone Group:\n")
        for cve in group:
            output_file.write(f"  {cve}\n")
        output_file.write("\n")
    output_file.write(f"Total number of clone groups: {len(clone_groups)}\n")

with open(PAIRS_OUTPUT_PATH, 'w') as output_file:
    for pair in clone_pairs:
        output_file.write(f"Clone Pair: {pair[0]}, {pair[1]}\n")
    output_file.write(f"Total number of clone pairs: {len(clone_pairs)}\n")

print(f"Clone groups have been saved to {GROUPS_OUTPUT_PATH}")
print(f"Clone pairs have been saved to {PAIRS_OUTPUT_PATH}")
print(f"Total number of clone groups: {len(clone_groups)}")
print(f"Total number of clone pairs: {len(clone_pairs)}")

import os
import re
from collections import defaultdict
from pymongo import MongoClient


# Start of DatabaseManager class
class DatabaseManager:
    def __init__(self, database_url="mongodb://localhost:27017/", database_name="SliceMetricsDB"):
        self.client = MongoClient(database_url)
        self.database = self.client[database_name]

    def create_collections(self):
        try:
            # Create collections if they don't exist
            if "VectorData" not in self.database.list_collection_names():
                self.database.create_collection("VectorData")
                print("Collection 'VectorData' created successfully.")

            if "TestVectorData" not in self.database.list_collection_names():    
                self.database.create_collection("TestVectorData")
                print("Collection 'TestVectorData' created successfully.")
        except Exception as ex:
            print(f"Error while creating collections: {ex}")

    def get_next_id(self, collection_name):
        collection = self.database[collection_name]
        last_doc = collection.find_one(sort=[("Id", -1)])
        if last_doc is None or "Id" not in last_doc:
            return 1
        else:
            return last_doc["Id"] + 1

    def insert_vector_data(self, collection_name, CVE_ID, SC, SCvg, SI, SS, method_name=None, variable_name=None, patched_code_content=None):
        try:
            next_id = self.get_next_id(collection_name)
            # Build record with new column names
            record = {
                "Id": next_id,
                "CVE_ID": CVE_ID,
                "SC": SC,
                "SCvg": SCvg,
                "SI": SI,
                "SS": SS,
            }
            # Optionally add extra fields if available
            if method_name is not None:
                record["MethodName"] = method_name
            if variable_name is not None:
                record["VariableName"] = variable_name
            if patched_code_content:
                record["PatchedCode"] = patched_code_content

            collection = self.database[collection_name]
            collection.insert_one(record)
            print(f"Inserted record with Id {next_id} into {collection_name}.")
        except Exception as ex:
            print(f"Error inserting data into {collection_name}: {ex}")

    def close(self):
        if self.client:
            self.client.close()
            print("MongoDB connection closed.")


# Start of SliceAnalyzer class
class SliceAnalyzer:
    @staticmethod
    def get_module_size_from_file(file_path):
        if not os.path.exists(file_path):
            print("File not found.")
            return 0

        with open(file_path, "r") as file:
            lines = file.readlines()
        return len(lines)

    @staticmethod
    def read_slice_profiles_from_file(file_path):
        slice_profiles = defaultdict(list)

        if not os.path.exists(file_path):
            print("File not found.")
            return slice_profiles

        with open(file_path, "r") as file:
            lines = file.readlines()

        for line in lines:
            if not line.strip():
                continue

            parts = SliceAnalyzer.split_ignoring_brackets(line.strip())
            if len(parts) < 8:
                print(f"Warning: Incomplete line format - skipping line: {line}")
                continue

            try:
                variable_name = parts[2] if parts[2].strip() else "<unnamed>"
                slice_profile = {
                    "File": parts[0],
                    "Function": parts[1],
                    "Variable": variable_name,
                    "Def": SliceAnalyzer.parse_set(parts[3], int),
                    "Use": SliceAnalyzer.parse_set(parts[4], int),
                    "Dvars": SliceAnalyzer.parse_set(parts[5], str),
                    "Ptrs": SliceAnalyzer.parse_set(parts[6], str),
                    "Cfuncs": SliceAnalyzer.parse_cfuncs(parts[7])
                }

                slice_profiles[slice_profile["Function"]].append(slice_profile)
            except Exception as ex:
                print(f"Error parsing line: {line}")
                print(f"Exception: {ex}")

        return slice_profiles

    @staticmethod
    def split_ignoring_brackets(input_string):
        matches = re.findall(r'[^,{]+{[^}]*}|[^,]+', input_string)
        if len(matches) > 8:
            combined_cfuncs = ",".join(matches[7:])
            matches = matches[:7] + [combined_cfuncs]
        return matches

    @staticmethod
    def parse_set(input_string, cast_func):
        content = input_string[input_string.find('{') + 1:].rstrip('}')
        if not content:
            return set()
        try:
            return set(map(cast_func, content.split(',')))
        except ValueError:
            valid_values = []
            for item in content.split(','):
                try:
                    valid_values.append(cast_func(item))
                except ValueError:
                    print(f"Warning: Skipping invalid value '{item}' in set")
            return set(valid_values)

    @staticmethod
    def parse_cfuncs(input_string):
        if "cfuncs{" not in input_string:
            return {}
        try:
            start_idx = input_string.find("cfuncs{") + len("cfuncs{")
            content = input_string[start_idx:-1]
            cfunc_entries = content.split('},')
            cfuncs = {}
            for entry in cfunc_entries:
                entry = entry.rstrip('}')
                if '{' in entry:
                    name, count = entry.split('{', 1)
                    cfuncs[name.strip()] = int(count.strip())
                else:
                    cfuncs[entry.strip()] = 1
            return cfuncs
        except Exception as e:
            print(f"Error parsing cfuncs: {e}")
            return {}

    @staticmethod
    def compute_slice_metrics(slice_profile, module_size):
        SC = (1 + len(slice_profile["Dvars"]) + len(slice_profile["Ptrs"])) / module_size
        SZ = len(slice_profile["Def"].union(slice_profile["Use"]))
        SCvg = SZ / module_size
        SI = (len(slice_profile["Dvars"]) + len(slice_profile["Ptrs"]) + len(slice_profile["Cfuncs"])) / module_size

        try:
            Sf = min(slice_profile["Def"]) if slice_profile["Def"] else 0
            Sl = max(slice_profile["Use"]) if slice_profile["Use"] else 0
        except ValueError as e:
            print(f"Warning: Invalid data in Def or Use - {e}")
            Sf, Sl = 0, 0

        SS = abs(Sl - Sf) / module_size if module_size > 0 else 0

        return SC, SZ, SCvg, SI, SS

    @staticmethod
    def generate_vs_vectors(slice_profiles, module_size):
        vs_vectors = {}
        for method, profiles in slice_profiles.items():
            for profile in profiles:
                metrics = SliceAnalyzer.compute_slice_metrics(profile, module_size)
                key = f"{method}|{profile['Variable']}"
                vs_vectors[key] = metrics
        return vs_vectors


# The rest of the code where we process all files in the tools directory                    
def process_files_in_bulk():
    analyzer = SliceAnalyzer()
    database_manager = DatabaseManager()

    print("Step 1: Is this testing data? (yes/no)")
    is_testing = input().strip().lower() == "yes"

    print("Step 2: Please provide the path to the file with code:")
    code_file_path = input().strip()
    module_size = analyzer.get_module_size_from_file(code_file_path)
    if module_size == 0:
        print("Invalid code file. Exiting...")
        return

    patched_code_content = None
    if not is_testing:
        print("Step 1.1: Please provide the CVE_ID:")
        cve_id = input().strip()
        print("Step 1.2: Please provide the path to the patched version file:")
        patched_file_path = input().strip()
        with open(patched_file_path, "r") as file:
            patched_code_content = file.read()

    print("Step 4: Please provide the path to the file with slice profiles:")
    slice_profiles_file_path = input().strip()
    slice_profiles = analyzer.read_slice_profiles_from_file(slice_profiles_file_path)

    if not slice_profiles:
        print("No valid slice profiles found. Exiting...")
        return

    print("Step 5: Initializing database...")
    database_manager.create_collections()

    collection_name = "TestVectorData" if is_testing else "VectorData"
    vs_vectors = analyzer.generate_vs_vectors(slice_profiles, module_size)

    print("Step 6: Inserting data into database...")
    for key, metrics in vs_vectors.items():
        # key is in the form "method|variable"
        method, variable = key.split("|")
        # Insert record with the new field names.
        database_manager.insert_vector_data(
            collection_name,
            cve_id,
            metrics[0],  # SC
            metrics[2],  # SCvg
            metrics[3],  # SI
            metrics[4],  # SS
            method_name=method,
            variable_name=variable,
            patched_code_content=patched_code_content
        )

    database_manager.close()
    print("All files processed successfully.")


# Run the bulk processing
if __name__ == "__main__":
    process_files_in_bulk()

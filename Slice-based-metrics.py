# Sample slicing results
slicing_results = """srcVul/vulnerable.c,snd_info_create_entry,entry,def{4,5,8,13,14,18},use{5,6,9,10,15,16,17,20,21},dvars{},ptrs{parent},cfuncs{list_add_tail{1},INIT_LIST_HEAD{1},mutex_init{1},kfree{1},sizeof{1}}
srcVul/vulnerable.c,snd_info_create_entry,parent,def{2},use{18,19,20},dvars{entry},ptrs{},cfuncs{list_add_tail{2}}
srcVul/vulnerable.c,snd_info_create_entry,name,def{2},use{8,9},dvars{},ptrs{},cfuncs{kstrdup{1}}
"""

# Initialize metrics
SC = {}
SZ = {}
Scvg = {}
SI = {}
SS = {}

# Split slicing results into individual slices
slices = slicing_results.strip().split("\n")

# Iterate through each slice and extract metrics
for slice in slices:
    parts = slice.split(",")
    slice_name = parts[2]
    def_set = parts[3].split("{")[1].split("}")[0].split(",")
    use_set = parts[4].split("{")[1].split("}")[0].split(",")
    dvars_set = parts[5].split("{")[1].split("}")[0].split(",")
    ptrs_set = parts[6].split("{")[1].split("}")[0].split(",")
    cfuncs_set = parts[7].split("{")[1].split("}")[0].split(",")

    # Calculate SC (Slice Count)
    module_size = len(use_set) # Module size is the number of use statements in this case
    SC[slice_name] = len(def_set)

    # Calculate SZ (Slice Size)
    SZ[slice_name] = len(def_set + use_set)

    # Calculate Scvg (SC Variability Group)
    Scvg[slice_name] = SZ[slice_name] / module_size if module_size > 0 else 0

    # Calculate SI (Slice Identifier)
    SI[slice_name] = len(set(dvars_set + ptrs_set + cfuncs_set))

    # Calculate SS (Semantic Slices)
    SS[slice_name] = len(cfuncs_set)

    # Calculate SS (Slice Spatial)
 first_statement = int(min(use_set)) # Find the first use statement
 last_statement = int(max(use_set)) # Find the last use statement
 module_size = len(use_set)  # Module size is the total number of statements
 SS[slice_name] = (last_statement - first_statement) / module_size

# Print the calculated metrics
print("SC (Slice Count):", SC)
print("SZ (Slice Size):", SZ)
print("Scvg (Slice Coverage):", Scvg)
print("SI (Slice Identifier):", SI)
print("SS (Slice Spatial):", SS)

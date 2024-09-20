# Sample slice-based metrics (replace with actual data)
slice_metrics = {
    "entry": {"SC": 6, "SZ": 12, "Scvg": 0.75, "SI": 4, "SS": 5},
    "parent": {"SC": 1, "SZ": 3, "Scvg": 0.33, "SI": 3, "SS": 2},
    "name": {"SC": 1, "SZ": 2, "Scvg": 0.5, "SI": 1, "SS": 1},
}

# Initialize slicing vectors
slicing_vectors = {
    "Variable": {},
    "Function": {},
    "File": {},
}

# Populate the slicing vectors
for slice_name, metrics in slice_metrics.items():
    # Variable-level slicing vector
    slicing_vectors["Variable"][slice_name] = [
        metrics["SC"],
        metrics["SZ"],
        metrics["Scvg"],
        metrics["SI"],
        metrics["SS"],
    ]

    # Function-level slicing vector
    slicing_vectors["Function"][slice_name] = [metrics["SC"], metrics["Scvg"], metrics["SI"]]

    # File-level slicing vector
    slicing_vectors["File"][slice_name] = [metrics["Scvg"], metrics["SI"]]

# Print the generated slicing vectors
for level, vectors in slicing_vectors.items():
    print(f"{level} Level Slicing Vectors:")
    for slice_name, vector in vectors.items():
        print(f"{slice_name}: {vector}")

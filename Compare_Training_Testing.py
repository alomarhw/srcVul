import sqlite3

# Function to compare entries from TestVectorData and TrainingData tables
def compare_test_vector_data(db_path, tolerance):
    # Connect to the SQLite database
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # SQL query to compare entries using a tolerance value
    query = f'''
        SELECT tv.Id AS TestID, tv.MethodName, tv.VariableName,
               tr.id AS TrainID, 
               tv.SC AS Test_SC, tr.Slice_Count AS Train_SC,
               tv.SCvg AS Test_SCvg, tr.Slice_Coverage AS Train_SCvg,
               tv.SS AS Test_SS, tr.Slice_Spatial AS Train_SS,
               tv.SI AS Test_SI, tr.Slice_Identifier AS Train_SI,
               tr.Patch_Content
        FROM TestVectorData tv
        JOIN TrainingData tr
        ON ABS(tv.SC - tr.Slice_Count) < {tolerance}
           AND ABS(tv.SCvg - tr.Slice_Coverage) < {tolerance}
           AND ABS(tv.SS - tr.Slice_Spatial) < {tolerance}
           AND ABS(tv.SI - tr.Slice_Identifier) < {tolerance}
        ORDER BY tv.Id, tr.id;
    '''

    # Execute the query
    cursor.execute(query)
    results = cursor.fetchall()

    # Close the database connection
    connection.close()

    # Check if any matches were found
    if not results:
        print("No matching entries found between TestVectorData and TrainingData.")
        return

    # Print the results
    print("TestID | MethodName | VariableName | TrainID | Test_SC | Train_SC | Test_SCvg | Train_SCvg | Test_SS | Train_SS | Test_SI | Train_SI | Patch_Content")
    print("-" * 220)
    for row in results:
        (test_id, method_name, variable_name, train_id, test_sc, train_sc,
         test_scvg, train_scvg, test_ss, train_ss, test_si, train_si, patch_content) = row
        
        # Print the row details including the full Patch_Content
        print(f"{test_id} | {method_name} | {variable_name} | {train_id} | {test_sc:.6f} | {train_sc:.6f} | "
              f"{test_scvg:.6f} | {train_scvg:.6f} | {test_ss:.6f} | {train_ss:.6f} | {test_si:.6f} | {train_si:.6f} | {patch_content}")

if __name__ == "__main__":
    db_path = r'C:\Users\Himal\Desktop\Research\srcVul\VectorOperations\SlicingVector_Generator\bin\Debug\net6.0\vectors.db'  # Update this path
    tolerance = 0.02  # Set the tolerance value for comparison 
    
    # Run the comparison
    compare_test_vector_data(db_path, tolerance)

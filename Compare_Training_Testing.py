import sqlite3

# Function to compare entries from TestVectorData and TrainingData tables and store results in ComparisonResults table
def compare_and_store_results(db_path, tolerance):
    # Connect to the SQLite database
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # Create the ComparisonResults table if it doesn't exist
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS ComparisonResults (
        TestID INTEGER,
        MethodName TEXT,
        VariableName TEXT,
        TrainID INTEGER,
        Test_SC REAL,
        Train_SC REAL,
        Test_SCvg REAL,
        Train_SCvg REAL,
        Test_SS REAL,
        Train_SS REAL,
        Test_SI REAL,
        Train_SI REAL,
        Patch_Content TEXT
    );
    '''
    cursor.execute(create_table_query)

    # SQL query to compare entries using a tolerance value
    comparison_query = f'''
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

    # Execute the comparison query
    cursor.execute(comparison_query)
    results = cursor.fetchall()

    # Check if any matches were found
    if not results:
        print("No matching entries found between TestVectorData and TrainingData.")
        connection.close()
        return

    # Insert the results into the ComparisonResults table
    insert_query = '''
    INSERT INTO ComparisonResults (
        TestID, MethodName, VariableName, TrainID,
        Test_SC, Train_SC, Test_SCvg, Train_SCvg,
        Test_SS, Train_SS, Test_SI, Train_SI, Patch_Content
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    '''
    cursor.executemany(insert_query, results)

    # Commit the changes
    connection.commit()

    # Print the number of rows inserted
    print(f"{len(results)} rows inserted into the ComparisonResults table.")

    # Close the database connection
    connection.close()

if __name__ == "__main__":
    db_path = r'C:\Users\Himal\Desktop\Research\srcVul\VectorOperations\SlicingVector_Generator\bin\Debug\net6.0\vectors.db'  # Update this path
    tolerance = 0.02  # Set the tolerance value for comparison 
    
    # Run the comparison and store results
    compare_and_store_results(db_path, tolerance)

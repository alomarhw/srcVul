using System.Data.SQLite;

public class DatabaseManager
{
    private SQLiteConnection connection;

    public void InitializeDatabase(string databasePath)
    {
        try
        {
            string fullPath = Path.GetFullPath(databasePath);
            Console.WriteLine($"Database full path: {fullPath}");

            connection = new SQLiteConnection($"Data Source={fullPath};Version=3;");
            connection.Open();
            Console.WriteLine("Database connection opened successfully.");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error opening database connection: {ex.Message}");
        }
    }

    public void CreateTables()
    {
        try
        {
            string createTrainingTableQuery = @"
                CREATE TABLE IF NOT EXISTS VectorData (
                    Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    MethodName TEXT,
                    VariableName TEXT,
                    SC REAL,
                    SCvg REAL,
                    SI INTEGER,
                    SS REAL,
                    PatchedCode TEXT
                );";

            string createTestingTableQuery = @"
                CREATE TABLE IF NOT EXISTS TestVectorData (
                    Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    MethodName TEXT,
                    VariableName TEXT,
                    SC REAL,
                    SCvg REAL,
                    SI INTEGER,
                    SS REAL
                );";

            using (var command = new SQLiteCommand(createTrainingTableQuery, connection))
            {
                command.ExecuteNonQuery();
                Console.WriteLine("VectorData table created successfully or already exists.");
            }

            using (var command = new SQLiteCommand(createTestingTableQuery, connection))
            {
                command.ExecuteNonQuery();
                Console.WriteLine("TestVectorData table created successfully or already exists.");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error while creating the tables: {ex.Message}");
        }
    }

    public void InsertVectorData(string tableName, string methodName, string variableName, double SC, double SCvg, double SI, double SS, string patchedCodeContent = null)
    {
        Console.WriteLine($"Inserting into {tableName}: Method={methodName}, Variable={variableName}, SC={SC}, SCvg={SCvg}, SI={SI}, SS={SS}");

        string insertQuery = tableName == "VectorData" ?
            $@"
                INSERT INTO {tableName} (MethodName, VariableName, SC, SCvg, SI, SS, PatchedCode)
                VALUES (@MethodName, @VariableName, @SC, @SCvg, @SI, @SS, @PatchedCode);" :
            $@"
                INSERT INTO {tableName} (MethodName, VariableName, SC, SCvg, SI, SS)
                VALUES (@MethodName, @VariableName, @SC, @SCvg, @SI, @SS);";

        using (var command = new SQLiteCommand(insertQuery, connection))
        {
            command.Parameters.AddWithValue("@MethodName", methodName);
            command.Parameters.AddWithValue("@VariableName", variableName);
            command.Parameters.AddWithValue("@SC", SC);
            command.Parameters.AddWithValue("@SCvg", SCvg);
            command.Parameters.AddWithValue("@SI", SI);
            command.Parameters.AddWithValue("@SS", SS);

            if (tableName == "VectorData")
            {
                command.Parameters.AddWithValue("@PatchedCode", patchedCodeContent);
            }

            command.ExecuteNonQuery();
        }
    }

    public void Close()
    {
        connection.Close();
    }
}

public class SliceAnalyzer
{
    public class SliceProfile
    {
        public string File { get; set; }
        public string Function { get; set; }
        public string Variable { get; set; }
        public HashSet<int> Def { get; set; }
        public HashSet<int> Use { get; set; }
        public HashSet<string> Dvars { get; set; }
        public HashSet<string> Ptrs { get; set; }
        public Dictionary<string, int> Cfuncs { get; set; }

        public SliceProfile()
        {
            Def = new HashSet<int>();
            Use = new HashSet<int>();
            Dvars = new HashSet<string>();
            Ptrs = new HashSet<string>();
            Cfuncs = new Dictionary<string, int>();
        }
    }

    public int GetModuleSizeFromFile(string filePath)
    {
        if (!File.Exists(filePath))
        {
            Console.WriteLine("File not found.");
            return 0;
        }

        string[] lines = File.ReadAllLines(filePath);
        return lines.Length;
    }

    public Dictionary<string, List<SliceProfile>> ReadSliceProfilesFromFile(string filePath)
    {
        var sliceProfiles = new Dictionary<string, List<SliceProfile>>();

        if (!File.Exists(filePath))
        {
            Console.WriteLine("File not found.");
            return sliceProfiles;
        }

        var lines = File.ReadAllLines(filePath);
        foreach (var line in lines)
        {
            if (string.IsNullOrWhiteSpace(line))
                continue;

            var parts = SplitIgnoringBrackets(line);

            if (parts.Length < 8)
            {
                Console.WriteLine($"Warning: Incomplete line format - skipping line: {line}");
                continue;
            }

            try
            {
                string variableName = string.IsNullOrWhiteSpace(parts[2]) ? "<unnamed>" : parts[2];

                var sliceProfile = new SliceProfile
                {
                    File = parts[0],
                    Function = parts[1],
                    Variable = variableName,
                    Def = ParseIntSet(parts[3]),
                    Use = ParseIntSet(parts[4]),
                    Dvars = ParseStringSet(parts[5]),
                    Ptrs = ParseStringSet(parts[6]),
                    Cfuncs = ParseCfuncs(parts[7])
                };

                if (!sliceProfiles.ContainsKey(sliceProfile.Function))
                {
                    sliceProfiles[sliceProfile.Function] = new List<SliceProfile>();
                }
                sliceProfiles[sliceProfile.Function].Add(sliceProfile);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error parsing line: {line}");
                Console.WriteLine($"Exception: {ex.Message}");
            }
        }

        return sliceProfiles;
    }

    private string[] SplitIgnoringBrackets(string input)
    {
        var matches = System.Text.RegularExpressions.Regex.Matches(input, @"[^,{]+{[^}]*}|[^,]+");

        if (matches.Count > 8)
        {
            var combinedCfuncs = string.Join(",", matches.Cast<System.Text.RegularExpressions.Match>().Skip(7).Select(m => m.Value));
            return matches.Cast<System.Text.RegularExpressions.Match>().Take(7).Select(m => m.Value)
                          .Append(combinedCfuncs).ToArray();
        }

        return matches.Cast<System.Text.RegularExpressions.Match>().Select(m => m.Value).ToArray();
    }

    private HashSet<int> ParseIntSet(string input)
    {
        var content = input.Substring(input.IndexOf('{') + 1).TrimEnd('}');
        return string.IsNullOrEmpty(content) ? new HashSet<int>() : new HashSet<int>(content.Split(',').Select(int.Parse));
    }

    private HashSet<string> ParseStringSet(string input)
    {
        var content = input.Substring(input.IndexOf('{') + 1).TrimEnd('}');
        return string.IsNullOrEmpty(content) ? new HashSet<string>() : new HashSet<string>(content.Split(','));
    }

    private Dictionary<string, int> ParseCfuncs(string input)
    {
        if (!input.Contains("cfuncs{"))
            return new Dictionary<string, int>();

        var startIndex = input.IndexOf("cfuncs{") + "cfuncs{".Length;
        int openBraces = 1;
        int endIndex = startIndex;

        while (endIndex < input.Length && openBraces > 0)
        {
            if (input[endIndex] == '{')
            {
                openBraces++;
            }
            else if (input[endIndex] == '}')
            {
                openBraces--;
            }
            endIndex++;
        }

        var content = input.Substring(startIndex, endIndex - startIndex - 1);
        var cfuncEntries = string.IsNullOrEmpty(content) ? new List<string>() : content.Split(new[] { "}," }, StringSplitOptions.None).ToList();

        var cfuncs = new Dictionary<string, int>();

        foreach (var entry in cfuncEntries)
        {
            var trimmedEntry = entry.TrimEnd('}');

            var funcParts = trimmedEntry.Split(new[] { '{' }, StringSplitOptions.RemoveEmptyEntries);

            if (funcParts.Length == 2)
            {
                cfuncs[funcParts[0].Trim()] = int.Parse(funcParts[1]);
            }
            else if (funcParts.Length == 1)
            {
                cfuncs[funcParts[0].Trim()] = 1;
            }
        }

        return cfuncs;
    }

    public Tuple<double, int, double, double, double> ComputeSliceMetrics(SliceProfile sliceProfile, int moduleSize)
    {
        double SC = (1 + sliceProfile.Dvars.Count + sliceProfile.Ptrs.Count) / (double)moduleSize;
        int SZ = sliceProfile.Def.Union(sliceProfile.Use).Count();
        double SCvg = SZ / (double)moduleSize;
        double SI = (sliceProfile.Dvars.Count + sliceProfile.Ptrs.Count + sliceProfile.Cfuncs.Count) / (double)moduleSize;
        int Sf = sliceProfile.Def.Min();
        int Sl = (sliceProfile.Use.Count > 0) ? sliceProfile.Use.Max() : 0;
        double SS = Math.Abs(Sl - Sf) / (double)moduleSize;

        return Tuple.Create(SC, SZ, SCvg, SI, SS);
    }

    public Dictionary<string, Tuple<double, int, double, double, double>> GenerateVsVectors(Dictionary<string, List<SliceProfile>> sliceProfiles, int moduleSize)
    {
        var vsVectors = new Dictionary<string, Tuple<double, int, double, double, double>>();

        foreach (var methodEntry in sliceProfiles)
        {
            string method = methodEntry.Key;
            foreach (var sliceProfile in methodEntry.Value)
            {
                var vsVector = ComputeSliceMetrics(sliceProfile, moduleSize);
                vsVectors[method + "|" + sliceProfile.Variable] = vsVector;
            }
        }

        return vsVectors;
    }

    public static void Main(string[] args)
    {
        var analyzer = new SliceAnalyzer();
        var databaseManager = new DatabaseManager();

        Console.WriteLine("Is this testing data? (yes/no)");
        string isTestingInput = Console.ReadLine()?.Trim().ToLower();
        bool isTesting = isTestingInput == "yes";

        // Step 1: Take file input for module size
        Console.WriteLine("Please provide the path to the file with code:");
        string codeFilePath = Console.ReadLine();
        int moduleSize = analyzer.GetModuleSizeFromFile(codeFilePath);

        if (moduleSize == 0)
        {
            Console.WriteLine("Invalid code file. Exiting...");
            return;
        }

        Console.WriteLine($"The module size (number of lines including whitespaces) is: {moduleSize}");

        // Step 2: Take file input for patched version only if not testing
        string patchedCodeContent = null;
        if (!isTesting)
        {
            Console.WriteLine("Please provide the path to the patched version file:");
            string patchedFilePath = Console.ReadLine();
            patchedCodeContent = File.ReadAllText(patchedFilePath);
        }

        // Step 3: Take file input for slice profiles
        Console.WriteLine("Please provide the path to the file with slice profiles:");
        string sliceProfilesFilePath = Console.ReadLine();
        var sliceProfiles = analyzer.ReadSliceProfilesFromFile(sliceProfilesFilePath);

        if (sliceProfiles.Count == 0)
        {
            Console.WriteLine("No valid slice profiles found. Exiting...");
            return;
        }

        // Step 4: Process and store vectors for all profiles combined
        databaseManager.InitializeDatabase("vectors.db");
        databaseManager.CreateTables();

        string tableName = isTesting ? "TestVectorData" : "VectorData";

        foreach (var methodEntry in sliceProfiles)
        {
            foreach (var sliceProfile in methodEntry.Value)
            {
                var vsVector = analyzer.ComputeSliceMetrics(sliceProfile, moduleSize);

                databaseManager.InsertVectorData(
                    tableName,
                    methodEntry.Key,
                    sliceProfile.Variable,
                    vsVector.Item1,
                    vsVector.Item3,
                    vsVector.Item4,
                    vsVector.Item5,
                    patchedCodeContent
                );
            }
        }

        databaseManager.Close();
        Console.WriteLine($"Data has been inserted into {tableName}.");
    }
}
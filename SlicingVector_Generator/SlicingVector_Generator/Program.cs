using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Data.SQLite;

public class DatabaseManager
{
	private SQLiteConnection connection;

	public void InitializeDatabase(string databasePath)
	{
		connection = new SQLiteConnection($"Data Source={databasePath};Version=3;");
		connection.Open();
	}

	public void CreateTables()
	{
		string createTableQuery = @"
            CREATE TABLE IF NOT EXISTS VectorData (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                MethodName TEXT,
                VariableName TEXT,
                SC REAL,
                SZ INTEGER,
                SCvg REAL,
                SI INTEGER,
                SS REAL
            );";

		using (var command = new SQLiteCommand(createTableQuery, connection))
		{
			command.ExecuteNonQuery();
		}
	}

	public void InsertVectorData(string methodName, string variableName, double SC, int SZ, double SCvg, double SI, double SS)
	{
		Console.WriteLine($"Inserting: Method={methodName}, Variable={variableName}, SC={SC}, SZ={SZ}, SCvg={SCvg}, SI={SI}, SS={SS}");

		string insertQuery = @"
            INSERT INTO VectorData (MethodName, VariableName, SC, SZ, SCvg, SI, SS)
            VALUES (@MethodName, @VariableName, @SC, @SZ, @SCvg, @SI, @SS);";

		using (var command = new SQLiteCommand(insertQuery, connection))
		{
			command.Parameters.AddWithValue("@MethodName", methodName);
			command.Parameters.AddWithValue("@VariableName", variableName);
			command.Parameters.AddWithValue("@SC", SC);
			command.Parameters.AddWithValue("@SZ", SZ);                       //only for debugging, can remove it later
			command.Parameters.AddWithValue("@SCvg", SCvg);
			command.Parameters.AddWithValue("@SI", SI);
			command.Parameters.AddWithValue("@SS", SS);

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

	// Method to calculate module size from a file
	public int GetModuleSizeFromFile(string filePath)
	{
		if (!File.Exists(filePath))
		{
			Console.WriteLine("File not found.");
			return 0;
		}

		string[] lines = File.ReadAllLines(filePath);  // Read all lines, including empty ones
		return lines.Length;  // Return the number of lines, including whitespaces
	}

	// Method to read slice profiles from a file (parses a complete src slice)
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

			// Regex pattern to capture everything inside {}, treating it as a single part
			var parts = SplitIgnoringBrackets(line);

			var sliceProfile = new SliceProfile
			{
				File = parts[0],
				Function = parts[1],
				Variable = parts[2],
				Def = ParseIntSet(parts[3]),   // def{...}
				Use = ParseIntSet(parts[4]),   // use{...}
				Dvars = ParseStringSet(parts[5]),  // dvars{...}
				Ptrs = ParseStringSet(parts[6]),   // ptrs{...}
				Cfuncs = ParseCfuncs(parts[7])     // cfuncs{...}
			};

			if (!sliceProfiles.ContainsKey(sliceProfile.Function))
			{
				sliceProfiles[sliceProfile.Function] = new List<SliceProfile>();
			}
			sliceProfiles[sliceProfile.Function].Add(sliceProfile);
		}

		return sliceProfiles;
	}

	// Method to split the line, considering content inside brackets as a single part
	private string[] SplitIgnoringBrackets(string input)
	{
		// This regex will capture everything inside {}, treating it as a single part, ignoring internal commas
		var matches = System.Text.RegularExpressions.Regex.Matches(input, @"[^,{]+{[^}]*}|[^,]+");

		// Now check if the result contains more than 8 parts (caused by commas inside cfuncs)
		// Merge any extra parts into the correct cfuncs part
		if (matches.Count > 8)
		{
			// Combine everything beyond the 7th part into one string
			var combinedCfuncs = string.Join(",", matches.Cast<System.Text.RegularExpressions.Match>().Skip(7).Select(m => m.Value));

			// Take the first 7 parts, and append the combined cfuncs as the 8th part
			return matches.Cast<System.Text.RegularExpressions.Match>().Take(7).Select(m => m.Value)
						  .Append(combinedCfuncs).ToArray();
		}

		return matches.Cast<System.Text.RegularExpressions.Match>().Select(m => m.Value).ToArray();
	}


	// Helper method to parse a set of integers from the "def{...}" and "use{...}" parts
	private HashSet<int> ParseIntSet(string input)
	{
		var content = input.Substring(input.IndexOf('{') + 1).TrimEnd('}');
		return string.IsNullOrEmpty(content) ? new HashSet<int>() : new HashSet<int>(content.Split(',').Select(int.Parse));
	}

	// Helper method to parse a set of strings from the "dvars{...}", "ptrs{...}" parts
	private HashSet<string> ParseStringSet(string input)
	{
		var content = input.Substring(input.IndexOf('{') + 1).TrimEnd('}');
		return string.IsNullOrEmpty(content) ? new HashSet<string>() : new HashSet<string>(content.Split(','));
	}

	// Helper method to parse a dictionary of cfuncs from the "cfuncs{...}" part
	private Dictionary<string, int> ParseCfuncs(string input)
	{
		// Ensure we're dealing with a "cfuncs{}" section
		if (!input.Contains("cfuncs{"))
			return new Dictionary<string, int>();

		// Find the start of 'cfuncs{'
		var startIndex = input.IndexOf("cfuncs{") + "cfuncs{".Length;

		// Find the matching closing brace for cfuncs using a balance counting approach
		int openBraces = 1; // We already have the opening 'cfuncs{'
		int endIndex = startIndex;

		// Go through the input and count the braces to find the matching closing brace
		while (endIndex < input.Length && openBraces > 0)
		{
			if (input[endIndex] == '{')
			{
				openBraces++; // We found another opening brace
			}
			else if (input[endIndex] == '}')
			{
				openBraces--; // We found a closing brace
			}
			endIndex++;
		}

		// Now we have the correct end index where the 'cfuncs' block ends
		// Extract the content between 'cfuncs{' and the matched closing '}'
		var content = input.Substring(startIndex, endIndex - startIndex - 1); // -1 to exclude the final '}'

		// Split the content by "}," to separate function entries correctly
		var cfuncEntries = string.IsNullOrEmpty(content) ? new List<string>() : content.Split(new[] { "}," }, StringSplitOptions.None).ToList();

		var cfuncs = new Dictionary<string, int>();

		// Iterate over each cfunc entry
		foreach (var entry in cfuncEntries)
		{
			// Trim the trailing '}' from each entry (if any)
			var trimmedEntry = entry.TrimEnd('}');

			// Split by "{" to separate function name and count
			var funcParts = trimmedEntry.Split(new[] { '{' }, StringSplitOptions.RemoveEmptyEntries);

			if (funcParts.Length == 2)
			{
				// If both function name and count are present
				cfuncs[funcParts[0].Trim()] = int.Parse(funcParts[1]);
			}
			else if (funcParts.Length == 1)
			{
				// If only the function name is present, assign a default count of 1
				cfuncs[funcParts[0].Trim()] = 1;
			}
		}

		return cfuncs;
	}


	public Tuple<double, int, double, double, double> ComputeSliceMetrics(SliceProfile sliceProfile, int moduleSize)
	{
		// Compute slice metrics based on the formula
		double SC = (1 + sliceProfile.Dvars.Count + sliceProfile.Ptrs.Count) / (double)moduleSize;
		int SZ = sliceProfile.Def.Union(sliceProfile.Use).Count();  // Union of Def and Use
		double SCvg = SZ / (double)moduleSize;
		double SI = (sliceProfile.Dvars.Count + sliceProfile.Ptrs.Count + sliceProfile.Cfuncs.Count) / (double)moduleSize;
		int Sf = sliceProfile.Def.Min();
		int Sl = (sliceProfile.Use.Count > 0) ? sliceProfile.Use.Max() : 0;  //if var is not used
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

		// Step 2: Take file input for slice profiles
		Console.WriteLine("Please provide the path to the file with slice profiles:");
		string sliceProfilesFilePath = Console.ReadLine();
		var sliceProfiles = analyzer.ReadSliceProfilesFromFile(sliceProfilesFilePath);

		if (sliceProfiles.Count == 0)
		{
			Console.WriteLine("No valid slice profiles found. Exiting...");
			return;
		}

		// Step 3: Process and store vectors for all profiles combined
		databaseManager.InitializeDatabase("vectors.db");
		databaseManager.CreateTables();

		foreach (var methodEntry in sliceProfiles)
		{
			// Iterate over each profile (each variable) in the function
			foreach (var sliceProfile in methodEntry.Value)
			{
				// Compute metrics for each individual profile
				var vsVector = analyzer.ComputeSliceMetrics(sliceProfile, moduleSize);

				// Insert combined result into the database
				databaseManager.InsertVectorData(
				methodEntry.Key,        // Method name
				sliceProfile.Variable,             // Store variable name 
				vsVector.Item1,         // SC
				vsVector.Item2,         // SZ
				vsVector.Item3,         // SCvg
				vsVector.Item4,         // SI
				vsVector.Item5          // SS
			);
			}
		}
		databaseManager.Close();
	}
}

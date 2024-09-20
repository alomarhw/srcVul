//using System;
//using System.Collections.Generic;
//using System.Linq;

//class Program
//{
//    class SliceInfo
//    {
//        public string VariableName { get; set; }
//        public List<int> DefinitionLines { get; set; } = new List<int>();
//        public List<int> UsageLines { get; set; } = new List<int>();
//        public HashSet<string> DependentVariables { get; set; } = new HashSet<string>();
//        public HashSet<string> Pointers { get; set; } = new HashSet<string>();
//        public Dictionary<string, int> CalledFunctions { get; set; } = new Dictionary<string, int>();
//        public int ModuleSizeInLoC { get; set; } = 1000; // Example, adjust according to actual size

//        public double SliceCount => 1; // Assuming one slice per variable for simplicity
//        public double SliceSize => DefinitionLines.Count + UsageLines.Count;
//        public double SliceCoverage => SliceSize / ModuleSizeInLoC;
//        public double SliceIdentifier => (DependentVariables.Count + Pointers.Count + CalledFunctions.Count) / (double)ModuleSizeInLoC;
//        public double SliceSpatial => UsageLines.Any() && DefinitionLines.Any() ? (UsageLines.Max() - DefinitionLines.Min()) / (double)ModuleSizeInLoC : 0;
//    }

//    static void Main(string[] args)
//    {
//        List<SliceInfo> slices = new List<SliceInfo>
//        {
//            new SliceInfo
//            {
//                VariableName = "entry",
//                DefinitionLines = new List<int> {4, 5, 8, 13, 14, 18},
//                UsageLines = new List<int> {5, 6, 9, 10, 15, 16, 17, 20, 21},
//                Pointers = new HashSet<string> {"parent"},
//                CalledFunctions = new Dictionary<string, int> {{"list_add_tail", 1}, {"INIT_LIST_HEAD", 1}, {"mutex_init", 1}, {"kfree", 1}, {"sizeof", 1}}
//            },
//            new SliceInfo
//            {
//                VariableName = "parent",
//                DefinitionLines = new List<int> {2},
//                UsageLines = new List<int> {18, 19, 20},
//                DependentVariables = new HashSet<string> {"entry"},
//                CalledFunctions = new Dictionary<string, int> {{"list_add_tail", 2}}
//            },
//            new SliceInfo
//            {
//                VariableName = "name",
//                DefinitionLines = new List<int> {2},
//                UsageLines = new List<int> {8, 9},
//                CalledFunctions = new Dictionary<string, int> {{"kstrdup", 1}}
//            }
//        };

//        // Generate Slicing Vectors
//        foreach (var slice in slices)
//        {
//            var slicingVector = new[] { slice.SliceCount, slice.SliceCoverage, slice.SliceIdentifier, slice.SliceSpatial };
//            Console.WriteLine($"Variable: {slice.VariableName}, Slicing Vector: ⟨{string.Join(", ", slicingVector.Select(v => v.ToString("F2")))}⟩");
//        }
//    }
//}

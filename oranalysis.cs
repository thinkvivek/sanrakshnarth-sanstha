using System;
using System.Collections.Generic;
using System.Data;
using Oracle.ManagedDataAccess.Client;
using System.Text.RegularExpressions;
using System.Linq;
using System.Text;

namespace UltimateProcAnalyzer
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Enter stored procedure name:");
            string procName = Console.ReadLine();

            string connectionString = "User Id=your_user;Password=your_password;Data Source=your_db;";

            try
            {
                string procCode = GetProcedureCode(procName, connectionString);
                var analysis = AnalyzeProcedure(procCode);
                string story = GenerateCompleteStory(analysis);
                
                Console.WriteLine("\nCOMPREHENSIVE ANALYSIS REPORT:");
                Console.WriteLine(story);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
            }
        }

        static string GetProcedureCode(string procName, string connectionString)
        {
            using (OracleConnection conn = new OracleConnection(connectionString))
            {
                conn.Open();
                string query = @"SELECT text FROM ALL_SOURCE 
                               WHERE name = :procName 
                               AND type = 'PROCEDURE' 
                               ORDER BY line";

                using (OracleCommand cmd = new OracleCommand(query, conn))
                {
                    cmd.Parameters.Add("procName", OracleDbType.Varchar2).Value = procName;
                    
                    using (OracleDataReader reader = cmd.ExecuteReader())
                    {
                        StringBuilder codeBuilder = new StringBuilder();
                        while (reader.Read())
                        {
                            codeBuilder.Append(reader["TEXT"].ToString());
                        }
                        return codeBuilder.ToString();
                    }
                }
            }
        }

        static AnalysisResult AnalyzeProcedure(string procCode)
        {
            var result = new AnalysisResult();
            
            // Basic Operations Analysis
            AnalyzeCrudOperations(procCode, result);
            
            // Advanced SQL Features
            AnalyzeQueryStructure(procCode, result);
            
            // Procedural Elements
            AnalyzeProceduralLogic(procCode, result);
            
            // Oracle Specific Features
            AnalyzeOracleSpecifics(procCode, result);

            return result;
        }

        static void AnalyzeCrudOperations(string code, AnalysisResult result)
        {
            var patterns = new Dictionary<string, string>
            {
                { "INSERT", @"INSERT\s+(INTO\s+)?([\w\.]+)" },
                { "UPDATE", @"UPDATE\s+([\w\.]+)" },
                { "DELETE", @"DELETE\s+(FROM\s+)?([\w\.]+)" },
                { "SELECT", @"SELECT\s+.+\s+INTO\s+.+\s+FROM\s+([\w\.]+)" }
            };

            foreach (var pattern in patterns)
            {
                var matches = Regex.Matches(code, pattern.Value, 
                    RegexOptions.IgnoreCase | RegexOptions.Multiline);
                
                foreach (Match match in matches)
                {
                    string table = match.Groups[match.Groups.Count - 1].Value.Trim();
                    if (!string.IsNullOrEmpty(table))
                    {
                        result.RecordOperation(pattern.Key, table);
                    }
                }
            }
        }

        static void AnalyzeQueryStructure(string code, AnalysisResult result)
        {
            // CTEs
            var cteMatches = Regex.Matches(code, @"WITH\s+([\w_]+)\s+AS\s*\(([^\)]+)\)", 
                RegexOptions.IgnoreCase | RegexOptions.Singleline);
            foreach (Match match in cteMatches)
            {
                result.CTEs.Add(new CteInfo {
                    Name = match.Groups[1].Value,
                    Definition = match.Groups[2].Value
                });
            }

            // Joins
            var joins = Regex.Matches(code, @"(JOIN)\s+([\w\.]+)", RegexOptions.IgnoreCase);
            foreach (Match match in joins)
            {
                result.Joins.Add(match.Groups[2].Value.Trim());
            }

            // Window Functions
            var windowFuncs = Regex.Matches(code, @"\b(ROW_NUMBER|RANK|DENSE_RANK|NTILE|LEAD|LAD)\s*\([^\)]*\)\s+OVER\s*\([^\)]*\)", 
                RegexOptions.IgnoreCase);
            result.WindowFunctions.AddRange(windowFuncs.Cast<Match>().Select(m => m.Value));

            // Set Operations
            var setOps = Regex.Matches(code, @"\b(UNION|INTERSECT|MINUS)(\s+ALL)?\b", RegexOptions.IgnoreCase);
            foreach (Match match in setOps)
            {
                result.SetOperations.Add(new SetOperation {
                    Type = match.Groups[1].Value.ToUpper(),
                    AllModifier = match.Groups[2].Success
                });
            }
        }

        static void AnalyzeProceduralLogic(string code, AnalysisResult result)
        {
            // Cursors
            var cursors = Regex.Matches(code, @"\bCURSOR\s+(\w+)\s+IS\s+SELECT", RegexOptions.IgnoreCase);
            foreach (Match match in cursors)
            {
                result.Cursors.Add(new CursorInfo { Name = match.Groups[1].Value });
            }

            // Loops
            var loops = Regex.Matches(code, @"\b(LOOP|FOR\s+.*?\s+IN|WHILE)\b", RegexOptions.IgnoreCase);
            result.LoopCount = loops.Count;

            // CASE Statements
            result.CaseStatements = Regex.Matches(code, @"\bCASE\b", RegexOptions.IgnoreCase).Count;
        }

        static void AnalyzeOracleSpecifics(string code, AnalysisResult result)
        {
            // Oracle Functions
            var oraFuncs = Regex.Matches(code, @"\b(NVL|DECODE|TO_DATE|TO_CHAR|LISTAGG)\s*\(", RegexOptions.IgnoreCase);
            result.OracleFunctions.AddRange(oraFuncs.Cast<Match>().Select(m => m.Groups[1].Value.ToUpper()));

            // Bulk Operations
            result.HasBulkOperations = Regex.IsMatch(code, @"\bBULK\s+COLLECT\b", RegexOptions.IgnoreCase);
        }

        static string GenerateCompleteStory(AnalysisResult analysis)
        {
            var story = new StringBuilder();
            
            story.AppendLine("DATA PROCESSING NARRATIVE");
            story.AppendLine("=========================");
            
            story.AppendLine("\n1. Data Sources & Transformations:");
            story.AppendLine($"- Works with {analysis.Tables.Count} main tables: {FormatList(analysis.Tables)}");
            if (analysis.CTEs.Count > 0)
            {
                story.AppendLine("- Creates temporary datasets using:");
                foreach (var cte in analysis.CTEs)
                {
                    story.AppendLine($"  * {cte.Name} based on {FormatList(cte.BaseTables)}");
                }
            }

            story.AppendLine("\n2. Data Manipulation:");
            story.AppendLine("- Performs these operations:");
            foreach (var op in analysis.Operations)
            {
                story.AppendLine($"  * {op.Key} on {FormatList(op.Value)}");
            }

            story.AppendLine("\n3. Advanced Processing:");
            if (analysis.WindowFunctions.Count > 0)
            {
                story.AppendLine("- Uses analytical functions for:");
                story.AppendLine($"  {FormatList(analysis.WindowFunctions.Distinct())}");
            }
            if (analysis.SetOperations.Count > 0)
            {
                story.AppendLine("- Combines data sets using:");
                story.AppendLine($"  {FormatList(analysis.SetOperations.Select(so => so.ToString()))}");
            }

            story.AppendLine("\n4. Business Logic Implementation:");
            if (analysis.Cursors.Count > 0)
            {
                story.AppendLine("- Processes data sequentially using:");
                story.AppendLine($"  {FormatList(analysis.Cursors.Select(c => c.Name))}");
            }
            if (analysis.LoopCount > 0)
            {
                story.AppendLine($"- Contains {analysis.LoopCount} iterative processing blocks");
            }
            if (analysis.CaseStatements > 0)
            {
                story.AppendLine($"- Implements {analysis.CaseStatements} conditional decision points");
            }

            story.AppendLine("\n5. Oracle-Specific Features:");
            story.AppendLine($"- Uses special functions: {FormatList(analysis.OracleFunctions.Distinct())}");
            story.AppendLine(analysis.HasBulkOperations ? 
                "- Employs bulk data operations for efficiency" : 
                "- Uses standard row-by-row processing");

            return story.ToString();
        }

        static string FormatList(IEnumerable<string> items)
        {
            var list = items.ToList();
            if (list.Count == 0) return "none";
            if (list.Count == 1) return list[0];
            return string.Join(", ", list.Take(list.Count - 1)) + " and " + list.Last();
        }
    }

    class AnalysisResult
    {
        public HashSet<string> Tables { get; } = new HashSet<string>();
        public Dictionary<string, List<string>> Operations { get; } = new Dictionary<string, List<string>>();
        public List<CteInfo> CTEs { get; } = new List<CteInfo>();
        public List<string> Joins { get; } = new List<string>();
        public List<string> WindowFunctions { get; } = new List<string>();
        public List<SetOperation> SetOperations { get; } = new List<SetOperation>();
        public List<CursorInfo> Cursors { get; } = new List<CursorInfo>();
        public int LoopCount { get; set; }
        public int CaseStatements { get; set; }
        public List<string> OracleFunctions { get; } = new List<string>();
        public bool HasBulkOperations { get; set; }

        public void RecordOperation(string operation, string table)
        {
            if (!Operations.ContainsKey(operation))
                Operations[operation] = new List<string>();
            
            Operations[operation].Add(table);
            Tables.Add(table);
        }
    }

    class CteInfo
    {
        public string Name { get; set; }
        public string Definition { get; set; }
        public List<string> BaseTables => Definition.Split(new[] {' '}, StringSplitOptions.RemoveEmptyEntries)
            .Where(word => word.Contains("."))
            .Select(table => table.Split('.')[1])
            .ToList();
    }

    class SetOperation
    {
        public string Type { get; set; }
        public bool AllModifier { get; set; }

        public override string ToString() => $"{Type}{(AllModifier ? " ALL" : "")}";
    }

    class CursorInfo
    {
        public string Name { get; set; }
    }
}

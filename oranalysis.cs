using System;
using System.Collections.Generic;
using System.Data;
using Oracle.ManagedDataAccess.Client;
using System.Text.RegularExpressions;
using System.Linq;
using System.Text;

namespace AdvancedProcAnalyzer
{
    class ProcStoryteller
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Enter stored procedure name:");
            string procName = Console.ReadLine();

            string connectionString = "User Id=your_user;Password=your_password;Data Source=your_db;";

            try
            {
                string procCode = GetProcedureCode(procName, connectionString);
                string story = CreateDataStory(procCode);
                
                Console.WriteLine("\nData Flow Story:");
                Console.WriteLine(story);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
            }
        }

        static string GetProcedureCode(string procName, string connectionString)
        {
            // Same implementation as previous example
            // ...
        }

        static string CreateDataStory(string procCode)
        {
            var analysis = new SqlAnalysisResult();
            
            AnalyzeStructure(procCode, analysis);
            DetectComplexFeatures(procCode, analysis);
            BuildRelationships(analysis);

            return GenerateNarrative(analysis);
        }

        static void AnalyzeStructure(string code, SqlAnalysisResult result)
        {
            // Detect CTEs
            var cteMatches = Regex.Matches(code, @"WITH\s+([\w_]+)\s+AS\s*\(([^\)]+)\)", 
                RegexOptions.IgnoreCase | RegexOptions.Singleline);
            
            foreach (Match match in cteMatches)
            {
                result.CTEs.Add(new CommonTableExpression
                {
                    Name = match.Groups[1].Value,
                    Definition = match.Groups[2].Value
                });
            }

            // Detect main query components
            var fromClauses = Regex.Matches(code, @"(FROM|JOIN)\s+([\w\.]+)(\s+AS\s+[\w_]+)?", 
                RegexOptions.IgnoreCase);
            
            foreach (Match match in fromClauses)
            {
                result.TablesUsed.Add(match.Groups[2].Value.Trim());
            }

            // Detect window functions
            var windowFunctions = Regex.Matches(code, @"\b(ROW_NUMBER|RANK|DENSE_RANK|NTILE|LEAD|LAG)\s*\(\s*[^\)]*\s*\)\s+OVER\s*\([^\)]*\)", 
                RegexOptions.IgnoreCase);
            
            foreach (Match match in windowFunctions)
            {
                result.WindowFunctions.Add(match.Value);
            }

            // Detect complex joins
            var joins = Regex.Matches(code, @"(INNER\s+JOIN|LEFT\s+OUTER\s+JOIN|RIGHT\s+OUTER\s+JOIN|FULL\s+OUTER\s+JOIN|CROSS\s+JOIN)\s+([\w\.]+)", 
                RegexOptions.IgnoreCase);
            
            foreach (Match match in joins)
            {
                result.Joins.Add(new SqlJoin
                {
                    Type = match.Groups[1].Value.Replace(" OUTER", "").Trim(),
                    Table = match.Groups[2].Value
                });
            }
        }

        static void DetectComplexFeatures(string code, SqlAnalysisResult result)
        {
            // Detect aggregate functions
            var aggregates = Regex.Matches(code, @"\b(SUM|AVG|COUNT|MIN|MAX)\s*\(\s*([^\)]+)\s*\)", 
                RegexOptions.IgnoreCase);
            
            foreach (Match match in aggregates)
            {
                result.Aggregates.Add(new AggregateFunction
                {
                    Function = match.Groups[1].Value.ToUpper(),
                    Column = match.Groups[2].Value.Trim()
                });
            }

            // Detect subqueries
            var subqueries = Regex.Matches(code, @"\(\s*SELECT\s+[^\)]+\)", 
                RegexOptions.IgnoreCase | RegexOptions.Singleline);
            
            result.HasSubqueries = subqueries.Count > 0;

            // Detect transaction control
            result.HasTransactions = Regex.IsMatch(code, @"\b(COMMIT|ROLLBACK)\b", 
                RegexOptions.IgnoreCase);
        }

        static void BuildRelationships(SqlAnalysisResult result)
        {
            // Build relationships between CTEs and base tables
            foreach (var cte in result.CTEs)
            {
                foreach (var table in result.TablesUsed)
                {
                    if (cte.Definition.Contains(table))
                    {
                        cte.BaseTables.Add(table);
                    }
                }
            }
        }

        static string GenerateNarrative(SqlAnalysisResult analysis)
        {
            var story = new StringBuilder();
            
            story.AppendLine("Data Processing Story:");
            story.AppendLine("----------------------");

            if (analysis.CTEs.Any())
            {
                story.AppendLine("The process begins by setting up temporary datasets:");
                foreach (var cte in analysis.CTEs)
                {
                    story.AppendLine($"- '{cte.Name}' created using {ListFormatter.Format(cte.BaseTables)}");
                }
                story.AppendLine();
            }

            story.AppendLine("Main operations include:");
            story.AppendLine($"- Working with {ListFormatter.Format(analysis.TablesUsed.Distinct())}");
            
            if (analysis.Joins.Any())
            {
                story.AppendLine("- Combining data through:");
                foreach (var join in analysis.Joins)
                {
                    story.AppendLine($"  * {join.Type} with {join.Table}");
                }
            }

            if (analysis.Aggregates.Any())
            {
                story.AppendLine("\nCalculations performed:");
                foreach (var agg in analysis.Aggregates)
                {
                    story.AppendLine($"- {agg.Function} of {agg.Column}");
                }
            }

            if (analysis.WindowFunctions.Any())
            {
                story.AppendLine("\nAdvanced analysis includes:");
                story.AppendLine("- Ranking and window-based calculations using:");
                foreach (var wf in analysis.WindowFunctions.Distinct())
                {
                    story.AppendLine($"  * {wf.Split('(')[0].Trim()} operations");
                }
            }

            story.AppendLine("\nFinal Steps:");
            story.AppendLine(analysis.HasTransactions ? 
                "- Uses transactions to ensure data consistency" : 
                "- Runs in auto-commit mode");

            return story.ToString();
        }
    }

    // Helper classes
    class SqlAnalysisResult
    {
        public List<string> TablesUsed { get; } = new List<string>();
        public List<CommonTableExpression> CTEs { get; } = new List<CommonTableExpression>();
        public List<SqlJoin> Joins { get; } = new List<SqlJoin>();
        public List<string> WindowFunctions { get; } = new List<string>();
        public List<AggregateFunction> Aggregates { get; } = new List<AggregateFunction>();
        public bool HasSubqueries { get; set; }
        public bool HasTransactions { get; set; }
    }

    class CommonTableExpression
    {
        public string Name { get; set; }
        public string Definition { get; set; }
        public List<string> BaseTables { get; } = new List<string>();
    }

    class SqlJoin
    {
        public string Type { get; set; }
        public string Table { get; set; }
    }

    class AggregateFunction
    {
        public string Function { get; set; }
        public string Column { get; set; }
    }

    static class ListFormatter
    {
        public static string Format(IEnumerable<string> items)
        {
            var list = items.ToList();
            if (list.Count == 0) return "";
            if (list.Count == 1) return list[0];
            
            return string.Join(", ", list.Take(list.Count - 1)) + 
                   " and " + list.Last();
        }
    }
}

using System;
using System.Text;
using System.Text.RegularExpressions;
using System.Windows.Forms;

namespace GenericSqlAnalyzer
{
    public partial class MainForm : Form
    {
        public MainForm()
        {
            InitializeComponent();
        }

        // Triggered when the Analyze button is clicked.
        private void btnAnalyze_Click(object sender, EventArgs e)
        {
            string sqlInput = txtInput.Text;
            if (string.IsNullOrWhiteSpace(sqlInput))
            {
                MessageBox.Show("Please enter a SQL stored procedure or query.", "Input Required", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            string analysisReport = GenerateGenericDetailedAnalysisReport(sqlInput);
            txtOutput.Text = analysisReport;
        }

        /// <summary>
        /// Generates a detailed analysis report for any SQL stored procedure or query.
        /// </summary>
        /// <param name="sql">The SQL text input.</param>
        /// <returns>A detailed analysis report string.</returns>
        private string GenerateGenericDetailedAnalysisReport(string sql)
        {
            StringBuilder report = new StringBuilder();

            // I. Overview Section
            report.AppendLine("### Detailed SQL Analysis Report");
            report.AppendLine();
            report.AppendLine("#### I. Overview of the SQL Input");
            report.AppendLine();
            report.AppendLine("- **Purpose:** This tool analyzes the SQL code and attempts to describe its overall structure and functionality.");
            report.AppendLine("- **SQL Type:** " + IdentifySqlType(sql));
            report.AppendLine("- **Final Outcome:** The analysis highlights key components such as CTEs, main queries, tables used, joins, grouping, aggregations, and any procedural constructs.");
            report.AppendLine();

            // II. Breakdown by Components
            report.AppendLine("#### II. Detailed Breakdown");
            report.AppendLine();

            // A. Detect Common Table Expressions (CTEs)
            var cteReports = AnalyzeCTEs(sql);
            if (!string.IsNullOrEmpty(cteReports))
            {
                report.AppendLine(cteReports);
            }
            else
            {
                report.AppendLine("**CTE Analysis:** No common table expressions (CTEs) were detected.");
            }
            report.AppendLine();

            // B. Main SELECT / DML / Procedure Body Analysis
            report.AppendLine("**Main Query / Procedure Analysis:**");
            report.AppendLine();

            // Extract SELECT block (if present) for further analysis
            string selectBlock = ExtractSelectBlock(sql);
            if (!string.IsNullOrEmpty(selectBlock))
            {
                report.AppendLine("**Main SELECT Statement:**");
                report.AppendLine("```sql");
                report.AppendLine(selectBlock);
                report.AppendLine("```");
                report.AppendLine();
                report.AppendLine(AnalyzeSelectBlock(selectBlock));
            }
            else
            {
                // If not a SELECT, check for other DML (INSERT, UPDATE, DELETE) or procedure structure.
                report.AppendLine(AnalyzeNonSelect(sql));
            }
            report.AppendLine();

            // C. Analyze Procedural or Loop Constructs (if any)
            string proceduralAnalysis = AnalyzeProceduralElements(sql);
            if (!string.IsNullOrEmpty(proceduralAnalysis))
            {
                report.AppendLine("**Procedural / Control Flow Analysis:**");
                report.AppendLine(proceduralAnalysis);
            }
            else
            {
                report.AppendLine("**Procedural / Control Flow Analysis:** No procedural constructs (loops, cursors, etc.) were detected.");
            }
            report.AppendLine();

            // III. Summary of Detected SQL Components
            report.AppendLine("#### III. Summary of Detected Components");
            report.AppendLine();
            report.AppendLine(GenerateComponentSummary(sql));
            report.AppendLine();

            // IV. Example / Hypothetical Output (if applicable)
            report.AppendLine("#### IV. Example / Hypothetical Output");
            report.AppendLine();
            report.AppendLine("If sample data were provided, the tool could simulate expected results based on the analysis above. This section is a placeholder for sample output demonstration.");
            report.AppendLine();

            // V. Conclusion
            report.AppendLine("#### V. Conclusion");
            report.AppendLine();
            report.AppendLine("This SQL analysis report summarizes the structure, purpose, and key components of the provided SQL code. It is designed to help understand the flow and output of the SQL stored procedure or query.");
            report.AppendLine();

            return report.ToString();
        }

        /// <summary>
        /// Identifies the type of SQL (SELECT, INSERT, UPDATE, DELETE, or a Stored Procedure).
        /// </summary>
        private string IdentifySqlType(string sql)
        {
            string upperSql = sql.ToUpper();
            if (upperSql.Contains("CREATE PROCEDURE") || upperSql.Contains("CREATE PROC") || upperSql.Contains("ALTER PROCEDURE"))
                return "Stored Procedure";
            if (upperSql.Contains("SELECT"))
                return "SELECT Query";
            if (upperSql.Contains("INSERT"))
                return "INSERT Query";
            if (upperSql.Contains("UPDATE"))
                return "UPDATE Query";
            if (upperSql.Contains("DELETE"))
                return "DELETE Query";
            return "Unknown Type";
        }

        /// <summary>
        /// Analyzes and extracts CTEs from the SQL.
        /// </summary>
        private string AnalyzeCTEs(string sql)
        {
            StringBuilder cteReport = new StringBuilder();
            // Look for a WITH clause at the start
            Regex withRegex = new Regex(@"WITH\s+(?<ctes>.*?)(?=SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|$)", RegexOptions.Singleline | RegexOptions.IgnoreCase);
            Match withMatch = withRegex.Match(sql);
            if (withMatch.Success)
            {
                string cteBlock = withMatch.Groups["ctes"].Value.Trim();
                // Split individual CTEs if there are commas at the top level.
                // (A simple split by "),", then reappend a closing parenthesis.)
                string[] cteParts = Regex.Split(cteBlock, @"\),", RegexOptions.IgnoreCase);
                int cteIndex = 1;
                foreach (string part in cteParts)
                {
                    string trimmedPart = part.Trim();
                    if (!string.IsNullOrEmpty(trimmedPart))
                    {
                        // Append missing closing parenthesis if it was removed during splitting.
                        if (!trimmedPart.EndsWith(")"))
                        {
                            trimmedPart += ")";
                        }
                        cteReport.AppendLine($"**CTE #{cteIndex}:**");
                        cteReport.AppendLine("```sql");
                        cteReport.AppendLine(trimmedPart);
                        cteReport.AppendLine("```");
                        cteReport.AppendLine("- This CTE is used to pre-process data. Its inner logic may involve joins, filtering, or aggregation.");
                        cteReport.AppendLine();
                        cteIndex++;
                    }
                }
            }
            return cteReport.ToString();
        }

        /// <summary>
        /// Extracts the main SELECT block from the SQL (if present).
        /// </summary>
        private string ExtractSelectBlock(string sql)
        {
            Regex selectRegex = new Regex(@"SELECT\s+.*", RegexOptions.Singleline | RegexOptions.IgnoreCase);
            Match selectMatch = selectRegex.Match(sql);
            if (selectMatch.Success)
            {
                return selectMatch.Value.Trim();
            }
            return string.Empty;
        }

        /// <summary>
        /// Analyzes the main SELECT block to extract information about tables, joins, aggregates, etc.
        /// </summary>
        private string AnalyzeSelectBlock(string selectBlock)
        {
            StringBuilder analysis = new StringBuilder();

            // Detect tables from FROM clauses
            analysis.AppendLine("**Tables / Sources Detected:**");
            Regex fromRegex = new Regex(@"\bFROM\s+([a-zA-Z0-9_\[\]\.]+)", RegexOptions.IgnoreCase);
            MatchCollection fromMatches = fromRegex.Matches(selectBlock);
            if (fromMatches.Count > 0)
            {
                foreach (Match match in fromMatches)
                {
                    analysis.AppendLine($"- {match.Groups[1].Value}");
                }
            }
            else
            {
                analysis.AppendLine("- No FROM clause detected.");
            }
            analysis.AppendLine();

            // Detect JOIN operations
            analysis.AppendLine("**JOINs Detected:**");
            Regex joinRegex = new Regex(@"\bJOIN\s+([a-zA-Z0-9_\[\]\.]+)", RegexOptions.IgnoreCase);
            MatchCollection joinMatches = joinRegex.Matches(selectBlock);
            if (joinMatches.Count > 0)
            {
                foreach (Match match in joinMatches)
                {
                    analysis.AppendLine($"- {match.Groups[1].Value}");
                }
            }
            else
            {
                analysis.AppendLine("- No JOIN operations detected.");
            }
            analysis.AppendLine();

            // Detect grouping and aggregates
            if (Regex.IsMatch(selectBlock, @"\bGROUP\s+BY\b", RegexOptions.IgnoreCase))
            {
                analysis.AppendLine("**Grouping Detected:** A GROUP BY clause was found.");
            }
            if (Regex.IsMatch(selectBlock, @"\b(AVG|COUNT|SUM|MIN|MAX)\s*\(", RegexOptions.IgnoreCase))
            {
                analysis.AppendLine("**Aggregate Functions Detected:** Aggregate functions (e.g., COUNT, SUM) were identified.");
            }
            analysis.AppendLine();

            // Detect DISTINCT
            if (Regex.IsMatch(selectBlock, @"\bSELECT\s+DISTINCT\b", RegexOptions.IgnoreCase))
            {
                analysis.AppendLine("**Distinct Usage:** The DISTINCT keyword is used to eliminate duplicate rows.");
            }
            analysis.AppendLine();

            // Detect subqueries (simple check)
            if (Regex.IsMatch(selectBlock, @"\(\s*SELECT", RegexOptions.IgnoreCase))
            {
                analysis.AppendLine("**Subqueries Detected:** The query contains one or more subqueries.");
            }
            analysis.AppendLine();

            return analysis.ToString();
        }

        /// <summary>
        /// Provides analysis for non-SELECT queries (INSERT, UPDATE, DELETE, or procedure bodies).
        /// </summary>
        private string AnalyzeNonSelect(string sql)
        {
            StringBuilder analysis = new StringBuilder();
            string upperSql = sql.ToUpper();
            if (upperSql.Contains("INSERT"))
            {
                analysis.AppendLine("- **INSERT Statement Detected:** This query inserts data into one or more tables.");
            }
            if (upperSql.Contains("UPDATE"))
            {
                analysis.AppendLine("- **UPDATE Statement Detected:** This query updates existing data.");
            }
            if (upperSql.Contains("DELETE"))
            {
                analysis.AppendLine("- **DELETE Statement Detected:** This query deletes data from a table.");
            }
            if (upperSql.Contains("CREATE PROCEDURE") || upperSql.Contains("ALTER PROCEDURE") || upperSql.Contains("CREATE PROC"))
            {
                analysis.AppendLine("- **Stored Procedure Detected:** This is a stored procedure containing procedural logic and one or more DML statements.");
            }
            return analysis.ToString();
        }

        /// <summary>
        /// Analyzes the SQL for procedural constructs such as loops, cursors, and conditional statements.
        /// </summary>
        private string AnalyzeProceduralElements(string sql)
        {
            StringBuilder procAnalysis = new StringBuilder();

            // Check for loops
            if (Regex.IsMatch(sql, @"\bFOR\s+.+\bLOOP\b", RegexOptions.IgnoreCase) ||
                Regex.IsMatch(sql, @"\bWHILE\b", RegexOptions.IgnoreCase))
            {
                procAnalysis.AppendLine("- **Loop Constructs Detected:** There are FOR or WHILE loops present.");
            }
            // Check for cursors
            if (Regex.IsMatch(sql, @"\bCURSOR\b", RegexOptions.IgnoreCase))
            {
                procAnalysis.AppendLine("- **Cursor Declaration Detected:** The SQL uses a cursor for row-by-row processing.");
            }
            // Check for CASE statements
            if (Regex.IsMatch(sql, @"\bCASE\b", RegexOptions.IgnoreCase))
            {
                procAnalysis.AppendLine("- **CASE Statements Detected:** The query includes CASE expressions.");
            }
            // Check for IF statements
            if (Regex.IsMatch(sql, @"\bIF\s+.+\bTHEN\b", RegexOptions.IgnoreCase))
            {
                procAnalysis.AppendLine("- **Conditional (IF) Statements Detected:** The procedure contains conditional logic.");
            }

            return procAnalysis.ToString();
        }

        /// <summary>
        /// Generates a summary of key components detected in the SQL.
        /// </summary>
        private string GenerateComponentSummary(string sql)
        {
            StringBuilder summary = new StringBuilder();
            summary.AppendLine("- **SQL Type:** " + IdentifySqlType(sql));
            summary.AppendLine("- **CTEs:** " + (Regex.IsMatch(sql, @"WITH\s+", RegexOptions.IgnoreCase) ? "Detected" : "Not Detected"));
            summary.AppendLine("- **SELECT / DML Statements:** " + (Regex.IsMatch(sql, @"\b(SELECT|INSERT|UPDATE|DELETE)\b", RegexOptions.IgnoreCase) ? "Detected" : "Not Detected"));
            summary.AppendLine("- **Joins:** " + (Regex.IsMatch(sql, @"\bJOIN\b", RegexOptions.IgnoreCase) ? "Detected" : "Not Detected"));
            summary.AppendLine("- **Aggregates:** " + (Regex.IsMatch(sql, @"\b(AVG|COUNT|SUM|MIN|MAX)\s*\(", RegexOptions.IgnoreCase) ? "Detected" : "Not Detected"));
            summary.AppendLine("- **Grouping:** " + (Regex.IsMatch(sql, @"\bGROUP\s+BY\b", RegexOptions.IgnoreCase) ? "Detected" : "Not Detected"));
            summary.AppendLine("- **Procedural Constructs:** " + ((Regex.IsMatch(sql, @"\bFOR\b", RegexOptions.IgnoreCase) ||
                                                                Regex.IsMatch(sql, @"\bWHILE\b", RegexOptions.IgnoreCase) ||
                                                                Regex.IsMatch(sql, @"\bCURSOR\b", RegexOptions.IgnoreCase) ||
                                                                Regex.IsMatch(sql, @"\bCASE\b", RegexOptions.IgnoreCase))
                                                                    ? "Detected" : "Not Detected"));
            return summary.ToString();
        }
    }
}

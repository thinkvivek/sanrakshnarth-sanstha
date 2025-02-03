using System;
using System.Text;
using System.Text.RegularExpressions;
using System.Windows.Forms;

namespace GenericStoredProcedureNarrative
{
    public partial class MainForm : Form
    {
        public MainForm()
        {
            InitializeComponent();
        }

        // Event handler when the Analyze button is clicked.
        private void btnAnalyze_Click(object sender, EventArgs e)
        {
            string sqlInput = txtInput.Text;
            if (string.IsNullOrWhiteSpace(sqlInput))
            {
                MessageBox.Show("Please enter a stored procedure or SQL query.", "Input Required", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            // Generate a narrative explanation of the stored procedure.
            string narrative = GenerateNarrativeExplanation(sqlInput);
            txtOutput.Text = narrative;
        }

        /// <summary>
        /// Generates a narrative explanation for any stored procedure or SQL query.
        /// This method attempts to generate a "story" that explains the overall logic of the SQL.
        /// </summary>
        /// <param name="sql">The SQL text input.</param>
        /// <returns>A narrative explanation string.</returns>
        private string GenerateNarrativeExplanation(string sql)
        {
            StringBuilder narrative = new StringBuilder();
            string normalizedSql = sql.Trim();

            narrative.AppendLine("### SQL Narrative Explanation");
            narrative.AppendLine();

            // Identify the type of SQL (Stored Procedure, SELECT, INSERT, etc.)
            string sqlType = IdentifySqlType(normalizedSql);
            narrative.AppendLine($"**SQL Type:** {sqlType}");
            narrative.AppendLine();

            // For stored procedures, try to provide a story for the overall structure.
            if (sqlType == "Stored Procedure")
            {
                narrative.AppendLine("This stored procedure appears to contain procedural logic combined with one or more SQL statements. Below is a high-level narrative of its structure:");
                narrative.AppendLine();
            }
            else
            {
                narrative.AppendLine("This SQL query appears to be a standalone query. Here is a narrative of its main parts:");
                narrative.AppendLine();
            }

            // Check for Common Table Expressions (CTEs)
            if (Regex.IsMatch(normalizedSql, @"^\s*WITH", RegexOptions.IgnoreCase))
            {
                narrative.AppendLine("1. **Common Table Expressions (CTEs) Detected:**");
                narrative.AppendLine("   The query uses one or more CTEs (defined using the WITH clause) to organize complex logic into smaller, reusable parts.");
                narrative.AppendLine("   - For example, one CTE might perform a self-join on a table to pre-process data, while another might aggregate or filter that data.");
                narrative.AppendLine();
            }
            else
            {
                narrative.AppendLine("1. **No CTEs Detected:**");
                narrative.AppendLine("   The query does not appear to use common table expressions. The logic is likely contained in one or more standalone SQL statements.");
                narrative.AppendLine();
            }

            // Look for multiple SELECT statements or query blocks
            int selectCount = Regex.Matches(normalizedSql, @"\bSELECT\b", RegexOptions.IgnoreCase).Count;
            narrative.AppendLine($"2. **Main Query Blocks:**");
            if (selectCount > 1)
            {
                narrative.AppendLine($"   There appear to be {selectCount} main SELECT statements or query blocks. This suggests that the procedure breaks the logic into multiple steps.");
            }
            else if (selectCount == 1)
            {
                narrative.AppendLine("   There is a single main SELECT statement in the procedure.");
            }
            else
            {
                narrative.AppendLine("   No SELECT statements were found; the procedure might be performing DML operations (INSERT, UPDATE, DELETE) or purely procedural work.");
            }
            narrative.AppendLine();

            // Analyze common parts (self-joins, aggregations, concatenations, etc.)
            if (Regex.IsMatch(normalizedSql, @"\bJOIN\b", RegexOptions.IgnoreCase))
            {
                narrative.AppendLine("3. **JOIN Operations:**");
                narrative.AppendLine("   The procedure uses JOINs to combine data from multiple tables. This is typically done to correlate data across related tables.");
                narrative.AppendLine();
            }

            if (Regex.IsMatch(normalizedSql, @"\bGROUP\s+BY\b", RegexOptions.IgnoreCase))
            {
                narrative.AppendLine("4. **Grouping and Aggregation:**");
                narrative.AppendLine("   The query includes a GROUP BY clause along with aggregate functions (such as COUNT, SUM, etc.) to summarize data across groups.");
                narrative.AppendLine();
            }

            if (Regex.IsMatch(normalizedSql, @"\bCONCAT|[+]\b", RegexOptions.IgnoreCase))
            {
                narrative.AppendLine("5. **Data Concatenation or Formatting:**");
                narrative.AppendLine("   The procedure uses concatenation functions to combine fields (for example, concatenating product names) to form readable outputs.");
                narrative.AppendLine();
            }

            // Check for procedural constructs such as loops, cursors, or conditional statements
            if (Regex.IsMatch(normalizedSql, @"\bFOR\s+.+\bLOOP\b", RegexOptions.IgnoreCase) ||
                Regex.IsMatch(normalizedSql, @"\bWHILE\b", RegexOptions.IgnoreCase))
            {
                narrative.AppendLine("6. **Procedural Constructs (Loops):**");
                narrative.AppendLine("   The stored procedure contains loop constructs (FOR or WHILE loops) to iterate over sets of data or perform repeated operations.");
                narrative.AppendLine();
            }

            if (Regex.IsMatch(normalizedSql, @"\bCURSOR\b", RegexOptions.IgnoreCase))
            {
                narrative.AppendLine("7. **Cursor Usage:**");
                narrative.AppendLine("   The procedure uses cursors to process query results row-by-row, which is common in procedural SQL code.");
                narrative.AppendLine();
            }

            if (Regex.IsMatch(normalizedSql, @"\bIF\s+.+\bTHEN\b", RegexOptions.IgnoreCase))
            {
                narrative.AppendLine("8. **Conditional Logic:**");
                narrative.AppendLine("   The procedure includes IF statements to conditionally execute code based on certain criteria.");
                narrative.AppendLine();
            }

            // Now, try to provide a holistic narrative combining these elements.
            narrative.AppendLine("### Holistic Narrative");
            narrative.AppendLine();
            narrative.AppendLine("Based on the analysis, here is a high-level narrative of the stored procedure:");
            narrative.AppendLine();

            // Build the narrative story based on some detected elements.
            if (Regex.IsMatch(normalizedSql, @"^\s*WITH", RegexOptions.IgnoreCase))
            {
                narrative.AppendLine("The stored procedure starts by defining one or more Common Table Expressions (CTEs) using the WITH clause. ");
                narrative.AppendLine("For example, the first CTE might perform a self-join on a table (such as `cust_orders`) to pair rows from the same order while removing duplicates (by comparing product IDs). ");
                narrative.AppendLine("The next CTE could then group these pairs and calculate how many times each pair occurs, effectively determining the frequency of product pairings.");
            }
            else
            {
                narrative.AppendLine("The stored procedure does not use CTEs, suggesting that its logic is contained within a single query or a series of procedural steps.");
            }

            narrative.AppendLine();
            narrative.AppendLine("Next, the main body of the procedure performs one or more SELECT operations. ");
            narrative.AppendLine("If multiple SELECT statements are present, each represents a distinct step in the overall logic. ");
            narrative.AppendLine("For instance, one SELECT might retrieve raw data, another might aggregate or filter that data, and a final SELECT could join additional tables (such as a `products` table) to enrich the results with human-readable names or other details.");
            narrative.AppendLine();
            narrative.AppendLine("Furthermore, the procedure may include procedural constructs such as loops or conditional statements to iterate over data or make decisions based on dynamic conditions. ");
            narrative.AppendLine("This combination of declarative SQL for data retrieval and procedural logic for control flow makes the stored procedure both powerful and flexible in handling complex business logic.");
            narrative.AppendLine();
            narrative.AppendLine("### Conclusion");
            narrative.AppendLine("In summary, this stored procedure is designed to process and transform data in multiple steps. ");
            narrative.AppendLine("It leverages CTEs to modularize its logic, performs JOINs and aggregations to combine and summarize data, and finally enriches the output by formatting the data (such as concatenating values). ");
            narrative.AppendLine("The use of loops, cursors, and conditional statements (if present) further indicates that the procedure handles more complex, row-by-row processing or conditional business logic.");
            narrative.AppendLine();
            narrative.AppendLine("This narrative provides a holistic understanding of the procedure's structure and purpose, regardless of the specific details of the SQL code.");

            return narrative.ToString();
        }

        /// <summary>
        /// Identifies the type of SQL based on certain keywords.
        /// </summary>
        private string IdentifySqlType(string sql)
        {
            string upperSql = sql.ToUpper();
            if (upperSql.Contains("CREATE PROCEDURE") ||
                upperSql.Contains("CREATE PROC") ||
                upperSql.Contains("ALTER PROCEDURE") ||
                upperSql.Contains("ALTER PROC"))
            {
                return "Stored Procedure";
            }
            if (upperSql.Contains("SELECT"))
            {
                return "SELECT Query";
            }
            if (upperSql.Contains("INSERT"))
            {
                return "INSERT Query";
            }
            if (upperSql.Contains("UPDATE"))
            {
                return "UPDATE Query";
            }
            if (upperSql.Contains("DELETE"))
            {
                return "DELETE Query";
            }
            return "Unknown Type";
        }
    }
}

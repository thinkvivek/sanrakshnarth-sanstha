using System;
using System.Data;
using System.IO;
using System.Linq;

public static class CsvHelper
{
    public static void WriteDataTableToPipeDelimitedCsv(DataTable table, string filePath)
    {
        using (var writer = new StreamWriter(filePath, false, System.Text.Encoding.UTF8, 65536)) // 64KB buffer
        {
            // Write header
            var columnNames = table.Columns.Cast<DataColumn>()
                                  .Select(col => EscapeCsvField(col.ColumnName));
            writer.WriteLine(string.Join("|", columnNames));

            // Write rows
            foreach (DataRow row in table.Rows)
            {
                var fields = row.ItemArray.Select(field => EscapeCsvField(field?.ToString() ?? ""));
                writer.WriteLine(string.Join("|", fields));
            }
        }
    }

    private static string EscapeCsvField(string field)
    {
        if (field.Contains("|") || field.Contains("\"") || field.Contains("\n") || field.Contains("\r"))
        {
            field = field.Replace("\"", "\"\"");
            return $"\"{field}\"";
        }
        return field;
    }
}

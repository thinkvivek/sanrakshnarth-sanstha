using System;
using System.Data;
using System.IO;
using System.Text;

public class CsvHelper
{
    public static void SaveDataTableToCsv(DataTable dtResult, string filePath)
    {
        if (dtResult == null || dtResult.Rows.Count == 0)
        {
            throw new ArgumentException("DataTable is empty or null.");
        }

        StringBuilder sb = new StringBuilder();

        // Write column headers
        string[] columnNames = Array.ConvertAll(dtResult.Columns.Cast<DataColumn>().ToArray(), col => col.ColumnName);
        sb.AppendLine(string.Join("|", columnNames));

        // Write row data
        foreach (DataRow row in dtResult.Rows)
        {
            string[] fields = Array.ConvertAll(row.ItemArray, field => field?.ToString()?.Replace("|", " ") ?? "");
            sb.AppendLine(string.Join("|", fields));
        }

        // Save to file
        File.WriteAllText(filePath, sb.ToString(), Encoding.UTF8);
    }
}

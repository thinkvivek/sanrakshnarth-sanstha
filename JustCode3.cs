using System;
using System.Collections.Generic;
using System.Data;
using System.IO;
using ClosedXML.Excel;
using ExcelDataReader;
using System.Linq;

class Program
{
    static void Main()
    {
        System.Text.Encoding.RegisterProvider(System.Text.CodePagesEncodingProvider.Instance);

        // Load data from .xls files, excluding the header row
        var worksheet1Data = ReadExcelFile("worksheet1.xls", out int numColumns, out List<string> headers);
        var worksheet2Data = ReadExcelFile("worksheet2.xls", out _, out _);

        if (worksheet1Data.Count == 0 || worksheet2Data.Count == 0)
        {
            Console.WriteLine("One of the worksheets is empty. Exiting.");
            return;
        }

        using (var workbook = new XLWorkbook())
        {
            // Create a new worksheet for differences
            var differencesSheet = workbook.Worksheets.Add("differences");

            // Add header with "SheetName" column and the actual headers from worksheet1
            differencesSheet.Cell(1, 1).Value = "SheetName";
            differencesSheet.Cell(1, 2).Value = "IsMatch";
            for (int col = 0; col < headers.Count; col++)
            {
                differencesSheet.Cell(1, col + 3).Value = headers[col];
            }

            // Generate potential matches
            var potentialMatches = new List<(int row1, int row2, int matches)>();
            for (int i = 0; i < worksheet1Data.Count; i++)
            {
                for (int j = 0; j < worksheet2Data.Count; j++)
                {
                    int matches = CountMatches(worksheet1Data[i], worksheet2Data[j]);
                    if (matches > 0)
                    {
                        potentialMatches.Add((i, j, matches));
                    }
                }
            }

            // Sort matches by number of matching columns in descending order
            potentialMatches = potentialMatches.OrderByDescending(x => x.matches).ToList();

            var matchedRows1 = new HashSet<int>();
            var matchedRows2 = new HashSet<int>();

            int currentRow = 2;

            // Process matches
            foreach (var match in potentialMatches)
            {
                if (matchedRows1.Contains(match.row1) || matchedRows2.Contains(match.row2))
                    continue;

                matchedRows1.Add(match.row1);
                matchedRows2.Add(match.row2);

                AddRow(differencesSheet, currentRow, "worksheet1", "Y", worksheet1Data[match.row1], worksheet2Data[match.row2], numColumns);
                currentRow++;
                AddRow(differencesSheet, currentRow, "worksheet2", "Y", worksheet2Data[match.row2], worksheet1Data[match.row1], numColumns);
                currentRow++;
            }

            // Add remaining unmatched rows from worksheet1
            for (int i = 0; i < worksheet1Data.Count; i++)
            {
                if (!matchedRows1.Contains(i))
                {
                    AddRow(differencesSheet, currentRow, "worksheet1", "N", worksheet1Data[i], null, numColumns);
                    currentRow++;
                }
            }

            // Add remaining unmatched rows from worksheet2
            for (int j = 0; j < worksheet2Data.Count; j++)
            {
                if (!matchedRows2.Contains(j))
                {
                    AddRow(differencesSheet, currentRow, "worksheet2", "N", worksheet2Data[j], null, numColumns);
                    currentRow++;
                }
            }

            workbook.SaveAs("differences.xlsx");
        }
    }

    static List<List<string>> ReadExcelFile(string filePath, out int numColumns, out List<string> headers)
    {
        var data = new List<List<string>>();
        headers = new List<string>();
        numColumns = 0;

        using (var stream = File.Open(filePath, FileMode.Open, FileAccess.Read))
        {
            using (var reader = ExcelDataReader.ExcelReaderFactory.CreateReader(stream))
            {
                var conf = new ExcelDataSetConfiguration
                {
                    ConfigureDataTable = _ => new ExcelDataTableConfiguration
                    {
                        UseHeaderRow = true // Use first row as column names
                    }
                };

                var result = reader.AsDataSet(conf);

                var table = result.Tables[0]; // Assuming the data is in the first sheet
                numColumns = table.Columns.Count;

                // Read headers
                for (int col = 0; col < table.Columns.Count; col++)
                {
                    headers.Add(table.Columns[col].ColumnName);
                }

                // Read data excluding header row
                for (int row = 0; row < table.Rows.Count; row++)
                {
                    var rowData = new List<string>();
                    for (int col = 0; col < table.Columns.Count; col++)
                    {
                        rowData.Add(table.Rows[row][col].ToString());
                    }
                    data.Add(rowData);
                }
            }
        }

        return data;
    }

    static int CountMatches(List<string> row1, List<string> row2)
    {
        int matches = 0;
        for (int col = 0; col < row1.Count; col++)
        {
            if (row1[col] == row2[col])
            {
                matches++;
            }
        }
        return matches;
    }

    static void AddRow(IXLWorksheet sheet, int row, string sheetName, string isMatch, List<string> rowData, List<string> compareRowData, int numColumns)
    {
        sheet.Cell(row, 1).Value = sheetName;
        sheet.Cell(row, 2).Value = isMatch;
        for (int col = 0; col < numColumns; col++)
        {
            var cell = sheet.Cell(row, col + 3);
            cell.Value = rowData[col];

            if (compareRowData != null && rowData[col] != compareRowData[col])
            {
                cell.Style.Fill.BackgroundColor = XLColor.Yellow;
            }
        }

        if (compareRowData == null)
        {
            sheet.Range(row, 3, row, numColumns + 2).Style.Fill.BackgroundColor = XLColor.LightGray;
        }
    }
}

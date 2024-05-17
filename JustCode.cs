using System;
using System.Collections.Generic;
using System.Data;
using System.IO;
using ClosedXML.Excel;
using ExcelDataReader;

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
            for (int col = 0; col < headers.Count; col++)
            {
                differencesSheet.Cell(1, col + 2).Value = headers[col];
            }

            // Match rows and add to differences sheet
            int currentRow = 2;
            var matchedRows2 = new HashSet<int>();
            for (int i = 0; i < worksheet1Data.Count; i++)
            {
                int bestMatchIndex = -1;
                int maxMatches = 0;

                for (int j = 0; j < worksheet2Data.Count; j++)
                {
                    if (matchedRows2.Contains(j))
                        continue;

                    int matches = CountMatches(worksheet1Data[i], worksheet2Data[j]);

                    if (matches > maxMatches)
                    {
                        maxMatches = matches;
                        bestMatchIndex = j;
                    }
                }

                if (bestMatchIndex != -1)
                {
                    matchedRows2.Add(bestMatchIndex);
                    AddRow(differencesSheet, currentRow, "worksheet1", worksheet1Data[i], worksheet2Data[bestMatchIndex], numColumns);
                    currentRow++;
                    AddRow(differencesSheet, currentRow, "worksheet2", worksheet2Data[bestMatchIndex], worksheet1Data[i], numColumns);
                    currentRow++;
                }
                else
                {
                    AddRow(differencesSheet, currentRow, "worksheet1", worksheet1Data[i], null, numColumns);
                    currentRow++;
                }
            }

            // Add remaining unmatched rows from worksheet2
            for (int j = 0; j < worksheet2Data.Count; j++)
            {
                if (!matchedRows2.Contains(j))
                {
                    AddRow(differencesSheet, currentRow, "worksheet2", worksheet2Data[j], null, numColumns);
                    currentRow++;
                }
            }

            workbook.SaveAs("differences.xls");
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
                for (int row = 1; row < table.Rows.Count; row++)
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

    static void AddRow(IXLWorksheet sheet, int row, string sheetName, List<string> rowData, List<string> compareRowData, int numColumns)
    {
        sheet.Cell(row, 1).Value = sheetName;
        for (int col = 0; col < numColumns; col++)
        {
            var cell = sheet.Cell(row, col + 2);
            cell.Value = rowData[col];

            if (compareRowData != null && rowData[col] != compareRowData[col])
            {
                cell.Style.Fill.BackgroundColor = XLColor.Yellow;
            }
        }

        if (compareRowData == null)
        {
            sheet.Range(row, 2, row, numColumns + 1).Style.Fill.BackgroundColor = XLColor.LightGray;
        }
    }
}

using System;
using System.Collections.Generic;
using System.Data;
using System.IO;
using System.Linq;
using ClosedXML.Excel;
using ExcelDataReader;

class Program
{
    static void Main()
    {
        System.Text.Encoding.RegisterProvider(System.Text.CodePagesEncodingProvider.Instance);

        // Load data from .xls files
        var worksheet1Data = ReadExcelFile("worksheet1.xls");
        var worksheet2Data = ReadExcelFile("worksheet2.xls");

        using (var workbook = new XLWorkbook())
        {
            // Create a new worksheet for differences
            var differencesSheet = workbook.Worksheets.Add("differences");

            // Add header with "SheetName" column
            differencesSheet.Cell(1, 1).Value = "SheetName";
            for (int col = 1; col <= 44; col++)
            {
                differencesSheet.Cell(1, col + 1).Value = $"Column{col}";
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
                    AddRow(differencesSheet, currentRow, "worksheet1", worksheet1Data[i], worksheet2Data[bestMatchIndex]);
                    currentRow++;
                    AddRow(differencesSheet, currentRow, "worksheet2", worksheet2Data[bestMatchIndex], worksheet1Data[i]);
                    currentRow++;
                }
                else
                {
                    AddRow(differencesSheet, currentRow, "worksheet1", worksheet1Data[i], null);
                    currentRow++;
                }
            }

            // Add remaining unmatched rows from worksheet2
            for (int j = 0; j < worksheet2Data.Count; j++)
            {
                if (!matchedRows2.Contains(j))
                {
                    AddRow(differencesSheet, currentRow, "worksheet2", worksheet2Data[j], null);
                    currentRow++;
                }
            }

            workbook.SaveAs("differences.xls");
        }
    }

    static List<List<string>> ReadExcelFile(string filePath)
    {
        var data = new List<List<string>>();

        using (var stream = File.Open(filePath, FileMode.Open, FileAccess.Read))
        {
            using (var reader = ExcelDataReader.ExcelReaderFactory.CreateReader(stream))
            {
                var result = reader.AsDataSet();

                var table = result.Tables[0]; // Assuming the data is in the first sheet

                for (int row = 0; row < table.Rows.Count; row++) // Including the header row for easier mapping
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

    static void AddRow(IXLWorksheet sheet, int row, string sheetName, List<string> rowData, List<string> compareRowData)
    {
        sheet.Cell(row, 1).Value = sheetName;
        for (int col = 0; col < rowData.Count; col++)
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
            sheet.Range(row, 2, row, 45).Style.Fill.BackgroundColor = XLColor.LightGray;
        }
    }
}

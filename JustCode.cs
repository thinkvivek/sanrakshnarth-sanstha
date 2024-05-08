using System;
using System.Collections.Generic;
using System.Drawing;
using OfficeOpenXml;
using OfficeOpenXml.Style;

class Program
{
    static void Main()
    {
        // Load Excel files into ExcelPackage objects
        ExcelPackage excelPackage1 = new ExcelPackage(new System.IO.FileInfo("worksheet1.xlsx"));
        ExcelPackage excelPackage2 = new ExcelPackage(new System.IO.FileInfo("worksheet2.xlsx"));

        // Get worksheets from ExcelPackage objects
        ExcelWorksheet worksheet1 = excelPackage1.Workbook.Worksheets[0];
        ExcelWorksheet worksheet2 = excelPackage2.Workbook.Worksheets[0];

        // Create a new ExcelPackage for differences
        ExcelPackage differencesPackage = new ExcelPackage();
        ExcelWorksheet differencesWorksheet = differencesPackage.Workbook.Worksheets.Add("Differences");

        // Add "SheetName" column header
        differencesWorksheet.Cells[1, 45].Value = "SheetName";

        // Copy headers to differences worksheet
        for (int col = 1; col <= worksheet1.Dimension.End.Column; col++)
        {
            differencesWorksheet.Cells[1, col].Value = worksheet1.Cells[1, col].Value;
        }

        // Compare rows
        int differencesRowIndex = 2;
        HashSet<int> matchedRows = new HashSet<int>();

        // Compare rows from worksheet1 to worksheet2
        for (int row1Index = 2; row1Index <= worksheet1.Dimension.End.Row; row1Index++)
        {
            var row1 = worksheet1.Cells[row1Index, 1, row1Index, worksheet1.Dimension.End.Column];

            // Find the best match row in worksheet2
            int bestMatchRowIndex = FindBestMatchRowIndex(row1, worksheet2, matchedRows);

            if (bestMatchRowIndex != -1)
            {
                var row2 = worksheet2.Cells[bestMatchRowIndex, 1, bestMatchRowIndex, worksheet2.Dimension.End.Column];
                CompareAndHighlightRows(row1, row2, differencesWorksheet, differencesRowIndex, "worksheet1", "worksheet2");
                matchedRows.Add(bestMatchRowIndex);
            }
            else
            {
                // No match found, mark the entire row from worksheet1 as extra
                HighlightRow(differencesWorksheet, differencesRowIndex, worksheet1.Dimension.End.Column, Color.Yellow);
                CopyRowToDifferences(row1, differencesWorksheet, differencesRowIndex, "worksheet1");
            }

            differencesRowIndex++;
        }

        // Compare remaining rows from worksheet2 to worksheet1
        for (int row2Index = 2; row2Index <= worksheet2.Dimension.End.Row; row2Index++)
        {
            if (!matchedRows.Contains(row2Index))
            {
                var row2 = worksheet2.Cells[row2Index, 1, row2Index, worksheet2.Dimension.End.Column];
                HighlightRow(differencesWorksheet, differencesRowIndex, worksheet1.Dimension.End.Column, Color.Yellow);
                CopyRowToDifferences(row2, differencesWorksheet, differencesRowIndex, "worksheet2");
                differencesRowIndex++;
            }
        }

        // Save the differences Excel sheet
        differencesPackage.SaveAs(new System.IO.FileInfo("differences.xlsx"));

        Console.WriteLine("Differences saved successfully.");
    }

    static int FindBestMatchRowIndex(ExcelRangeBase row1, ExcelWorksheet worksheet, HashSet<int> matchedRows)
    {
        int bestMatchRowIndex = -1;
        int maxMatchingColumns = 0;

        for (int rowIndex = 2; rowIndex <= worksheet.Dimension.End.Row; rowIndex++)
        {
            if (matchedRows.Contains(rowIndex))
                continue; // Skip already matched rows

            var currentRow = worksheet.Cells[rowIndex, 1, rowIndex, worksheet.Dimension.End.Column];
            int matchingColumns = CountMatchingColumns(row1, currentRow);

            if (matchingColumns > maxMatchingColumns)
            {
                maxMatchingColumns = matchingColumns;
                bestMatchRowIndex = rowIndex;
            }
        }

        return bestMatchRowIndex;
    }

    static int CountMatchingColumns(ExcelRangeBase row1, ExcelRangeBase row2)
    {
        int matchingColumns = 0;

        for (int col = 1; col <= row1.End.Column; col++)
        {
            if (row1[1, col].Value.Equals(row2[1, col].Value))
            {
                matchingColumns++;
            }
        }

        return matchingColumns;
    }

    static void CompareAndHighlightRows(ExcelRangeBase row1, ExcelRangeBase row2, ExcelWorksheet differencesWorksheet, int rowIndex, string sheet1Name, string sheet2Name)
    {
        for (int col = 1; col <= row1.End.Column; col++)
        {
            if (!row1[1, col].Value.Equals(row2[1, col].Value))
            {
                HighlightCell(differencesWorksheet, rowIndex, col, Color.Red);
            }
        }

        // Copy row1 and row2 to differences worksheet
        CopyRowToDifferences(row1, differencesWorksheet, rowIndex, sheet1Name);
        CopyRowToDifferences(row2, differencesWorksheet, rowIndex + 1, sheet2Name); // Add one to avoid overwriting row1
    }

    static void HighlightRow(ExcelWorksheet worksheet, int rowIndex, int numColumns, Color color)
    {
        for (int col = 1; col <= numColumns; col++)
        {
            HighlightCell(worksheet, rowIndex, col, color);
        }
    }

    static void HighlightCell(ExcelWorksheet worksheet, int rowIndex, int colIndex, Color color)
    {
        worksheet.Cells[rowIndex, colIndex].Style.Fill.PatternType = ExcelFillStyle.Solid;
        worksheet.Cells[rowIndex, colIndex].Style.Fill.BackgroundColor.SetColor(color);
    }

    static void CopyRowToDifferences(ExcelRangeBase sourceRow, ExcelWorksheet differencesWorksheet, int rowIndex, string sheetName)
    {
        for (int col = 1; col <= sourceRow.End.Column; col++)
        {
            differencesWorksheet.Cells[rowIndex, col].Value = sourceRow[1, col].Value;
        }

        differencesWorksheet.Cells[rowIndex, 45].Value = sheetName; // Add sheet name
    }
}

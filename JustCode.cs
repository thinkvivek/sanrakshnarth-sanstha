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
        using (ExcelPackage excelPackage1 = new ExcelPackage(new System.IO.FileInfo("worksheet1.xlsx")))
        using (ExcelPackage excelPackage2 = new ExcelPackage(new System.IO.FileInfo("worksheet2.xlsx")))
        {
            // Get worksheets from ExcelPackage objects
            ExcelWorksheet worksheet1 = excelPackage1.Workbook.Worksheets[0];
            ExcelWorksheet worksheet2 = excelPackage2.Workbook.Worksheets[0];

            // Create a new ExcelPackage for differences
            using (ExcelPackage differencesPackage = new ExcelPackage())
            {
                ExcelWorksheet differencesWorksheet = differencesPackage.Workbook.Worksheets.Add("Differences");

                // Add "SheetName" column header
                differencesWorksheet.Cells[1, 1].Value = "SheetName";

                // Copy headers to differences worksheet
                for (int col = 1; col <= worksheet1.Dimension.End.Column; col++)
                {
                    differencesWorksheet.Cells[1, col + 1].Value = worksheet1.Cells[1, col].Value;
                }

                // Compare rows
                int differencesRowIndex = 2;
                HashSet<int> matchedRows = new HashSet<int>();

                // Compare each row of worksheet1 with each row of worksheet2
                for (int row1Index = 2; row1Index <= worksheet1.Dimension.End.Row; row1Index++)
                {
                    var row1 = worksheet1.Cells[row1Index, 1, row1Index, worksheet1.Dimension.End.Column];

                    // Initialize variables to keep track of the best match
                    int bestMatchRowIndex = -1;
                    int maxMatchingColumns = 0;

                    // Compare current row of worksheet1 with each row of worksheet2
                    for (int row2Index = 2; row2Index <= worksheet2.Dimension.End.Row; row2Index++)
                    {
                        if (matchedRows.Contains(row2Index))
                            continue; // Skip already matched rows

                        var row2 = worksheet2.Cells[row2Index, 1, row2Index, worksheet2.Dimension.End.Column];
                        int matchingColumns = CountMatchingColumns(row1, row2);

                        // Update best match if the current row from worksheet2 has more matching columns
                        if (matchingColumns > maxMatchingColumns)
                        {
                            maxMatchingColumns = matchingColumns;
                            bestMatchRowIndex = row2Index;
                        }
                    }

                    if (bestMatchRowIndex != -1)
                    {
                        // Add matched rows to differences worksheet
                        var matchedRow1 = worksheet1.Cells[row1Index, 1, row1Index, worksheet1.Dimension.End.Column];
                        var matchedRow2 = worksheet2.Cells[bestMatchRowIndex, 1, bestMatchRowIndex, worksheet2.Dimension.End.Column];
                        AddMatchedRowsToDifferences(matchedRow1, matchedRow2, differencesWorksheet, differencesRowIndex, "worksheet1", "worksheet2");

                        // Mark row from worksheet2 as matched
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

                // Add remaining unmatched rows from worksheet2 to differences worksheet
                for (int row2Index = 2; row2Index <= worksheet2.Dimension.End.Row; row2Index++)
                {
                    if (!matchedRows.Contains(row2Index))
                    {
                        var unmatchedRow2 = worksheet2.Cells[row2Index, 1, row2Index, worksheet2.Dimension.End.Column];
                        HighlightRow(differencesWorksheet, differencesRowIndex, worksheet1.Dimension.End.Column, Color.Yellow);
                        CopyRowToDifferences(unmatchedRow2, differencesWorksheet, differencesRowIndex, "worksheet2");
                        differencesRowIndex++;
                    }
                }

                // Save the differences Excel sheet
                differencesPackage.SaveAs(new System.IO.FileInfo("differences.xlsx"));

                Console.WriteLine("Differences saved successfully.");
            }
        }
    }

    static int CountMatchingColumns(ExcelRangeBase row1, ExcelRangeBase row2)
    {
        int matchingColumns = 0;

        for (int col = row1.Start.Column; col <= row1.End.Column; col++)
        {
            // Get cell values from row1 and row2
            object value1 = row1.Worksheet.Cells[row1.Start.Row, col].Value;
            object value2 = row2.Worksheet.Cells[row2.Start.Row, col].Value;

            // Compare cell values
            if (value1 != null && value2 != null && value1.Equals(value2))
            {
                matchingColumns++;
            }
        }

        return matchingColumns;
    }

    static void AddMatchedRowsToDifferences(ExcelRangeBase row1, ExcelRangeBase row2, ExcelWorksheet differencesWorksheet, int rowIndex, string sheet1Name, string sheet2Name)
    {
        // Copy matched rows from worksheet1 and worksheet2 to differences worksheet
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
        for (int col = sourceRow.Start.Column; col <= sourceRow.End.Column; col++)
        {
            // Get cell value from the source row
            object cellValue = sourceRow.Worksheet.Cells[sourceRow.Start.Row, col].Value;

            // Set the cell value in the differences worksheet
            differencesWorksheet.Cells[rowIndex, col].Value = cellValue;
        }

        // Set the sheet name in the extra column
        differencesWorksheet.Cells[rowIndex, 1].Value = sheetName;
    }
}

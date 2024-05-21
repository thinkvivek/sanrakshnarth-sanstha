using System;
using System.Collections.Generic;
using System.Data;
using System.IO;
using ClosedXML.Excel;

class Program
{
    static void Main(string[] args)
    {
        string worksheet1Path = "worksheet1.xls";
        string worksheet2Path = "worksheet2.xls";
        string differencesPath = "differences.xlsx";

        var worksheet1Data = ReadWorksheet(worksheet1Path);
        var worksheet2Data = ReadWorksheet(worksheet2Path);

        var differences = CompareWorksheets(worksheet1Data, worksheet2Data);

        WriteDifferences(differences, differencesPath);
    }

    static DataTable ReadWorksheet(string filePath)
    {
        using (var workbook = new XLWorkbook(filePath))
        {
            var worksheet = workbook.Worksheet(1);
            var dataTable = new DataTable();

            bool firstRow = true;
            foreach (var row in worksheet.RowsUsed())
            {
                if (firstRow)
                {
                    foreach (var cell in row.Cells())
                    {
                        dataTable.Columns.Add(cell.Value.ToString());
                    }
                    firstRow = false;
                }
                else
                {
                    var dataRow = dataTable.NewRow();
                    int i = 0;
                    foreach (var cell in row.Cells())
                    {
                        dataRow[i] = cell.Value.ToString();
                        i++;
                    }
                    dataTable.Rows.Add(dataRow);
                }
            }

            return dataTable;
        }
    }

    static List<Dictionary<string, object>> CompareWorksheets(DataTable dt1, DataTable dt2)
    {
        var differences = new List<Dictionary<string, object>>();
        var matchedRows = new HashSet<int>();

        foreach (DataRow row1 in dt1.Rows)
        {
            int maxMatches = -1;
            DataRow bestMatchRow = null;
            int bestMatchIndex = -1;

            for (int i = 0; i < dt2.Rows.Count; i++)
            {
                if (matchedRows.Contains(i)) continue;

                DataRow row2 = dt2.Rows[i];
                int matchCount = 0;

                for (int j = 0; j < dt1.Columns.Count; j++)
                {
                    if (row1[j].ToString() == row2[j].ToString())
                    {
                        matchCount++;
                    }
                }

                if (matchCount > maxMatches)
                {
                    maxMatches = matchCount;
                    bestMatchRow = row2;
                    bestMatchIndex = i;
                }
            }

            if (bestMatchRow != null)
            {
                matchedRows.Add(bestMatchIndex);
                var difference = new Dictionary<string, object>();

                for (int j = 0; j < dt1.Columns.Count; j++)
                {
                    difference[$"Column{j}"] = new
                    {
                        Worksheet1 = row1[j].ToString(),
                        Worksheet2 = bestMatchRow[j].ToString(),
                        IsMatch = row1[j].ToString() == bestMatchRow[j].ToString()
                    };
                }

                differences.Add(difference);
            }
            else
            {
                var difference = new Dictionary<string, object>();

                for (int j = 0; j < dt1.Columns.Count; j++)
                {
                    difference[$"Column{j}"] = new
                    {
                        Worksheet1 = row1[j].ToString(),
                        Worksheet2 = null,
                        IsMatch = false
                    };
                }

                differences.Add(difference);
            }
        }

        for (int i = 0; i < dt2.Rows.Count; i++)
        {
            if (matchedRows.Contains(i)) continue;

            DataRow row2 = dt2.Rows[i];
            var difference = new Dictionary<string, object>();

            for (int j = 0; j < dt2.Columns.Count; j++)
            {
                difference[$"Column{j}"] = new
                {
                    Worksheet1 = null,
                    Worksheet2 = row2[j].ToString(),
                    IsMatch = false
                };
            }

            differences.Add(difference);
        }

        return differences;
    }

    static void WriteDifferences(List<Dictionary<string, object>> differences, string filePath)
    {
        using (var workbook = new XLWorkbook())
        {
            var worksheet = workbook.Worksheets.Add("Differences");

            worksheet.Cell(1, 1).Value = "SheetName";
            worksheet.Cell(1, 2).Value = "IsMatch";

            int columnIndex = 3;

            foreach (var key in differences[0].Keys)
            {
                worksheet.Cell(1, columnIndex).Value = key;
                columnIndex += 2;
            }

            int rowIndex = 2;

            foreach (var difference in differences)
            {
                columnIndex = 1;
                worksheet.Cell(rowIndex, columnIndex).Value = "Worksheet1";
                worksheet.Cell(rowIndex + 1, columnIndex).Value = "Worksheet2";

                columnIndex++;
                bool allMatch = true;
                foreach (var key in difference.Keys)
                {
                    var cellData = (dynamic)difference[key];

                    worksheet.Cell(rowIndex, columnIndex).Value = cellData.IsMatch ? "Y" : "N";
                    worksheet.Cell(rowIndex, columnIndex + 1).Value = cellData.Worksheet1;
                    worksheet.Cell(rowIndex + 1, columnIndex + 1).Value = cellData.Worksheet2;

                    if (!cellData.IsMatch)
                    {
                        worksheet.Cell(rowIndex, columnIndex + 1).Style.Fill.BackgroundColor = XLColor.Yellow;
                        worksheet.Cell(rowIndex + 1, columnIndex + 1).Style.Fill.BackgroundColor = XLColor.Yellow;
                        allMatch = false;
                    }

                    columnIndex += 2;
                }

                worksheet.Cell(rowIndex, 2).Value = allMatch ? "Y" : "N";
                worksheet.Cell(rowIndex + 1, 2).Value = allMatch ? "Y" : "N";

                rowIndex += 2;
            }

            workbook.SaveAs(filePath);
        }
    }
}

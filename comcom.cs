using System;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using System.Linq;
using OfficeOpenXml;
using OfficeOpenXml.Style;
using CsvHelper;

class Program
{
    static void Main(string[] args)
    {
        // File paths
        string file1Path = "File1.xlsx"; // Change to your file path
        string file2Path = "File2.xlsx"; // Change to your file path
        string diffFilePath = "diff.xlsx";

        // Load data from files
        var file1Data = LoadData(file1Path, "File1");
        var file2Data = LoadData(file2Path, "File2");

        // Compare data
        var diffData = CompareData(file1Data, file2Data);

        // Generate the diff file
        GenerateDiffFile(diffData, diffFilePath);

        Console.WriteLine("Comparison completed. Diff file created at: " + diffFilePath);
    }

    static List<RowData> LoadData(string filePath, string fileName)
    {
        var data = new List<RowData>();

        if (filePath.EndsWith(".xlsx") || filePath.EndsWith(".xls"))
        {
            using (var package = new ExcelPackage(new FileInfo(filePath)))
            {
                var worksheet = package.Workbook.Worksheets[0];
                int rowCount = worksheet.Dimension.Rows;
                int colCount = worksheet.Dimension.Columns;

                for (int row = 2; row <= rowCount; row++) // Skip header row
                {
                    var rowData = new RowData
                    {
                        FileName = fileName,
                        Cells = new List<string>()
                    };

                    for (int col = 1; col <= colCount; col++)
                    {
                        rowData.Cells.Add(worksheet.Cells[row, col].Text);
                    }

                    data.Add(rowData);
                }
            }
        }
        else if (filePath.EndsWith(".csv"))
        {
            using (var reader = new StreamReader(filePath))
            using (var csv = new CsvReader(reader, System.Globalization.CultureInfo.InvariantCulture))
            {
                while (csv.Read())
                {
                    var rowData = new RowData
                    {
                        FileName = fileName,
                        Cells = csv.Parser.Record.ToList()
                    };

                    data.Add(rowData);
                }
            }
        }

        return data;
    }

    static List<DiffRow> CompareData(List<RowData> file1Data, List<RowData> file2Data)
    {
        var diffData = new List<DiffRow>();

        foreach (var row1 in file1Data)
        {
            var maxMatchRow = file2Data
                .Select(row2 => new
                {
                    Row = row2,
                    MatchCount = row1.Cells.Zip(row2.Cells, (c1, c2) => c1 == c2).Count(match => match)
                })
                .OrderByDescending(x => x.MatchCount)
                .FirstOrDefault();

            if (maxMatchRow == null || maxMatchRow.MatchCount < row1.Cells.Count)
            {
                diffData.Add(new DiffRow
                {
                    FileName = row1.FileName,
                    Cells = row1.Cells,
                    MatchRow = maxMatchRow?.Row,
                    MatchCount = maxMatchRow?.MatchCount ?? 0
                });
            }
        }

        foreach (var row2 in file2Data)
        {
            var maxMatchRow = file1Data
                .Select(row1 => new
                {
                    Row = row1,
                    MatchCount = row2.Cells.Zip(row1.Cells, (c1, c2) => c1 == c2).Count(match => match)
                })
                .OrderByDescending(x => x.MatchCount)
                .FirstOrDefault();

            if (maxMatchRow == null || maxMatchRow.MatchCount < row2.Cells.Count)
            {
                diffData.Add(new DiffRow
                {
                    FileName = row2.FileName,
                    Cells = row2.Cells,
                    MatchRow = maxMatchRow?.Row,
                    MatchCount = maxMatchRow?.MatchCount ?? 0
                });
            }
        }

        return diffData;
    }

    static void GenerateDiffFile(List<DiffRow> diffData, string diffFilePath)
    {
        using (var package = new ExcelPackage())
        {
            var worksheet = package.Workbook.Worksheets.Add("Diff");

            // Add headers
            worksheet.Cells[1, 1].Value = "FileName";
            for (int col = 2; col <= diffData[0].Cells.Count + 1; col++)
            {
                worksheet.Cells[1, col].Value = $"Column {col - 1}";
            }

            // Add data
            int rowIndex = 2;
            foreach (var diffRow in diffData)
            {
                worksheet.Cells[rowIndex, 1].Value = diffRow.FileName;

                for (int col = 0; col < diffRow.Cells.Count; col++)
                {
                    worksheet.Cells[rowIndex, col + 2].Value = diffRow.Cells[col];

                    if (diffRow.MatchRow != null && diffRow.Cells[col] != diffRow.MatchRow.Cells[col])
                    {
                        worksheet.Cells[rowIndex, col + 2].Style.Fill.PatternType = ExcelFillStyle.Solid;
                        worksheet.Cells[rowIndex, col + 2].Style.Fill.BackgroundColor.SetColor(Color.Yellow);
                    }
                }

                if (diffRow.MatchCount == 0)
                {
                    for (int col = 1; col <= diffRow.Cells.Count + 1; col++)
                    {
                        worksheet.Cells[rowIndex, col].Style.Fill.PatternType = ExcelFillStyle.Solid;
                        worksheet.Cells[rowIndex, col].Style.Fill.BackgroundColor.SetColor(Color.Orange);
                    }
                }

                rowIndex++;
            }

            // Save the file
            package.SaveAs(new FileInfo(diffFilePath));
        }
    }
}

class RowData
{
    public string FileName { get; set; }
    public List<string> Cells { get; set; }
}

class DiffRow
{
    public string FileName { get; set; }
    public List<string> Cells { get; set; }
    public RowData MatchRow { get; set; }
    public int MatchCount { get; set; }
}

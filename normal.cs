using System;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using System.Linq;
using OfficeOpenXml;
using OfficeOpenXml.Style;

namespace ExcelComparer
{
    public class Program
    {
        public class RowData
        {
            public List<object> Values { get; set; }
            public string FileName { get; set; }
            public bool Matched { get; set; }
            public int MatchScore { get; set; }
        }

        // Add column names to exclude from comparison
        private static readonly List<string> ExcludedColumns = new List<string> 
        { 
            "ColumnToExclude1",
            "ColumnToExclude2"
        };

        public static void Main(string[] args)
        {
            ExcelPackage.LicenseContext = LicenseContext.NonCommercial;
            const string file1Path = "File1.xlsx";
            const string file2Path = "File2.xlsx";
            const string outputPath = "diff.xlsx";

            try
            {
                var headers = GetHeaders(file1Path);
                ValidateHeaders(file1Path, file2Path);
                
                var excludedIndices = GetExcludedColumnIndices(headers);

                var file1Rows = ReadExcelFile(file1Path, "File1.xlsx");
                var file2Rows = ReadExcelFile(file2Path, "File2.xlsx");

                ProcessExactMatches(ref file1Rows, ref file2Rows, excludedIndices);
                var (matchedPairs, singleRows) = FindBestMatches(file1Rows, file2Rows, excludedIndices);

                GenerateDiffFile(outputPath, headers, excludedIndices, matchedPairs, singleRows);
                Console.WriteLine("Comparison completed successfully!");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
            }
        }

        private static List<int> GetExcludedColumnIndices(List<string> headers)
        {
            return headers.Select((h, idx) => new { h, idx })
                .Where(x => ExcludedColumns.Contains(x.h))
                .Select(x => x.idx)
                .ToList();
        }

        private static List<string> GetHeaders(string filePath)
        {
            using var package = new ExcelPackage(new FileInfo(filePath));
            var worksheet = package.Workbook.Worksheets[0];
            return Enumerable.Range(1, worksheet.Dimension.Columns)
                .Select(col => worksheet.Cells[1, col].Text)
                .ToList();
        }

        private static void ValidateHeaders(string file1Path, string file2Path)
        {
            var headers1 = GetHeaders(file1Path);
            var headers2 = GetHeaders(file2Path);

            if (!headers1.SequenceEqual(headers2))
                throw new Exception("Headers in both files do not match.");
        }

        private static List<RowData> ReadExcelFile(string filePath, string fileName)
        {
            var rows = new List<RowData>();
            using var package = new ExcelPackage(new FileInfo(filePath));
            var worksheet = package.Workbook.Worksheets[0];

            for (int row = 2; row <= worksheet.Dimension.Rows; row++)
            {
                var values = Enumerable.Range(1, worksheet.Dimension.Columns)
                    .Select(col => worksheet.Cells[row, col].Value)
                    .ToList();

                rows.Add(new RowData { Values = values, FileName = fileName });
            }
            return rows;
        }

        private static void ProcessExactMatches(ref List<RowData> file1Rows, ref List<RowData> file2Rows, 
            List<int> excludedIndices)
        {
            var file1Groups = GroupRows(file1Rows, excludedIndices);
            var file2Groups = GroupRows(file2Rows, excludedIndices);

            foreach (var key in file1Groups.Keys.Intersect(file2Groups.Keys).ToList())
            {
                var minCount = Math.Min(file1Groups[key].Count, file2Groups[key].Count);
                file1Groups[key].RemoveRange(0, minCount);
                file2Groups[key].RemoveRange(0, minCount);
            }

            file1Rows = file1Groups.Values.SelectMany(g => g).ToList();
            file2Rows = file2Groups.Values.SelectMany(g => g).ToList();
        }

        private static Dictionary<string, List<RowData>> GroupRows(List<RowData> rows, List<int> excludedIndices)
        {
            return rows.GroupBy(r => string.Join("|", r.Values
                    .Where((v, idx) => !excludedIndices.Contains(idx))
                    .Select(v => v?.ToString() ?? "")))
                .ToDictionary(g => g.Key, g => g.ToList());
        }

        private static (List<Tuple<RowData, RowData>> matchedPairs, List<RowData> singleRows) FindBestMatches(
            List<RowData> file1Rows, List<RowData> file2Rows, List<int> excludedIndices)
        {
            var matchedPairs = new List<Tuple<RowData, RowData>>();
            var remainingFile2 = new List<RowData>(file2Rows);
            var singleRows = new List<RowData>();

            foreach (var row1 in file1Rows.Where(r => !r.Matched))
            {
                var bestMatch = remainingFile2
                    .Select(row2 => new 
                    { 
                        Row = row2, 
                        Score = CountMatchingColumns(row1.Values, row2.Values, excludedIndices) 
                    })
                    .OrderByDescending(x => x.Score)
                    .FirstOrDefault();

                if (bestMatch != null && bestMatch.Score > 0)
                {
                    row1.Matched = true;
                    bestMatch.Row.Matched = true;
                    matchedPairs.Add(Tuple.Create(row1, bestMatch.Row));
                    remainingFile2.Remove(bestMatch.Row);
                }
                else
                {
                    singleRows.Add(row1);
                }
            }

            singleRows.AddRange(remainingFile2.Where(r => !r.Matched));
            return (matchedPairs, singleRows);
        }

        private static int CountMatchingColumns(List<object> values1, List<object> values2, List<int> excludedIndices)
        {
            int count = 0;
            for (int i = 0; i < values1.Count; i++)
            {
                if (excludedIndices.Contains(i)) continue;
                if (AreEqual(values1[i], values2[i])) count++;
            }
            return count;
        }

        private static bool AreEqual(object val1, object val2)
        {
            if (val1 == null && val2 == null) return true;
            if (val1 == null || val2 == null) return false;

            if (IsNumeric(val1) && IsNumeric(val2))
                return Convert.ToDouble(val1) == Convert.ToDouble(val2);

            return val1.ToString() == val2.ToString();
        }

        private static bool IsNumeric(object value)
        {
            return value is sbyte || value is byte || value is short || value is ushort ||
                   value is int || value is uint || value is long || value is ulong ||
                   value is float || value is double || value is decimal;
        }

        private static void GenerateDiffFile(string outputPath, List<string> headers, List<int> excludedIndices,
            List<Tuple<RowData, RowData>> matchedPairs, List<RowData> singleRows)
        {
            using var package = new ExcelPackage();
            var worksheet = package.Workbook.Worksheets.Add("diff");

            // Create headers
            var allHeaders = new[] { "FileName" }.Concat(headers).ToList();
            CreateHeaders(worksheet, allHeaders);

            int currentRow = 2;

            // Add matched pairs
            foreach (var (row1, row2) in matchedPairs)
            {
                AddRow(worksheet, currentRow++, row1, headers, excludedIndices, row2);
                AddRow(worksheet, currentRow++, row2, headers, excludedIndices, row1);
            }

            // Add single rows
            foreach (var row in singleRows)
            {
                AddRow(worksheet, currentRow++, row, headers, excludedIndices);
                ColorRow(worksheet, currentRow - 1, allHeaders.Count, Color.Orange);
            }

            FormatWorksheet(worksheet, allHeaders.Count);
            package.SaveAs(new FileInfo(outputPath));
        }

        private static void CreateHeaders(ExcelWorksheet worksheet, List<string> headers)
        {
            for (int i = 0; i < headers.Count; i++)
            {
                var cell = worksheet.Cells[1, i + 1];
                cell.Value = headers[i];
                cell.Style.Font.Bold = true;
                cell.Style.Fill.PatternType = ExcelFillStyle.Solid;
                cell.Style.Fill.BackgroundColor.SetColor(Color.LightGray);
            }
        }

        private static void AddRow(ExcelWorksheet worksheet, int rowNum, RowData row, 
            List<string> headers, List<int> excludedIndices, RowData compareRow = null)
        {
            worksheet.Cells[rowNum, 1].Value = row.FileName;

            for (int i = 0; i < headers.Count; i++)
            {
                var cell = worksheet.Cells[rowNum, i + 2];
                cell.Value = row.Values[i];

                if (compareRow != null && !excludedIndices.Contains(i) && !AreEqual(row.Values[i], compareRow.Values[i]))
                {
                    cell.Style.Fill.PatternType = ExcelFillStyle.Solid;
                    cell.Style.Fill.BackgroundColor.SetColor(Color.Yellow);
                }
            }
        }

        private static void ColorRow(ExcelWorksheet worksheet, int row, int colCount, Color color)
        {
            using var range = worksheet.Cells[row, 1, row, colCount];
            range.Style.Fill.PatternType = ExcelFillStyle.Solid;
            range.Style.Fill.BackgroundColor.SetColor(color);
        }

        private static void FormatWorksheet(ExcelWorksheet worksheet, int colCount)
        {
            // Auto-fit columns and set numeric format
            for (int i = 1; i <= colCount; i++)
            {
                worksheet.Column(i).AutoFit();
                if (i > 1 && worksheet.Cells[2, i].Value != null && 
                    IsNumeric(worksheet.Cells[2, i].Value))
                {
                    worksheet.Column(i).Style.Numberformat.Format = "0";
                }
            }
        }
    }
}

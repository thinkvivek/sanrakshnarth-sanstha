using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;

class CsvMerger
{
    public static void MergePipeDelimitedCsvFiles(string inputDirectory, string keyword, string outputFilePath)
    {
        var csvFiles = Directory.GetFiles(inputDirectory, "*.csv")
                                .Where(f => Path.GetFileName(f).IndexOf(keyword, StringComparison.OrdinalIgnoreCase) >= 0)
                                .ToList();

        if (csvFiles.Count == 0)
        {
            Console.WriteLine($"No CSV files containing keyword '{keyword}' found in the directory.");
            return;
        }

        bool isFirstFile = true;

        using (var writer = new StreamWriter(outputFilePath))
        {
            foreach (var file in csvFiles)
            {
                using (var reader = new StreamReader(file))
                {
                    string? line;
                    bool isFirstLine = true;

                    while ((line = reader.ReadLine()) != null)
                    {
                        if (isFirstLine)
                        {
                            if (isFirstFile)
                            {
                                writer.WriteLine(line); // Write header only from the first file
                                isFirstFile = false;
                            }
                            isFirstLine = false;
                            continue;
                        }

                        writer.WriteLine(line); // Write data lines
                    }
                }
            }
        }

        Console.WriteLine($"Merged {csvFiles.Count} file(s) containing keyword '{keyword}' into: {outputFilePath}");
    }
}





public static void MergeCsvs(string folder, string keyword, string outputFile)
{
    var files = Directory.GetFiles(folder, "*.csv")
                         .Where(f => Path.GetFileName(f).Contains(keyword, StringComparison.OrdinalIgnoreCase));

    using var writer = new StreamWriter(outputFile);
    bool wroteHeader = false;

    foreach (var file in files)
    {
        var lines = File.ReadLines(file);
        if (!wroteHeader) {
            foreach (var line in lines) writer.WriteLine(line); // write all lines including header
            wroteHeader = true;
        }
        else {
            foreach (var line in lines.Skip(1)) writer.WriteLine(line); // skip header
        }
    }
}


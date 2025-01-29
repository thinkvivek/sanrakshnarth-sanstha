private static (List<Tuple<RowData, RowData>> matchedPairs, List<RowData> singleRows) FindBestMatches(
    List<RowData> file1Rows, List<RowData> file2Rows, List<int> excludedIndices)
{
    var allPairs = new List<Tuple<RowData, RowData, int>>();
    
    // Create matrix of all possible pairs
    foreach (var row1 in file1Rows.Where(r => !r.Matched))
    {
        foreach (var row2 in file2Rows.Where(r => !r.Matched))
        {
            var score = CountMatchingColumns(row1.Values, row2.Values, excludedIndices);
            allPairs.Add(Tuple.Create(row1, row2, score));
        }
    }

    // Sort by descending score
    var sortedPairs = allPairs
        .OrderByDescending(p => p.Item3)
        .ThenBy(p => p.Item1.Values[0]) // Secondary sort criteria
        .ToList();

    var matchedPairs = new List<Tuple<RowData, RowData>>();
    var matchedFile1 = new HashSet<RowData>();
    var matchedFile2 = new HashSet<RowData>();

    foreach (var pair in sortedPairs)
    {
        if (!matchedFile1.Contains(pair.Item1) && !matchedFile2.Contains(pair.Item2))
        {
            matchedPairs.Add(Tuple.Create(pair.Item1, pair.Item2));
            matchedFile1.Add(pair.Item1);
            matchedFile2.Add(pair.Item2);
        }
    }

    // Handle remaining unpaired rows
    var singleRows = file1Rows.Except(matchedFile1)
        .Concat(file2Rows.Except(matchedFile2))
        .ToList();

    return (matchedPairs, singleRows);
}

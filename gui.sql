WITH ReportStats AS (
  SELECT 
    ReportName,
    TotalAccountCount,
    DaysCount,
    TotalRunTime,
    -- Calculate efficiency metric
    TotalRunTime / (TotalAccountCount * DaysCount) AS RuntimePerAccountDay,
    -- Z-score within parameter buckets
    (TotalRunTime - AVG(TotalRunTime) OVER (PARTITION BY AccountBucket, DaysBucket)) 
    / (STDEV(TotalRunTime) OVER (PARTITION BY AccountBucket, DaysBucket)) AS ZScore
  FROM 
    StatisticsTable
  CROSS APPLY (
    SELECT 
      CASE 
        WHEN TotalAccountCount <= 100 THEN '0-100'
        WHEN TotalAccountCount <= 500 THEN '101-500'
        ELSE '500+' 
      END AS AccountBucket,
      CASE 
        WHEN DaysCount <= 7 THEN '1-7'
        WHEN DaysCount <= 30 THEN '8-30'
        ELSE '30+' 
      END AS DaysBucket
  ) AS Buckets
)
SELECT 
  ReportName,
  AVG(RuntimePerAccountDay) AS AvgEfficiency,
  COUNT(*) AS TotalRuns,
  MAX(ZScore) AS MaxZScore
FROM 
  ReportStats
GROUP BY 
  ReportName
ORDER BY 
  AvgEfficiency DESC;


SELECT
  ReportName,
  TotalAccountCount,
  DaysCount,
  TotalRunTime,
  -- Account Buckets (4 groups)
  NTILE(4) OVER (ORDER BY TotalAccountCount) AS AccountQuartile,
  -- Days Buckets (3 groups)
  NTILE(3) OVER (ORDER BY DaysCount) AS DaysTertile
FROM
  StatisticsTable;

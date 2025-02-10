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


WITH ReportStats AS (
  SELECT 
    Client,  -- Include Client in the analysis
    ReportName,
    TotalAccountCount,
    DaysCount,
    TotalRunTime,
    -- Runtime per account-day (handle division by zero)
    TotalRunTime / NULLIF(TotalAccountCount * DaysCount, 0) AS RuntimePerAccountDay,
    -- Z-score within parameter buckets
    (TotalRunTime - AVG(TotalRunTime) OVER (PARTITION BY AccountBucket, DaysBucket)) 
    / NULLIF(STDEV(TotalRunTime) OVER (PARTITION BY AccountBucket, DaysBucket), 0) AS ZScore
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
  Client,
  ReportName,
  AVG(RuntimePerAccountDay) AS AvgEfficiency,
  COUNT(*) AS TotalRuns,
  MAX(ZScore) AS MaxZScore
FROM 
  ReportStats
GROUP BY 
  Client, ReportName  -- Group by both Client and ReportName
ORDER BY 
  AvgEfficiency DESC;  -- Prioritize the most inefficient client-report combinations





WITH ReportStats AS (
  SELECT 
    s.Client,
    s.ReportName,
    s.TotalAccountCount,
    s.DaysCount,
    s.TotalRunTime,
    -- Calculate runtime per account-day (handle division by zero)
    s.TotalRunTime / NULLIF(s.TotalAccountCount * s.DaysCount, 0) AS RuntimePerAccountDay,
    -- Calculate Z-score within parameter buckets
    (s.TotalRunTime - AVG(s.TotalRunTime) OVER (PARTITION BY b.AccountBucket, b.DaysBucket)
    / NULLIF(STDDEV(s.TotalRunTime) OVER (PARTITION BY b.AccountBucket, b.DaysBucket), 0) AS ZScore
  FROM 
    StatisticsTable s
  CROSS JOIN LATERAL (
    SELECT 
      CASE 
        WHEN s.TotalAccountCount <= 100 THEN '0-100'
        WHEN s.TotalAccountCount <= 500 THEN '101-500'
        ELSE '500+' 
      END AS AccountBucket,
      CASE 
        WHEN s.DaysCount <= 7 THEN '1-7'
        WHEN s.DaysCount <= 30 THEN '8-30'
        ELSE '30+' 
      END AS DaysBucket
    FROM DUAL
  ) b
)
SELECT 
  Client,
  ReportName,
  AVG(RuntimePerAccountDay) AS AvgEfficiency,
  COUNT(*) AS TotalRuns,
  MAX(ZScore) AS MaxZScore
FROM 
  ReportStats
GROUP BY 
  Client, ReportName
ORDER BY 
  AvgEfficiency DESC;

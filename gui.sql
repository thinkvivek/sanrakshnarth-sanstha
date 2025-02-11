WITH report_stats_normalized AS (
    SELECT
        ClientID,
        ReportName,
        TotalRunningTime / (AccountCount * DaysCount) AS normalized_time,
        TotalRunningTime,
        AccountCount,
        DaysCount,
        RunDate
    FROM report_stats
    WHERE AccountCount > 0 AND DaysCount > 0
),
aggregated AS (
    SELECT
        ClientID,
        ReportName,
        MEDIAN(normalized_time) AS median_normalized_time,
        MAX(normalized_time) AS max_normalized_time,
        COUNT(*) AS run_count
    FROM report_stats_normalized
    GROUP BY ClientID, ReportName
),
ranked_reports AS (
    SELECT
        aggregated.*,
        ROW_NUMBER() OVER (
            PARTITION BY ClientID 
            ORDER BY median_normalized_time DESC
        ) AS report_rank
    FROM aggregated
    WHERE run_count >= 3  -- Adjust threshold for "consistency"
)
SELECT
    ClientID,
    ReportName,
    median_normalized_time,
    max_normalized_time,
    run_count,
    ROUND((max_normalized_time - median_normalized_time) / median_normalized_time * 100, 2) 
        AS outlier_percent_diff  -- Flag significant outliers
FROM ranked_reports
WHERE report_rank <= 10
ORDER BY ClientID, report_rank;



WITH report_stats_normalized AS (
    SELECT
        ReportName,
        TotalRunningTime / (AccountCount * DaysCount) AS normalized_time,
        TotalRunningTime,
        AccountCount,
        DaysCount,
        RunDate
    FROM report_stats
    WHERE AccountCount > 0 AND DaysCount > 0
),
aggregated AS (
    SELECT
        ReportName,
        MEDIAN(normalized_time) AS median_normalized_time,
        MAX(normalized_time) AS max_normalized_time,
        COUNT(*) AS run_count
    FROM report_stats_normalized
    GROUP BY ReportName
),
ranked_reports AS (
    SELECT
        aggregated.*,
        ROW_NUMBER() OVER (
            ORDER BY median_normalized_time DESC
        ) AS report_rank
    FROM aggregated
    WHERE run_count >= 3  -- Consistency threshold (adjust as needed)
)
SELECT
    ReportName,
    median_normalized_time,
    max_normalized_time,
    run_count,
    ROUND((max_normalized_time - median_normalized_time) / median_normalized_time * 100, 2) 
        AS outlier_percent_diff
FROM ranked_reports
WHERE report_rank <= 25
ORDER BY report_rank;



WITH report_stats_normalized AS (
    SELECT
        ReportName,
        TotalRunningTime / (AccountCount * DaysCount) AS normalized_time,
        TotalRunningTime,
        AccountCount,
        DaysCount,
        RunDate
    FROM report_stats
    WHERE AccountCount > 0 AND DaysCount > 0
),
aggregated AS (
    SELECT
        ReportName,
        MEDIAN(normalized_time) AS median_normalized_time,
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY normalized_time) AS p95_normalized_time,
        COUNT(*) AS run_count
    FROM report_stats_normalized
    GROUP BY ReportName
),
ranked_reports AS (
    SELECT
        aggregated.*,
        ROW_NUMBER() OVER (
            ORDER BY median_normalized_time DESC
        ) AS report_rank
    FROM aggregated
    WHERE run_count >= 3  -- Consistency threshold (adjust as needed)
)
SELECT
    ReportName,
    median_normalized_time,
    p95_normalized_time,  -- Now using the 95th percentile instead of MAX
    run_count,
    ROUND((p95_normalized_time - median_normalized_time) / median_normalized_time * 100, 2) 
        AS outlier_percent_diff
FROM ranked_reports
WHERE report_rank <= 25
ORDER BY report_rank;


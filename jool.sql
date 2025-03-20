WITH expected_triggers AS (
    -- Replace this with the actual list of expected trigger names
    SELECT 'Trigger1' AS trigger_name FROM dual UNION ALL
    SELECT 'Trigger2' FROM dual UNION ALL
    SELECT 'Trigger3' FROM dual UNION ALL
    SELECT 'Trigger4' FROM dual -- Add all expected triggers here
),
daily_triggers AS (
    SELECT 
        TRUNC(date_inserted) AS trigger_date,
        trigger_name
    FROM your_table
),
all_dates AS (
    -- Generate a date range (last 30 days, adjust as needed)
    SELECT TRUNC(SYSDATE) - LEVEL + 1 AS report_date
    FROM dual
    CONNECT BY LEVEL <= 30
),
trigger_analysis AS (
    -- Find missing triggers for each date
    SELECT 
        ad.report_date AS "Date",
        TO_CHAR(ad.report_date, 'Day') AS "Day of the Week",
        COUNT(dt.trigger_name) AS "Total Triggers on that day",
        LISTAGG(et.trigger_name, ', ') WITHIN GROUP (ORDER BY et.trigger_name) AS "Missing Triggers"
    FROM all_dates ad
    CROSS JOIN expected_triggers et
    LEFT JOIN daily_triggers dt 
        ON ad.report_date = dt.trigger_date 
        AND et.trigger_name = dt.trigger_name
    WHERE dt.trigger_name IS NULL  -- Missing triggers
    GROUP BY ad.report_date
    ORDER BY ad.report_date DESC
)
SELECT * FROM trigger_analysis;

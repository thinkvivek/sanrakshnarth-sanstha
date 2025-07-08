DECLARE @TableName SYSNAME = 'YourTableName';
DECLARE @SchemaName SYSNAME = 'dbo'; -- Change if different
DECLARE @SQL NVARCHAR(MAX) = '';

SELECT @SQL = STRING_AGG(CAST(IndexScript AS NVARCHAR(MAX)), CHAR(13) + CHAR(10) + 'GO' + CHAR(13) + CHAR(10))
FROM (
    SELECT 
        'CREATE ' + 
        CASE WHEN i.is_unique = 1 THEN 'UNIQUE ' ELSE '' END +
        i.type_desc + ' INDEX [' + i.name + '] ON [' + @SchemaName + '].[' + @TableName + '] (' +
        STRING_AGG(QUOTENAME(c.name) + 
                   CASE ic.is_descending_key WHEN 1 THEN ' DESC' ELSE ' ASC' END, ', ') 
                   WITHIN GROUP (ORDER BY ic.key_ordinal) + 
        ')' +
        ISNULL(
            (SELECT ' INCLUDE (' + 
                STRING_AGG(QUOTENAME(c2.name), ', ') 
                FROM sys.index_columns ic2
                JOIN sys.columns c2 ON ic2.object_id = c2.object_id AND ic2.column_id = c2.column_id
                WHERE ic2.object_id = i.object_id AND ic2.index_id = i.index_id AND ic2.is_included_column = 1
            + ')'
        , '') AS IndexScript
    FROM sys.indexes i
    JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
    JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
    WHERE i.object_id = OBJECT_ID(@SchemaName + '.' + @TableName)
      AND i.is_primary_key = 0 -- Skip PK
      AND i.is_disabled = 0
    GROUP BY i.name, i.is_unique, i.type_desc, i.object_id, i.index_id
) AS Scripts;

PRINT @SQL;

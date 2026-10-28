-- PostgreSQL only. Execute with etl.analytics.query_library.run_query.
-- Rank before country filtering so an older revision cannot become current.
WITH ranked AS (
    SELECT s.*, row_number() OVER (
        PARTITION BY identity_key, storage_destination ORDER BY revision DESC, id DESC
    ) AS revision_rank
    FROM __WAREHOUSE_SCHEMA__.nds_v31_source AS s
    WHERE s.identity->>'project' = :project AND s.storage_destination = :destination
), scoped AS (
    SELECT * FROM ranked
    WHERE (CAST(:country AS text) IS NULL OR country = :country)
      AND (CAST(:event AS text) IS NULL OR identity->>'event' = :event)
      AND (CAST(:instrument AS text) IS NULL OR identity->>'instrument' = :instrument)
      AND (CAST(:instance AS text) IS NULL OR identity->>'instance' = :instance)
), latest AS (
    SELECT * FROM scoped WHERE revision_rank = 1
)
, classified AS (
    SELECT s.contract_hash,
        CASE WHEN NOT (CAST(s.payload AS jsonb) ? :field) THEN 'absent'
             WHEN CAST(s.payload AS jsonb)->:field = 'null'::jsonb THEN 'json_null'
             WHEN CAST(s.payload AS jsonb)->:field = '""'::jsonb THEN 'empty'
             ELSE 'present' END AS raw_state,
        CASE WHEN v.source_id IS NULL THEN 'validation_layer_missing'
             ELSE coalesce(v.issues->>:field, 'no_issue') END AS validation_issue
    FROM latest AS s
    LEFT JOIN __WAREHOUSE_SCHEMA__.nds_v31_validated AS v ON v.source_id = s.id
)
SELECT contract_hash, CAST(:field AS text) AS field, raw_state, validation_issue, count(*) AS records
FROM classified
GROUP BY contract_hash, raw_state, validation_issue
ORDER BY contract_hash, raw_state, validation_issue;

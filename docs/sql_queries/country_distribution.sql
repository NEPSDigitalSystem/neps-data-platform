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
    SELECT s.*,
        CASE WHEN country IN ('Ghana','Sierra Leone','Tanzania') THEN country
             ELSE 'UNMAPPED_SCOPE' END AS country_scope,
        CASE WHEN NOT (CAST(payload AS jsonb) ? 'country') THEN 'ABSENT'
             WHEN CAST(payload AS jsonb)->'country' = 'null'::jsonb THEN 'JSON_NULL'
             WHEN CAST(payload AS jsonb)->'country' = '""'::jsonb THEN 'EMPTY'
             WHEN jsonb_typeof(CAST(payload AS jsonb)->'country') = 'string'
                  AND payload->>'country' IN ('1','2','3') THEN payload->>'country'
             ELSE 'UNMAPPED' END AS raw_country_code
    FROM latest AS s
), labelled AS (
    SELECT *, CASE raw_country_code WHEN '1' THEN 'Ghana' WHEN '2' THEN 'Sierra Leone'
                   WHEN '3' THEN 'Tanzania' ELSE NULL END AS raw_country_label
    FROM classified
)
SELECT contract_hash, country_scope, raw_country_code,
    CASE WHEN raw_country_code IN ('ABSENT','JSON_NULL','EMPTY') THEN 'omitted'
         WHEN raw_country_label IS NULL OR country_scope = 'UNMAPPED_SCOPE' THEN 'unmapped'
         WHEN raw_country_label = country_scope THEN 'match' ELSE 'mismatch' END AS country_consistency,
    count(*) AS latest_records,
    count(DISTINCT identity->>'participant') AS native_source_participants,
    count(DISTINCT nullif(nds_participant_id,'')) AS mapped_nds_participants
FROM labelled
GROUP BY contract_hash, country_scope, raw_country_code, raw_country_label
ORDER BY contract_hash, country_scope, raw_country_code;

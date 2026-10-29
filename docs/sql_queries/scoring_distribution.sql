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
, candidates AS (
    SELECT s.id AS source_id, s.contract_hash, s.source_metadata_hash, s.country,
        count(d.id) AS candidate_count, min(d.id) AS candidate_id
    FROM latest AS s
    LEFT JOIN __WAREHOUSE_SCHEMA__.nds_v31_derived AS d ON d.source_id = s.id
      AND d.result->>'algorithm_version' = :algorithm_version
      AND d.result->>'metadata_policy_version' = :metadata_policy_version
    GROUP BY s.id, s.contract_hash, s.source_metadata_hash, s.country
), selected AS (
    SELECT c.*, CAST(d.result AS jsonb) AS result
    FROM candidates AS c
    LEFT JOIN __WAREHOUSE_SCHEMA__.nds_v31_derived AS d
      ON c.candidate_count = 1 AND d.id = c.candidate_id
), expanded AS (
    SELECT s.*, names.score_name, s.result->'scores'->names.score_name AS entry
    FROM selected AS s
    CROSS JOIN (VALUES ('EPI'),('ESI'),('SBI'),('MHDI'),('K6_total'),
                       ('BRS_100'),('MSPSS_100'),('GSE_100'),('PFI'),('NSES')) AS names(score_name)
), parsed AS (
    SELECT *,
      CASE WHEN jsonb_typeof(entry->'value') = 'object' THEN
        CASE WHEN ((entry->'value') - 'numerator' - 'denominator') = '{}'::jsonb
             AND jsonb_typeof(entry->'value'->'numerator') = 'number'
             AND jsonb_typeof(entry->'value'->'denominator') = 'number'
             AND entry->'value'->>'numerator' ~ '^-?[0-9]+$'
             AND entry->'value'->>'denominator' ~ '^[0-9]+$'
           THEN (entry->'value'->>'numerator')::numeric /
                nullif((entry->'value'->>'denominator')::numeric, 0) END END AS score_value,
      CASE WHEN jsonb_typeof(entry->'issues') = 'array'
           THEN jsonb_array_length(entry->'issues') ELSE NULL END AS issue_count,
      CASE WHEN jsonb_typeof(entry->'issues') = 'array' THEN NOT EXISTS (
        SELECT 1 FROM jsonb_array_elements(entry->'issues') AS reason
        WHERE jsonb_typeof(reason) IS DISTINCT FROM 'object'
          OR jsonb_typeof(reason->'field') IS DISTINCT FROM 'string'
          OR coalesce(reason->>'field','') = ''
          OR coalesce(reason->>'state','') NOT IN ('missing','refused','unknown',
               'not_applicable','invalid','applicability_unverified')
      ) ELSE false END AS reasons_valid
    FROM expanded
), classified AS (
    SELECT *, CASE
      WHEN candidate_count = 0 THEN 'unscored'
      WHEN candidate_count > 1 THEN 'ambiguous'
      WHEN result->>'contract_sha256' IS DISTINCT FROM contract_hash THEN 'malformed'
      WHEN entry->'value' = 'null'::jsonb AND issue_count > 0 AND reasons_valid THEN 'unavailable'
      WHEN score_value IS NULL OR issue_count IS DISTINCT FROM 0 OR NOT reasons_valid THEN 'malformed'
      WHEN score_value < 0 OR score_value > CASE WHEN score_name = 'K6_total' THEN 24 ELSE 100 END
        OR (score_name = 'K6_total' AND score_value <> trunc(score_value)) THEN 'out_of_range'
      ELSE 'valid' END AS score_state
    FROM parsed
)
SELECT contract_hash, source_metadata_hash, country, score_name,
    CAST(:algorithm_version AS text) AS algorithm_version,
    CAST(:metadata_policy_version AS text) AS metadata_policy_version,
    count(*) AS latest_records,
    count(*) FILTER (WHERE score_state = 'valid') AS available,
    count(*) FILTER (WHERE score_state = 'unavailable') AS unavailable,
    count(*) FILTER (WHERE score_state = 'unscored') AS unscored,
    count(*) FILTER (WHERE score_state = 'ambiguous') AS ambiguous,
    count(*) FILTER (WHERE score_state = 'malformed') AS malformed,
    count(*) FILTER (WHERE score_state = 'out_of_range') AS out_of_range,
    avg(score_value) FILTER (WHERE score_state = 'valid') AS mean,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY score_value::double precision)
        FILTER (WHERE score_state = 'valid') AS median,
    stddev_samp(score_value) FILTER (WHERE score_state = 'valid') AS sample_sd,
    min(score_value) FILTER (WHERE score_state = 'valid') AS minimum,
    max(score_value) FILTER (WHERE score_state = 'valid') AS maximum
FROM classified
GROUP BY contract_hash, source_metadata_hash, country, score_name
ORDER BY contract_hash, source_metadata_hash, country, score_name;

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
SELECT row_number() OVER (ORDER BY identity_key, id) AS sample_ordinal,
    revision, contract_version, contract_hash,
    (SELECT count(*) FROM jsonb_object_keys(CAST(payload AS jsonb))) AS payload_key_count,
    source_metadata_hash IS NOT NULL AS metadata_hash_present,
    intake_revision_id IS NOT NULL AS intake_link_present,
    nullif(nds_participant_id,'') IS NOT NULL AS nds_mapping_present
FROM latest
WHERE :dataset_class IN ('synthetic','approved_deidentified')
ORDER BY identity_key, id
LIMIT :sample_limit;

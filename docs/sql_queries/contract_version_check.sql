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
SELECT contract_version, contract_hash,
    contract_version = :expected_contract_version AND contract_hash = :expected_contract_hash AS matches_expected_contract,
    count(*) AS retained_revisions,
    count(*) FILTER (WHERE revision_rank = 1) AS latest_records,
    count(DISTINCT source_version) AS source_version_labels,
    count(DISTINCT source_metadata_hash) AS metadata_snapshots,
    count(*) FILTER (WHERE revision_rank = 1 AND source_metadata_hash IS NULL) AS latest_missing_metadata_hash,
    count(*) FILTER (WHERE revision_rank = 1 AND intake_revision_id IS NULL) AS latest_missing_intake_link
FROM scoped
GROUP BY contract_version, contract_hash
ORDER BY contract_version, contract_hash;

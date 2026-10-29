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
SELECT
    (SELECT count(*) FROM scoped) AS retained_revisions,
    count(*) AS latest_records,
    count(DISTINCT identity->>'participant') AS native_source_participants,
    count(DISTINCT nullif(nds_participant_id, '')) AS mapped_nds_participants,
    count(*) FILTER (WHERE nullif(nds_participant_id, '') IS NULL) AS unmapped_latest_records
FROM latest;

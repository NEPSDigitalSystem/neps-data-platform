from __future__ import annotations

import pandas as pd
import structlog
from sqlalchemy import text

from etl.config import Settings
from etl.load.db import create_db_engine

logger = structlog.get_logger(__name__)


def analyze_distress_trends(settings: Settings) -> None:
    """Analyze longitudinal distress trends for participants and flag critical cases."""
    logger.info("starting_distress_trend_analysis")
    
    engine = create_db_engine(settings)
    
    # Extract records
    query = """
    SELECT record_id, month, anxiety_score, depression_score, survey_date
    FROM redcap.raw_redcap_monthly_self_report
    ORDER BY record_id, month ASC
    """
    
    try:
        df = pd.read_sql(query, engine)
    except Exception as e:
        logger.error("failed_to_read_monthly_reports", error=str(e))
        return

    if df.empty:
        logger.info("no_data_for_analysis")
        return

    # Filter out records where scores might be missing
    df = df.dropna(subset=['anxiety_score', 'depression_score'])

    flags = []
    
    for record_id, group in df.groupby("record_id"):
        if len(group) < 2:
            continue
            
        group = group.sort_values("month")
        # Get the latest score
        latest = group.iloc[-1]
        
        # Get previous average
        prev_group = group.iloc[:-1]
        prev_anxiety_avg = prev_group["anxiety_score"].mean()
        prev_depression_avg = prev_group["depression_score"].mean()
        
        flag_reason = []
        is_critical = False
        
        if prev_anxiety_avg > 0 and latest["anxiety_score"] > prev_anxiety_avg * 1.2:
            flag_reason.append("Anxiety spiked >20%")
            is_critical = True
            
        if prev_depression_avg > 0 and latest["depression_score"] > prev_depression_avg * 1.2:
            flag_reason.append("Depression spiked >20%")
            is_critical = True
            
        if is_critical:
            flags.append({
                "record_id": record_id,
                "latest_month": latest["month"],
                "flag_date": latest["survey_date"],
                "reason": " | ".join(flag_reason)
            })
            
    flags_df = pd.DataFrame(flags)
    
    with engine.begin() as conn:
        # Create schema if not exists
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS analytics"))
        
        # Write to database, overwrite old flags
        if not flags_df.empty:
            flags_df.to_sql(
                "distress_flags",
                con=conn,
                schema="analytics",
                if_exists="replace",
                index=False
            )
            logger.info("critical_trends_flagged", count=len(flags_df))
        else:
            # Create an empty table to clear old flags
            conn.execute(text("DROP TABLE IF EXISTS analytics.distress_flags"))
            logger.info("no_critical_trends_detected")


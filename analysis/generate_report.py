import pandas as pd

trend = pd.read_csv(
    "analysis/outputs/trend_summary.csv"
)

risk = pd.read_csv(
    "analysis/outputs/high_risk_participants.csv"
)

groups = pd.read_csv(
    "analysis/outputs/trajectory_groups.csv"
)

print("\n========================")
print("NEPS ANALYTICS REPORT")
print("========================")

print("\nTrend Summary")

print(
    "Baseline Stress:",
    round(
        trend.iloc[0]["perceived_stress_score"],
        2
    )
)

print(
    "Final Stress:",
    round(
        trend.iloc[-1]["perceived_stress_score"],
        2
    )
)

print(
    "Change:",
    round(
        trend.iloc[-1]["perceived_stress_score"]
        -
        trend.iloc[0]["perceived_stress_score"],
        2
    )
)

print("\nRisk Monitoring")

print(
    "High Risk Participants:",
    len(risk)
)

print("\nTrajectory Groups")

print(
    groups["trajectory_group"]
    .value_counts()
)

print("\nReport Complete")

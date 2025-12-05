import streamlit as st
import pandas as pd
from staffing import staffing_from_forecast

import random
import pandas as pd
from datetime import datetime, timedelta
from erlang import erlang_c, required_agents

st.title("Workforce Auto-Scheduling App")

uploaded_file = st.file_uploader("Upload 7-day interval forecast (Excel)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("Uploaded forecast data:", df.head())

    shrinkage = st.number_input("Shrinkage %", min_value=0, max_value=100, value=30)
    interval_minutes = st.selectbox("Interval", [30, 15], index=0)

    if st.button("Generate Schedule"):
        # 1 — convert forecast to staffing
        results = staffing_from_forecast(df, shrinkage, interval_minutes)

        weekly_intervals = []
        for day, info in results.items():
            for r in info["staff"]:
                weekly_intervals.append({
                    "interval_start": f"{day} {r['interval_start']}",
                    "required_after_shrinkage": r["required_after_shrinkage"]
                })

        # 2 — build roster
        out_path, roster_df, inflex_df, sp_df = build_weekly_roster_auto(
            weekly_intervals,
            agents=None,
            out_path="weekly_roster.xlsx",
            shift_length_hours=9,
            start_hours=list(range(24))  # random start hour from 0–23
        )

        # 3 — output results
        with open(out_path, "rb") as f:
            st.download_button("Download Weekly Roster", f, "weekly_roster.xlsx")

        st.subheader("Generated Roster")
        st.dataframe(roster_df)

        st.subheader("Inflex Report")
        st.dataframe(inflex_df)

        st.subheader("Shift Pools")
        st.dataframe(sp_df)

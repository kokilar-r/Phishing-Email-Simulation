import streamlit as st
import sqlite3
import os
import pandas as pd
import plotly.express as px
st.set_page_config(
    page_title="Phishing Awareness Dashboard",
    page_icon="📊",
    layout="wide")
st.title("📊 Phishing Awareness Dashboard")
st.caption("Cyber Security Awareness Training")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_NAME = os.path.join(BASE_DIR, "phishing_simulation.db")
def load_responses():
    if not os.path.exists(DATABASE_NAME):
        return pd.DataFrame()
    connection = sqlite3.connect(DATABASE_NAME)
    try:
        df = pd.read_sql_query("""SELECT email_name, user_answer, correct_answer,result, participant_id FROM responses
            ORDER BY id""",connection)
    except sqlite3.Error:
        df = pd.DataFrame()
    finally:
        connection.close()
    return df
if st.button("🔄 Refresh Dashboard"):
    st.rerun()
df = load_responses()
if df.empty:
    st.info("No responses found. Complete the simulation first.")
    st.stop()
df["result"] = df["result"].astype(str).str.strip().str.title()
df["email_name"] = df["email_name"].astype(str)
correct_count = int((df["result"] == "Correct").sum())
wrong_count = int((df["result"] == "Wrong").sum())
total_responses = len(df)
scored_count = correct_count + wrong_count
awareness_score = (correct_count / scored_count * 100 if scored_count else 0)
st.subheader("📌 Simulation Summary")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Responses", total_responses)
col2.metric("Correct Answers", correct_count)
col3.metric("Wrong Answers", wrong_count)
col4.metric("Awareness Score", f"{awareness_score:.1f}%")
st.divider()
st.subheader("🥧 Correct vs Wrong Answers")
pie_data = pd.DataFrame({
    "Result": ["Correct", "Wrong"],
    "Count": [correct_count, wrong_count]})
pie_data = pie_data[pie_data["Count"] > 0]
if not pie_data.empty:
    fig_pie = px.pie(
        pie_data,
        names="Result",
        values="Count",
        title="Answer Distribution",
        hole=0.35,
        color="Result",
        color_discrete_map={
            "Correct": "#2EAD66",
            "Wrong": "#E74C3C"
        }
    )

    fig_pie.update_traces(
        textposition="inside",
        textinfo="label+percent+value"
    )

    st.plotly_chart(fig_pie, use_container_width=True)

st.divider()

# BAR CHART
st.subheader("📊 Email-wise Performance")

chart_data = df[df["result"].isin(["Correct", "Wrong"])]

if not chart_data.empty:
    email_summary = (
        chart_data.groupby(["email_name", "result"])
        .size()
        .reset_index(name="Count")
    )

    fig_bar = px.bar(
        email_summary,
        x="email_name",
        y="Count",
        color="result",
        barmode="group",
        text="Count",
        title="Correct and Wrong Answers by Email",
        labels={
            "email_name": "Email",
            "Count": "Number of Responses",
            "result": "Answer Result"
        },
        color_discrete_map={
            "Correct": "#2EAD66",
            "Wrong": "#E74C3C"
        }
    )

    fig_bar.update_traces(textposition="outside")
    fig_bar.update_layout(
        xaxis_title="Email",
        yaxis_title="Number of Responses",
        legend_title="Result"
    )

    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("No scored answers available for the bar chart.")

st.divider()

# RESPONSE DETAILS
st.subheader("📋 Response Details")

display_df = df[
    [
        "email_name",
        "user_answer",
        "correct_answer",
        "result",
        "participant_id"
    ]
].copy()

display_df.columns = [
    "Email",
    "Your Answer",
    "Correct Answer",
    "Result",
    "Participant ID"
]

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)

# DOWNLOAD CSV
csv_data = display_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Download Results as CSV",
    data=csv_data,
    file_name="phishing_awareness_results.csv",
    mime="text/csv"
)

st.caption(
    "Educational phishing awareness simulation. "
    "Use only with authorized participants and sample emails."
)

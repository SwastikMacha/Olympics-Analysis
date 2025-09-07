import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff

import preprocessor, helper

# ----------------------------
# Load and preprocess data
# ----------------------------
df = pd.read_csv("athlete_events.csv")
region_df = pd.read_csv("noc_regions.csv")
df = preprocessor.preprocess(df, region_df)

# ----------------------------
# Sidebar Navigation
# ----------------------------
st.sidebar.title("🏅 Olympics Analysis")
st.sidebar.image(
    "https://e7.pngegg.com/pngimages/1020/402/png-clipart-2024-summer-olympics-brand-circle-area-olympic-rings-olympics-logo-text-sport.png",
    use_container_width=True
)

user_menu = st.sidebar.radio(
    "📌 Select an Option",
    ("Medal Tally", "Overall Analysis", "Country-wise Analysis", "Athlete-wise Analysis")
)

# ----------------------------
# Medal Tally
# ----------------------------
if user_menu == "Medal Tally":
    st.sidebar.header("Filters")
    years, countries = helper.country_year_list(df)

    selected_year = st.sidebar.selectbox("Select Year", years)
    selected_country = st.sidebar.selectbox("Select Country", countries)

    medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)

    # Dynamic title
    if selected_year == "Overall" and selected_country == "Overall":
        st.title("🏆 Overall Medal Tally")
    elif selected_year != "Overall" and selected_country == "Overall":
        st.title(f"Medal Tally in {selected_year} Olympics")
    elif selected_year == "Overall" and selected_country != "Overall":
        st.title(f"{selected_country} – Overall Performance")
    else:
        st.title(f"{selected_country} Performance in {selected_year} Olympics")

    st.table(medal_tally)

# ----------------------------
# Overall Analysis
# ----------------------------
if user_menu == "Overall Analysis":
    editions = df["Year"].nunique() - 1
    cities = df["City"].nunique()
    sports = df["Sport"].nunique()
    events = df["Event"].nunique()
    athletes = df["Name"].nunique()
    nations = df["region"].nunique()

    st.title("📊 Top Statistics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Editions", editions)
    col2.metric("Host Cities", cities)
    col3.metric("Sports", sports)

    col1, col2, col3 = st.columns(3)
    col1.metric("Events", events)
    col2.metric("Nations", nations)
    col3.metric("Athletes", athletes)

    # Nations over time
    nations_over_time = helper.data_over_time(df, "region")
    st.plotly_chart(px.line(nations_over_time, x="Year", y="Count", title="Participating Nations Over the Years"))

    # Events over time
    events_over_time = helper.data_over_time(df, "Event")
    st.plotly_chart(px.line(events_over_time, x="Year", y="Count", title="Events Over the Years"))

    # Athletes over time
    athlete_over_time = helper.data_over_time(df, "Name")
    st.plotly_chart(px.line(athlete_over_time, x="Year", y="Count", title="Athletes Over the Years"))

    # Heatmap of events by sport
    st.subheader("Events Distribution by Sport & Year")
    fig, ax = plt.subplots(figsize=(20, 20))
    pivot_df = df.drop_duplicates(["Year", "Sport", "Event"])
    sns.heatmap(
        pivot_df.pivot_table(index="Sport", columns="Year", values="Event", aggfunc="count").fillna(0).astype(int),
        annot=True,
        ax=ax
    )
    st.pyplot(fig)

    # Most successful athletes
    st.subheader("Most Successful Athletes")
    sport_list = sorted(df["Sport"].unique().tolist())
    sport_list.insert(0, "Overall")
    selected_sport = st.selectbox("Select a Sport", sport_list)
    st.table(helper.most_successful(df, selected_sport))

# ----------------------------
# Country-wise Analysis
# ----------------------------
if user_menu == "Country-wise Analysis":
    st.sidebar.header("Filters")
    country_list = sorted(df["region"].dropna().unique().tolist())
    selected_country = st.sidebar.selectbox("Select a Country", country_list)

    # Medal trend
    country_df = helper.yearwise_medal_tally(df, selected_country)
    st.title(f"{selected_country} – Medal Tally Over the Years")
    st.plotly_chart(px.line(country_df, x="Year", y="Medal"))

    # Heatmap by sport
    st.subheader(f"{selected_country} Performance by Sport")
    fig, ax = plt.subplots(figsize=(20, 20))
    heatmap_data = helper.country_event_heatmap(df, selected_country)

    if heatmap_data.empty:
        st.warning(f"No data available to display heatmap for {selected_country}.")
    else:
        sns.heatmap(heatmap_data, annot=True, ax=ax)
    st.pyplot(fig)

    # Top athletes
    st.subheader(f"Top 10 Athletes of {selected_country}")
    st.table(helper.most_successful_countrywise(df, selected_country))

# ----------------------------
# Athlete-wise Analysis
# ----------------------------
if user_menu == "Athlete-wise Analysis":
    athlete_df = df.drop_duplicates(subset=["Name", "region"])

    # Age distribution
    x1 = athlete_df["Age"].dropna()
    x2 = athlete_df[athlete_df["Medal"] == "Gold"]["Age"].dropna()
    x3 = athlete_df[athlete_df["Medal"] == "Silver"]["Age"].dropna()
    x4 = athlete_df[athlete_df["Medal"] == "Bronze"]["Age"].dropna()

    fig = ff.create_distplot([x1, x2, x3, x4],
                             ["Overall Age", "Gold Medalists", "Silver Medalists", "Bronze Medalists"],
                             show_hist=False, show_rug=False)
    fig.update_layout(autosize=False, width=1000, height=600)
    st.subheader("Age Distribution of Athletes")
    st.plotly_chart(fig)

    # Age distribution by sport
    st.subheader("Age Distribution of Gold Medalists by Sport")
    famous_sports = ["Basketball", "Judo", "Football", "Athletics", "Swimming", "Badminton", "Sailing",
                     "Gymnastics", "Handball", "Weightlifting", "Wrestling", "Hockey", "Rowing", "Fencing",
                     "Shooting", "Boxing", "Cycling", "Tennis", "Volleyball", "Table Tennis", "Baseball"]
    x, names = [], []
    for sport in famous_sports:
        temp_df = athlete_df[athlete_df["Sport"] == sport]
        x.append(temp_df[temp_df["Medal"] == "Gold"]["Age"].dropna())
        names.append(sport)
    fig = ff.create_distplot(x, names, show_hist=False, show_rug=False)
    fig.update_layout(autosize=False, width=1000, height=600)
    st.plotly_chart(fig)

    # Height vs Weight
    st.subheader("Height vs Weight Analysis")
    sport_list = sorted(df["Sport"].unique().tolist())
    sport_list.insert(0, "Overall")
    selected_sport = st.selectbox("Select a Sport", sport_list)
    temp_df = helper.weight_v_height(df, selected_sport)
    fig, ax = plt.subplots()
    sns.scatterplot(x="Weight", y="Height", data=temp_df, hue="Medal", style="Sex", s=60, ax=ax)
    st.pyplot(fig)

    # Male vs Female participation
    st.subheader("Male vs Female Participation Over the Years")
    final = helper.men_vs_women(df)
    fig = px.line(final, x="Year", y=["Male", "Female"], title="Participation Trends")
    fig.update_layout(autosize=False, width=1000, height=600)
    st.plotly_chart(fig)

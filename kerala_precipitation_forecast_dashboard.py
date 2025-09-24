import streamlit as st
import folium
import json
from streamlit_folium import folium_static
import pandas as pd
import plotly.express as px

# --- Data ---
future_years = [2025, 2026, 2027, 2028, 2029, 2030]
future_predictions = [53929.17, 52886.41, 54020.01, 54448.36, 54710.53, 55310.82]

# --- Create DataFrame ---
df = pd.DataFrame({
    "Year": future_years,
    "Precipitation (mm)": future_predictions
})

# --- Helper Functions ---
def get_color(value):
    if value > 55000:
        return '#08306b'
    elif value > 54500:
        return '#08519c'
    elif value > 54000:
        return '#2171b5'
    elif value > 53500:
        return '#4292c6'
    elif value > 53000:
        return '#6baed6'
    elif value > 52000:
        return '#9ecae1'
    else:
        return '#c6dbef'

def get_alert_category(value):
    if value > 55000:
        return "🚨 Very Heavy"
    elif value > 54500:
        return "🔴 Heavy"
    elif value > 53500:
        return "🟠 Medium"
    elif value > 52000:
        return "🟡 Light"
    else:
        return "🟢 Normal"

# --- Load GeoJSON ---
with open("state.geojson", "r", encoding="utf-8") as f:
    kerala_geojson = json.load(f)

# --- Streamlit Setup ---
st.set_page_config(page_title="🌧️ Kerala Precipitation Forecast", layout="wide")
st.title(":droplet: Kerala Long-Term Precipitation Outlook (2025–2030)")
st.markdown("<h5 style='color:gray;'>Forecast. Visualize. Compare. Understand Kerala's Rainfall Future.</h5>", unsafe_allow_html=True)

# --- Sidebar View Option ---
view_option = st.sidebar.radio("Choose View:", ["🌐 Map View", "📊 Chart View"])

# --- Sidebar Statistics ---
st.sidebar.markdown("---")
st.sidebar.subheader(":bar_chart: Summary")
st.sidebar.write(f"**Max:** {max(future_predictions):,.2f} mm")
st.sidebar.write(f"**Min:** {min(future_predictions):,.2f} mm")
st.sidebar.write(f"**Average:** {sum(future_predictions)/len(future_predictions):,.2f} mm")

# --- Map Tiles ---
tile_options = {
    "CartoDB Positron": ("CartoDB positron", None),
    "OpenStreetMap": ("OpenStreetMap", None),
    "Stamen Terrain": ("Stamen Terrain", "Map tiles by Stamen Design, CC BY 3.0 — Map data © OpenStreetMap contributors"),
    "Stamen Toner": ("Stamen Toner", "Map tiles by Stamen Design, CC BY 3.0 — Map data © OpenStreetMap contributors")
}
selected_tile = st.sidebar.selectbox("🛰️ Select Map Tile Style", list(tile_options.keys()))
map_tile, map_attr = tile_options[selected_tile]

# --- User Forecast Input ---
st.sidebar.markdown("---")
st.sidebar.subheader("📲 Your Forecast Inputs")
user_input = []
for year in future_years:
    val = st.sidebar.number_input(f"{year} (mm):", min_value=0.0, value=0.0, step=100.0)
    user_input.append(val)

# --- Map View ---
if view_option == "🌐 Map View":
    selected_year = st.slider("Select Year", min_value=2025, max_value=2030, step=1)
    idx = future_years.index(selected_year)
    selected_value = future_predictions[idx]

    # Alert
    st.subheader(f"🔔 {selected_year} Rainfall Alert: {get_alert_category(selected_value)}")
    if selected_value > 55000:
        st.error(f"🚨 Alert: Very High Rainfall Predicted — {selected_value:.2f} mm")

    # Map
    if map_attr:
        m = folium.Map(location=[10.5, 76.5], zoom_start=7, tiles=map_tile, attr=map_attr)
    else:
        m = folium.Map(location=[10.5, 76.5], zoom_start=7, tiles=map_tile)

    folium.GeoJson(
        kerala_geojson,
        style_function=lambda x, val=selected_value: {
            'fillColor': get_color(val),
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.6,
        }
    ).add_to(m)

    folium.Marker(
        location=[10.15, 76.6],
        popup=f"{selected_year} Predicted: {selected_value:.2f} mm", 
        icon=folium.Icon(color="blue", icon="cloud")
    ).add_to(m)

    folium_static(m, width=900, height=600)

# --- Chart View ---
elif view_option == "📊 Chart View":
    chart_type = st.selectbox("📊 Select Chart Type", [
        "📊 Bar Chart (Model Only)",
        "📈 Line Chart (Model Only)",
        "🧱 Stacked Bar Chart (Model vs You)",
        "📉 Multi-Line Chart (Model vs You)"
    ])

    # --- Determine year-specific alert for first year (2025) ---
    alert_year = future_years[0]
    alert_value = future_predictions[0]
    alert_category = get_alert_category(alert_value)

    # --- Rainfall Alert Banner ---
    st.markdown(f"""
    <div style='background-color:#fff8e1; padding:10px; border-left:6px solid #ffb300; border-radius:6px; margin-top:10px; margin-bottom:10px;'>
        🔔 <b style='color:#333;'>Rainfall Alert ({alert_year}):</b> 
        <span style='color:#d84315; font-weight:bold;'>{alert_category}</span> — 
        <span style='color:#333;'>Predicted:</span> <b style='color:#333;'>{alert_value:.2f} mm</b>
    </div>
    """, unsafe_allow_html=True)

    # --- Render Charts ---
    if chart_type == "📊 Bar Chart (Model Only)":
        fig = px.bar(df, x="Year", y="Precipitation (mm)", color="Year",
                     title="Bar Chart: Model Predicted Precipitation",
                     color_discrete_sequence=px.colors.sequential.Blues)
        st.plotly_chart(fig, use_container_width=True)
        st.download_button("📥 Download Chart", fig.to_image(format="png"), file_name="bar_chart.png")

    elif chart_type == "📈 Line Chart (Model Only)":
        fig = px.line(df, x="Year", y="Precipitation (mm)", markers=True,
                      title="Line Chart: Model Predicted Precipitation",
                      color_discrete_sequence=["#1f77b4"])
        fig.update_traces(line=dict(width=3))
        st.plotly_chart(fig, use_container_width=True)
        st.download_button("📥 Download Chart", fig.to_image(format="png"), file_name="line_chart.png")

    elif chart_type == "🧱 Stacked Bar Chart (Model vs You)":
        comp_df = pd.DataFrame({
            "Year": future_years * 2,
            "Source": ["Model"] * 6 + ["User"] * 6,
            "Precipitation (mm)": future_predictions + user_input
        })
        fig = px.bar(comp_df, x="Year", y="Precipitation (mm)",
                     color="Source", barmode="group",
                     title="Stacked Bar Chart: Model vs Your Prediction",
                     color_discrete_map={"Model": "skyblue", "User": "white"})
        st.plotly_chart(fig, use_container_width=True)
        st.download_button("📥 Download Chart", fig.to_image(format="png"), file_name="stacked_bar_chart.png")

    elif chart_type == "📉 Multi-Line Chart (Model vs You)":
        df_multi = pd.DataFrame({
            "Year": future_years * 2,
            "Precipitation (mm)": future_predictions + user_input,
            "Source": ["Model"] * 6 + ["User"] * 6
        })
        fig = px.line(df_multi, x="Year", y="Precipitation (mm)", color="Source",
                      markers=True,
                      title="Multiple Line Chart: Model vs Your Forecast",
                      color_discrete_map={"Model": "skyblue", "User": "white"})
        fig.update_traces(line=dict(width=3))
        st.plotly_chart(fig, use_container_width=True)
        st.download_button("📥 Download Chart", fig.to_image(format="png"), file_name="multi_line_chart.png")

    # --- Trend Summary ---
    percent_change = (df['Precipitation (mm)'].iloc[-1] - df['Precipitation (mm)'].iloc[0]) / df['Precipitation (mm)'].iloc[0] * 100
    max_year = df.loc[df['Precipitation (mm)'].idxmax(), 'Year']
    min_year = df.loc[df['Precipitation (mm)'].idxmin(), 'Year']
    st.markdown(f"""
    <div style='background-color:#f1f1f1; padding:12px; border-radius:8px; color:#333;'>
        <b>Trend Summary:</b><br>
        ➤ Overall change from 2025 to 2030: <b>{percent_change:.2f}%</b><br>
        ➤ Highest rainfall predicted in: <b>{max_year}</b><br>
        ➤ Lowest rainfall predicted in: <b>{min_year}</b>
    </div>
    """, unsafe_allow_html=True)

# --- Trend Table ---
st.markdown("---")
st.subheader("📉 Trend Insights")
trend_df = df.copy()
trend_df['Change (mm)'] = trend_df['Precipitation (mm)'].diff()
trend_df['Percent Change (%)'] = trend_df['Precipitation (mm)'].pct_change() * 100
trend_df['Alert Level'] = trend_df['Precipitation (mm)'].apply(get_alert_category)
st.dataframe(trend_df.round(2), use_container_width=True)

# --- Forecast Comparison ---
st.markdown("---")
st.subheader("📊 Forecast Comparison Table")
comparison_df = pd.DataFrame({
    "Year": future_years,
    "Model Prediction (mm)": future_predictions,
    "Your Prediction (mm)": user_input
})
comparison_df["Difference"] = comparison_df["Your Prediction (mm)"] - comparison_df["Model Prediction (mm)"]
comparison_df["Alert"] = comparison_df["Model Prediction (mm)"].apply(get_alert_category)
st.dataframe(comparison_df.round(2), use_container_width=True)

# --- Download Forecast Data ---
st.markdown("---")
st.subheader(":page_facing_up: Forecast Data Table")
st.dataframe(df, use_container_width=True)

csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📂 Download CSV",
    data=csv,
    file_name='kerala_precipitation_forecast.csv',
    mime='text/csv'
)

# --- Footer ---
st.markdown("---")
st.markdown("© 2025 Gayathri G Murali | All rights reserved.")

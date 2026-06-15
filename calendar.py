import streamlit as st
import pandas as pd

# Set up page config for a polished dashboard look
st.set_page_config(page_title="Course Dashboard", layout="wide")
st.title("📅 Course Schedule & Directory")

# 1. Fetch your Google Sheet data
# Replace with your actual Sheet ID and Sheet Name
SHEET_ID = "15nhId0BxuKaO_6fhjccMuM8PvrSPy0mi4t6GWVaNvNc"
SHEET_NAME = "July2026"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

@st.cache_data(ttl=600) # Caches data for 10 minutes so it's lightning fast
def load_data():
    return pd.read_csv(csv_url)

df = load_data()

# 2. Create the two-tab layout
tab1, tab2 = st.tabs(["🗓️ Calendar View", "🔍 Course Directory"])

# --- TAB 1: CALENDAR VIEW ---
with tab1:
    st.subheader("Upcoming Calendar Entries")
    
    # Select only the columns required for the calendar tab
    calendar_df = df[["Course", "Date", "Time", "Location", "Mode"]].copy()
    
    # Custom color-coding function for the "Mode" column
    def color_mode(val):
        if val == 'Online':
            return 'background-color: #d1ecf1; color: #0c5460; font-weight: bold;'
        elif val == 'Presencial':
            return 'background-color: #d4edda; color: #155724; font-weight: bold;'
        elif val == 'Self-Paced':
            return 'background-color: #fff3cd; color: #856404; font-weight: bold;'
        return ''

    # Render a beautiful, interactive data table
    st.dataframe(
        calendar_df.style.applymap(color_mode, subset=['Mode']),
        use_container_width=True,
        hide_index=True
    )

# --- TAB 2: EXPANDABLE PANEL SUMMARY ---
with tab2:
    st.subheader("Courses Grouped by Name")
    
    # Get unique course names to group them
    unique_courses = df["Course"].dropna().unique()
    
    for course in unique_courses:
        # Filter rows belonging to this specific course group
        course_data = df[df["Course"] == course]
        
        # Create an elegant native expandable accordion panel
        with st.expander(f"📚 {course} ({len(course_data)} sessions/entries)"):
            for idx, row in course_data.iterrows():
                # Display all detailed metrics neatly inside the panel
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Date/Time:** {row['Date']} @ {row['Time']}")
                    st.markdown(f"**Mode:** `{row['Mode']}`")
                with col2:
                    st.markdown(f"**Location:** {row['Location']}")
                    st.markdown(f"**Registration Open:** {row['Registration Open']}")
                with col3:
                    st.markdown(f"**Registered:** {row['Registered?']}")
                    if pd.notna(row['Link']):
                        st.markdown(f"[🔗 Access Link]({row['Link']})")
                st.divider() # Sub-divider between multiple sessions of the same course

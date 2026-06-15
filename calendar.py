import streamlit as st
import pandas as pd
from streamlit_calendar import calendar

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
    st.subheader("🗓️ Course Schedule")

    # 1. Display the Color-Coded Legend above the calendar
    st.markdown("#### Mode Legend")
    col_leg1, col_leg2, col_leg3 = st.columns(3)
    with col_leg1:
        st.markdown("🔵 **Online**")
    with col_leg2:
        st.markdown("🟢 **Presencial**")
    with col_leg3:
        st.markdown("🟡 **Self-Paced**")
    st.write("") # Spacer

    # 2. Map Modes to beautiful Hex Colors (Background & Text)
    color_map = {
        "Online": {"bg": "#1e3a8a", "text": "#ffffff"},      # Deep Blue
        "Presencial": {"bg": "#065f46", "text": "#ffffff"},  # Deep Green
        "Self-Paced": {"bg": "#b45309", "text": "#ffffff"}   # Warm Amber
    }

    # 3. Transform the Google Sheet data into FullCalendar Event objects
    calendar_events = []
    
    for idx, row in df.iterrows():
        # Skip if there's no valid date
        if pd.isna(row['Date']):
            continue
            
        # Clean up date format (Ensure it's YYYY-MM-DD string)
        try:
            date_str = pd.to_datetime(row['Date']).strftime('%Y-%m-%d')
        except:
            continue # Skip row if date is unparseable

        # Construct the layout inside the visual 'pill'
        # e.g., "Python Basics | 14:00 | Room 4B" or just "SQL Intro | 10:00"
        time_info = f" | {row['Time']}" if pd.notna(row['Time']) else ""
        loc_info = f" @ {row['Location']}" if (pd.notna(row['Location']) and str(row['Location']).strip().lower() != 'nan') else ""
        pill_title = f"{row['Course']}{time_info}{loc_info}"

        # Determine pill coloring based on the course mode
        mode = row['Mode'] if pd.notna(row['Mode']) else "Online"
        colors = color_map.get(mode, {"bg": "#374151", "text": "#ffffff"})

        # Build the event dictionary structure expected by FullCalendar
        event = {
            "title": pill_title,
            "start": date_str,
            "end": date_str,
            "backgroundColor": colors["bg"],
            "textColor": colors["text"],
            "borderColor": colors["bg"],
            "allDay": True # Keeps it neatly displayed as a banner row/pill across the day cell
        }
        calendar_events.append(event)

    # 4. Configure Calendar Options
    calendar_options = {
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridMonth,dayGridWeek"
        },
        "initialView": "dayGridMonth",
        "selectable": True,
        "editable": False
    }

    # 5. Inject custom styling to make sure pills look modern and sleek
    custom_css = """
        .fc-event {
            padding: 4px 6px;
            font-size: 0.85rem !important;
            border-radius: 6px !important;
            font-weight: 500 !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
    """

    # 6. Render the Component
    calendar(
        events=calendar_events,
        options=calendar_options,
        custom_css=custom_css
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

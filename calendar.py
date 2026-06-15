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

    # 1. Legend
    st.markdown("#### Mode Legend")
    col_leg1, col_leg2, col_leg3 = st.columns(3)
    with col_leg1: st.markdown("🔵 **Online**")
    with col_leg2: st.markdown("🟢 **Presencial**")
    with col_leg3: st.markdown("🟡 **Self-Paced**")
    st.write("") 

    # Colors mapping
    color_map = {
        "Online": {"bg": "#1e3a8a", "text": "#ffffff"},
        "Presencial": {"bg": "#065f46", "text": "#ffffff"},
        "Self-Paced": {"bg": "#b45309", "text": "#ffffff"}
    }

    # 2. Build Events List & embed extended properties for the click handler
    calendar_events = []
    for idx, row in df.iterrows():
        if pd.isna(row['Date']):
            continue
        try:
            date_str = pd.to_datetime(row['Date']).strftime('%Y-%m-%d')
        except:
            continue

        time_info = f" | {row['Time']}" if pd.notna(row['Time']) else ""
        loc_info = f" @ {row['Location']}" if (pd.notna(row['Location']) and str(row['Location']).strip().lower() != 'nan') else ""
        pill_title = f"{row['Course']}{time_info}{loc_info}"

        mode = row['Mode'] if pd.notna(row['Mode']) else "Online"
        colors = color_map.get(mode, {"bg": "#374151", "text": "#ffffff"})

        event = {
            "title": pill_title,
            "start": date_str,
            "end": date_str,
            "backgroundColor": colors["bg"],
            "textColor": colors["text"],
            "borderColor": colors["bg"],
            "allDay": True,
            # We pass extra details inside 'extendedProps' to capture them on click
            "extendedProps": {
                "course_name": str(row['Course']),
                "time": str(row['Time']) if pd.notna(row['Time']) else "N/A",
                "location": str(row['Location']) if pd.notna(row['Location']) else "N/A",
                "mode": mode,
                "link": str(row['Link']) if pd.notna(row['Link']) else "",
                "registered": str(row['Registered?']) if pd.notna(row['Registered?']) else "No",
                "reg_open": str(row['Registration Open']) if pd.notna(row['Registration Open']) else "N/A"
            }
        }
        calendar_events.append(event)

    calendar_options = {
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridMonth,dayGridWeek"
        },
        "initialView": "dayGridMonth",
        "selectable": True,
    }

    custom_css = """
        .fc-event { padding: 4px 6px; font-size: 0.85rem !important; border-radius: 6px !important; cursor: pointer; }
    """

    # 3. Render calendar component and catch its return state
    state = calendar(
        events=calendar_events,
        options=calendar_options,
        custom_css=custom_css,
        key="interactive_calendar" # Fixed key preserves component state
    )

    # 4. The Interactivity Layer: Catch the click event details
    # When a user clicks a pill, state['eventClick'] populates dynamically
    if state and "eventClick" in state:
        event_data = state["eventClick"]["event"]
        props = event_data.get("extendedProps", {})

        st.write("---")
        # Generate a clean inspection panel for the clicked item
        with st.container(border=True):
            st.markdown(f"### 🔍 Session Details: **{props.get('course_name')}**")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"**⏰ Time:** {props.get('time')}")
                st.markdown(f"**📍 Location:** {props.get('location')}")
            with c2:
                st.markdown(f"**💻 Mode:** `{props.get('mode')}`")
                st.markdown(f"**📝 Registration Status:** {props.get('reg_open')}")
            with c3:
                st.markdown(f"**✅ Registered?:** {props.get('registered')}")
                # Render a clickable primary button if a valid registration hyperlink exists
                link_url = props.get('link')
                if link_url and link_url.startswith("http"):
                    st.link_button("🔗 Open Registration Link", link_url, use_container_width=True)
                else:
                    st.caption("No link available for this session.")
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

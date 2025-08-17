import streamlit as st
import requests
import json
from datetime import datetime
import math
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Hardcoded users for login (change passwords to something secret)
USERS = {
    "husband": "password1",  # Change this
    "wife": "password2"      # Change this
}

# List of all 52 weeks for 2025 Come Follow Me (Doctrine and Covenants)
weeks = [
    {"number": 1, "dates": "December 30–January 5", "title": "The Restoration of the Fulness of the Gospel of Jesus Christ", "references": "Restoration Proclamation"},
    {"number": 2, "dates": "January 6–12", "title": "Hearken, O Ye People", "references": "Doctrine and Covenants 1"},
    {"number": 3, "dates": "January 13–19", "title": "I Saw a Pillar of Light", "references": "Joseph Smith—History 1:1–26"},
    {"number": 4, "dates": "January 20–26", "title": "The Hearts of the Children Shall Turn to Their Fathers", "references": "Doctrine and Covenants 2; Joseph Smith—History 1:27–65"},
    {"number": 5, "dates": "January 27–February 2", "title": "My Work Shall Go Forth", "references": "Doctrine and Covenants 3–5"},
    {"number": 6, "dates": "February 3–9", "title": "This Is the Spirit of Revelation", "references": "Doctrine and Covenants 6–9"},
    {"number": 7, "dates": "February 10–16", "title": "That You May Come Off Conqueror", "references": "Doctrine and Covenants 10–11"},
    {"number": 8, "dates": "February 17–23", "title": "Upon You My Fellow Servants", "references": "Doctrine and Covenants 12–13; Joseph Smith—History 1:66–75"},
    {"number": 9, "dates": "February 24–March 2", "title": "The Worth of Souls Is Great", "references": "Doctrine and Covenants 14–17"},
    {"number": 10, "dates": "March 3–9", "title": "Stand as a Witness", "references": "Doctrine and Covenants 18–19"},
    {"number": 11, "dates": "March 10–16", "title": "The Rise of the Church of Christ", "references": "Doctrine and Covenants 20–22"},
    {"number": 12, "dates": "March 17–23", "title": "Strengthen the Church", "references": "Doctrine and Covenants 23–26"},
    {"number": 13, "dates": "March 24–30", "title": "All Things Must Be Done in Order", "references": "Doctrine and Covenants 27–28"},
    {"number": 14, "dates": "March 31–April 6", "title": "Jesus Christ Will Gather His People", "references": "Doctrine and Covenants 29"},
    {"number": 15, "dates": "April 7–13", "title": "You Are Called to Preach My Gospel", "references": "Doctrine and Covenants 30–36"},
    {"number": 16, "dates": "April 14–20", "title": "I Am He Who Liveth, I Am He Who Was Slain", "references": "Easter"},
    {"number": 17, "dates": "April 21–27", "title": "If Ye Are Not One Ye Are Not Mine", "references": "Doctrine and Covenants 37–40"},
    {"number": 18, "dates": "April 28–May 4", "title": "My Law to Govern My Church", "references": "Doctrine and Covenants 41–44"},
    {"number": 19, "dates": "May 5–11", "title": "The Promises Shall Be Fulfilled", "references": "Doctrine and Covenants 45"},
    {"number": 20, "dates": "May 12–18", "title": "Seek Ye Earnestly the Best Gifts", "references": "Doctrine and Covenants 46–48"},
    {"number": 21, "dates": "May 19–25", "title": "That Which Is of God Is Light", "references": "Doctrine and Covenants 49–50"},
    {"number": 22, "dates": "May 26–June 1", "title": "A Faithful, a Just, and a Wise Steward", "references": "Doctrine and Covenants 51–57"},
    {"number": 23, "dates": "June 2–8", "title": "Anxiously Engaged in a Good Cause", "references": "Doctrine and Covenants 58–59"},
    {"number": 24, "dates": "June 9–15", "title": "All Things Shall Work Together for Your Good", "references": "Doctrine and Covenants 60–62"},
    {"number": 25, "dates": "June 16–22", "title": "The Lord Requireth the Heart and a Willing Mind", "references": "Doctrine and Covenants 63–65"},
    {"number": 26, "dates": "June 23–29", "title": "Worth the Riches of the Whole Earth", "references": "Doctrine and Covenants 66–70"},
    {"number": 27, "dates": "June 30–July 6", "title": "No Weapon That Is Formed against You Shall Prosper", "references": "Doctrine and Covenants 71–75"},
    {"number": 28, "dates": "July 7–13", "title": "Great Shall Be Their Reward and Eternal Shall Be Their Glory", "references": "Doctrine and Covenants 76"},
    {"number": 29, "dates": "July 14–20", "title": "I Will Lead You Along", "references": "Doctrine and Covenants 77–80"},
    {"number": 30, "dates": "July 21–27", "title": "Where Much Is Given Much Is Required", "references": "Doctrine and Covenants 81–83"},
    {"number": 31, "dates": "July 28–August 3", "title": "The Power of Godliness", "references": "Doctrine and Covenants 84"},
    {"number": 32, "dates": "August 4–10", "title": "Stand Ye in Holy Places", "references": "Doctrine and Covenants 85–87"},
    {"number": 33, "dates": "August 11–17", "title": "Establish a House of God", "references": "Doctrine and Covenants 88"},
    {"number": 34, "dates": "August 18–24", "title": "A Principle with Promise", "references": "Doctrine and Covenants 89–92"},
    {"number": 35, "dates": "August 25–31", "title": "Receive of His Fulness", "references": "Doctrine and Covenants 93"},
    {"number": 36, "dates": "September 1–7", "title": "For the Salvation of Zion", "references": "Doctrine and Covenants 94–97"},
    {"number": 37, "dates": "September 8–14", "title": "Let Every Man Learn His Duty", "references": "Doctrine and Covenants 98–101"},
    {"number": 38, "dates": "September 15–21", "title": "After Much Tribulation Cometh the Blessing", "references": "Doctrine and Covenants 102–105"},
    {"number": 39, "dates": "September 22–28", "title": "To Have the Heavens Opened", "references": "Doctrine and Covenants 106–108"},
    {"number": 40, "dates": "September 29–October 5", "title": "It Is Thy House, a Place of Thy Holiness", "references": "Doctrine and Covenants 109–110"},
    {"number": 41, "dates": "October 6–12", "title": "General Conference", "references": "General Conference"},
    {"number": 42, "dates": "October 13–19", "title": "I Will Order All Things for Your Good", "references": "Doctrine and Covenants 111–114"},
    {"number": 43, "dates": "October 20–26", "title": "O God, Where Art Thou?", "references": "Doctrine and Covenants 115–120"},
    {"number": 44, "dates": "October 27–November 2", "title": "A Marvelous Work and a Wonder", "references": "Doctrine and Covenants 121–123"},
    {"number": 45, "dates": "November 3–9", "title": "Not without Honor, Save in His Own Country", "references": "Doctrine and Covenants 124"},
    {"number": 46, "dates": "November 10–16", "title": "A Voice of Gladness for the Living and the Dead", "references": "Doctrine and Covenants 125–128"},
    {"number": 47, "dates": "November 17–23", "title": "Prepare Every Needful Thing", "references": "Doctrine and Covenants 129–132"},
    {"number": 48, "dates": "November 24–30", "title": "When We Obtain Any Blessing from God, It Is by Obedience", "references": "Doctrine and Covenants 133"},
    {"number": 49, "dates": "December 1–7", "title": "A City of Stake, for the Curtains of Zion", "references": "Doctrine and Covenants 134–136"},
    {"number": 50, "dates": "December 8–14", "title": "The Vision of the Redemption of the Dead", "references": "Doctrine and Covenants 137–138"},
    {"number": 51, "dates": "December 15–21", "title": "We Believe", "references": "The Articles of Faith and Official Declarations 1 and 2"},
    {"number": 52, "dates": "December 22–28", "title": "The Family Is Central to the Creator’s Plan", "references": "The

# Function to connect to Google Sheets
def connect_to_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials_json = st.secrets["google_sheets"]["credentials"]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(credentials_json), scope)
    client = gspread.authorize(credentials)
    spreadsheet_id = st.secrets["google_sheets"]["spreadsheet_id"]
    return client.open_by_key(spreadsheet_id)

# Function to find current week based on date
def get_current_week():
    today = datetime.now().date()
    for week in weeks:
        start_str, end_str = week['dates'].split('–')
        start_month_day = start_str.split(' ')
        end_month_day = end_str.split(' ')
        start_date = datetime(2025 if 'January' not in start_str else 2026, datetime.strptime(start_month_day[0], '%B').month, int(start_month_day[1])).date()
        end_date = datetime(2025 if 'January' not in end_str else 2026, datetime.strptime(end_month_day[0], '%B').month, int(end_month_day[1])).date()
        if start_date <= today <= end_date:
            return week['number'] - 1
    return 0  # Default to first week

# Function to fetch scripture JSON
@st.cache_data
def load_scriptures(book):
    urls = {
        "dc": "https://raw.githubusercontent.com/bcbooks/scriptures-json/master/doctrine-and-covenants.json",
        "pgp": "https://raw.githubusercontent.com/bcbooks/scriptures-json/master/pearl-of-great-price.json"
    }
    url = urls.get(book)
    if url:
        response = requests.get(url)
        return json.loads(response.text)
    return None

# Function to parse references and get all verses
def get_verses_from_references(references):
    verses = []
    if "Doctrine and Covenants" in references:
        dc = load_scriptures("dc")
        parts = references.replace("Doctrine and Covenants ", "").split(";")
        for part in parts:
            part = sátpart.strip()
            if '–' in part:
                start, end = map(int, part.split('–'))
                for sec in range(start, end + 1):
                    verses += [v['text'] for v in dc[str(sec)]['verses']]
            else:
                section = int(part)
                verses += [v['text'] for v in dc[str(section)]['verses']]
    elif "Joseph Smith—History" in references:
        pgp = load_scriptures("pgp")
        parts = references.split(":")[1].split("–")
        start, end = int(parts[0]), int(parts[1])
        jsh = pgp['js-h']['1']['verses']
        verses += [v['text'] for v in jsh[start-1:end]]
    return verses

# Function to split verses into 7 days
def split_into_days(verses):
    if not verses:
        return ["No verses available" for _ in range(7)]
    verses_per_day = math.ceil(len(verses) / 7)
    days = [verses[i:i + verses_per_day] for i in range(0, len(verses), verses_per_day)]
    while len(days) < 7:
        days.append([])
    return days

# Function to fetch special text
def get_special_text(ref):
    if "Restoration Proclamation" in ref:
        url = "https://www.churchofjesuschrist.org/study/manual/gospel-topics/the-restoration-of-the-fulness-of-the-gospel-of-jesus-christ-a-bicentennial-proclamation-to-the-world?lang=eng"
    elif "Family" in ref:
        url = "https://www.churchofjesuschrist.org/study/manual/the-family-a-proclamation-to-the-world/the-family-a-proclamation-to-the-world?lang=eng"
    elif "Articles of Faith" in ref:
        pgp = load_scriptures("pgp")
        af = pgp['articles-of-faith CPS']['1']['verses']
        od1 = pgp['official-declaration-1']['introduction'] + pgp['official-declaration-1']['text']
        od2 = pgp['official-declaration-2']['introduction'] + pgp['official-declaration-2']['text']
        return '\n'.join([v['text'] for v in af]) + '\n\nOfficial Declaration 1:\n' + od1 + '\n\nOfficial Declaration 2:\n' + od2
    elif "Easter" in ref or "Christmas" in ref or "General Conference" in ref:
        return f"Reflect on {ref}. Read related scriptures or review conference talks."
    else:
        return "No text available."
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    paragraphs = soup.find_all('p')
    return '\n\n'.join(p.text for p in paragraphs if p.text.strip())

# Connect to Google Sheets
sheet = connect_to_sheets()
thoughts_sheet = sheet.worksheet("Sheet1")  # First sheet for thoughts
comments_sheet = sheet.worksheet("Comments")  # Second sheet for comments

# App starts here
st.title("Couples Scripture Study App - Come Follow Me 2025")
st.image("https://www.churchofjesuschrist.org/imgs/5f6b4b0b5f6b4b0b5f6b4b0b5f6b4b0b/full/!1600%2C900/0/default.jpg", caption="Come Follow Me")

# Login system
if 'user' not in st.session_state:
    st.subheader("Login")
    username = st.text_input("Username (husband or wife)")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in USERS and password == USERS[username]:
            st.session_state.user = username
            st.session_state.other = "wife" if username == "husband" else "husband"
            st.rerun()
        else:
            st.error("Invalid login")
else:
    user = st.session_state.user
    other = st.session_state.other
    st.write(f"Welcome, {user.capitalize()}! (Logout by refreshing the page if needed)")

    # Sidebar table of contents
    st.sidebar.title("Table of Contents")
    default_week = get_current_week()
    selected_week = st.sidebar.selectbox("Select Week", [f"Week {w['number']}: {w['dates']} - {w['title']}" for w in weeks], index=default_week)
    week_index = int(selected_week.split(":")[0].split(" ")[1]) - 1
    week = weeks[week_index]

    # Main content for the week
    st.header(f"Week {week['number']}: {week['title']}")
    st.write(f"Dates: {week['dates']}")
    st.write(f"References: {week['references']}")

    # Get verses or special text
    if any(x in week['references'] for x in ["Proclamation", "Articles", "Easter", "Christmas", "General Conference"]):
        daily_readings = [get_special_text(week['references'])] * 7
    else:
        all_verses = get_verses_from_references(week['references'])
        daily_readings = split_into_days(all_verses)

    # Tabs for 7 days
    days = st.tabs([f"Day {i+1}" for i in range(7)])
    for day_idx, tab in enumerate(days):
        with tab:
            # Display scripture
            st.subheader(f"Day {day_idx+1} Reading")
            reading = daily_readings[day_idx]
            if isinstance(reading, list):
                st.write("\n".join(reading))
            else:
                st.write(reading)

            # User's thoughts
            st.subheader("Your Thoughts and Impressions")
            thoughts_data = thoughts_sheet.get_all_records()
            your_thoughts = next((row['thoughts'] for row in thoughts_data if row['week'] == week['number'] and row['day'] == day_idx+1 and row['user'] == user), None)
            if your_thoughts:
                st.write(your_thoughts)
                st.info("You have submitted your thoughts.")
            else:
                thoughts = st.text_area("Write your thoughts here", key=f"thoughts_{day_idx}")
                if st.button("Submit Thoughts", key=f"submit_thoughts_{day_idx}"):
                    timestamp = datetime.now().isoformat()
                    thoughts_sheet.append_row([week['number'], day_idx+1, user, thoughts, timestamp])
                    st.success("Submitted!")
                    st.rerun()

            # Other person's thoughts and comment
            if your_thoughts:
                other_thoughts = next((row['thoughts'] for row in thoughts_data if row['week'] == week['number'] and row['day'] == day_idx+1 and row['user'] == other), None)
                if other_thoughts:
                    st.subheader(f"{other.capitalize()}'s Thoughts")
                    st.write(other_thoughts)

                    # Comment on other's thoughts
                    comments_data = comments_sheet.get_all_records()
                    your_comment = next((row['comment'] for row in comments_data if row['week'] == week['number'] and row['day'] == day_idx+1 and row['commenter'] == user), None)
                    if your_comment:
                        st.subheader("Your Comment")
                        st.write(your_comment)
                    else:
                        comment = st.text_area(f"Comment on {other}'s thoughts (optional)", key=f"comment_{day_idx}")
                        if st.button("Submit Comment", key=f"submit_comment_{day_idx}"):
                            timestamp = datetime.now().isoformat()
                            comments_sheet.append_row([week['number'], day_idx+1, user, comment, timestamp])
                            st.success("Comment submitted!")
                            st.rerun()
                else:
                    st.info(f"{other.capitalize()} has not submitted thoughts yet.")

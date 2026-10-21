
import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import html

# ==================== Page Settings ====================
st.set_page_config(
    page_title="My Reading List",
    layout="centered"
)

# ==================== CSS Design ====================
st.markdown("""
<style>
    .stApp {
        background-color: #F1F5F9;
    }

    .block-container {
        max-width: 850px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Header */
    .header {
        background-color: #A78BFA;
        padding: 25px;
        border-radius: 18px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    }

    .header h1 {
        color: white;
        font-size: 28px;
        margin: 0;
    }

    .header p {
        color: #F5F3FF;
        margin-top: 8px;
        margin-bottom: 0;
    }

    /* Book Titles */
    .book-title {
        color: #243247;
        font-size: 16px;
        font-weight: 600;
    }

    .completed-title {
        color: #9CA3AF;
        font-size: 16px;
        text-decoration: line-through;
    }

    /* General Buttons */
    div.stButton > button {
        border-radius: 10px;
        font-weight: 600;
        border: 1px solid #E2E8F0;
        transition: background-color 0.2s ease,
                    border-color 0.2s ease,
                    color 0.2s ease;
    }

    /* Primary Buttons */
    div.stButton > button[kind="primary"],
    div[data-testid="stFormSubmitButton"] button {
        background-color: #8B5CF6;
        color: #FFFFFF;
        border: none;
        border-radius: 10px;
        font-weight: 600;
    }

    div.stButton > button[kind="primary"]:hover,
    div[data-testid="stFormSubmitButton"] button:hover {
        background-color: #7C3AED;
        color: #FFFFFF;
        border: none;
    }

    /* Book Title Input */
    div[data-testid="stTextInput"] input {
        border: 1.5px solid #C4B5FD;
        border-radius: 10px;
        background-color: #FFFFFF;
        color: #243247;
    }

    div[data-testid="stTextInput"] input:focus {
        border-color: #8B5CF6;
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2);
        outline: none;
    }

    /* Delete Button - Purple Hover */
    div.stButton > button[key^="delete_"] {
        background-color: #FFFFFF;
        color: #475569;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
    }

    div.stButton > button[key^="delete_"]:hover {
        background-color: #F3E8FF;
        color: #6B21A8;
        border: 1px solid #DDD6FE;
    }

    /* Metrics Style */
    div[data-testid="stMetric"] {
        background-color: white;
        padding: 12px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
    }
</style>
""", unsafe_allow_html=True)


# ==================== Data Storage ====================
FILE_PATH = Path(__file__).resolve().with_name(
    "reading_list.json"
)


def load_books():
    default_books = [
        {
            "id": 1,
            "title": "The Old Man and the Sea",
            "completed": False
        },
        {
            "id": 2,
            "title": "The Giver",
            "completed": True
        },
        {
            "id": 3,
            "title": "Veil of Shadows",
            "completed": False
        }
    ]

    if not FILE_PATH.exists():
        return default_books

    try:
        with open(FILE_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            return default_books

        books = []

        for index, book in enumerate(data, start=1):
            if not isinstance(book, dict):
                continue

            title = book.get("title", "")

            if not isinstance(title, str) or not title.strip():
                continue

            book_id = book.get("id", index)

            if not isinstance(book_id, int) or isinstance(book_id, bool):
                book_id = index

            books.append({
                "id": book_id,
                "title": title,
                "completed": book.get("completed", False) is True
            })

        return books

    except (json.JSONDecodeError, OSError):
        return default_books


def save_books():
    try:
        with open(FILE_PATH, "w", encoding="utf-8") as file:
            json.dump(
                st.session_state.books,
                file,
                ensure_ascii=False,
                indent=4
            )
        return True

    except OSError as error:
        st.error(f"Could not save the reading list: {error}")
        return False


# ==================== Session State ====================
if "books" not in st.session_state:
    st.session_state.books = load_books()

if "filter_tab" not in st.session_state:
    st.session_state.filter_tab = "All"


# ==================== Header ====================
today = datetime.now().strftime("%A, %b %d, %Y")

st.markdown(f"""
<div class="header">
    <h1>My Reading List</h1>
    <p>{today}</p>
</div>
""", unsafe_allow_html=True)


# ==================== Add Book ====================
st.subheader("Add a new book")

with st.form("add_book_form", clear_on_submit=True):
    new_title = st.text_input(
        "Book title",
        placeholder="Enter book or novel title"
    )

    submitted = st.form_submit_button(
        "Add Book",
        type="primary",
        use_container_width=True
    )

    if submitted:
        title = new_title.strip()

        if not title:
            st.warning("Please enter a book title.")

        elif any(
            book["title"].casefold() == title.casefold()
            for book in st.session_state.books
        ):
            st.info("This book is already in your list.")

        else:
            next_id = max(
                (
                    book["id"]
                    for book in st.session_state.books
                    if isinstance(book["id"], int)
                    and not isinstance(book["id"], bool)
                ),
                default=0
            ) + 1

            st.session_state.books.insert(0, {
                "id": next_id,
                "title": title,
                "completed": False
            })

            if save_books():
                st.rerun()


# ==================== Completion Count ====================
completed_books = sum(
    1 for book in st.session_state.books
    if book["completed"]
)


# ==================== Filters + Clear Button ====================
st.write("")

filter1, filter2, filter3, spacer_col, clear_col = st.columns(
    [1, 1, 1, 0.45, 1.7],
    vertical_alignment="center"
)

filters = [
    (filter1, "All"),
    (filter2, "Pending"),
    (filter3, "Completed")
]

for column, filter_name in filters:
    with column:
        if st.button(
            filter_name,
            key=f"filter_{filter_name}",
            type=(
                "primary"
                if st.session_state.filter_tab == filter_name
                else "secondary"
            ),
            use_container_width=True
        ):
            st.session_state.filter_tab = filter_name
            st.rerun()


# ==================== Clear Completed Button ====================
with clear_col:
    if completed_books > 0:
        if st.button(
            "Clear Completed",
            key="clear_completed",
            use_container_width=True
        ):
            st.session_state.books = [
                book for book in st.session_state.books
                if not book["completed"]
            ]

            if save_books():
                st.rerun()

st.divider()


# ==================== Filter Books ====================
if st.session_state.filter_tab == "Pending":
    visible_books = [
        book for book in st.session_state.books
        if not book["completed"]
    ]

elif st.session_state.filter_tab == "Completed":
    visible_books = [
        book for book in st.session_state.books
        if book["completed"]
    ]

else:
    visible_books = st.session_state.books


# ==================== Display Books ====================
if not visible_books:
    st.info("No books in this section yet.")

for book in visible_books:
    with st.container(border=True):
        check_col, info_col, delete_col = st.columns(
            [0.10, 0.68, 0.22],
            vertical_alignment="center"
        )

        # Completion Checkbox
        with check_col:
            checked = st.checkbox(
                "Completed",
                value=book["completed"],
                key=f"completed_{book['id']}",
                label_visibility="collapsed"
            )

            if checked != book["completed"]:
                book["completed"] = checked

                if save_books():
                    st.rerun()

        # Book Information
        with info_col:
            safe_title = html.escape(book["title"])

            if book["completed"]:
                st.markdown(
                    f'<div class="completed-title">'
                    f'{safe_title}</div>',
                    unsafe_allow_html=True
                )
                st.caption("Completed")

            else:
                st.markdown(
                    f'<div class="book-title">'
                    f'{safe_title}</div>',
                    unsafe_allow_html=True
                )
                st.caption("Currently reading / To read")

        # Delete Button
        with delete_col:
            if st.button(
                "Delete",
                key=f"delete_{book['id']}",
                use_container_width=True
            ):
                st.session_state.books = [
                    item for item in st.session_state.books
                    if item["id"] != book["id"]
                ]

                if save_books():
                    st.rerun()




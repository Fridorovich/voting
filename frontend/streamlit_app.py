import streamlit as st
import requests
from datetime import datetime
import os
from typing import List, Dict
import json
import uuid
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")


def init_session_state():
    session_keys = {
        'access_token': None,
        'refresh_token': None,
        'user_email': None,
        'is_logged_in': False,
        'polls': [],
        'user_votes': {}
    }
    for key, value in session_keys.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


def register_user(email: str, password: str):
    """New user register"""
    url = f"{BASE_URL}/auth/register"
    data = {"email": email, "password": password}
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            st.success("User registered successfully!")
            return True
        st.error(f"Registration failed:"
                 f" {response.json().get('detail', 'Unknown error')}"
                 )
        return False
    except Exception as e:
        st.error(f"Registration error: {str(e)}")
        return False


def login_user(email: str, password: str):
    """User authentification"""
    url = f"{BASE_URL}/auth/login"
    data = {"email": email, "password": password}
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  # Exception generation
        tokens = response.json()
        st.session_state.update({
            'access_token': tokens['access_token'],
            'refresh_token': tokens['refresh_token'],
            'user_email': email,
            'is_logged_in': True
        })
        st.success("Logged in successfully!")
        return True
    except requests.HTTPError as e:
        if e.response.status_code == 401:
            st.error("Login failed: Invalid credentials")
        else:
            st.error(f"Login failed: {e.response.text}")
        return False
    except Exception as e:
        st.error(f"Login error: {str(e)}")
        return False


def logout_user():
    """Log out"""
    st.session_state.update({
        'access_token': None,
        'refresh_token': None,
        'user_email': None,
        'is_logged_in': False,
        'polls': [],
        'user_votes': {}
    })
    st.success("Logged out successfully!")


def refresh_access_token():
    """Updating access token"""
    if not st.session_state.refresh_token:
        return False
    try:
        response = requests.post(
            f"{BASE_URL}/auth/token/refresh",
            json={"refresh_token": st.session_state.refresh_token}
        )
        if response.status_code == 200:
            tokens = response.json()
            st.session_state.access_token = tokens['access_token']
            st.session_state.refresh_token = tokens['refresh_token']
            return True
        return False
    except Exception as e:
        st.error(f"Token refresh error: {str(e)}")
        return False


def get_all_polls():
    """Getting all polls"""
    try:
        response = requests.get(f"{BASE_URL}/polls/")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching polls: {str(e)}")
        return []


def refresh_polls():
    """Updating list of polls"""
    st.session_state.polls = get_all_polls()


def create_new_poll(poll_data: Dict):
    """Creating new poll"""
    headers = {
        "Authorization": f"Bearer {st.session_state.access_token}",
        "Content-Type": "application/json"
    }

    try:
        params = {"token": st.session_state.access_token}
        response = requests.post(
            f"{BASE_URL}/polls/polls",
            json=poll_data,
            headers=headers,
            params=params

        )
        if response.status_code == 200:
            st.success("Poll created successfully!")
            st.rerun()
        else:
            try:
                error_detail = response.json().get("detail", "Unknown error")
                st.error(f"Failed to create poll: {error_detail}")
            except json.JSONDecodeError:
                st.error(f"Server returned invalid response: {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")


def submit_vote(poll_id: int, choice_ids: List[int]):
    """Vote submission"""
    if not st.session_state.is_logged_in:
        st.warning("You must be logged in to vote.")
        return

    headers = {
        "Authorization": f"Bearer {st.session_state.access_token}",
        "Content-Type": "application/json"
    }
    try:
        params = {"token": st.session_state.access_token, "poll_id": poll_id}
        response = requests.post(
            f"{BASE_URL}/polls/{poll_id}/vote",
            json={"choice_ids": choice_ids},
            headers=headers,
            params=params
        )
        if response.status_code == 200:
            st.session_state.user_votes[poll_id] = True
            st.success("Vote submitted!")
            return True
        else:
            st.error(f"Voting failed: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"Error submitting vote: {str(e)}")
        return False


def close_poll(poll_id: int, new_close_date: str = None):
    """Closing poll"""
    headers = {
        "Authorization": f"Bearer {st.session_state.access_token}",
        "Content-Type": "application/json"
    }
    close_data = {"new_close_date": new_close_date} if new_close_date else {}
    params = {"token": st.session_state.access_token, "poll_id": poll_id}
    try:
        response = requests.post(
            f"{BASE_URL}/polls/{poll_id}/close",
            json=close_data,
            headers=headers,
            params=params
        )
        if response.status_code == 200:
            st.success("Poll closed successfully!")
            st.rerun()
        else:
            st.error(f"Failed to close poll: "
                     f"{response.json().get('detail', 'Unknown error')}"
                     )
    except Exception as e:
        st.error(f"Error closing poll: {str(e)}")


def auth_forms():
    """Authentification form"""
    st.header("Authentication")
    tab1, tab2, tab3 = st.tabs(["Login", "Register", "View Polls"])

    with tab1:
        st.subheader("Login")
        with st.form("Login Form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                if login_user(email, password):
                    st.rerun()

    with tab2:
        st.subheader("Register")
        with st.form("Register Form"):
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input(
                "Password",
                type="password",
                key="reg_password"
            )
            if st.form_submit_button("Register"):
                if register_user(reg_email, reg_password):
                    st.rerun()

    with tab3:
        st.subheader("View Polls")
        display_closed_polls()


def get_all_polls_request():
    response = requests.get(f"{BASE_URL}/polls")
    if response.status_code != 200:
        st.error("Error loading polls")
        return
    polls = response.json()
    return polls


def display_closed_polls():
    polls = get_all_polls()
    closed_polls = [p for p in polls if p['is_closed']]
    st.write("### Closed polls")
    for poll in closed_polls:
        render_poll(poll, is_active=False)


def display_active_polls():
    polls = get_all_polls()

    active_polls = [p for p in polls if not p['is_closed']]
    st.write("### Active polls")
    for poll in active_polls:
        render_poll(poll, is_active=True)


def show_voting_form(poll: Dict, session_key: str):
    poll_id = poll['id']
    response = requests.get(f"{BASE_URL}/polls/{poll_id}").json()
    choices = response['choices']

    if f'selected_{poll_id}' not in st.session_state:
        st.session_state[f'selected_{poll_id}'] = []
    selected_ids = st.session_state[f'selected_{poll_id}']

    if response['is_multiple_choice']:
        for choice in choices:
            is_checked = choice['id'] in selected_ids
            checkbox = st.checkbox(
                choice['text'],
                value=is_checked,
                key=f"checkbox_{poll_id}_{choice['id']}_{session_key}"
            )

            if checkbox:
                if choice['id'] not in st.session_state[f'selected_{poll_id}']:
                    st.session_state[f'selected_{poll_id}'].append(choice['id'])
            else:
                if choice['id'] in st.session_state[f'selected_{poll_id}']:
                    st.session_state[f'selected_{poll_id}'].remove(choice['id'])

        new_ids = st.session_state[f'selected_{poll_id}']
    else:
        selected_id = selected_ids[0] if selected_ids else None
        new_choice = st.radio(
            "Choose the variant:",
            options=choices,
            format_func=lambda x: x['text'],
            index=next((i for i, c in enumerate(choices) if c['id'] == selected_id), 0),
            key=f"radio_{poll_id}_{session_key}"
        )
        new_ids = [new_choice['id']]

    if st.button("✅ Accept", key=f"submit_{poll_id}_{session_key}"):
        if new_ids:
            success = submit_vote(poll_id, new_ids)
            if success:
                st.session_state.user_votes[poll_id] = True
                st.session_state[f'poll_session_{poll_id}'] = str(uuid.uuid4())
                del st.session_state[f'selected_{poll_id}']
                st.rerun()
        else:
            st.warning("Choose at least 1 variant")


def show_results(poll: Dict, session_key: str):
    """Reflection of the result with unique keys"""
    if (not poll.get("is_closed")):
        st.write("Your vote is accounted")
    else:
        results = poll.get("results", {})
        total = 0
        for res in results.values():
            total += res

        if total == 0:
            st.write("No votes yet")
            return

        for i, (option, votes) in enumerate(results.items()):
            percent = (votes / total) * 100
            st.progress(
                percent / 100,
                text=f"{option}: {votes} votes ({percent:.1f}%)",
            )


def render_poll(poll: Dict, is_active: bool):
    poll_id = poll['id']
    container = st.container()

    if f'poll_session_{poll_id}' not in st.session_state:
        st.session_state[f'poll_session_{poll_id}'] = str(uuid.uuid4())

    session_key = st.session_state[f'poll_session_{poll_id}']

    with container:
        st.write(f"**{poll['title']}**")
        st.write(f"{poll['description']}")
        if f'selected_{poll_id}' not in st.session_state:
            st.session_state[f'selected_{poll_id}'] = []

        if is_active and not st.session_state.user_votes.get(poll_id, False):
            show_voting_form(poll, session_key)
        else:
            show_results(poll, session_key)

    if is_active and st.session_state.is_logged_in:
        if st.button(f"Close Poll", key=f"close_poll_{poll_id}"):
            close_poll(poll_id)


def handle_close_poll(poll_id: int):
    try:
        response = requests.post(
            f"{BASE_URL}/polls/{poll_id}/close",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        if response.status_code == 200:
            st.success("Poll is closed")
            st.rerun()
    except Exception as e:
        st.error(f"Error: {str(e)}")


def create_poll_form():
    """Creating poll form"""
    if not st.session_state.is_logged_in:
        st.warning("You must be logged in to create a poll.")
        return

    with st.form("Create Poll"):
        st.header("Create New Poll")
        title = st.text_input("Title*")
        description = st.text_area("Description")
        choices = st.text_area("Options (one per line)*").split('\n')
        is_multiple = st.checkbox("Allow multiple choices")
        close_date = st.date_input("Close Date")
        close_time = st.time_input("Close Time")

        if st.form_submit_button("Create Poll"):
            if not title or len(choices) < 2:
                st.error("Title and at least 2 options are required")
                return
            poll_data = {
                "title": title,
                "description": description,
                "choices": [c.strip() for c in choices if c.strip()],
                "is_multiple_choice": is_multiple,
                "close_date": datetime.combine(close_date, close_time).isoformat()
            }
            create_new_poll(poll_data)


st.title("Polling System")

if not st.session_state.is_logged_in:
    auth_forms()
else:
    st.header(f"Welcome, {st.session_state.user_email}!")

    tab1, tab2, tab3 = st.tabs(["Active Polls", "Closed Polls", "Create Poll"])

    with tab1:
        display_active_polls()

    with tab2:
        display_closed_polls()

    with tab3:
        create_poll_form()

    if st.button("Logout"):
        logout_user()
        st.rerun()

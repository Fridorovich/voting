import streamlit as st
import requests
from datetime import datetime
import os
from typing import List, Dict
import json

# Конфигурация
BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Инициализация состояния сессии
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

# Функции аутентификации
def register_user(email: str, password: str):
    """Регистрация нового пользователя"""
    url = f"{BASE_URL}/auth/register"
    data = {"email": email, "password": password}
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            st.success("User registered successfully!")
            return True
        st.error(f"Registration failed: {response.json().get('detail', 'Unknown error')}")
        return False
    except Exception as e:
        st.error(f"Registration error: {str(e)}")
        return False

def login_user(email: str, password: str):
    """Аутентификация пользователя"""
    url = f"{BASE_URL}/auth/login"
    data = {"email": email, "password": password}
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            tokens = response.json()
            st.session_state.update({
                'access_token': tokens['access_token'],
                'refresh_token': tokens['refresh_token'],
                'user_email': email,
                'is_logged_in': True
            })
            st.success("Logged in successfully!")
            return True
        st.error("Login failed: Invalid credentials")
        return False
    except Exception as e:
        st.error(f"Login error: {str(e)}")
        return False

def logout_user():
    """Выход из системы"""
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
    """Обновление access token"""
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

# Функции для работы с опросами
@st.cache_data(ttl=60)
def get_all_polls():
    """Получение всех опросов"""
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    try:
        response = requests.get(f"{BASE_URL}/polls/", headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching polls: {str(e)}")
        return []

def refresh_polls():
    """Обновление списка опросов"""
    st.cache_data.clear()
    st.session_state.polls = get_all_polls()

def create_new_poll(poll_data: Dict):
    headers = {
        "Authorization": f"Bearer {st.session_state.access_token}",
        "Content-Type": "application/json"
    }
    try:
        # Добавляем токен в query-параметры
        params = {"token": st.session_state.access_token}

        # Правильный URL с учетом структуры эндпоинта
        response = requests.post(
            f"{BASE_URL}/polls/polls",
            json=poll_data,
            headers=headers,
            params=params
        )

        # Логирование для отладки
        st.write("Request URL:", response.request.url)
        st.write("Request Headers:", response.request.headers)
        st.write("Request Body:", response.request.body.decode())
        st.write("Response Status Code:", response.status_code)
        st.write("Response Text:", response.text)

        if response.status_code == 200:
            st.success("Poll created successfully!")
            refresh_polls()
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
    """Отправка голоса"""
    headers = {
        "Authorization": f"Bearer {st.session_state.access_token}",
        "Content-Type": "application/json"
    }
    st.write(choice_ids)
    try:
        params = {"token": st.session_state.access_token, "poll_id" : poll_id}
        response = requests.post(
            f"{BASE_URL}/polls/{poll_id}/vote",
            json={"choice_ids": choice_ids},
            headers=headers,
            params= params
        )
        if response.status_code == 200:
            st.session_state.user_votes[poll_id] = True
            st.success("Vote submitted!")
            refresh_polls()
        else:
            st.error(f"Voting failed: {response.json().get('detail', 'Unknown error')}")
    except Exception as e:
        st.error(f"Error submitting vote: {str(e)}")

def close_poll(poll_id: int, new_close_date: str = None):
    """Закрытие опроса"""
    headers = {
        "Authorization": f"Bearer {st.session_state.access_token}",
        "Content-Type": "application/json"
    }
    close_data = {"new_close_date": new_close_date} if new_close_date else {}
    try:
        params = {"token": st.session_state.access_token}
        response = requests.post(
            f"{BASE_URL}/polls/{poll_id}/close",
            json=close_data,
            headers=headers,
            params=params
        )
        if response.status_code == 200:
            st.success("Poll closed successfully!")
            refresh_polls()
        else:
            st.error(f"Failed to close poll: {response.json().get('detail', 'Unknown error')}")
    except Exception as e:
        st.error(f"Error closing poll: {str(e)}")

# Компоненты интерфейса
def auth_forms():
    """Формы аутентификации"""
    with st.form("Login Form"):
        st.header("Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            login_user(email, password)
            st.rerun()

    with st.form("Register Form"):
        st.header("Register")
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        if st.form_submit_button("Register"):
            if register_user(reg_email, reg_password):
                st.rerun()

def render_poll(poll: Dict):
    """Отрисовка одного опроса"""
    with st.container(border=True):
        st.subheader(poll['title'])
        if poll.get('description'):
            st.caption(poll['description'])

        closed = poll.get('is_closed', False)
        voted = st.session_state.user_votes.get(poll['id'], False)

        if closed or voted:
            show_results(poll)
        else:
            show_voting_form(poll)

        # Кнопка для закрытия опроса
        st.write(poll)
        if not closed and st.session_state.user_email == poll.get('creator_email'):
            if st.button("Close Poll", key=f"close_btn_{poll['id']}"):
                close_poll(poll['id'])

def show_results(poll: Dict):
    """Отображение результатов опроса"""

    results = poll.get('results', {})
    total = sum(results.values())
    if total == 0:
        st.write("No votes yet")
        return

    for option, votes in results.items():
        percent = (votes / total) * 100
        st.progress(
            percent / 100,
            text=f"{option}: {votes} votes ({percent:.1f}%)"
        )

def show_voting_form(poll: Dict):
    """Форма голосования"""
    poll_id = poll.get("id")
    url = f"{BASE_URL}/polls/{poll_id}"
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    response = requests.get(url, headers=headers).json()

    choices = response["choices"]

    selected = []

    if poll.get('is_multiple_choice'):
        for choice in choices:
            if st.checkbox(choice['text'], key=f"cb_{poll['id']}_{choice['id']}"):
                selected.append(choice['id'])
    else:
        option = st.radio(
            "Select option:",
            [choice['id'] for choice in choices],
            format_func=lambda x: next(c['text'] for c in choices if c['id'] == x),
            key=f"radio_{poll['id']}"
        )
        selected.append(option)

    if st.button("Submit Vote", key=f"btn_{poll['id']}"):
        if selected:
            submit_vote(poll['id'], selected)
        else:
            st.warning("Please select at least one option")

def create_poll_form():
    """Форма создания опроса"""
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

# Главный интерфейс
st.title("Polling System")

if not st.session_state.is_logged_in:
    auth_forms()
else:
    st.header(f"Welcome, {st.session_state.user_email}!")

    # Загрузка опросов при первом входе
    if not st.session_state.polls:
        st.session_state.polls = get_all_polls()

    # Навигация
    tab1, tab2, tab3 = st.tabs(["Active Polls", "Closed Polls", "Create Poll"])

    with tab1:
        st.subheader("Active Polls")
        active_polls = [p for p in st.session_state.polls if not p.get('is_closed')]
        if not active_polls:
            st.info("No active polls available")
        for poll in active_polls:
            render_poll(poll)

    with tab2:
        st.subheader("Closed Polls")
        closed_polls = [p for p in st.session_state.polls if p.get('is_closed')]
        if not closed_polls:
            st.info("No closed polls available")
        for poll in closed_polls:
            render_poll(poll)

    with tab3:
        create_poll_form()

    # Кнопка выхода
    if st.button("Logout"):
        logout_user()
        st.rerun()

import streamlit as st
import requests
from datetime import datetime
import os
from typing import List, Dict
import json
import time
import uuid
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
        response.raise_for_status()  # Генерирует исключение при 4xx/5xx статусах
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
def get_all_polls():
    """Получение всех опросов"""
    try:
        response = requests.get(f"{BASE_URL}/polls/")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching polls: {str(e)}")
        return []

def refresh_polls():
    """Обновление списка опросов"""
    st.session_state.polls = get_all_polls()

def create_new_poll(poll_data: Dict):
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
    """Отправка голоса"""
    if not st.session_state.is_logged_in:
        st.warning("You must be logged in to vote.")
        return

    headers = {
        "Authorization": f"Bearer {st.session_state.access_token}",
        "Content-Type": "application/json"
    }
    try:
        params = {"token": st.session_state.access_token, "poll_id" : poll_id}
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

# def close_poll(poll_id: int, new_close_date: str = None):
#     """Закрытие опроса"""
#     headers = {
#         "Authorization": f"Bearer {st.session_state.access_token}",
#         "Content-Type": "application/json"
#     }
#     close_data = {"new_close_date": new_close_date} if new_close_date else {}
#     try:
#         response = requests.post(
#             f"{BASE_URL}/polls/{poll_id}/close",
#             json=close_data,
#             headers=headers
#         )
#         if response.status_code == 200:
#             st.success("Poll closed successfully!")
#             refresh_polls()
#         else:
#             st.error(f"Failed to close poll: {response.json().get('detail', 'Unknown error')}")
#     except Exception as e:
#         st.error(f"Error closing poll: {str(e)}")

def auth_forms():
    """Формы аутентификации"""
    st.header("Authentication")
    tab1, tab2, tab3 = st.tabs(["Login", "Register", "View Polls"])

    with tab1:
        st.subheader("Login")
        with st.form("Login Form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                if login_user(email, password):  # rerun только при успехе
                    st.rerun()

    with tab2:
        st.subheader("Register")
        with st.form("Register Form"):
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            if st.form_submit_button("Register"):
                if register_user(reg_email, reg_password):
                    st.rerun()

    with tab3:
        st.subheader("View Polls")
        display_closed_polls()

def get_all_polls_request():
    response = requests.get(f"{BASE_URL}/polls")
    if response.status_code != 200:
        st.error("Ошибка загрузки опросов")
        return
    polls = response.json()
    return polls

def display_closed_polls():
    polls = get_all_polls()
    closed_polls = [p for p in polls if p['is_closed']]
    st.write("### Завершенные опросы")
    for poll in closed_polls:
        render_poll(poll, is_active=False)

def display_active_polls():
    polls = get_all_polls()
    
    # Разделение опросов с гарантией уникальности
    active_polls = [p for p in polls if not p['is_closed']]
    # Уникальные ключи для вкладок
    st.write("### Активные опросы")
    for poll in active_polls:
        render_poll(poll, is_active=True)

    
def show_voting_form(poll: Dict, session_key: str):
    poll_id = poll['id']
    response = requests.get(f"{BASE_URL}/polls/{poll_id}").json()
    choices = response['choices']

    # Инициализация выбранных ID, если их нет в session_state
    if f'selected_{poll_id}' not in st.session_state:
        st.session_state[f'selected_{poll_id}'] = []
    selected_ids = st.session_state[f'selected_{poll_id}']

    # Отображение вариантов ответа
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
        # Для radio тоже используем объекты словарей
        new_choice = st.radio(
            "Выберите вариант:",
            options=choices,  # <- Передаем сами объекты
            format_func=lambda x: x['text'],  # <- Берем текст из словаря
            index=next((i for i, c in enumerate(choices) if c['id'] == selected_id), 0),
            key=f"radio_{poll_id}_{session_key}"
        )
        new_ids = [new_choice['id']]  # Теперь работает

    # Кнопка отправки голоса (остается без изменений)
    if st.button("✅ Подтвердить", key=f"submit_{poll_id}_{session_key}"):
        if new_ids:
            success = submit_vote(poll_id, new_ids)
            st.write(success)
            if success:
                st.session_state.user_votes[poll_id] = True
                st.session_state[f'poll_session_{poll_id}'] = str(uuid.uuid4())
                del st.session_state[f'selected_{poll_id}']
                st.rerun()
        else:
            st.warning("Choose at least 1 variant")

def show_results(poll: Dict, session_key: str):
    """Отображение результатов с уникальными ключами"""
    if (poll.get("is_closed") == False):
        st.write("Your vote is accounted")
    else :
        poll_id = poll["id"]
        results = poll.get("results", {})
        total = 0
        for res in results.values():
            total += res

        if total == 0:
            st.write("Голосов пока нет")
            return

        for i, (option, votes) in enumerate(results.items()):
            percent = (votes / total) * 100
            st.progress(
                percent / 100,
                text=f"{option}: {votes} голосов ({percent:.1f}%)",
                # key=f"progress_{poll_id}_{session_key}_{i}"
            )

def render_poll(poll: Dict, is_active: bool):
    poll_id = poll['id']
    container = st.container()

    # Инициализация уникального ключа сессии для опроса
    if f'poll_session_{poll_id}' not in st.session_state:
        st.session_state[f'poll_session_{poll_id}'] = str(uuid.uuid4())

    session_key = st.session_state[f'poll_session_{poll_id}']

    with container:
        # Заголовок опроса с уникальным ключом
        st.write(f"**{poll['title']}**")

        # Состояние для выбранных вариантов
        if f'selected_{poll_id}' not in st.session_state:
            st.session_state[f'selected_{poll_id}'] = []

        # Форма голосования или результаты
        if is_active and not st.session_state.user_votes.get(poll_id, False):
            show_voting_form(poll, session_key)
        else:
            show_results(poll, session_key)


def handle_close_poll(poll_id: int):
    try:
        response = requests.post(
            f"{BASE_URL}/polls/{poll_id}/close",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        if response.status_code == 200:
            st.success("Опрос закрыт!")
            refresh_polls()
    except Exception as e:
        st.error(f"Ошибка: {str(e)}")

def create_poll_form():
    """Форма создания опроса"""
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

# Главный интерфейс
st.title("Polling System")

if not st.session_state.is_logged_in:
    auth_forms()
else:
    st.header(f"Welcome, {st.session_state.user_email}!")

    # Навигация
    tab1, tab2, tab3 = st.tabs(["Active Polls", "Closed Polls", "Create Poll"])

    with tab1:
        display_active_polls()

    with tab2:
        display_closed_polls()

    with tab3:
        create_poll_form()

    # Кнопка выхода
    if st.button("Logout"):
        logout_user()
        st.rerun()

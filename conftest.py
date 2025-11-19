"""Фикстуры для тестов"""
import pytest
from helpers.api_client import ApiClient
from helpers.generators import generate_random_string


BASE_URL = 'https://qa-scooter.praktikum-services.ru'


@pytest.fixture
def api_client():
    """Фикстура для клиента API"""
    return ApiClient(BASE_URL)


@pytest.fixture
def create_courier_payload():
    """Фикстура для создания payload курьера"""
    def _create_payload(login=None, password=None, first_name=None):
        login = login or generate_random_string(10)
        password = password or generate_random_string(10)
        first_name = first_name or generate_random_string(10)
        
        return {
            "login": login,
            "password": password,
            "firstName": first_name
        }
    return _create_payload


@pytest.fixture
def register_new_courier(api_client, create_courier_payload):
    """Фикстура для регистрации нового курьера"""
    couriers_to_delete = []
    
    def _register():
        payload = create_courier_payload()
        response = api_client.register_new_courier(payload)
        
        if response.status_code == 201:
            couriers_to_delete.append((payload["login"], payload["password"]))
        
        return response, payload
    
    yield _register
    
    # Удаляем созданных курьеров после теста
    for login, password in couriers_to_delete:
        login_response = api_client.login_courier(login, password)
        if login_response.status_code == 200:
            courier_id = login_response.json()['id']
            api_client.delete_courier(courier_id)


@pytest.fixture
def create_order(api_client):
    """Фикстура для создания заказа"""
    orders_to_cancel = []
    
    def _create(color=None):
        from data.order_data import get_order_payload
        payload = get_order_payload(color)
        response = api_client.create_order(payload)
        
        if response.status_code == 201:
            track = response.json()['track']
            orders_to_cancel.append(track)
        
        return response
    
    yield _create
    
    # Отменяем заказы после теста
    for track in orders_to_cancel:
        api_client.cancel_order(track)
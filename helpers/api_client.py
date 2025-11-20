"""Клиент для работы с API Яндекс Самокат"""
import requests
from helpers.generators import generate_random_string


class ApiClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def register_new_courier(self, payload):
        """Регистрация нового курьера"""
        return requests.post(f'{self.base_url}/api/v1/courier', data=payload)

    def login_courier(self, login, password):
        """Логин курьера"""
        payload = {"login": login, "password": password}
        return requests.post(f'{self.base_url}/api/v1/courier/login', data=payload)

    def delete_courier(self, courier_id):
        """Удаление курьера"""
        return requests.delete(f'{self.base_url}/api/v1/courier/{courier_id}')

    def create_order(self, payload):
        """Создание заказа"""
        return requests.post(f'{self.base_url}/api/v1/orders', json=payload)

    def get_orders_list(self):
        """Получение списка заказов"""
        return requests.get(f'{self.base_url}/api/v1/orders')

    def get_order_by_track(self, track):
        """Получение заказа по треку"""
        return requests.get(f'{self.base_url}/api/v1/orders/track', params={'t': track})

    def accept_order(self, order_id, courier_id):
        """Принятие заказа курьером"""
        return requests.put(f'{self.base_url}/api/v1/orders/accept/{order_id}', 
                          params={'courierId': courier_id})

    def cancel_order(self, track):
        """Отмена заказа"""
        return requests.put(f'{self.base_url}/api/v1/orders/cancel', params={'track': track})
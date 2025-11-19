"""Тесты для создания курьера"""
import pytest
import allure
from helpers.generators import generate_random_string


@allure.feature('Создание курьера')
class TestCourierCreation:
    
    @allure.title('Успешное создание курьера')
    def test_create_courier_success(self, api_client, create_courier_payload):
        with allure.step('Создать нового курьера'):
            payload = create_courier_payload()
            response = api_client.register_new_courier(payload)
        
        with allure.step('Проверить код ответа и тело ответа'):
            assert response.status_code == 201
            assert response.json() == {"ok": True}
    
    @allure.title('Нельзя создать двух одинаковых курьеров')
    def test_create_duplicate_courier_fails(self, api_client, create_courier_payload):
        with allure.step('Создать первого курьера'):
            payload = create_courier_payload()
            first_response = api_client.register_new_courier(payload)
            assert first_response.status_code == 201
        
        with allure.step('Попытаться создать второго курьера с такими же данными'):
            second_response = api_client.register_new_courier(payload)
        
        with allure.step('Проверить ошибку дублирования'):
            assert second_response.status_code == 409
            assert second_response.json()["message"] == "Этот логин уже используется. Попробуйте другой."
    
    @allure.title('Создание курьера без обязательных полей')
    @pytest.mark.parametrize('missing_field', ['login', 'password'])
    def test_create_courier_missing_field_fails(self, api_client, create_courier_payload, missing_field):
        with allure.step('Подготовить данные курьера без обязательного поля'):
            payload = create_courier_payload()
            del payload[missing_field]
        
        with allure.step('Отправить запрос без обязательного поля'):
            response = api_client.register_new_courier(payload)
        
        with allure.step('Проверить ошибку'):
            assert response.status_code == 400
            assert response.json()["message"] == "Недостаточно данных для создания учетной записи"
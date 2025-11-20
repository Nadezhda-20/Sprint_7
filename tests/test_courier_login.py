"""Тесты для логина курьера"""
import pytest
import allure
from helpers.generators import generate_random_string


@allure.feature('Логин курьера')
class TestCourierLogin:
    
    @allure.title('Успешный логин курьера')
    def test_courier_login_success(self, api_client, register_new_courier):
        with allure.step('Зарегистрировать нового курьера'):
            response, payload = register_new_courier()
            assert response.status_code == 201
        
        with allure.step('Выполнить логин'):
            login_response = api_client.login_courier(payload["login"], payload["password"])
        
        with allure.step('Проверить успешный логин'):
            assert login_response.status_code == 200
            assert "id" in login_response.json()
    
    @allure.title('Логин без обязательных полей')
    @pytest.mark.parametrize('missing_field', ['login', 'password'])
    def test_courier_login_missing_field_fails(self, api_client, missing_field):
        with allure.step('Подготовить данные для логина без обязательного поля'):
            payload = {
                "login": "test_login",
                "password": "test_password"
            }
            del payload[missing_field]
        
        with allure.step('Отправить запрос без обязательного поля'):
            # Используем низкоуровневый запрос, так как метод login_courier требует оба поля
            response = api_client.login_courier(
                payload.get("login", ""), 
                payload.get("password", "")
            )
        
        with allure.step('Проверить ошибку'):
            assert response.status_code == 400
            assert response.json()["message"] == "Недостаточно данных для входа"
    
    @allure.title('Логин с неверными данными')
    def test_courier_login_wrong_credentials_fails(self, api_client):
        with allure.step('Попытаться войти с неверными данными'):
            response = api_client.login_courier("nonexistent", "wrongpassword")
        
        with allure.step('Проверить ошибку'):
            assert response.status_code == 404
            assert response.json()["message"] == "Учетная запись не найдена"
    
    @allure.title('Логин под несуществующим пользователем')
    def test_courier_login_nonexistent_fails(self, api_client):
        with allure.step('Попытаться войти под несуществующим пользователем'):
            response = api_client.login_courier("nonexistent_user_12345", "password123")
        
        with allure.step('Проверить ошибку'):
            assert response.status_code == 404
            assert response.json()["message"] == "Учетная запись не найдена"
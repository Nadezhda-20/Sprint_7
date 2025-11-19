"""Тесты для удаления курьера"""
import allure


@allure.feature('Удаление курьера')
class TestCourierDelete:
    
    @allure.title('Успешное удаление курьера')
    def test_delete_courier_success(self, api_client, register_new_courier):
        with allure.step('Создать тестового курьера'):
            response, payload = register_new_courier()
            assert response.status_code == 201
        
        with allure.step('Получить ID курьера'):
            login_response = api_client.login_courier(payload["login"], payload["password"])
            assert login_response.status_code == 200
            courier_id = login_response.json()['id']
        
        with allure.step('Удалить курьера'):
            response = api_client.delete_courier(courier_id)
        
        with allure.step('Проверить успешное удаление'):
            assert response.status_code == 200
            assert response.json() == {"ok": True}
    
    @allure.title('Удаление курьера без ID')
    def test_delete_courier_without_id_fails(self, api_client):
        with allure.step('Попытаться удалить курьера без ID'):
            # Используем низкоуровневый запрос для эмуляции запроса без ID
            response = api_client.delete_courier("")
        
        with allure.step('Проверить ошибку'):
            assert response.status_code == 404
    
    @allure.title('Удаление несуществующего курьера')
    def test_delete_nonexistent_courier_fails(self, api_client):
        with allure.step('Попытаться удалить несуществующего курьера'):
            response = api_client.delete_courier(999999)
        
        with allure.step('Проверить ошибку'):
            assert response.status_code == 404
            assert response.json()["message"] == "Курьера с таким id нет."
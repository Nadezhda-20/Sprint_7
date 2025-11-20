"""Тесты для получения заказа по номеру"""
import allure


@allure.feature('Получение заказа по номеру')
class TestGetOrderByTrack:
    
    @allure.title('Успешное получение заказа по треку')
    def test_get_order_by_track_success(self, api_client, create_order):
        with allure.step('Создать тестовый заказ'):
            order_response = create_order()
            assert order_response.status_code == 201
            track = order_response.json()['track']
        
        with allure.step('Получить заказ по треку'):
            response = api_client.get_order_by_track(track)
        
        with allure.step('Проверить успешное получение'):
            assert response.status_code == 200
            data = response.json()
            assert "order" in data
            order = data['order']
            assert "id" in order
            assert "track" in order
            assert order["track"] == track
    
    @allure.title('Получение заказа без номера трека')
    def test_get_order_without_track_fails(self, api_client):
        with allure.step('Попытаться получить заказ без трека'):
            # Используем низкоуровневый запрос без параметра track
            response = api_client.get_order_by_track(None)
        
        with allure.step('Проверить ошибку'):
            assert response.status_code == 400
            assert response.json()["message"] == "Недостаточно данных для поиска"
    
    @allure.title('Получение несуществующего заказа')
    def test_get_nonexistent_order_fails(self, api_client):
        with allure.step('Попытаться получить несуществующий заказ'):
            response = api_client.get_order_by_track(999999)
        
        with allure.step('Проверить ошибку'):
            assert response.status_code == 404
            assert response.json()["message"] == "Заказ не найден"
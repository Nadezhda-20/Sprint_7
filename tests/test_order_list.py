"""Тесты для получения списка заказов"""
import allure


@allure.feature('Список заказов')
class TestOrderList:
    
    @allure.title('Получение списка заказов')
    def test_get_order_list(self, api_client):
        with allure.step('Получить список заказов'):
            response = api_client.get_orders_list()
        
        with allure.step('Проверить ответ'):
            assert response.status_code == 200
            data = response.json()
            assert "orders" in data
            assert isinstance(data["orders"], list)
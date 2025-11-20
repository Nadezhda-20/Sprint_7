"""Тесты для создания заказа"""
import pytest
import allure


@allure.feature('Создание заказа')
class TestOrderCreation:
    
    @allure.title('Создание заказа с разными цветами')
    @pytest.mark.parametrize('color', [["BLACK"], ["GREY"], ["BLACK", "GREY"], []])
    def test_create_order_with_different_colors(self, create_order, color):
        with allure.step('Создать заказ с указанным цветом'):
            response = create_order(color)
        
        with allure.step('Проверить успешное создание заказа'):
            assert response.status_code == 201
            assert "track" in response.json()
    
    @allure.title('Проверка наличия track в ответе')
    def test_create_order_has_track(self, create_order):
        with allure.step('Создать заказ'):
            response = create_order()
        
        with allure.step('Проверить наличие track'):
            assert response.status_code == 201
            data = response.json()
            assert "track" in data
            assert isinstance(data["track"], int)
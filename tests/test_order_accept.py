"""Тесты для принятия заказа"""
import allure


@allure.feature('Принятие заказа')
class TestOrderAccept:
    
    @allure.title('Успешное принятие заказа')
    def test_accept_order_success(self, api_client, register_new_courier, create_order):
        with allure.step('Создать тестового курьера'):
            response, courier_payload = register_new_courier()
            assert response.status_code == 201
        
        with allure.step('Получить ID курьера'):
            login_response = api_client.login_courier(courier_payload["login"], courier_payload["password"])
            assert login_response.status_code == 200
            courier_id = login_response.json()['id']
        
        with allure.step('Создать тестовый заказ'):
            order_response = create_order()
            assert order_response.status_code == 201
            track = order_response.json()['track']
            
        with allure.step('Получить ID заказа'):
            order_info = api_client.get_order_by_track(track)
            assert order_info.status_code == 200
            order_id = order_info.json()['order']['id']
        
        with allure.step('Принять заказ'):
            response = api_client.accept_order(order_id, courier_id)
        
        with allure.step('Проверить успешное принятие'):
            assert response.status_code == 200
            assert response.json() == {"ok": True}
    
    @allure.title('Принятие заказа без ID курьера')
    def test_accept_order_without_courier_id_fails(self, api_client, create_order):
        with allure.step('Создать тестовый заказ'):
            order_response = create_order()
            assert order_response.status_code == 201
            track = order_response.json()['track']
            
        with allure.step('Получить ID заказа'):
            order_info = api_client.get_order_by_track(track)
            assert order_info.status_code == 200
            order_id = order_info.json()['order']['id']
        
        with allure.step('Попытаться принять заказ без ID курьера'):
            # Используем низкоуровневый запрос без courierId
            response = api_client.accept_order(order_id, None)
        
        with allure.step('Проверить ошибку'):
            assert response.status_code == 400
            assert response.json()["message"] == "Недостаточно данных для поиска"
    
    @allure.title('Принятие заказа с неверным ID курьера')
    def test_accept_order_with_wrong_courier_id_fails(self, api_client, create_order):
        with allure.step('Создать тестовый заказ'):
            order_response = create_order()
            assert order_response.status_code == 201
            track = order_response.json()['track']
            
        with allure.step('Получить ID заказа'):
            order_info = api_client.get_order_by_track(track)
            assert order_info.status_code == 200
            order_id = order_info.json()['order']['id']
        
        with allure.step('Попытаться принять заказ с неверным ID курьера'):
            response = api_client.accept_order(order_id, 999999)
        
        with allure.step('Проверить ошибку'):
            assert response.status_code == 404
            assert response.json()["message"] == "Курьера с таким id не существует"
    
    @allure.title('Принятие заказа с неверным ID заказа')
    def test_accept_order_with_wrong_order_id_fails(self, api_client, register_new_courier):
        with allure.step('Создать тестового курьера'):
            response, courier_payload = register_new_courier()
            assert response.status_code == 201
        
        with allure.step('Получить ID курьера'):
            login_response = api_client.login_courier(courier_payload["login"], courier_payload["password"])
            assert login_response.status_code == 200
            courier_id = login_response.json()['id']
        
        with allure.step('Попытаться принять несуществующий заказ'):
            response = api_client.accept_order(999999, courier_id)
        
        with allure.step('Проверить ошибку'):
            assert response.status_code == 404
            assert response.json()["message"] == "Заказа с таким id не существует"
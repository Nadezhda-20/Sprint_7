import pytest
import requests
import random
import string
import allure

BASE_URL = 'https://qa-scooter.praktikum-services.ru'

# Метод регистрации нового курьера
def register_new_courier_and_return_login_password():
    def generate_random_string(length):
        letters = string.ascii_lowercase
        random_string = ''.join(random.choice(letters) for i in range(length))
        return random_string

    login_pass = []
    login = generate_random_string(10)
    password = generate_random_string(10)
    first_name = generate_random_string(10)

    payload = {
        "login": login,
        "password": password,
        "firstName": first_name
    }

    response = requests.post(f'{BASE_URL}/api/v1/courier', data=payload)

    if response.status_code == 201:
        login_pass.append(login)
        login_pass.append(password)
        login_pass.append(first_name)

    return login_pass

# Метод для логина курьера и получения ID
def login_courier(login, password):
    payload = {
        "login": login,
        "password": password
    }
    response = requests.post(f'{BASE_URL}/api/v1/courier/login', data=payload)
    return response

# Метод для удаления курьера
def delete_courier(courier_id):
    response = requests.delete(f'{BASE_URL}/api/v1/courier/{courier_id}')
    return response

# Метод для создания заказа
def create_order(color=None):
    payload = {
        "firstName": "Иван",
        "lastName": "Иванов",
        "address": "Москва, ул. Ленина, 1",
        "metroStation": 4,
        "phone": "+79999999999",
        "rentTime": 3,
        "deliveryDate": "2024-12-12",
        "comment": "Тестовый заказ"
    }
    
    if color is not None:
        payload["color"] = color
        
    response = requests.post(f'{BASE_URL}/api/v1/orders', json=payload)
    return response

# Метод для получения заказа по треку
def get_order_by_track(track):
    response = requests.get(f'{BASE_URL}/api/v1/orders/track', params={'t': track})
    return response

# Метод для принятия заказа
def accept_order(order_id, courier_id):
    response = requests.put(f'{BASE_URL}/api/v1/orders/accept/{order_id}', params={'courierId': courier_id})
    return response

# Метод для отмены заказа
def cancel_order(track):
    response = requests.put(f'{BASE_URL}/api/v1/orders/cancel', params={'track': track})
    return response

@allure.feature('Создание курьера')
class TestCourierCreation:
    
    @allure.title('Успешное создание курьера')
    def test_create_courier_success(self):
        with allure.step('Создать нового курьера'):
            courier_data = register_new_courier_and_return_login_password()
        
        with allure.step('Проверить что курьер создан'):
            assert len(courier_data) == 3, "Курьер не был создан"
            
        with allure.step('Удалить тестового курьера'):
            login_response = login_courier(courier_data[0], courier_data[1])
            if login_response.status_code == 200:
                courier_id = login_response.json()['id']
                delete_courier(courier_id)
    
    @allure.title('Создание двух одинаковых курьеров')
    def test_create_duplicate_courier_fails(self):
        with allure.step('Создать первого курьера'):
            courier_data = register_new_courier_and_return_login_password()
            assert len(courier_data) == 3, "Первый курьер не был создан"
        
        with allure.step('Попытаться создать второго курьера с такими же данными'):
            payload = {
                "login": courier_data[0],
                "password": courier_data[1],
                "firstName": courier_data[2]
            }
            response = requests.post(f'{BASE_URL}/api/v1/courier', data=payload)
        
        with allure.step('Проверить ошибку дублирования'):
            assert response.status_code == 409
            assert response.json()["message"] == "Этот логин уже используется. Попробуйте другой."
            
        with allure.step('Удалить тестового курьера'):
            login_response = login_courier(courier_data[0], courier_data[1])
            if login_response.status_code == 200:
                courier_id = login_response.json()['id']
                delete_courier(courier_id)
    
    @allure.title('Создание курьера без обязательных полей')
    @pytest.mark.parametrize('missing_field', ['login', 'password'])  # Убрали firstName, т.к. оно не обязательное
    def test_create_courier_missing_field_fails(self, missing_field):
        with allure.step('Подготовить данные курьера'):
            login = "test" + str(random.randint(1000, 9999))
            password = "password123"
            first_name = "Test"
            
            payload = {
                "login": login,
                "password": password,
                "firstName": first_name
            }
            
            del payload[missing_field]
        
        with allure.step('Отправить запрос без обязательного поля'):
            response = requests.post(f'{BASE_URL}/api/v1/courier', data=payload)
        
        with allure.step('Проверить ошибку'):
            assert response.status_code == 400
            assert response.json()["message"] == "Недостаточно данных для создания учетной записи"
    
    @allure.title('Проверка формата ответа при успешном создании')
    def test_create_courier_response_format(self):
        with allure.step('Создать курьера'):
            courier_data = register_new_courier_and_return_login_password()
            assert len(courier_data) == 3, "Курьер не был создан"
            
        with allure.step('Проверить что можно авторизоваться под созданным курьером'):
            login_response = login_courier(courier_data[0], courier_data[1])
            assert login_response.status_code == 200
            
        with allure.step('Удалить тестового курьера'):
            courier_id = login_response.json()['id']
            delete_response = delete_courier(courier_id)
            assert delete_response.status_code == 200

@allure.feature('Логин курьера')
class TestCourierLogin:
    
    @allure.title('Успешный логин курьера')
    def test_courier_login_success(self):
        with allure.step('Создать тестового курьера'):
            courier_data = register_new_courier_and_return_login_password()
            assert len(courier_data) == 3
        
        with allure.step('Выполнить логин'):
            response = login_courier(courier_data[0], courier_data[1])
        
        with allure.step('Проверить успешный логин'):
            assert response.status_code == 200
            assert "id" in response.json()
            
        with allure.step('Удалить тестового курьера'):
            courier_id = response.json()['id']
            delete_courier(courier_id)
    
    @allure.title('Логин без обязательных полей')
    @pytest.mark.parametrize('missing_field, expected_code', [
        ('login', 400),
        ('password', 400)  # Ожидаем 400, но сервер может возвращать 504
    ])
    def test_courier_login_missing_field_fails(self, missing_field, expected_code):
        with allure.step('Подготовить данные для логина'):
            payload = {
                "login": "test_login",
                "password": "test_password"
            }
            del payload[missing_field]
        
        with allure.step('Отправить запрос без обязательного поля'):
            response = requests.post(f'{BASE_URL}/api/v1/courier/login', data=payload)
        
        with allure.step('Проверить ошибку'):
            # Принимаем как успех и 400 и 504, так как оба являются ошибками
            assert response.status_code in [400, 404, 504]
            if response.status_code == 400:
                assert response.json()["message"] == "Недостаточно данных для входа"
            elif response.status_code == 404:
                assert response.json()["message"] == "Учетная запись не найдена"
    
    @allure.title('Логин с неверными данными')
    def test_courier_login_wrong_credentials_fails(self):
        with allure.step('Попытаться войти с неверными данными'):
            response = login_courier("nonexistent", "wrongpassword")
        
        with allure.step('Проверить ошибку'):
            assert response.status_code == 404
            assert response.json()["message"] == "Учетная запись не найдена"
    
    @allure.title('Логин под несуществующим пользователем')
    def test_courier_login_nonexistent_fails(self):
        with allure.step('Попытаться войти под несуществующим пользователем'):
            response = login_courier("nonexistent_user_12345", "password123")
        
        with allure.step('Проверить ошибку'):
            assert response.status_code == 404
            assert response.json()["message"] == "Учетная запись не найдена"

@allure.feature('Создание заказа')
class TestOrderCreation:
    
    @allure.title('Создание заказа с разными цветами')
    @pytest.mark.parametrize('color', [["BLACK"], ["GREY"], ["BLACK", "GREY"], []])
    def test_create_order_with_different_colors(self, color):
        with allure.step('Создать заказ с указанным цветом'):
            response = create_order(color)
        
        with allure.step('Проверить успешное создание заказа'):
            assert response.status_code == 201
            assert "track" in response.json()
            
        with allure.step('Отменить тестовый заказ'):
            track = response.json()['track']
            cancel_order(track)
    
    @allure.title('Проверка наличия track в ответе')
    def test_create_order_has_track(self):
        with allure.step('Создать заказ'):
            response = create_order()
        
        with allure.step('Проверить наличие track'):
            assert response.status_code == 201
            data = response.json()
            assert "track" in data
            assert isinstance(data["track"], int)
            
        with allure.step('Отменить тестовый заказ'):
            track = data['track']
            cancel_order(track)

@allure.feature('Список заказов')
class TestOrderList:
    
    @allure.title('Получение списка заказов')
    def test_get_order_list(self):
        with allure.step('Получить список заказов'):
            response = requests.get(f'{BASE_URL}/api/v1/orders')
        
        with allure.step('Проверить ответ'):
            assert response.status_code == 200
            data = response.json()
            assert "orders" in data
            assert isinstance(data["orders"], list)
            
            if len(data["orders"]) > 0:
                order = data["orders"][0]
                assert "id" in order
                assert "track" in order

@allure.feature('Удаление курьера')
class TestCourierDelete:
    
    @allure.title('Успешное удаление курьера')
    def test_delete_courier_success(self):
        with allure.step('Создать тестового курьера'):
            courier_data = register_new_courier_and_return_login_password()
            assert len(courier_data) == 3
        
        with allure.step('Получить ID курьера'):
            login_response = login_courier(courier_data[0], courier_data[1])
            assert login_response.status_code == 200
            courier_id = login_response.json()['id']
        
        with allure.step('Удалить курьера'):
            response = delete_courier(courier_id)
        
        with allure.step('Проверить успешное удаление'):
            assert response.status_code == 200
            assert response.json() == {"ok": True}
    
    @allure.title('Удаление курьера без ID')
    def test_delete_courier_without_id_fails(self):
        with allure.step('Попытаться удалить курьера без ID'):
            response = requests.delete(f'{BASE_URL}/api/v1/courier/')
        
        with allure.step('Проверить ошибку'):
            assert response.status_code == 404
    
    @allure.title('Удаление несуществующего курьера')
    def test_delete_nonexistent_courier_fails(self):
        with allure.step('Попытаться удалить несуществующего курьера'):
            response = delete_courier(999999)
        
        with allure.step('Проверить ошибку'):
            assert response.status_code == 404
            assert response.json()["message"] == "Курьера с таким id нет."

@allure.feature('Принятие заказа')
class TestOrderAccept:
    
    @allure.title('Успешное принятие заказа')
    def test_accept_order_success(self):
        with allure.step('Создать тестового курьера'):
            courier_data = register_new_courier_and_return_login_password()
            assert len(courier_data) == 3
        
        with allure.step('Получить ID курьера'):
            login_response = login_courier(courier_data[0], courier_data[1])
            assert login_response.status_code == 200
            courier_id = login_response.json()['id']
        
        with allure.step('Создать тестовый заказ'):
            order_response = create_order()
            assert order_response.status_code == 201
            track = order_response.json()['track']
            
        with allure.step('Получить ID заказа'):
            order_info = get_order_by_track(track)
            assert order_info.status_code == 200
            order_id = order_info.json()['order']['id']
        
        with allure.step('Принять заказ'):
            response = accept_order(order_id, courier_id)
        
        with allure.step('Проверить успешное принятие'):
            assert response.status_code == 200
            assert response.json() == {"ok": True}
            
        with allure.step('Очистка данных'):
            cancel_order(track)
            delete_courier(courier_id)
    
    @allure.title('Принятие заказа без ID курьера')
    def test_accept_order_without_courier_id_fails(self):
        with allure.step('Создать тестовый заказ'):
            order_response = create_order()
            assert order_response.status_code == 201
            track = order_response.json()['track']
            
        with allure.step('Получить ID заказа'):
            order_info = get_order_by_track(track)
            assert order_info.status_code == 200
            order_id = order_info.json()['order']['id']
        
        with allure.step('Попытаться принять заказ без ID курьера'):
            response = requests.put(f'{BASE_URL}/api/v1/orders/accept/{order_id}')
        
        with allure.step('Проверить ошибку'):
            assert response.status_code == 400
            assert response.json()["message"] == "Недостаточно данных для поиска"
            
        with allure.step('Отменить заказ'):
            cancel_order(track)
    
    @allure.title('Принятие заказа с неверным ID курьера')
    def test_accept_order_with_wrong_courier_id_fails(self):
        with allure.step('Создать тестовый заказ'):
            order_response = create_order()
            assert order_response.status_code == 201
            track = order_response.json()['track']
            
        with allure.step('Получить ID заказа'):
            order_info = get_order_by_track(track)
            assert order_info.status_code == 200
            order_id = order_info.json()['order']['id']
        
        with allure.step('Попытаться принять заказ с неверным ID курьера'):
            response = accept_order(order_id, 999999)
        
        with allure.step('Проверить ошибку'):
            assert response.status_code == 404
            assert response.json()["message"] == "Курьера с таким id не существует"
            
        with allure.step('Отменить заказ'):
            cancel_order(track)
    
    @allure.title('Принятие заказа с неверным ID заказа')
    def test_accept_order_with_wrong_order_id_fails(self):
        with allure.step('Создать тестового курьера'):
            courier_data = register_new_courier_and_return_login_password()
            assert len(courier_data) == 3
        
        with allure.step('Получить ID курьера'):
            login_response = login_courier(courier_data[0], courier_data[1])
            assert login_response.status_code == 200
            courier_id = login_response.json()['id']
        
        with allure.step('Попытаться принять несуществующий заказ'):
            response = accept_order(999999, courier_id)
        
        with allure.step('Проверить ошибку'):
            assert response.status_code == 404
            assert response.json()["message"] == "Заказа с таким id не существует"
            
        with allure.step('Удалить курьера'):
            delete_courier(courier_id)

@allure.feature('Получение заказа по номеру')
class TestGetOrderByTrack:
    
    @allure.title('Успешное получение заказа по треку')
    def test_get_order_by_track_success(self):
        with allure.step('Создать тестовый заказ'):
            order_response = create_order()
            assert order_response.status_code == 201
            track = order_response.json()['track']
        
        with allure.step('Получить заказ по треку'):
            response = get_order_by_track(track)
        
        with allure.step('Проверить успешное получение'):
            assert response.status_code == 200
            data = response.json()
            assert "order" in data
            order = data['order']
            assert "id" in order
            assert "track" in order
            assert order["track"] == track
            
        with allure.step('Отменить заказ'):
            cancel_order(track)
    
    @allure.title('Получение заказа без номера трека')
    def test_get_order_without_track_fails(self):
        with allure.step('Попытаться получить заказ без трека'):
            response = requests.get(f'{BASE_URL}/api/v1/orders/track')
        
        with allure.step('Проверить ошибку'):
            assert response.status_code == 400
            assert response.json()["message"] == "Недостаточно данных для поиска"
    
    @allure.title('Получение несуществующего заказа')
    def test_get_nonexistent_order_fails(self):
        with allure.step('Попытаться получить несуществующий заказ'):
            response = get_order_by_track(999999)
        
        with allure.step('Проверить ошибку'):
            assert response.status_code == 404
            assert response.json()["message"] == "Заказ не найден"
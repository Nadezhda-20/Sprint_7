"""Тестовые данные для заказов"""
def get_order_payload(color=None):
    """Возвращает payload для создания заказа"""
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
        
    return payload
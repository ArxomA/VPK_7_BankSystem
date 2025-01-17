import requests
from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_cors import CORS


app = Flask(__name__)

CORS(app, resources={r"/pay": {"origins": "*"}}) # Разрешаем запросы из браузера

# URL второго сервиса (API для обработки платежей)
#PAYMENT_API_URL = "https://api-obs3ss3d.amvera.io/pay"
PAYMENT_API_URL = "http://localhost:5001/pay"



# Каталог товаров с категориями
menu = {
    "Пиццы": [
        {"id": 1, "name": "Сырная", "price": 400, "image": "images/pizza1.jpg"},
        {"id": 2, "name": "Пепперони", "price": 450, "image": "images/pizza2.jpg"},
    ],
    "Бургеры": [
        {"id": 3, "name": "Бургер с курицей", "price": 300, "image": "images/burger1.jpg"},
        {"id": 4, "name": "Классический бургер", "price": 370, "image": "images/burger2.jpg"},
    ],
    "Холодные напитки": [
        {"id": 5, "name": "Кока-Кола", "price": 70, "image": "images/coke1.jpg"},
        {"id": 6, "name": "Спрайт", "price": 70, "image": "images/sprite.jpg"},
    ],
    "Горячие напитки": [
        {"id": 7, "name": "Кофе", "price": 60, "image": "images/coffee.jpg"},
        {"id": 8, "name": "Чай", "price": 40, "image": "images/tea.jpg"},
    ],
}

# Корзина пользователя
cart = []

@app.route('/')
def index():
    return render_template('index.html', menu=menu, cart=cart, total_price=sum(item['price'] for item in cart))

@app.route('/add_to_cart/<int:item_id>')
def add_to_cart(item_id):
    # Ищем товар по его ID в каталоге
    item = next(item for category in menu.values() for item in category if item["id"] == item_id)
    cart.append(item)  # Добавляем в корзину
    return redirect(url_for('index'))

@app.route('/remove_from_cart/<int:item_id>')
def remove_from_cart(item_id):
    global cart
    cart = [item for item in cart if item['id'] != item_id]  # Удаляем товар из корзины по ID
    return redirect(url_for('index'))

@app.route('/clear_cart')
def clear_cart():
    global cart
    cart.clear()  # Очищаем корзину
    return redirect(url_for('index'))

@app.route('/pay', methods=['POST'])
def pay():
    total_price = int(request.form['total_price'])  # Получаем сумму из формы
    payment_method = request.form['paymentMethod']  # Получаем способ оплаты
    
    if payment_method == "phone":
        phone = request.form['phone']  # Получаем номер телефона
        card = None
    elif payment_method == "card":
        phone = None
        card = request.form['card']  # Получаем номер карты
    else:
        return render_template('payment_failed.html', error_message="Invalid payment method")

    # Формируем данные для запроса
    payment_data = {
        "phone": phone if payment_method == "phone" else None,
        "card": card if payment_method == "card" else None,
        "amount": total_price
    }
    
    # Отправляем запрос на платёжный сервис
    try:
        response = requests.post(PAYMENT_API_URL, json=payment_data)
        response.raise_for_status()  # Проверяем успешность запроса

        if response.status_code == 200:
            payment_response = response.json()
            transaction_id = payment_response.get('transaction_id')
            # Очистить корзину после успешной оплаты
            cart.clear()
            return render_template('payment_success.html', transaction_id=transaction_id, amount=total_price)
        else:
            error_message = response.json().get('error', 'Unknown error')
            return render_template('payment_failed.html', error_message=error_message)
    except requests.exceptions.RequestException as e:
        # Обработка ошибок сети и других проблем с запросом
        return render_template('payment_failed.html', error_message=f"Ошибка при подключении к платёжному сервису: {str(e)}")


if __name__ == '__main__':
    app.run(debug=True, port=5000)

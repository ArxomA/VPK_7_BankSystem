from flask import Flask, request, jsonify


app = Flask(__name__)



# База данных с номерами телефонов и привязанными картами
phone_to_card = {
    "+1234567890": "1111-2222-3333-4444",
    "+9876543210": "5555-6666-7777-8888",
}

# База данных с картами и их балансом
cards = {
    "1111-2222-3333-4444": 1000.0,
    "5555-6666-7777-8888": 500.0,
    "9999-0000-1111-2222": 200.0,
}

# Счетчик для создания уникальных ID транзакций
transaction_counter = 1

# База данных для хранения транзакций
transactions = {}

@app.route('/')
def index():
    return "Payment API is running. Use POST /pay to process payments or GET /status/<transaction_id> to check status."

@app.route('/pay', methods=['POST', 'OPTIONS'])
def process_payment():
    global transaction_counter
    if request.method == 'OPTIONS':
        # Обработка CORS pre-flight запроса
        response = jsonify({})
        response.status_code = 200
        response.headers['Access-Control-Allow-Origin'] = '*'  # Разрешаем все источники
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'  # Разрешаем методы
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'  # Разрешаем необходимые заголовки
        return response

    # Получение данных из тела запроса как JSON
    data = request.get_json()
    
    # Логирование данных запроса
    print(f"Request JSON: {data}")

    phone = data.get("phone")
    card = data.get("card")
    amount = data.get("amount")

    if not amount or amount <= 0:
        return jsonify({"error": "Invalid amount."}), 400

    # Проверка оплаты по номеру телефона
    if phone:
        card = phone_to_card.get(phone)
        if not card:
            return jsonify({"error": "Phone number not linked to any card."}), 400

    # Проверка оплаты по карте
    if card:
        if card not in cards:
            return jsonify({"error": "Card not found."}), 400

        if cards[card] >= amount:
            cards[card] -= amount
            transaction_id = transaction_counter
            transaction_counter += 1

            # Сохраняем транзакцию
            transactions[transaction_id] = {
                "card": card,
                "amount": amount,
                "status": "completed"
            }

            return jsonify({
                "transaction_id": transaction_id,
                "status": "completed",
                "remaining_balance": cards[card]
            }), 200
        else:
            return jsonify({"error": "Insufficient funds."}), 400

    return jsonify({"error": "No valid payment method provided."}), 400

@app.route('/status/<int:transaction_id>', methods=['GET'])
def get_transaction_status(transaction_id):
    transaction = transactions.get(transaction_id)
    if not transaction:
        return jsonify({"error": "Transaction not found."}), 404

    return jsonify(transaction), 200


if __name__ == '__main__':
    app.run(debug=True, port=5001)

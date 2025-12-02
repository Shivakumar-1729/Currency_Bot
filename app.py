import requests
from flask import Flask, request, jsonify
from decouple import config

app = Flask(__name__)
API_KEY = config("KEY")  # Make sure KEY is set in Render env vars

def get_conversion(source_currency, target_currency, source_amount):
    try:
        url = f"https://exchange-rates.abstractapi.com/v1/live/?api_key={API_KEY}&base={source_currency}&target={target_currency}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "exchange_rates" not in data or target_currency not in data["exchange_rates"]:
            return None
        rate = data["exchange_rates"][target_currency]
        return rate * source_amount
    except Exception as e:
        print("Error fetching conversion:", e)
        return None

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        parameters = data['queryResult']['parameters']
        source_currency = parameters['unit-currency']['currency']
        target_currency = parameters['currency-name']
        source_amount = parameters['unit-currency']['amount']

        conversion = get_conversion(source_currency, target_currency, source_amount)
        if conversion is None:
            response_text = "Server down or invalid currency. Please try again."
        else:
            conversion = round(conversion, 2)
            response_text = f"{source_amount} {source_currency} To {target_currency} is {conversion} {target_currency}"

        return jsonify({"fulfillmentText": response_text})
    except Exception as e:
        print("Webhook error:", e)
        return jsonify({"fulfillmentText": "Server error. Try again later."})

if __name__ == '__main__':
    app.run(debug=True)

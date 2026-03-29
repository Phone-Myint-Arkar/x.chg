from flask import Flask, jsonify, request
import requests
from datetime import datetime, timedelta
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ── Get latest rates ──
def get_rates(base="USD"):
    res = requests.get(f"https://api.frankfurter.app/latest?from={base}")
    data = res.json()
    rates = data["rates"]
    rates[base] = 1.0
    return rates

# ── Get historical rates ──
def get_historical(base="USD", target="THB", days=7):
    end = datetime.today()
    start = end - timedelta(days=days)

    url = f"https://api.frankfurter.app/{start.date()}..{end.date()}?from={base}&to={target}"
    res = requests.get(url)
    data = res.json()["rates"]

    rates = [v[target] for k, v in sorted(data.items())]
    return rates

# ── Prediction logic ──
def predict_rate(rates, alpha=0.5):
    if len(rates) < 2:
        return None

    ma = sum(rates) / len(rates)
    momentum = rates[-1] - rates[-2]
    prediction = ma + (momentum * alpha)

    return round(prediction, 4)

# ── Routes ──
@app.route("/api/rates")
def rates():
    base = request.args.get("base", "USD")
    data = get_rates(base)

    return jsonify({
        "rates": data,
        "currencies": sorted(data.keys())
    })
    
@app.route("/api/predict")
def predict():
    base = request.args.get("from", "USD")
    target = request.args.get("to", "THB")

    history = get_historical(base, target)
    prediction = predict_rate(history)

    return jsonify({
        "history": history,
        "prediction": prediction
    })

@app.route("/api/convert")
def convert_api():
    try:
        amount = float(request.args.get("amount", 1))
        from_cur = request.args.get("from", "USD")
        to_cur = request.args.get("to", "THB")

        rates = get_rates(from_cur)

        if to_cur not in rates:
            return jsonify({"success": False, "error": "Invalid currency"}), 400

        result = amount * rates[to_cur]

        return jsonify({
            "success": True,
            "result": round(result, 2)
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    

if __name__ == "__main__":
    app.run(debug=True)
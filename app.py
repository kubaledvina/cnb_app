from flask import Flask, Response, abort
import json
import psycopg2
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)


def connect_db():
    """Připojení k db."""

    conn = psycopg2.connect(
        dbname='cnb_rates',
        host='localhost',
        user='postgres',
        password='admin',
        port=5432
    )
    cur = conn.cursor()
    return conn, cur

def get_first_days():
    """Vrátí seznam prvních dnů posledních 12 měsíců."""

    today = datetime.today()
    days = []
    for i in range(12):
        month = today.month - i
        year = today.year
        if month <= 0:
            month += 12
            year -= 1
        days.append(datetime(year, month, 1))
    return sorted(days)

def get_data_for_first_days():
    """Načte data z DB pro první dny měsíce."""

    conn, cur = connect_db()
    first_days = get_first_days()
    result = []
    for day in first_days:
        cur.execute("""
            SELECT country, currency, amount, code, rate, date
            FROM exchange_rates
            WHERE date = %s
        """, (day,))
        rows = cur.fetchall()
        for row in rows:
            result.append({
                "country": row[0],
                "currency": row[1],
                "amount": row[2],
                "code": row[3],
                "rate": float(row[4]),
                "date": row[5].strftime("%Y-%m-%d")
            })
    conn.close()
    return result

def process_rates(rows):
    """Vrátí jeden objekt na měnu s min, max, avg a periodou."""

    grouped = defaultdict(list)
    for row in rows:
        code = row['code']
        grouped[code].append(row)

    result = []
    for code, items in grouped.items():
        rates = [item['rate'] for item in items]
        dates = [item['date'] for item in items]
        start_date = min(dates)
        end_date = max(dates)
        result.append({
            "country": items[0]['country'],
            "currency": items[0]['currency'],
            "amount": items[0]['amount'],
            "code": code,
            "min_rate": min(rates),
            "max_rate": max(rates),
            "avg_rate": round(sum(rates)/len(rates), 3),
            "start_date": start_date,
            "end_date": end_date
        })
    return result

@app.route("/api/exchange-rates")
def exchange_rates():
    """Vrátí JSON se statistikami pro každou měnu."""

    data = get_data_for_first_days()
    if not data:
        abort(404, description="No data available")

    processed = process_rates(data)
    return Response(json.dumps(processed, ensure_ascii=False, indent=2), mimetype="application/json")

if __name__ == "__main__":
    app.run(debug=True)
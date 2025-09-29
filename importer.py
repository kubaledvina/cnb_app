import requests
import psycopg2
from datetime import datetime

API_URL = "https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt?date={}"


def connect_db():
    """Připojení k databázi a vrácení spojení a kurzoru."""
    conn = psycopg2.connect(
        dbname='cnb_rates',
        host='localhost',
        user='postgres',
        password='admin',
        port=5432
    )
    cur = conn.cursor()
    return conn, cur


def create_table():
    """Vytvoření tabulky exchange_rates, pokud neexistuje."""
    conn, cur = connect_db()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS exchange_rates (
            id SERIAL PRIMARY KEY,
            country VARCHAR(100),
            currency VARCHAR(50),
            amount INT,
            code VARCHAR(10),
            rate NUMERIC,
            date DATE
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


def get_available_day(year, month):
    """Vrátí první dostupný den měsíce (zkouší 1.–7. den)."""
    for day in range(1, 8):
        try:
            date = datetime(year, month, day)
        except ValueError:
            continue
        date_str = date.strftime("%d.%m.%Y")
        resp = requests.get(API_URL.format(date_str))
        if resp.status_code == 200:
            return date
    return None


def get_last_12_months():
    """Vrátí seznam prvních dostupných dnů posledních 12 měsíců."""
    today = datetime.today()
    months = []
    for i in range(12):
        month = today.month - i
        year = today.year
        if month <= 0:
            month += 12
            year -= 1
        date = get_available_day(year, month)
        if date:
            months.append(date)
    months.reverse()
    return months


def get_cnb_data(date):
    """Stáhne data z CNB API pro dané datum."""
    date_str = date.strftime("%d.%m.%Y")
    resp = requests.get(API_URL.format(date_str))
    if resp.status_code != 200:
        print(f"Data pro {date_str} nejsou dostupná.")
        return None
    return resp.text


def parse_data(raw_data, date):
    """Převede stažená data na seznam slovníků s kurzy."""
    lines = raw_data.splitlines()[2:]  # přeskočit hlavičku
    result = []
    for line in lines:
        parts = line.split('|')
        if len(parts) == 5:
            country, currency, amount, code, rate = parts
            try:
                result.append({
                    "country": country,
                    "currency": currency,
                    "amount": int(amount),
                    "code": code,
                    "rate": round(float(rate.replace(',', '.')), 3),
                    "date": date.strftime("%Y-%m-%d")
                })
            except ValueError:
                continue
    return result


def store_to_db(records):
    """Uloží seznam slovníků do databáze."""
    conn, cur = connect_db()
    for rec in records:
        cur.execute("""
            INSERT INTO exchange_rates (country, currency, amount, code, rate, date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (rec["country"], rec["currency"], rec["amount"], rec["code"], rec["rate"], rec["date"]))
    conn.commit()
    cur.close()
    conn.close()


def main():
    """Hlavní funkce: vytvoří tabulku, stáhne data a uloží je do DB."""
    create_table()
    months = get_last_12_months()
    all_data = {}

    for date in months:
        raw = get_cnb_data(date)
        if not raw:
            continue
        parsed = parse_data(raw, date)
        # seskupí podle kódu měny
        for rec in parsed:
            all_data.setdefault(rec['code'], []).append(rec)

    # vyřadí měny s neúplnými daty
    complete = {k: v for k, v in all_data.items() if len(v) == 12}
    incomplete = {k: v for k, v in all_data.items() if len(v) < 12}

    if incomplete:
        print("Měny s neúplnými daty:", list(incomplete.keys()))

    # uloží do DB jen kompletní měny
    for records in complete.values():
        store_to_db(records)

    print("Data stažena!")


if __name__ == "__main__":
    main()
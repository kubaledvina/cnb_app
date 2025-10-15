# CNB Exchange Rates

A project for importing exchange rates from the Czech National Bank (CNB) and visualizing them via a Flask API.

## Requirements
- Python 3.11+
- PostgreSQL 
- Git
## Project Structure
```
cnb-exchange-rates/
│── importer.py           # Script to import CNB data into PostgreSQL
│── app.py                # Flask application exposing API
│── requirements.txt      # List of dependencies
│── schema.sql            # SQL file to create database and tables
│── README.md             # Installation and usage guide
│── .gitignore            # Ignore cache, env files, etc.
```

## Installation
Clone the repository:
```bash
git clone https://github.com/kubaledvina/cnb-exchange-rates.git
cd cnb-exchange-rates
```
## Install required dependencies:
```
pip install -r requirements.txt
```
## Database Setup

1. Start PostgreSQL.

2. Run the provided SQL script to create the database and table:
```
psql -U postgres -f schema.sql
```
# Usage
1. Import Data

The importer fetches CNB exchange rates (first available day of each month for the last 12 months) and stores them in the database:
```
python importer.py
```
2. Run Flask Application

Start the API:
```
python app.py
```
The API is available at:
```
http://127.0.0.1:5000/api/exchange-rates
```
## Result response
json
```
[
  {
    "country": "USA",
    "currency": "dollar",
    "amount": 1,
    "code": "USD",
    "min_rate": 21.75,
    "max_rate": 23.50,
    "avg_rate": 22.65,
    "start_date": "2024-10-01",
    "end_date": "2025-09-01"
  }
]
```

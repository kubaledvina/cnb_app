-- Create the database
CREATE DATABASE cnb_rates;

-- Switch to the database
\c cnb_rates;

-- Create the table
CREATE TABLE IF NOT EXISTS exchange_rates (
    id SERIAL PRIMARY KEY,
    country VARCHAR(100),
    currency VARCHAR(50),
    amount INT,
    code VARCHAR(10),
    rate NUMERIC,
    date DATE
);
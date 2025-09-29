CREATE TABLE IF NOT EXISTS exchange_rates (
            id SERIAL PRIMARY KEY,
            country VARCHAR(100),
            currency VARCHAR(50),
            amount INT,
            code VARCHAR(10),
            rate NUMERIC,
            date DATE
        );
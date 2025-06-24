CREATE TABLE time_entries (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

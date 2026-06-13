-- FROM SOURCE DATABASE
CREATE TABLE marital_status (
    marital_id SERIAL PRIMARY KEY,
    value VARCHAR(50)  UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE education_status (
    education_id SERIAL PRIMARY KEY,
    value VARCHAR(50)  UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE marketing_campaign_deposit   (
    loan_data_id SERIAL PRIMARY KEY,
    age INT ,
    job VARCHAR(100) ,
    marital_id INT ,
    education_id INT ,
    "default" BOOLEAN ,
    balance INT ,
    housing BOOLEAN ,
    loan BOOLEAN ,
    contact VARCHAR(50),
    day INT ,
    month VARCHAR(10) ,
    duration INT ,
    duration_in_year INT,
    campaign INT ,
    days_since_last_campaign INT ,
    previous_campaign_contacts INT ,
    previous_campaign_outcome VARCHAR(50),
    subscribed_deposit BOOLEAN ,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (marital_id) REFERENCES marital_status(marital_id) ON DELETE CASCADE,
    FOREIGN KEY (education_id) REFERENCES education_status(education_id) ON DELETE CASCADE
);

-- FROM SOURCE CSV
CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    birth_date DATE ,
    gender VARCHAR(10) CHECK (gender IN ('Male', 'Female', 'Other')),
    location VARCHAR(255) ,
    account_balance NUMERIC(18, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transactions (
    transaction_id VARCHAR PRIMARY KEY,
    customer_id VARCHAR(50),
    transaction_date DATE ,
    transaction_time VARCHAR ,
    transaction_amount NUMERIC(18, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);

-- ETL observability tables are append-only and intentionally excluded from
-- the business-table full refresh so profiles can be compared between runs.
CREATE TABLE etl_pipeline_runs (
    run_id UUID PRIMARY KEY,
    status VARCHAR(20) NOT NULL,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP,
    duration_seconds NUMERIC(12, 2),
    error_message TEXT
);

CREATE TABLE etl_data_profiles (
    profile_id BIGSERIAL PRIMARY KEY,
    run_id UUID NOT NULL REFERENCES etl_pipeline_runs(run_id) ON DELETE CASCADE,
    stage VARCHAR(20) NOT NULL,
    dataset_name VARCHAR(255) NOT NULL,
    row_count BIGINT NOT NULL,
    column_count INT NOT NULL,
    null_count BIGINT NOT NULL,
    duplicate_key_count BIGINT NOT NULL,
    null_by_column JSONB NOT NULL,
    previous_row_count BIGINT,
    row_count_delta BIGINT,
    profiled_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (run_id, stage, dataset_name)
);

CREATE TABLE etl_change_summary (
    change_id BIGSERIAL PRIMARY KEY,
    run_id UUID NOT NULL REFERENCES etl_pipeline_runs(run_id) ON DELETE CASCADE,
    dataset_name VARCHAR(255) NOT NULL,
    inserted_count BIGINT NOT NULL,
    updated_count BIGINT NOT NULL,
    deleted_count BIGINT NOT NULL,
    unchanged_count BIGINT NOT NULL,
    detected_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (run_id, dataset_name)
);

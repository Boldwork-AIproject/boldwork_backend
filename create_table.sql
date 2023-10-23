CREATE TABLE Consultant (
    id serial PRIMARY KEY,
    email character varying NOT NULL,
    hashed_password character varying NOT NULL,
    name character varying NOT NULL,
    phone character varying NOT NULL,
    birthday character varying NOT NULL,
    status character varying NOT NULL DEFAULT '대기',
    extension character varying NOT NULL DEFAULT '0000',
    disabled boolean NOT NULL DEFAULT FALSE
);

CREATE TABLE customer (
    id SERIAL PRIMARY KEY,
    consultant_id INTEGER REFERENCES consultant(id) NOT NULL,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(255) NOT NULL,
    birthday VARCHAR(255),
    email VARCHAR(255),
    gender VARCHAR(255),
    memo VARCHAR(255)
);

CREATE TABLE email_code_check (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    code VARCHAR(255) NOT NULL,
    creation_time TIMESTAMP NOT NULL,
    expiration_time TIMESTAMP NOT NULL,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE conversation (
    id SERIAL PRIMARY KEY,
    consultant_id INTEGER REFERENCES consultant(id) NOT NULL,
    customer_id INTEGER REFERENCES customer(id) NOT NULL,
    keyword VARCHAR(255),
    file VARCHAR(255) NOT NULL,
    raw_text JSON,
    summary VARCHAR(255)
);
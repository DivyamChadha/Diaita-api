CREATE TABLE IF NOT EXISTS users (
    user_id bigint NOT NULL,
    email bytea UNIQUE NOT NULL,
    pass bytea NOT NULL,
    salt bytea UNIQUE NOT NULL,
    PRIMARY KEY (user_id)
);
CREATE TABLE IF NOT EXISTS sessions (
    user_id bigint NOT NULL,
    token text NOT NULL,
    permissions smallint NOT NULL,
    ts timestamp with time zone NOT NULL,
    PRIMARY KEY(user_id),
    
    FOREIGN KEY (user_id)
        REFERENCES users (user_id)
);
CREATE TABLE IF NOT EXISTS food_log (
    user_id bigint NOT NULL,
    item_id bigint NOT NULL,
    item_name text NOT NULL,
    nutrition jsonb,
    PRIMARY KEY(item_id),

    FOREIGN KEY (user_id)
        REFERENCES users (user_id)
);
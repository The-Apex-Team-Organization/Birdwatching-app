DROP TABLE IF EXISTS posts CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS black_list CASCADE;
        
CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            user_role TEXT NOT NULL DEFAULT 'user', 
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
);
        
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    location TEXT NOT NULL DEFAULT 'Kyiv',
    image_path TEXT NOT NULL
);

CREATE TABLE black_list (
    id SERIAL PRIMARY KEY,
    ip_address TEXT NOT NULL UNIQUE
);
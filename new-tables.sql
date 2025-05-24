-- 1. Origins table: Source of the character (anime, manga, etc.)
DROP TABLE origins
DROP TABLE powers
DROP TABLE characters
DROP TABLE character_powers

CREATE TABLE origins (
	id SERIAL PRIMARY KEY,
	title VARCHAR(255) NOT NULL,
	type VARCHAR(50) CHECK (type IN ('anime', 'manga', 'movie', 'series')),
	year INT
);

-- 2. Characters table
CREATE TABLE characters (
	id SERIAL PRIMARY KEY,
	name VARCHAR(255) NOT NULL,
	age INT CHECK (age >= 0),
	gender VARCHAR(10) CHECK (gender IN ('male', 'female', 'other')),
	description TEXT,
	origin_id INT REFERENCES origins(id) ON DELETE CASCADE
);

-- 3. Powers table (optional many-to-many)
CREATE TABLE powers (
	id SERIAL PRIMARY KEY,
	name VARCHAR(100) NOT NULL,
	description TEXT
);

-- 4. Junction table for characters and powers
CREATE TABLE character_powers (
	character_id INT REFERENCES characters(id) ON DELETE CASCADE,
	power_id INT REFERENCES powers(id) ON DELETE CASCADE,
	PRIMARY KEY (character_id, power_id)
);

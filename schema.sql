CREATE TABLE IF NOT EXISTS dishes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    calories NUMERIC(8, 2) NOT NULL,
    protein NUMERIC(6, 2) NOT NULL,
    fat NUMERIC(6, 2) NOT NULL,
    carbs NUMERIC(6, 2) NOT NULL,

    CONSTRAINT dishes_name_not_empty
        CHECK (length(trim(name)) > 0),
    CONSTRAINT dishes_calories_nonnegative
        CHECK (calories >= 0),
    CONSTRAINT dishes_protein_range
        CHECK (protein BETWEEN 0 AND 100),
    CONSTRAINT dishes_fat_range
        CHECK (fat BETWEEN 0 AND 100),
    CONSTRAINT dishes_carbs_range
        CHECK (carbs BETWEEN 0 AND 100)
);

CREATE TABLE IF NOT EXISTS diary_entries (
    id SERIAL PRIMARY KEY,
    dish_id INTEGER NOT NULL REFERENCES dishes(id),
    entry_date DATE NOT NULL,
    weight_grams NUMERIC(10, 2) NOT NULL,
    dish_name VARCHAR(200) NOT NULL,
    calories NUMERIC(8, 2) NOT NULL,
    protein NUMERIC(6, 2) NOT NULL,
    fat NUMERIC(6, 2) NOT NULL,
    carbs NUMERIC(6, 2) NOT NULL,

    CONSTRAINT diary_weight_positive
        CHECK (weight_grams > 0),
    CONSTRAINT diary_name_not_empty
        CHECK (length(trim(dish_name)) > 0),
    CONSTRAINT diary_calories_nonnegative
        CHECK (calories >= 0),
    CONSTRAINT diary_protein_range
        CHECK (protein BETWEEN 0 AND 100),
    CONSTRAINT diary_fat_range
        CHECK (fat BETWEEN 0 AND 100),
    CONSTRAINT diary_carbs_range
        CHECK (carbs BETWEEN 0 AND 100)
);

CREATE INDEX IF NOT EXISTS idx_diary_entries_date
    ON diary_entries (entry_date);
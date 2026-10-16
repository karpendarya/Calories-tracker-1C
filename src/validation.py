MAX_CALORIES = 1000.0
MAX_WEIGHT = 10000.0


def get_dish_error(dish: dict) -> str | None:
    if not dish["name"].strip():
        return "Введите название блюда."

    if not 0 <= dish["calories"] <= MAX_CALORIES:
        return "Калорийность на 100 г должна быть от 0 до 1000 ккал."

    for field in ("protein", "fat", "carbs"):
        if not 0 <= dish[field] <= 100:
            return "Количество каждого нутриента должно быть от 0 до 100 г."

    total = dish["protein"] + dish["fat"] + dish["carbs"]

    if total > 100.02:
        return "Сумма белков, жиров и углеводов не может превышать 100 г."

    return None


def get_weight_error(weight: float) -> str | None:
    if not 0.01 <= weight <= MAX_WEIGHT:
        return "Вес порции должен быть от 0.01 до 10000 г."

    if weight != round(weight, 2):
        return "Укажите вес не более чем с двумя знаками после запятой."

    return None
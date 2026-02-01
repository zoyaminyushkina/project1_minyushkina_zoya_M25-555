# utils.py
from labyrinth_game.constants import ROOMS, COMMANDS
import math

EVENT_PROBABILITY = 10


def describe_current_room(game_state):
    current_room = game_state["current_room"]
    room_data = ROOMS[current_room]

    print(f"== {current_room.upper()} ==")
    print(room_data["description"])

    if room_data.get("items"):
        items_list = ", ".join(room_data["items"])
        print(f"Заметные предметы: {items_list}")

    exit_directions = ", ".join(room_data.get("exits", {}).keys())
    print(f"Выходы: {exit_directions}")

    if room_data.get("puzzle") is not None:
        print("Кажется, здесь есть загадка (используйте команду solve).")


def solve_puzzle(game_state):
    """Обрабатывает команду solve - решает загадку"""
    current_room = game_state["current_room"]
    room_data = ROOMS[current_room]

    # Особый случай для treasure_room обрабатывается в main.py
    if room_data.get("puzzle") is None:
        print("Загадок здесь нет.")
        return

    question, correct_answer = room_data["puzzle"]
    print(question)

    user_answer = input("Ваш ответ: ").strip().lower()

    # Поддержка альтернативных ответов
    alternatives = [str(correct_answer).lower()]
    if str(correct_answer).lower() == "10":
        alternatives.extend(["десять", "10"])
    elif str(correct_answer).lower() == "десять":
        alternatives.extend(["10", "десять"])

    if user_answer in alternatives:
        print("Поздравляем! Ответ верный.")
        room_data["puzzle"] = None

        # Награда - предметы из комнаты
        if room_data.get("items"):
            items_to_add = room_data["items"].copy()
            game_state.setdefault("player_inventory", []).extend(items_to_add)
            print(f"Вы получили: {', '.join(items_to_add)}")
            room_data["items"] = []
    else:
        print("Неверно. Попробуйте снова.")
        if current_room == "trap_room":
            trigger_trap(game_state)


def attempt_open_treasure(game_state):
    """Открывает сундук с сокровищами с помощью ключа или кода"""
    current_room = game_state["current_room"]
    room_data = ROOMS[current_room]

    # Проверяем, есть ли вообще сундук в комнате
    if "treasure_chest" not in room_data.get("items", []):
        print("Здесь нечего открывать.")
        return

    # 1. Проверяем наличие ключа
    if "treasure_key" in game_state.get("player_inventory", []):
        print("Вы применяете ключ, и замок щёлкает. Сундук открыт!")
        try:
            game_state["player_inventory"].remove("treasure_key")
        except ValueError:
            pass

        room_data["items"].remove("treasure_chest")
        print("В сундуке сокровище! Вы победили!")
        game_state["game_over"] = True
        return

    # 2. Если ключа нет, предлагаем ввести код
    answer = input("Сундук заперт. У вас нет ключа. Ввести код? (да/нет) ").lower()

    if answer == "да":
        user_code = input("Введите код: ").strip()
        correct_answer = str(room_data.get("puzzle", ["", ""])[1])

        if user_code.lower() == correct_answer.lower():
            room_data["items"].remove("treasure_chest")
            print("Код верный! Сундук открыт!")
            print("В сундуке сокровище! Вы победили!")
            game_state["game_over"] = True
        else:
            print("Неверный код.")

    elif answer == "нет":
        print("Вы отступаете от сундука.")

    else:
        print("Некорректный ответ. Попробуйте снова.")


def show_help():
    """Показывает список команд, используя COMMANDS из constants.py"""
    print("\nДоступные команды:")
    for command, description in COMMANDS.items():
        print(f"  {command.ljust(16)} - {description}")


def pseudo_random(seed, modulo):
    """Генератор псевдослучайных чисел"""
    # Используем константы из ТЗ
    x = math.sin(seed * 12.9898) * 43758.5453
    fractional_part = x - math.floor(x)
    result = int(fractional_part * modulo)
    return result


def trigger_trap(game_state):
    print("Ловушка активирована! Пол стал дрожать...")

    inventory = game_state.get("player_inventory", [])
    if inventory:
        index = pseudo_random(seed=len(inventory), modulo=len(inventory))
        # защита от некорректного индекса
        if 0 <= index < len(inventory):
            lost_item = inventory.pop(index)
            print(f"Вы потеряли предмет: {lost_item}")
        else:
            print("Ошибка при выборе предмета для потери.")
    else:
        danger = pseudo_random(seed=game_state.get("steps_taken", 0), modulo=10)
        if danger < 3:
            print("Вы попали в ловушку и игра окончена!")
            game_state["game_over"] = True
        else:
            print("Вы едва увернулись от ловушки, но уцелели.")


def random_event(game_state):
    """Случайные события при перемещении"""
    steps = game_state.get("steps_taken", 0)

    if pseudo_random(seed=steps, modulo=EVENT_PROBABILITY) != 0:
        return

    event_type = pseudo_random(seed=steps, modulo=3)
    current_room = game_state["current_room"]

    if event_type == 0:  # Находка
        print("Вы нашли на полу монетку!")
        ROOMS[current_room]["items"].append("coin")

    elif event_type == 1:  # Испуг
        print("Вы услышали странный шорох...")
        if "sword" in game_state.get("player_inventory", []):
            print("Но вы отпугнули существо своим мечом!")

    elif event_type == 2:  # Ловушка
        if current_room == "trap_room" and "torch" not in game_state.get(
            "player_inventory", []
        ):
            print("Вы заметили опасность впереди!")
            trigger_trap(game_state)

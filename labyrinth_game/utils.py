# utils.py
from labyrinth_game.constants import ROOMS
import math

# именованная константа вместо "магического числа"
EVENT_PROBABILITY = 10  # 1 из 10 шансов для события

def describe_current_room(game_state):
    current_room = game_state['current_room']
    room_data = ROOMS[current_room]  # Достаем данные этой комнаты

    print(f"== {current_room.upper()} ==")
    print(room_data['description'])

    if room_data.get('items'):
        items_list = ', '.join(room_data['items'])
        print(f"Заметные предметы: {items_list}")

    exit_directions = ', '.join(room_data.get('exits', {}).keys())
    print(f"Выходы: {exit_directions}")

    if room_data.get('puzzle') is not None:
        print("Кажется, здесь есть загадка (используйте команду solve).")


def solve_puzzle(game_state):
    # локальный импорт get_input, чтобы избежать круговых импортов
    from player_actions import get_input

    current_room = game_state['current_room']
    room_data = ROOMS[current_room]

    if room_data.get('puzzle') is None:
        print("Загадок здесь нет.")
        return

    question, correct_answer = room_data['puzzle']
    print(question)

    user_answer = get_input("Ваш ответ: ").strip().lower()

    # Поддержка альтернативных ответов (например, "10" и "десять")
    alternatives = [str(correct_answer).lower()]
    if str(correct_answer).lower() == '10':
        alternatives.append('десять')
    elif str(correct_answer).lower() == 'десять':
        alternatives.append('10')

    if user_answer in alternatives:
        print("Поздравляем! Ответ верный.")
        room_data['puzzle'] = None  # убираем загадку

        reward = room_data.get('reward', room_data.get('items', []))

        if reward:
            game_state.setdefault('player_inventory', []).extend(reward)
            print(f"Вы заработали: {', '.join(reward)}")
            if 'items' in room_data:
                room_data['items'] = []
        else:
            print("Загадка решена, но награды нет.")
    else:
        print("Неверно. Попробуйте снова.")
        if current_room == 'trap_room':
            trigger_trap(game_state)


def attempt_open_treasure(game_state):
    # локальный импорт get_input, чтобы избежать круговых импортов
    from player_actions import get_input

    current_room = game_state['current_room']
    room_data = ROOMS[current_room]

    # проверяем ключ 'rusty_key' как основной ключ сокровищницы
    if 'rusty_key' in game_state.get('player_inventory', []):
        print("Вы применяете ключ, и замок щёлкает. Сундук открыт!")
        try:
            game_state['player_inventory'].remove('rusty_key')
        except ValueError:
            pass
        if 'treasure_chest' in room_data.get('items', []):
            room_data['items'].remove('treasure_chest')
        print("В сундуке сокровище! Вы победили!")
        game_state['game_over'] = True
        return

    answer = get_input("У вас нет ключа, чтобы открыть сундук. Возможно, вам известен код? (да/нет) ").lower()
    if answer == 'да':
        game_key = get_input("Отлично! Введи свой код: ")
        if game_key.lower() == room_data.get('puzzle', ['', ''])[1].lower():
            if 'treasure_chest' in room_data.get('items', []):
                room_data['items'].remove('treasure_chest')
            print("Вы применяете пароль, и замок щёлкает. Сундук открыт!")
            print("В сундуке сокровище! Вы победили!")
            game_state['game_over'] = True
        else:
            print("Некорректный код. Попробуйте снова.")
    elif answer == 'нет':
        print("Вы отступаете от сундука.")
    else:
        print("Некорректный ответ. Попробуйте снова.")


def show_help(COMMANDS):
    print("\nДоступные команды:")
    for command, description in COMMANDS.items():
        print(f"  {command.ljust(16)} - {description}")


def pseudo_random(seed, modulo):
    x = math.sin(seed * 12.1233) * 45731.5428
    fractional_part = x - math.floor(x)
    result = int(fractional_part * modulo)
    return result


def trigger_trap(game_state):
    print("Ловушка активирована! Пол стал дрожать...")

    inventory = game_state.get('player_inventory', [])
    if inventory:
        index = pseudo_random(seed=len(inventory), modulo=len(inventory))
        # защита от некорректного индекса
        if 0 <= index < len(inventory):
            lost_item = inventory.pop(index)
            print(f"Вы потеряли предмет: {lost_item}")
        else:
            print("Ошибка при выборе предмета для потери.")
    else:
        danger = pseudo_random(seed=game_state.get('steps_taken', 0), modulo=10)
        if danger < 3:
            print("Вы попали в ловушку и игра окончена!")
            game_state['game_over'] = True
        else:
            print("Вы едва увернулись от ловушки, но уцелели.")


def random_event(game_state):
    # используем унифицированный ключ 'steps_taken'
    steps = game_state.get('steps_taken', 0)

    # Сначала решаем, произойдет ли событие
    if pseudo_random(seed=steps, modulo=EVENT_PROBABILITY) != 0:
        return  # событие не произошло

    event_type = pseudo_random(seed=steps, modulo=3)

    if event_type == 0:  # Находка
        print("Вы нашли на полу монетку!")
        current_room_items = game_state.get('current_room_items', [])
        current_room_items.append('coin')
        game_state['current_room_items'] = current_room_items

    elif event_type == 1:  # Испуг
        print("Вы услышали странный шорох...")
        inventory = game_state.get('player_inventory', [])
        if 'sword' in inventory:
            print("Но вы отпугнули существо своим мечом!")

    elif event_type == 2:  # Ловушка
        if game_state.get('current_room') == 'trap_room':
            inventory = game_state.get('player_inventory', [])
            if 'torch' not in inventory:
                print("Вы заметили опасность впереди!")
                trigger_trap(game_state)

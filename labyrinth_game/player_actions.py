# player_actions.py
from labyrinth_game.constants import ROOMS


def show_inventory(game_state):
    if game_state.get('player_inventory'):
        current_inventory = game_state['player_inventory']
        print(', '.join(current_inventory))
    else:
        print('Инвентарь в руках отсутствует!')


def get_input(prompt="> "):
    try:
        user_input = input(prompt)
        return user_input
    except (KeyboardInterrupt, EOFError):
        print("\nВыход из игры.")
        return "quit"


def move_player(game_state, direction):
    # локальный импорт, чтобы избежать круговых импортов при загрузке модулей
    from labyrinth_game.utils import random_event


    current_room = game_state['current_room']
    room_data = ROOMS[current_room]
    actionable_exits = room_data['exits']

    # Проверяем, можно ли пойти в выбранном направлении
    if direction in actionable_exits:
        next_room = actionable_exits[direction]

        # Проверка: если следующая комната — treasure_room
        if next_room == 'treasure_room':
            # Проверяем наличие ключа в player_inventory
            if 'rusty_key' in game_state.get('player_inventory', []):
                print("Вы используете найденный ключ, чтобы открыть путь в комнату сокровищ.")
                game_state['current_room'] = next_room
                game_state['steps_taken'] += 1
                new_room_data = ROOMS[next_room]
                print(new_room_data['description'])
                random_event(game_state)
            else:
                print("Дверь заперта. Нужен ключ, чтобы пройти дальше.")
            return  # Выходим из функции, чтобы не выполнять лишние действия

        # Обычное перемещение
        game_state['current_room'] = next_room
        game_state['steps_taken'] += 1
        new_room_data = ROOMS[next_room]
        print(new_room_data['description'])
        random_event(game_state)

    else:
        print('Нельзя пойти в этом направлении.')


def take_item(game_state, item_name):
    current_room = game_state['current_room']
    room_data = ROOMS[current_room]
    actionable_items = room_data.get('items', [])

    if item_name in actionable_items:
        game_state.setdefault('player_inventory', []).append(item_name)
        room_data['items'].remove(item_name)
        print(f"Вы подняли: {item_name}")

    else:
        print("Такого предмета здесь нет.")


def use_item(game_state, item_name):
    # Проверяем, есть ли предмет у игрока
    if item_name not in game_state.get('player_inventory', []):
        print("У вас нет такого предмета.")
        return

    # Определяем действие в зависимости от предмета
    match item_name:
        case 'torch':
            print("Вы поднимаете факел — стало светлее вокруг.")
        case 'sword':
            print("Вы держите меч в руках — чувствуете уверенность и силу.")
        case 'bronze_box':
            if 'rusty_key' not in game_state.get('player_inventory', []):
                print("Вы открыли бронзовую шкатулку и нашли ржавый ключ!")
                game_state['player_inventory'].append('rusty_key')
            else:
                print("В шкатулке пусто.")
        case _:
            print(f"Вы не знаете, как использовать {item_name}.")

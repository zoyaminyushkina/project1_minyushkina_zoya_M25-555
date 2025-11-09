# main.py

from labyrinth_game.constants import COMMANDS
from labyrinth_game.utils import describe_current_room, solve_puzzle, attempt_open_treasure, show_help
from labyrinth_game.player_actions import show_inventory, get_input, move_player, take_item, use_item

def process_command(game_state, command: str):
    """
    Обрабатывает команду игрока и вызывает соответствующую функцию.
    """
    parts = command.strip().split()
    if not parts:
        print("Пустая команда.")
        return

    action = parts[0].lower()
    arg = parts[1].lower() if len(parts) > 1 else None

    match action:
        case "look":
            describe_current_room(game_state)

        case "go":
            if arg:
                move_player(game_state, arg)
            else:
                print("Куда вы хотите пойти?")

        case "take":
            if arg:
                take_item(game_state, arg)
            else:
                print("Что вы хотите взять?")

        case "use":
            if arg:
                use_item(game_state, arg)
            else:
                print("Что вы хотите использовать?")

        case "inventory":
            show_inventory(game_state)

        case "solve":
            current_room = game_state['current_room']
            if current_room == 'treasure_room':
                attempt_open_treasure(game_state)
            else:
                solve_puzzle(game_state)

        case "quit" | "exit":
            game_state['game_over'] = True
            print("Вы вышли из игры.")

        case "help":
            show_help(COMMANDS)

        case _:
            print("Неизвестная команда. Напишите 'help' для списка доступных команд.")


def main():
    print("Добро пожаловать в Лабиринт сокровищ!")

    # Состояние игры
    game_state = {
        'player_inventory': [],
        'current_room': 'entrance',
        'game_over': False,
        'steps_taken': 0
    }

    describe_current_room(game_state)

    while not game_state['game_over']:
        command = get_input("Введите команду: ")
        process_command(game_state, command)


if __name__ == "__main__":
    main()

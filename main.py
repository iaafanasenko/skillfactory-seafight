from random import randint


class BoardOutException(Exception):
    pass


class DoubleShot(Exception):
    pass


class ShipIsNotPossible(Exception):
    pass


class Dot:
    def __init__(self, x: int = 0, y: int = 0):
        Dot.verify_coord(x)
        Dot.verify_coord(y)
        self._x = x
        self._y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    @classmethod
    def verify_coord(cls, x):
        if type(x) != int or x < 0 or x > 5:
            raise BoardOutException(f"\033[31mКоординаты должны быть целыми числами в интервале от 1 до 6.\033[0m")

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x):
        Dot.verify_coord(x)
        self._x = x

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        Dot.verify_coord(y)
        self._y = y

    @property
    def coord(self):
        return self.x, self.y

    def set_coord(self, x, y):
        Dot.verify_coord(x)
        Dot.verify_coord(y)
        self._x = x
        self._y = y


class Ship:
    def __init__(self, length: int, x: int, y: int, direction: str):
        Ship.verify_length(length)
        Ship.verify_coord(x)
        Ship.verify_coord(y)
        Ship.verify_direction(direction)
        self._length = length
        self._x = x
        self._y = y
        self._direction = direction
        self.lives = length

    @classmethod
    def verify_length(cls, length):
        if length not in [1, 2, 3]:
            raise TypeError(f"\033[31mДлина корабля должна быть более 1, но менее 3.\033[0m")

    @classmethod
    def verify_coord(cls, x):
        if type(x) != int or x < 0 or x > 5:
            raise TypeError(f"\033[31mКоординаты должны быть целыми числами в интервале от 1 до 6.\033[0m")

    @classmethod
    def verify_direction(cls, direction):
        if direction != 'h' and direction != 'v':
            raise TypeError(f"\033[31mКорабли должны располагаться по горизонтали или по вертикали.\033[0m")

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, length):
        Ship.verify_length(length)
        self._length = length

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x):
        Ship.verify_coord(x)
        self._x = x

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        Ship.verify_coord(y)
        self._y = y

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, direction):
        Ship.verify_direction(direction)
        self._direction = direction

    @property
    def dots(self) -> list[tuple]:
        return [(self.x, self.y + _) for _ in range(self.length)] if self.direction == 'h' \
            else [(self.x + _, self.y) for _ in range(self.length)]

    @property
    def contour(self) -> list[tuple]:
        if self._direction == 'h':
            cont = [(i, self.y + j) for i in (self.x - 1, self.x + 1) if 0 <= i <= 5
                    for j in range(-1, self.length + 1) if 0 <= self.y + j <= 5] \
                 + [(self.x, j) for j in (self.y - 1, self.y + self.length) if 0 <= j <= 5]
        else:
            cont = [(self.x + i, j) for i in range(-1, self.length + 1) if 0 <= self.x + i <= 5
                    for j in (self.y - 1, self.y + 1) if 0 <= j <= 5] \
                 + [(i, self.y) for i in (self.x - 1, self.x + self.length) if 0 <= i <= 5]
        return cont


class Board:
    def __init__(self, player: str, game_board: list[list[tuple]] = None,
                 ships: list[Ship] = None, ships_alive: int = 0):
        self.player = player
        self.game_board = game_board if game_board else [[' ' for _ in range(6)] for _ in range(6)]
        self.hid = True if self.player == 'AI' else False
        self.ships = ships if ships else []
        self.ships_alive = ships_alive
        self.board_print = [[' ' if self.hid and self.game_board[i][j] == chr(9632)
                            else self.game_board[i][j] for j in range(6)] for i in range(6)]
        self.shoots = []

    def print_board(self) -> None:
        print(f" {self.player}{' '*2}" + "".join(f"{i + 1}{' ' * 3}" for i in range(6)))
        print(f"{' '*3}{'_'*25}")
        for i in range(6):
            print(f" {i + 1} | " + "".join(f"{self.board_print[i][j]} | " for j in range(6)))
            print(f"{' ' * 3}{'_' * 25}")
        print(f"\nОсталось кораблей: {self.ships_alive}\n")

    def add_ship(self, ship: Ship) -> None:
        self.ships.append(ship)
        self.ships_alive += 1
        for i in range(len(ship.dots)):
            self.game_board[ship.dots[i][0]][ship.dots[i][1]] = chr(9632)
        if not self.hid:
            for i in range(len(ship.dots)):
                self.board_print[ship.dots[i][0]][ship.dots[i][1]] = chr(9632)


class Player:
    def __init__(self, board: Board):
        self.board = board

    def ask(self):
        pass

    def move(self, i, j, player, turn) -> int:
        self.board.shoots.append((i, j))
        if self.board.game_board[i][j] == ' ':
            self.board.game_board[i][j] = '*'
            self.board.board_print[i][j] = '*'
            print(f"\033[31mПромах.\033[0m\n")
        elif self.board.game_board[i][j] == chr(9632):
            self.board.game_board[i][j] = 'X'
            self.board.board_print[i][j] = 'X'
            for ship in self.board.ships:
                if (i, j) in ship.dots:
                    turn = Game.turns(turn)
                    ship.lives -= 1
                    if ship.lives == 0:
                        self.board.ships_alive -= 1
                        for (x, y) in ship.contour:
                            if self.board.game_board[x][y] == ' ':
                                self.board.game_board[x][y] = 'o'
                            if self.board.board_print[x][y] == ' ':
                                self.board.board_print[x][y] = 'o'
                            if (x, y) not in self.board.shoots:
                                self.board.shoots.append((x, y))
                        print(f"\033[33mКорабль потоплен.\033[0m\n")
                    else:
                        print(f"\033[33mКорабль поражен.\033[0m\n")
        self.board.print_board()
        if self.board.ships_alive == 0:
            if player == 'AI':
                print(f"\033[31mВсе Ваши корабли потоплены. Вы проиграли!\033[0m\n")
            else:
                print(f"\033[33mВы победили!\033[0m\n")

            return -1

        _ = input("Переход хода. Нажмите 'Enter' для продолжения.\n")

        return turn


class User(Player):
    def __init__(self, board: Board):
        Player.__init__(self, board)

    def ask(self) -> tuple[int, int]:
        self.board.print_board()
        while True:
            try:
                x = int(input(f"\033[32mВведите координату по х: \033[0m")) - 1
                y = int(input(f"\033[32mВведите координату по y: \033[0m")) - 1
                dot = Dot(x, y)
                if (dot.x, dot.y) in self.board.shoots:
                    raise DoubleShot
                print()
                return dot.x, dot.y
            except ValueError:
                print(f"\033[31mКоординаты должны быть целыми числами в интервале от 1 до 6.\033[0m\n")
            except BoardOutException:
                print(f"\033[31mКоординаты должны быть целыми числами в интервале от 1 до 6.\033[0m\n")
            except DoubleShot:
                print(f"\033[31mИзвестно, что кораблей в этих координатах нет или корабль уже был потоплен. Укажите другие координаты.\033[0m\n")


class AI(Player):
    def __init__(self, board: Board):
        Player.__init__(self, board)

    def ask(self) -> tuple[int, int]:
        while True:
            try:
                dot = Dot(randint(0, 5), randint(0, 5))
                if (dot.x, dot.y) in self.board.shoots:
                    raise DoubleShot
                return dot.x, dot.y
            except DoubleShot:
                pass


class Game:
    def __init__(self):
        self.player = [User(Board('AI')), AI(Board('Вы'))]

    def start(self) -> None:
        for p in [0, 1]:
            Game.random_board(self.player[p].board)

        Game.greet()

        self.player[1].board.print_board()

        self.loop()
    @staticmethod
    def turns(i: int) -> int:
        return 1 if i == 0 else 0

    def loop(self) -> None:
        turn = 1
        while turn != -1:
            turn = Game.turns(turn)
            x, y = self.player[turn].ask()
            turn = self.player[turn].move(x, y, self.player[Game.turns(turn)].board.player, turn)

    @staticmethod
    def greet() -> str:
        print("\n" "\033[34mИгра 'Морской бой'\033[0m\n")

    @staticmethod
    def random_board(b: Board) -> None:
        bd = {(i, j) for i in range(6) for j in range(6)}
        while True:
            full = set()
            length = 3
            while length >= 1:
                i = 1
                while i <= 4 - length:
                    fault_count = 0
                    while True:
                        try:
                            sh = Ship(length, randint(0, 5), randint(0, 5),
                                      'h' if randint(0, 1) else 'v')
                            if set(sh.dots).difference(bd) != set() \
                                    or set(sh.dots).intersection(full) != set():
                                raise ShipIsNotPossible
                            full = (full.union(set(sh.dots))).union(set(sh.contour))
                            b.add_ship(sh)
                            i += 1
                            break
                        except ShipIsNotPossible:
                            fault_count += 1
                            if fault_count == 100:
                                i, length = 5, 0
                                break
                length -= 1
            break


if __name__ == '__main__':
    game = Game()
    game.start()
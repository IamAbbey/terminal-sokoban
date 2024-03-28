from collections import deque
import sys
import time
from typing import Deque
import blessed
from src.model import Stage, get_stages
import enum

import src.character as character


def echo(text):
    # print without newline and flush
    print(text, end="", flush=True)


class Direction(enum.StrEnum):
    KEY_LEFT = "KEY_LEFT"
    KEY_RIGHT = "KEY_RIGHT"
    KEY_UP = "KEY_UP"
    KEY_DOWN = "KEY_DOWN"


class MovementHistory:
    def __init__(self):
        self.stack: Deque[Direction] = deque([])

    def push(self, direction: Direction):
        self.stack.append(direction)

    def pop(self):
        return self.stack.pop()

    def is_empty(self):
        return len(self.stack) == 0

    def peek(self) -> Direction:
        return self.stack[-1]


class Sokoban:
    def __init__(
        self, stages: list[Stage], term: blessed.Terminal, start_index: int = 0
    ):
        # the Terminal Instance
        self.term: blessed.Terminal = term

        # The different sokoban stages
        self.stages: list[Stage] = stages

        # The current stage, increases as player completes each stage
        self.stage_count: int = start_index
        self.stage: Stage = self.stages[self.stage_count]

        # The current player position
        self.player_position_index: int = self.stage.player_start_index

        # The current box positions
        self.box_position_index_list: list[int] = sorted(self.stage.box_start_position)

        self.width: int = self.stage.dimension[0]
        self.height: int = self.stage.dimension[1]

        self.movement_history: MovementHistory = MovementHistory()

    def draw_board(self, won=False):
        echo(self.term.home + self.term.on_black + self.term.clear_eol)

        echo(self.term.on_black + self.term.webgreen(" SOKOBAN ♥️ "))
        echo(self.term.move_xy(0, 1))
        echo(
            self.term.move_xy(0, 2)
            + self.term.on_black
            + self.term.webgreen(f" STAGE {self.stage_count + 1} of {len(self.stages)}")
        )
        echo(
            self.term.move_xy(0, 3)
            + self.term.on_black
            + self.term.webgreen(f" NAME: {self.stage.name.upper()}")
        )
        echo(self.term.move_down)

        for index in range(self.width * self.height):
            display = self.term.on_black("  ")

            if index % self.width == 0:
                echo("\r\n" + self.term.on_black("  "))

            # The order of the below condition is needed
            # to ensure that box position and player position are dynamic
            if index in self.stage.static_index_list:
                display = character.green_squareblock if won else character.squareblock

            if index in self.stage.box_storage_position_list:
                display = character.box_spot

            if index == self.player_position_index:
                display = character.player

            if index in self.box_position_index_list:
                display = character.box

            if (
                index in self.box_position_index_list
                and index in self.stage.box_storage_position_list
            ):
                display = character.green_squareblock

            echo(self.term.on_black + display)

        echo("\r\n")
        echo("\r\n")
        echo(
            self.term.on_black
            + self.term.webgreen(
                " - Use the arrow keys to move the player around. \r\n - (r) Reverse move \r\n - (z) Restart current stage \r\n - (q) Quit"
            )
        )

    def next_stage(self):
        """Proceed to next stage"""
        self.set_state(self.stage_count + 1)

    def set_state(self, stage_count: int):
        """reinitialize neccessary states"""
        self.stage_count = stage_count
        if self.stage_count < len(self.stages):
            self.stage = self.stages[self.stage_count]

            self.player_position_index = self.stage.player_start_index
            self.box_position_index_list = sorted(self.stage.box_start_position)
            self.width = self.stage.dimension[0]
            self.height = self.stage.dimension[1]

            self.draw_board()

    def is_valid_move(self, position: int, direction: Direction):
        """
        Checks if the movement to position X is valid (usually the player's or box's new position),
        A movement is not valid if there is a wall in that position already
        A movement is not valid if there is a box in that position followed by another box or wall
        """
        if position in self.stage.static_index_list:
            return False
        elif position in self.box_position_index_list:
            if (
                self.get_next_positon(position, direction)
                in self.stage.static_index_list + self.box_position_index_list
            ):
                return False

        return True

    def get_next_positon(self, position: int, direction: Direction):
        match direction:
            case Direction.KEY_LEFT:
                return position - 1
            case Direction.KEY_RIGHT:
                return position + 1
            case Direction.KEY_UP:
                return position - self.width
            case Direction.KEY_DOWN:
                return position + self.width
            case _:
                raise ValueError("Invalid direction")

    def get_reverse_positon(self, position: int, direction: Direction):
        match direction:
            case Direction.KEY_LEFT:
                return position + 1
            case Direction.KEY_RIGHT:
                return position - 1
            case Direction.KEY_UP:
                return position + self.width
            case Direction.KEY_DOWN:
                return position - self.width
            case _:
                raise ValueError("Invalid direction")

    def make_move(self, direction: Direction):
        # Get the next position in specified direction
        new_position = self.get_next_positon(self.player_position_index, direction)

        # Decide if the movement in that direction is valid
        if self.is_valid_move(new_position, direction):
            # if there is a box in the new position the player is suppose to be
            if new_position in self.box_position_index_list:
                brick_postion_index = self.box_position_index_list.index(new_position)

                # Move the box forward
                self.box_position_index_list[brick_postion_index] = (
                    self.get_next_positon(new_position, direction)
                )

                # Move the player to the box previous position
                self.player_position_index = new_position

            else:
                # if there is no box in the new position the player is suppose to be
                # Move the player to the new position
                self.player_position_index = new_position

            # Re-draw board
            self.draw_board()

            # Record movement direction
            self.movement_history.push(direction)

    def reverse_move(self):
        # Get last recorded movement direction
        direction = self.movement_history.peek()

        # Get player's reverse position in specified direction
        reverse_position = self.get_reverse_positon(
            self.player_position_index, direction
        )

        if (
            # if there is currently a box in front of player
            box_position := self.get_next_positon(self.player_position_index, direction)
        ) in self.box_position_index_list:
            box_postion_index = self.box_position_index_list.index(box_position)

            # Move box backward to the player current position
            self.box_position_index_list[box_postion_index] = (
                # self.get_reverse_positon(box_position, direction)
                self.player_position_index
            )

            # Move player backward
            self.player_position_index = reverse_position
        else:
            # Move player backward
            self.player_position_index = reverse_position

        self.draw_board()
        self.movement_history.pop()

    def start(self):
        # Move cursor to (0,0), set background to gray10 and clear screen
        echo(self.term.home + self.term.on_black + self.term.clear)

        # Draw board
        self.draw_board()

        with self.term.raw(), self.term.keypad(), self.term.location(), self.term.hidden_cursor():
            # get key input
            while (keypress := self.term.inkey()) != "q":
                if keypress == "r":
                    # Only make a reversement movement if movement hisory is not empty
                    if not self.movement_history.is_empty():
                        self.reverse_move()

                if keypress == "z":
                    # hard reset stage
                    self.set_state(self.stage_count)

                # else if key pressed is each of the arrow keys, make a movement
                elif keypress.name in Direction._member_names_:
                    self.make_move(direction=keypress.name)

                # Player is said to complete(WON) a stage if the box positions matches the expected storage position
                if sorted(self.box_position_index_list) == sorted(
                    self.stage.box_storage_position_list
                ):
                    self.draw_board(won=True)
                    time.sleep(1)
                    echo(self.term.home + self.term.on_black + self.term.clear)
                    self.next_stage()


def start():
    try:
        start_index = abs(int(sys.argv[1]) - 1) if len(sys.argv) >= 2 else 0
    except ValueError:
        start_index = 0

    term = blessed.Terminal()
    sokoban = Sokoban(stages=get_stages(), start_index=start_index, term=term)
    sokoban.start()

    echo(term.home + term.clear)


if __name__ == "__main__":
    start()

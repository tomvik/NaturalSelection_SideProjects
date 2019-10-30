import pygame
import random
from typing import List, Tuple

import Rectangle
from Character import Character
from Stage import Stage
from Food_Manager import FoodManager


class CharacterManager:
    def __init__(self, character_size: int, character_color: List[int]):
        self.__characters = list()
        self.__finished_characters = list()
        self.__character_size = character_size
        self.__character_color = character_color
        self.__initial_amount = 0

    # Spans randomly throughout the stage the amount of characters
    # selected with random values of sensing and speed, within the range.
    # Replaces the list of characters.
    def initialize_character_list(self, amount: int,
                                  sensing_range: Tuple[int, int],
                                  speed_range: Tuple[int, int],
                                  stage: Stage):
        characters = list()
        x_min, y_min, x_max, y_max = stage.get_stage_limits()
        x_max -= self.__character_size
        y_max -= self.__character_size

        while len(characters) < amount:
            current_x = random.randint(x_min, x_max)
            current_y = random.randint(y_min, y_max)
            current_limits = (current_x, current_y,
                              current_x + self.__character_size,
                              current_y + self.__character_size)
            current_speed = random.randint(speed_range[0], speed_range[1])
            current_sensing = random.randint(sensing_range[0],
                                             sensing_range[1])

            blocks = False
            for character in characters:
                if character.area_collide(current_limits):
                    blocks = True
                    break

            if blocks is False:
                characters.append(Character(current_x,
                                            current_y,
                                            self.__character_size,
                                            self.__character_size,
                                            self.__character_color,
                                            stage.get_stage_color(),
                                            stage.get_win(),
                                            len(characters) + 1,
                                            current_speed,
                                            current_sensing))

        self.__characters = characters
        self.__initial_amount = amount

    # Returns the list of characters.
    def get_list(self) -> List[Character]:
        return self.__characters

    # Draws all the characters.
    def draw(self):
        for character in self.__characters:
            character.draw()

    # Deletes the indexed character.
    def delete_index(self, index: int):
        del self.__characters[index]

    # Returns the number of characters that haven't finished.
    def characters_left(self) -> int:
        return len(self.__characters)

    # Moves all the characters.
    # They may also eat some food.
    def move_characters(self, food_manager: FoodManager, stage: Stage,
                        only_walls: bool):
        characters_left = self.characters_left()
        i = 0
        while i < characters_left:
            movement = self.__get_direction(i, stage, food_manager)
            if self.__characters[i].finished():
                self.__move_home(i)
                i -= 1
                characters_left -= 1
            else:
                self.__move_character(i, movement,
                                      self.__get_blockings(i,
                                                           stage.get_walls(),
                                                           only_walls),
                                      food_manager)
            i += 1

    # Moves the character home, and transfers it to the finished list.
    def __move_home(self, index: int):
        self.__finished_characters.append(self.__characters.pop(index))
        self.__finished_characters[-1].move_home()

    # Returns the blockings for the current index.
    def __get_blockings(self, current: int, walls: List[Rectangle.Rectangle],
                        only_walls: bool) -> List[Rectangle.Rectangle]:
        if only_walls:
            return walls
        left_hand = characters[:current]
        right_hand = characters[current+1:]
        return left_hand + right_hand + walls

    # Returns the direction to the closest wall of the indexed character.
    # If it arrives home, it does nothing and sets the variable on the
    # character.
    def __goto_closest_wall(self, index: int, stage: Stage) -> Tuple[int, int]:
        wall, movement = stage.closest_wall_to(self.__characters[index])
        if self.__characters[index].would_collide(wall, movement):
            self.__characters[index].arrived_home()
            return (0, 0)
        return movement

    # Returns the direction to the closest food of the indexed character.
    # If there's no food left, it returns a random movement.
    def __goto_closest_food(self, index: int,
                            food_manager: FoodManager) -> Tuple[int, int]:
        if food_manager.food_left() is 0:
            return self.__characters[index].get_random_move()
        return food_manager.direction_to_closest_food(self.__characters[index])

    # Returns the direction that the character shall follow.
    def __get_direction(self, index: int, stage: Stage,
                        food_manager: FoodManager) -> Tuple[int, int]:
        if (self.__characters[index].is_hungry() is False):
            return self.__goto_closest_wall(index, stage)
        return self.__goto_closest_food(index, food_manager)

    # Moves the character a certain dx and dy times its own speed, plus
    # checks on the foods and eats if the character is hungry.
    def __move_character(self, index: int, dir: Tuple[int, int],
                         blockings: List[Rectangle.Rectangle],
                         food_manager: FoodManager):
        self.__characters[index].move(dir[0], dir[1], blockings)
        food_manager.maybe_is_eating(self.__characters[index])
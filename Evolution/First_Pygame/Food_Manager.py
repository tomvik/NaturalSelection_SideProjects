import pygame
import random
from typing import List, Tuple

import Rectangle
from Food import Food
import Stage
import Distances
from Character import Character
from Common_Types import *


class FoodManager:
    def __init__(self, food_size: Size, food_color: Color,
                 update_step: int, update_day: int):
        self.__foods = list()
        self.__food_size = food_size
        self.__food_color = food_color
        self.__initial_amount = 0
        self.__target_amount = 0
        self.__update_step = update_step
        self.__update_days = update_day
        self.__days_to_update = self.__update_days
        self.__range_of_values = (0, 0)
        self.__stage_limits = Limits(0, 0, 0, 0)
        self.__stage_color = Color(0, 0, 0)

    # Spans randomly throughout the stage the amount of food selected with
    # random values of nutrition within the range.
    # Replaces the list of foods.
    def initialize(self, amount: int, target_amount: int,
                   range_of_values: Tuple[int, int],
                   stage: Stage.Stage,
                   blockings: List[Rectangle.Rectangle]):
        foods = list()
        width, height = blockings[0].get_size()
        limits = stage.get_stage_limits()
        self.__stage_limits = Limits(limits.x_min + width,
                                     limits.y_min + height,
                                     limits.x_max - width,
                                     limits.y_max - height)
        self.__stage_color = stage.get_stage_color()
        self.__range_of_values = range_of_values

        self.__foods = self.__span_random_food(amount, blockings)
        self.__initial_amount = amount
        self.__target_amount = target_amount

    # Returns the list of food.
    def get_list(self) -> List[Food]:
        return self.__foods

    # Returns how much food is left.
    def food_left(self) -> int:
        return len(self.__foods)

    # Sets the target food and resets the days to update variable.
    def set_target_food(self, target_food: int):
        self.__days_to_update = self.__update_days
        self.__target_amount = target_food

    # Returns the direction to the closes food from the character received.
    # If the food is within distance of the speed, it will also move
    # towards it. And it returns True if in fact there's a food nearby.
    def direction_to_closest_food(self,
                                  character: Character) -> \
            Tuple[Direction, bool]:
        food = Distances.closest_of_all_L2(character, self.__foods,
                                           character.get_sensing())
        d, within_r = Distances.sensing_direction(character, food,
                                                  character.get_sensing())
        if within_r:
            d2, within_r = Distances.sensing_direction(character, food,
                                                       character.get_speed())
            if within_r:
                character.draw_background()
                center = food.get_center()
                character.move(center.x, center.y, [], True)
                return Direction(0, 0), True
            else:
                return d, True
        else:
            return Direction(0, 0), False

    # Delete the specific food.
    def delete_index(self, index: int):
        del self.__foods[index]

    # Draws all the foods.
    def draw(self):
        for food in self.__foods:
            food.draw()

    # Feeds the character that it receives and returns true if it has been
    # completely fed.
    def maybe_is_eating(self, character: Character) -> bool:
        c = 0
        character_was_hungry = character.is_hungry()
        indexes = Distances.smart_collide(character, self.__foods)
        for index in indexes:
            if character.is_hungry() is False:
                break
            character.feed(self.__foods[index - c].get_nutritional_value())
            del self.__foods[index - c]
            c += 1
        return character_was_hungry != character.is_hungry()

    # Spans the initial amount of food throughout the already defined stage.
    def reset_foods(self, blockings: List[Rectangle.Rectangle]):
        self.__days_to_update -= 1
        if self.__days_to_update is 0:
            if self.__initial_amount > self.__target_amount:
                self.__initial_amount -= self.__update_step
                self.__initial_amount = max(self.__target_amount,
                                            self.__initial_amount)
            self.__days_to_update = self.__update_days
        self.__foods = self.__span_random_food(self.__initial_amount,
                                               blockings)

    # Sorts the food list according to its x coordinate.
    def xsort(self):
        self.__foods.sort(key=lambda x: x._rectangle.left)

    # Spans a random amount of food throughout the specified stage.
    def __span_random_food(self, amount: int,
                           blockings: List[Rectangle.Rectangle]) -> List[Food]:
        foods = list()
        while len(foods) < amount:
            current_value = random.randint(self.__range_of_values[0],
                                           self.__range_of_values[1])

            current_x, current_y = Rectangle.free_random_position(
                self.__stage_limits, self.__food_size, blockings + foods)

            rectangle = PointSize(current_x, current_y,
                                  self.__food_size.width,
                                  self.__food_size.height)
            foods.append(Food(len(foods)+1,
                              rectangle,
                              self.__food_color, self.__stage_color,
                              current_value))
        return foods

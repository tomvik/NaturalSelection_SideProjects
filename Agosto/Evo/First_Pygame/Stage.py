import pygame
from typing import List, Tuple

from Rectangle import Rectangle
from Clock import Clock
import TextBox
import Distances


class Stage:
    def __init__(self, size: Tuple[int, int],
                 stage_colors: Tuple[List[int], List[int]],
                 win: pygame.Surface, fps: int,
                 clock_font: Tuple[str, int], clock_font_color: List[int],
                 ttl: int, text_box_font: Tuple[str, int]):
        self.__characters_name = "Characters"
        self.__foods_name = "Foods"
        self.__ttl_name = "Ttl"
        self.__fps_name = "Fps"
        self.__days_name = "Days"

        self.__width = size[0]
        self.__height = size[1]
        self.__stage_color = stage_colors[0]
        self.__walls_color = stage_colors[1]
        self.__win = win
        self.__days = 0

        self.__window_width, self.__window_height = self.__win.get_size()
        self.__wall_width = (self.__window_width - self.__width) / 2
        self.__wall_height = (self.__window_height - self.__height) / 2

        self.__walls, self.__stage = self.__initialize_stage()
        self.__text_boxes = self.__initialize_text_boxes(text_box_font)

        clock_pos = (self.__width + self.__wall_width + 1,
                     self.__height + self.__wall_height)
        self.__clock = Clock(fps, clock_pos,
                             self.__stage_color, self.__walls_color,
                             clock_font, clock_font_color, self.__win, ttl)

    # Initializes the stage and returns its walls and stage.
    def __initialize_stage(self) -> Tuple[List[Rectangle], Rectangle]:
        wall_rects = (pygame.Rect(0, 0,
                                  self.__wall_width, self.__window_height),
                      pygame.Rect(0, 0,
                                  self.__window_width, self.__wall_height),
                      pygame.Rect(self.__wall_width+self.__width, 0,
                                  self.__wall_width, self.__window_height),
                      pygame.Rect(0, self.__wall_height+self.__height,
                                  self.__window_width, self.__wall_height))
        stage_rect = pygame.Rect(self.__wall_width, self.__wall_height,
                                 self.__width, self.__height)

        walls = list()
        for wall in wall_rects:
            walls.append(Rectangle(wall, self.__walls_color,
                                   self.__stage_color, self.__win))
        stage = Rectangle(stage_rect, self.__stage_color,
                          self.__walls_color, self.__win)
        return walls, stage

    # Initializes the text boxes. This part is partly hard_coded.
    def __initialize_text_boxes(self, font: Tuple[str, int]) -> \
            List[TextBox.TextBox]:
        text_boxes = list()

        colors = (self.__stage_color, self.__walls_color)
        position = (self.__width+(self.__wall_width)+10, self.__wall_height)
        separations = (5, 10)
        per_row = 2
        is_input = (False, True,
                    False, True,
                    False, True,
                    False, True,
                    False, False)
        data = (("", "# of Characters:"), (self.__characters_name, "50 "),
                ("", "# of Foods:"), (self.__foods_name, "50 "),
                ("", "Time of Round (s):"), (self.__ttl_name, "5  "),
                ("", "fps:"), (self.__fps_name, "40 "),
                ("", "days:"), (self.__days_name, "0  "))
        return TextBox.create_matrix(position, colors, separations, per_row,
                                     self.__win, is_input, data, font)

    # Returns the walls.
    def get_walls(self) -> List[Rectangle]:
        return self.__walls

    # Returns the stage.
    def get_stage(self) -> Rectangle:
        return self.__stage

    # Returns the stage color.
    def get_stage_color(self) -> List[int]:
        return self.__stage_color

    # Returns the wall color.
    def get_walls_color(self) -> List[int]:
        return self.__walls_color

    # Returns the window.
    def get_win(self) -> pygame.Surface:
        return self.__win

    # Returns the Stage limits as in: x_min, y_min, x_max, y_max
    def get_stage_limits(self) -> List[int]:
        return (self.__stage.get_limits())

    # Returns the amount of days that has passed.
    def get_days(self) -> int:
        return self.__days

    # Draws all the text boxes.
    def draw_boxes(self):
        for box in self.__text_boxes:
            box.draw()

    # Returns True if it's under its Time To Live, otherwise False.
    def update_clock(self):
        self.__clock.update_clock()
        self.__clock.draw()
        return self.__clock.still_valid()

    # Return the value of each text_box on a list.
    def get_text_values(self) -> List[int]:
        return_values = list()
        for text_box in self.__text_boxes:
            if text_box.is_input():
                return_values.append(text_box.get_value())
        return return_values

    # Returns the closest wall to the object and its direction towards it.
    def closest_wall_to(self,
                        a: Rectangle) -> Tuple[Rectangle, Tuple[int, int]]:
        selected_wall = Distances.closest_of_all_Linf(a, self.__walls)
        direction = Distances.cardinal_system_direction(a, selected_wall)
        return selected_wall, direction

    # Resets the clock back to 0.
    def reset_clock(self):
        self.__clock.reset()

    # Sets the new TTL.
    def set_ttl_seconds(self, ttl: int):
        self.__clock.set_ttl(ttl*1000)

    # Sets the new FPS.
    def set_fps(self, fps: int):
        self.__clock.set_fps(fps)

    # Handle the events for each text box.
    def handle_event(self, event: pygame.event):
        for text_box in self.__text_boxes:
            text_box.handle_event(event)
            text_box.draw()

    # Handles the in-game updates.
    def handle_in_game(self, characters: int, foods: int) -> bool:
        self.__text_boxes[self.__box_index(
            self.__characters_name)].write(str(characters))
        self.__text_boxes[self.__box_index(
            self.__foods_name)].write(str(foods))
        self.draw_boxes()
        return self.update_clock()

    # Handles the updates necessary for the new round.
    def new_round_stage(self, characters: int, foods: int):
        self.__days += 1
        self.reset_clock()
        self.__text_boxes[self.__box_index(
            self.__days_name)].write(str(self.__days))
        self.handle_in_game(characters, foods)

    # Returns the index of the box with the desired name.
    def __box_index(self, name: str) -> int:
        for i in range(len(self.__text_boxes)):
            if self.__text_boxes[i].get_name() == name:
                return i
        return -1

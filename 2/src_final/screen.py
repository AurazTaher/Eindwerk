#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
from waveshare_OLED import OLED_1in51
import config
from PIL import Image,ImageDraw,ImageFont
from modules.module import Module
from time import sleep

class Screen:
    def __init__(self, n_rows, n_columns):
        self.display = OLED_1in51.OLED_1in51()
        self.display.Init()
        self.display.clear()
        self.number_rows = n_rows
        self.number_columns = n_columns
        self.width = self.display.width
        self.height = self.display.height
        self.canvas = Image.new('1', (self.width, self.height), 'WHITE')
        self.modules = []
        self.terminate = False

    def add_module(self, module):
        self.modules.append(module)

    def debug_render(self):
        """
        function to debug the screen size with, it draws all the rows and columns onto the screen
        this way we can debug if each component is drawn onto their own grid slots
        """
        row_height = self.height / self.number_rows
        column_width = self.width / self.number_columns
        draw = ImageDraw.Draw(self.canvas)

        for i in range(self.number_rows + 1):
            start_x, end_x = 0, self.width
            y = i * row_height
            draw.line([(start_x, y), (end_x,y)], "BLACK")
        for i in range(self.number_columns + 1):
            start_y, end_y = 0, self.height
            x = i * column_width
            draw.line([(x,start_y),(x, end_y)], "BLACK")

        self.display.ShowImage(self.display.getbuffer(self.canvas))

          
    def __get_rect(self,row, col, end_row, end_col):
        """
        this function calculates the rectangle in which to draw a module
        :argument row: the row on which the module starts to render (0-index)
        :argument col: the column on which the module starts to render (0-index)
        :argument end_row: the row on which the module ends to render (0-index)
        :argument end_col: the column on which the module ends to render (0-index)

        :return tuple containing the (start_x, start_y, end_x, end_y) pixel coordinates
        """
        row_height = self.height / self.number_rows
        column_width = self.width / self.number_columns

        start_x, end_x = (col * column_width), (col * column_width) + (end_col - col) * column_width
        start_y, end_y = (row * row_height), (row*row_height) + (end_row - row) * row_height

        return (start_x, start_y, end_x, end_y)

    # ff test code
    def test(self, text):
        start_x, start_y, end_x, end_y = self.__get_rect(0,0,2,1)
        width = end_x - start_x
        height = end_y - start_y
        font = ImageFont.truetype(config.FONT_FILE, size=12)
        draw = ImageDraw.Draw(self.canvas)
        draw.text((start_x,height/2), text, font=font, fill=0)
        self.display.ShowImage(self.display.getbuffer(self.canvas))

    def run(self):
        """
        function that controls the draw loop of the screen, in this function each component will get drawn onto the screen
        """
        while (not self.terminate):
            # self.debug_render()
            for module in self.modules:
                module_row = module.row
                module_col = module.column
                module_end_row = module.end_row
                module_end_col = module.end_column
                start_x, start_y, end_x, end_y = self.__get_rect(module_row,module_col, module_end_row,module_end_col)
                module.draw(self.canvas, start_x, start_y, end_x, end_y)
            self.display.ShowImage(self.display.getbuffer(self.canvas))
            sleep(2)
            self.display.clear()
            self.canvas = Image.new('1', (self.width, self.height), 'WHITE')
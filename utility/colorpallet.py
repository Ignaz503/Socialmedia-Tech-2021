from enum import Enum

from colour import Color
from utility.color import mix
import random

class DefaultColorPallet(Enum):
  USER_COLOR = ("#45e9ce","#1fbfff")
  SUBREDDIT_COLOR = "#e94560"
  FONT_COLOR ="#fefefe"
  BACKGROUND_COLOR ="#121220"
  EDGE_COLOR = ("#3e5c7f","#ff5f1f")

class ColorPallet:
  __colors:list[Color]
  def __init__(self, colors: list[Color]) -> None:
      self.__colors = colors

  def get(self,idx:int)->Color:
    assert(idx > 0 and idx < len(self.__colors))
    return self.__colors[idx]

  @staticmethod
  def random(size: int):
    colors: list[Color] = []
    base = Color(rgb=(1.0,1.0,1.0))

    for i in range(0,size):
      col = Color(rgb=(random.random(),
        random.random(),
        random.random()))
      colors.append(mix(col,base))
    return ColorPallet(colors)

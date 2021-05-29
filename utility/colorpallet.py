from enum import Enum

from colour import Color
from scipy.sparse.construct import rand
from utility.color import mix
import random
import math

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
    assert(idx >= 0 and idx < len(self.__colors))
    return self.__colors[idx]

  def length(self):
    return len(self.__colors)

  @staticmethod
  def random(size: int, make_neon: bool, mix_base: Color = Color(rgb=(1.0,1.0,1.0))):
    colors: list[Color] = []
    
    for _ in range(0,size):
      col = Color(rgb=(random.random(),
        random.random(),
        random.random()))
      col = mix(col,mix_base)

      if make_neon:
        h,s,l = col.get_hsl()
        s = random.randint(85,100)/100
        l = random.randint(50,60)/100
        col = Color(hsl=(h,s,l))
      colors.append(col)
    return ColorPallet(colors)

  @staticmethod
  def even_dist_hsl_neon(size: int):
    colors: list[Color] = []

    step = 0.93 / size

    for i in range(0,size):
      h =  i * step
      if h > 1.0:
        h = 1.0
      colors.append(Color(hsl=( h, random.randint(85,100)/100, random.randint(50,60)/100)))  
    return ColorPallet(colors)



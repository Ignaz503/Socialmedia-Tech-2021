from re import T
import time
from typing import Union
from colour import Color
from enum import Enum
class HSLValues(Enum):
  H = 0
  S = 1
  L = 2
  ALL = 3

def __interpolate(v1:float,v2:float,t:float)->float:
  if v1 > v2:
    temp = v1
    v1 = v2
    v2 = temp
  assert(t >= 0 and t <= 1.0)
  return (1.0-t)*v1 + t*v2

def interpolate_rgb(c1:Color,c2:Color,t:float)->Color:
  r1,g1,b1 = c1.get_rgb()
  r2,g2,b2 = c2.get_rgb()

  return Color(rgb=(
    __interpolate(r1,r2,t),
    __interpolate(g1,g2,t),
    __interpolate(b1,b2,t)))

def interpolate_hsl(c1:Color,c2:Color,t:float,mode:HSLValues=HSLValues.ALL)->Color:
  h1,s1,l1 = c1.get_hsl()
  h2,s2,l2 = c2.get_hsl()

  if mode is HSLValues.H:
    return Color(hsl=(__interpolate(h1,h2,t),s1,l1))
  if mode is HSLValues.S:
    return Color(hsl=(h1,__interpolate(s1,s2,t),l1))
  if mode is HSLValues.L:
    return Color(hsl=(h1,s1,__interpolate(l1,l2,t)))
  return Color(hsl=(
    __interpolate(h1,h2,t),
    __interpolate(s1,s2,t),
    __interpolate(l1,l2,t)))

class ColorGradient:
  def __init__(self, start: Color, end: Color, granularity:int, pre_generate:bool) -> None:
      self.__start = start
      self.__end= end
      self.__granularity = granularity
      self.__is_pre_generated = pre_generate
      if pre_generate:
        self.__gradient = list(start.range_to(end,granularity))

  def get(self, idx: Union[float,int])-> Color:
    if isinstance(idx,int):
      return self.__get_int(idx)
    if isinstance(idx,float):
      return self.__get_float(idx)

  def __get_float(self,t: float):
    assert(t >= 0 and t<=1.0)
    idx = round((self.__granularity-1)*t)
    return self.__get_int(idx)

  def __get_int(self, idx:int)->Color:
    if self.__is_pre_generated:
      return self.__gradient[idx]
    else:
      return self.__loop_search(idx)

  def __loop_search(self,to:int)->Color:
    c = 0
    for col in self.__start.range_to(self.__end,self.__granularity):
      if c == to:
        return col
      c += 1

  def __getitem__(self,key:Union[int,float]):
    return self.get(key)

import math
  
def get_hours_minutes_seconds(val: float)->tuple[int,int,int]:
  min_f = val/60
  if min_f >= 1.0:
    res = [0,0,0]
    frac_s,min_i = math.modf(min_f)
    seconds = math.ceil(60*frac_s)
    res[2] = seconds
    h_f = min_i/60
    if h_f >= 1.0:
      frac_m,h_i = math.modf(h_f)
      minutes = math.ceil(60*frac_m)
      res[1] = minutes
      res[0] = math.floor(h_i)
      return tuple(res)
    else:
      res[1] = math.floor(min_i)
      return tuple(res)
  else:
    return (0,0,math.floor(val))

def get_seconds(hms: tuple[int,int,int])->int:
  return (hms[0]*60*60)+(hms[1]*60)+hms[2]
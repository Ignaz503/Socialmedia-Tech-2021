import random
import numpy as np

def define_index_dict_for_adj_mat(subs: list[str]):
  idx_dict = {}
  count = 0
  for sub in subs:
    idx_dict[sub] = count
    count +=1
  return idx_dict

def random_adjacency_mat(size:int, likelyhood:  float) -> np.ndarray:

  arr = np.zeros((size,size), dtype=np.int32)

  for i in range(0,size):
    for j in range(0,size):
      if i == j:
        continue
      if random.random() <= likelyhood:
        arr[i,j] += 1
        arr[j,i] += 1
  return arr
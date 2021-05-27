from queue import PriorityQueue
from typing import Any, Callable, Generator, Iterable

def __queue_gen(q: PriorityQueue):
  while not q.empty():
    yield q.get()

def group(to_group: Iterable[Any],int_converter:Callable[[Any],int],max_group_size:int) -> Generator[tuple[int,list[Any]],None,None]:
  
  queue = PriorityQueue()
  queue.put((0,[]))

  for g in to_group:
    val = int_converter(g)

    smallest = queue.get()

    if smallest[0] + val <= max_group_size:
      priority,lis = smallest
      priority+=val
      lis.append(g)
      queue.put((priority,lis))
    else:
      #resinsert smallest and insert new group
      queue.put(smallest)
      queue.put((val,[g]))
  
  return lambda: __queue_gen(queue)

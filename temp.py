
from concurrent.futures import ThreadPoolExecutor
from time import sleep
 
values = [3,4,5,6]
 
def cube(x):
    print(f'Cube of {x}:{x*x*x}')
 
 
if __name__ == '__main__':
    result =[]
    with ThreadPoolExecutor(max_workers=5) as exe:
        exe.submit(cube,2)
         
        # Maps the method 'cube' with a list of values.
        result = exe.map(cube,values)
     
    for r in result:
      print(r)
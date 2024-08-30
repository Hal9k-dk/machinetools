ITEM_WIDTH = 15

def arrange(items, size_x, size_y):
    y = 0
    while len(items) < size_x * size_y:
        items.append('---')
    for idx, item in enumerate(items):
        print(str(item).ljust(ITEM_WIDTH), end='')
        if ((idx + 1) % size_x) == 0:
            print('')
            y = y +1
            if y >= size_y:
                return items[idx+1:]
        
    return []

def gen_nuts(size):
    return [ f'M{size} møtrik',
             f'M{size} låsemøtrik',
             f'M{size} skive',
             f'M{size} fj.skive' ]

m3s = [
    4, 5, 6, 8, 10, 12, 16, 18, 20, 25, 30, 40, 50
]
m3 = [f'M3 x {n}' for n in m3s]
m3us = [
    4, 6, 8, 10, 12, 16, 18, 20, 25, 40
]
m3u = [f'M3 x {n}U' for n in m3us]
m3special = [ 'M3 x 10 m/skive', 'M3 x 10 stor' ]
m3all = gen_nuts(3) + m3
m3all.append(m3special[0])
m3all = m3all + m3u
m3all.append(m3special[1])
selfthread = ([ 'SS 2 x 6',  'SS 2 x 7', 'SS 2.9 x 6.5', 'SS 2.9 x 13' ] +
              [f'SS 3 x {n}' for n in [ 8, 10, 12, 14, 16 ]] +
              [f'SS  B&O {n+1}' for n in range(5) ])
pinol = [f'Pinol {n+1}' for n in range(12) ]

small = [ 'M2 skive', 'M2 x 4U' ] + m3all + selfthread + pinol

small_x = 5
small_y = 4
print('\n=== 4 x 5 klar\n')
rest = arrange(small, small_x, small_y)
print('\n=== 4 x 5 klar\n')
rest = arrange(rest, small_x, small_y)
print('\n=== 4 x 6 klar\n')
small_y = 6
rest = arrange(rest, small_x, small_y)

m4s = [
    6, 8, 10, 16, 20, 25, 30, 35, 60
]
m4 = [f'M4 x {n}' for n in m4s]
m4us = [
    6, 8, 10, 16, 20, 25, 30, 40
]
m4u = [f'M4 x {n}U' for n in m4us]

m5s = [
    6, 10, 16, 20, 25, 30, 40
]
m5 = [f'M5 x {n}' for n in m5s]
m5us = [
    10, 16, 25, 40
]
m5u = [f'M5 x {n}U' for n in m5us]

# TODO

m6s = [
    6, 10, 16, 20, 25, 30, 40
]
m6 = [f'M6 x {n}' for n in m6s]
m6us = [
    10, 16, 25, 40
]
m6u = [f'M6 x {n}U' for n in m6us]

medium = gen_nuts(4) + m4 + m4u + gen_nuts(5) + m5 + m5u + gen_nuts(6) + m6 + m6u

medium_x = 4
medium_y = 12
print('\n=== 12 x 4 klar\n')
rest = arrange(medium, medium_x, medium_y)

print('\n\n==============')

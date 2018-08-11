import time, dis
from django.db.backends.sqlite3 import base

start = time.time()  # 1.000459909439087

time.sleep(1)
d = {"x": 1, 'y': 2, 'z': 'alexsb'}

d = dict(x=1, y=2, z='alexsb')


print(time.time() - start)

print(dis.dis("tuple((1, 2))"))
print(dis.dis("{1}"))

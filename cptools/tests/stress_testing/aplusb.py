import random
import sys

seed = sys.argv[1]
rnd = random.randint(1, 30)

if rnd == 30:
    print(-100)  # Obviously wrong
else:
    print(sum(map(int, input().split())))

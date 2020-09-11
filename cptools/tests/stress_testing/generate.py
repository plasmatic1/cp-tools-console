import random
import sys

seed = int(sys.argv[1])
random.seed(seed)

a = random.randint(1, 10)
b = random.randint(1, 10)

print(a, b)

if random.randint(1, 10) >= 5:
    sys.stderr.write('spfa go brrr\n')
else:
    sys.stderr.write(str(a + b) + '\n')

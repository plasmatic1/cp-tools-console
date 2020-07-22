from sys import argv

exp = int(argv[2])
out = int(argv[3])

if out == exp:
    print('OK')
else:
    print(f'diff {abs(exp - out)}, wanted {exp}, got {out}')

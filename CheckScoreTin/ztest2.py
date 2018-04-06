a = '1 A 11 A 21 C 31 A 2 C 12 C 22 D 32 D 3 C 13 C 23 D 33 D 4 C 14 C 24 D 34 D 5 D 15 D 25 A 35 D 6 D 16 D 26 C 36 C 7 D 17 D 27 C 37 C 8 D 18 D 28 C 38 C 9 B 19 B 29 B 39 B 10 B 20 B 30 B 40 B'
b = a.split(sep = ' ')
c = list(filter(lambda x: x in ['A', 'B', 'C', 'D'], b))
d = list(filter(lambda x: x not in ['A', 'B', 'C', 'D'], b))
e = list(zip([int(k) for k in d], c))
f = sorted(e, key= lambda x: x[0])
result = [i[1] for i in f ]
print(result)

import pandas as pd

df = pd.DataFrame()
df['sdf'] = result
df.to_csv('ssffs.csv')
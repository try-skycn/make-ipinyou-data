import sys
from collections import Counter

filename = sys.argv[1]

d = Counter()

with open(filename, "r") as f:
	for line in f:
		d.update(["{}\t{}".format(i, x) for i, x in enumerate(line.strip().split()[1:-1], start=1) if x.strip() != '' and x.strip() != 'null'])

l = [x for x, cnt in d.most_common() if cnt >= 5]
l.sort(key=lambda x: int(x.split('\t')[0]))
with open("idmap", "w") as f:
	for x in l:
		print(x, file=f)

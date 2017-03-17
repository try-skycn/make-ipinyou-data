import sys, numpy as np, json, os
datadir, idmapfile, outfile = sys.argv[1:]

metafile = os.path.join(datadir, ".meta")
trainfile = os.path.join(datadir, "train")
testfile = os.path.join(datadir, "test")


with open(metafile, "r") as f:
	meta = json.load(f)
l = [None] + [[None, ] for i in range(28)]
with open(idmapfile, "r") as f:
	for line in f:
		fid, x = line.strip().split('\t')
		l[int(fid)].append(x)
m = [None] + [{} for i in range(28)]
for submap, sublist in zip(m[1:], l[1:]):
	for i, x in enumerate(sublist[1:], start=1):
		submap[x] = i
sizes = [None] + [len(sublist) for sublist in l[1:]]
names = [info["name"] for info in meta["field"][:-1]]
dtypes = [info["type"] for info in meta["field"][:-1]]

from h5py import File
f = File(outfile, "w")
f.attrs["names"] = json.dumps(names)
f.attrs["dtypes"] = json.dumps(dtypes)
f.attrs["sizes"] = json.dumps(sizes)
f.attrs["index2cate"] = json.dumps(l)
f.attrs["cate2index"] = json.dumps(m)
train = f.create_dataset("train", (15395258, 29), dtype=int)
test = f.create_dataset("test", (4100716, 29), dtype=int)

def dump(infile, dset):
	with open(infile, "r") as fin:
		for i, line in enumerate(fin):
			line = line.strip().split('\t')[:-1]
			dset[i] = np.array([int(line[0])] + [submap.get(x, 0) for submap, x in zip(m[1:], line[1:])])

dump(trainfile, train)
dump(testfile, test)

f.close()

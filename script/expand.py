import os, sys, argparse
import shutil
import imp
import json
from collections import Counter
from itertools import chain

NEWLINE = '\n'

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("-f", dest = "f", type = str)
	parser.add_argument("-t", dest = "t", type = str)
	parser.add_argument("--config", dest = "config", type = str)
	parser.add_argument("--skip", dest = "skip", default=1, type = int)
	return parser.parse_args()

args = parse_args()

def main():
	os.makedirs(args.t, exist_ok=True)

	files = [filename for filename in os.listdir(args.f)]
	meta_data = []

	makers = imp.load_source('', args.config).makers
	names = list(chain(*[maker.names for maker in makers]))
	typs = list(chain(*[maker.types for maker in makers]))

	for file in files:
		file_from = os.path.join(args.f, file)
		file_to = os.path.join(args.t, file)
		skip = args.skip
		size = 0
		with open(file_from, 'r') as ff, open(file_to, 'w') as ft:
			for line in ff:
				if skip > 0:
					skip -= 1
					continue
				items = line.strip('\n').split('\t')
				new_items = list(chain(*[maker.make(val) for maker, val in zip(makers, items)]))
				ft.write('\t'.join(new_items) + NEWLINE)
				size += 1
		meta_data.append({'file': file, 'size': size})

	meta_field = []
	for name, typ in zip(names, typs):
		meta_field.append({'name': name, 'type': typ})

	meta = {'data': meta_data, 'field': meta_field}
	with open(os.path.join(args.t, '.meta'), 'w') as fmeta:
		json.dump(meta, fmeta, indent='\t')

if __name__ == '__main__':
	main()

from ipinyoulib.lib import *
from ipinyoulib.metalib import *


NEWLINE = '\n'
TMP_DIR = '.tmp'
IND_TMP_DIR = '.tmp/ind'
IND_TMP_SHUFFLE = '.tmp/shuffle'


class TmpFolder:
	def __init__(self, *tmpdirs):
		self.tmpdir = os.path.join(*tmpdirs)

	def __enter__(self):
		os.makedirs(self.tmpdir, exist_ok=True)
		return self.tmpdir

	def __exit__(self, *args):
		shutil.rmtree(self.tmpdir)


class MultiFile:
	def __init__(self, files, mode='r'):
		self.files = files
		self.fps = [open(file, mode) for file in self.files]

	def __enter__(self):
		return self

	def __exit__(self, *args):
		for fp in self.fps:
			fp.close()

	def __iter__(self):
		for lines in zip(*self.fps):
			yield [line.strip('\n') for line in lines]

	def get(self, ind):
		return self.fps[ind]

	def write(self, vals):
		for fp, val in zip(self.fps, vals):
			fp.write(val)
			fp.write(NEWLINE)


def random_decision(decision_rate):
	return random.random() < decision_rate


def random_selection(*args):
	random_num = random.random()
	for i, prob in enumerate(args):
		if random_num < prob:
			return i
	return len(args)


def sample(input_path, input_info, output_path, expected_num):
	input_size = input_info['size']
	selection_rate = expected_num / input_size

	output_size, output_positive, output_negative = 0, 0, 0

	with open(input_path, 'r') as fi, open(output_path, 'w') as fo:
		for line in fi:
			if random_decision(selection_rate):
				fo.write(line)
				output_size += 1
				if is_positive(line):
					output_positive += 1
				else:
					output_negative += 1

	return DataObjInfo(output_path, dict(size=output_size, positive=output_positive, negative=output_negative))


def split(input_path, input_info, *args):
	accu_sizes = []
	accu_probs = []
	total_size = 0
	for output_path, subsize in args[:-1]:
		total_size += subsize
		accu_sizes.append(total_size)
	assert total_size <= input_info['size'], "Spliting out %d entries totally but only %d entries available." % (totally, input_info['size'])
	for accu_size in accu_sizes:
		accu_probs.append(accu_size / input_info['size'])

	output_paths = [output_path for output_path, _ in args]
	output_sizes, output_positives, output_negatives = [0 for _ in args], [0 for _ in args], [0 for _ in args]
	with open(input_path, 'r') as fi, MultiFile(output_paths, 'w') as fo:
		for line in fi:
			selection = random_selection(*accu_probs)
			fo.get(selection).write(line)
			output_sizes[selection] += 1
			if is_positive(line):
				output_positives[selection] += 1
			else:
				output_negatives[selection] += 1

	return [DataObjInfo(output_path, dict(size=output_sizes[i], positive=output_positives[i], negative=output_negatives[i])) for i, output_path in enumerate(output_paths)]


def nds(input_path, input_info, output_path, expected_ratio):
	input_positive = input_info['positive']
	input_negative = input_info['negative']
	expected_negative = input_positive * expected_ratio

	assert expected_negative < input_negative, 'While negative down sampling %s to %s, expected num of negatives %d is smaller than input negatives %d' % (input_path, output_path, expected_negative, input_negative)
	negative_selection_rate = expected_negative / input_negative

	output_size, output_positive, output_negative = 0, 0, 0
	with open(input_path, 'r') as fi, open(output_path, 'w') as fo:
		for line in fi:
			if is_positive(line):
				fo.write(line)
				output_size += 1
				output_positive += 1
			elif random_decision(negative_selection_rate):
				fo.write(line)
				output_size += 1
				output_negative += 1

	return DataObjInfo(output_path, dict(size=output_size, positive=output_positive, negative=output_negative))


def shuffle(input_path, output_path):
	with TmpFolder(IND_TMP_SHUFFLE) as tmp_dir:
		left_path = os.path.join(tmp_dir, 'left')
		right_path = os.path.join(tmp_dir, 'right')

		current_path = input_path
		for _ in range(7):
			with open(current_path, 'r') as fi, open(left_path, 'w') as fo_left, open(right_path, 'w') as fo_right:
				for line in fi:
					if random_decision(0.5):
						fo_left.write(line)
					else:
						fo_right.write(line)
			with open(output_path, 'w') as fo:
				with open(left_path, 'r') as fi_left:
					for line in fi_left:
						fo.write(line)
				with open(right_path, 'r') as fi_right:
					for line in fi_right:
						fo.write(line)
			current_path = output_path


def make_index(data, threshold, withnull):
	c = Counter(data)

	null_list = [key for key, val in c.items() if val < threshold or key == 'null']
	for key in null_list:
		del c[key]

	l = (['null'] if withnull and null_list != [] else []) + [key for key, val in c.most_common()]
	m = {key: i for i, key in enumerate(l)}

	return m


def make_num_field(input_pathpak, output_pathpak, threshold):
	for ipath, opath in zip(input_pathpak, output_pathpak):
		shutil.copyfile(ipath, opath)


def make_cate_field(input_pathpak, output_pathpak, threshold):
	datapak = []
	for path in input_pathpak:
		with open(path, 'r') as fi:
			datapak.append([line.strip('\n') for line in fi])

	m = make_index(chain(*datapak), threshold, withnull=True)

	for path, data in zip(output_pathpak, datapak):
		with open(path, 'w') as fo:
			for item in data:
				fo.write(str(m.get(item, 0)) + NEWLINE)
	
	return m


def make_set_field(input_pathpak, output_pathpak, threshold):
	datapak = []
	for path in input_pathpak:
		with open(path, 'r') as fi:
			datapak.append([line.strip('\n').split(',') for line in fi])

	m = make_index(chain(*chain(*datapak)), threshold, withnull=False)

	for path, data in zip(output_pathpak, datapak):
		with open(path, 'w') as fo:
			for collection in data:
				output_collection = [m.get(item, None) for item in collection]
				output_collection = [str(item) for item in output_collection if item is not None]
				fo.write(','.join(output_collection) + NEWLINE)
	
	return m


make_field = {
	'num': make_num_field,
	'set': make_set_field,
	'cate': make_cate_field
}


def ind(input_pathpak, fieldpak_info, output_pathpak, threshold):
	namepak = [info['name'] for info in fieldpak_info]
	typepak = [info['type'] for info in fieldpak_info]
	mappak = {}
	output_fieldpak_info = FieldPackageInfo(None, [])

	tmp_name = lambda name, path: '.'.join([name, os.path.basename(path)])

	with TmpFolder(IND_TMP_DIR, 'raw') as raw_dir, TmpFolder(IND_TMP_DIR, 'cooked') as cooked_dir:
		table = [[tmp_name(name, path) for name in namepak] for path in input_pathpak]
		raw_table = np.array([[os.path.join(raw_dir, j) for j in i] for i in table])
		cooked_table = np.array([[os.path.join(cooked_dir, j) for j in i] for i in table])

		for i, path in enumerate(input_pathpak):
			with open(path, 'r') as fi, MultiFile(raw_table[i, :], 'w') as fo:
				for line in fi:
					fo.write(line.strip('\n').split('\t'))

		for j, (name, typ) in enumerate(zip(namepak, typepak)):
			m = make_field[typ](raw_table[:, j], cooked_table[:, j], threshold)
			mappak[name] = m
			field_info = dict(**fieldpak_info[j])
			if m is not None:
				field_info['size'] = len(m)
			output_fieldpak_info.append(field_info)

		for i, path in enumerate(output_pathpak):
			with MultiFile(cooked_table[i, :], 'r') as fi, open(path, 'w') as fo:
				for entry in fi:
					fo.write('\t'.join(entry) + NEWLINE)

	return output_fieldpak_info, mappak


class PackageManager():
	def __init__(self, path):
		self.path = path
		self.meta = PackageInfo(path)
		self.command_ind = 0

		self.tmp_folder = TmpFolder(TMP_DIR)
		self.tmp_folder.__enter__()

		self.meta['log'].append('load from %s' % path)

	def _new_task(self):
		new_path = os.path.join(TMP_DIR, 'step_' + str(self.command_ind))
		os.makedirs(new_path, exist_ok=True)
		self.command_ind += 1
		return new_path

	def index(self, threshold):
		new_path = self._new_task()
		map_path = os.path.join(new_path, '.map')

		path_items = self.meta['data'].items()
		pathpak = [(os.path.join(new_path, key), val.path) for key, val in path_items]
		input_pathpak = [y for x, y in pathpak]
		output_pathpak = [x for x, y in pathpak]
		self.meta['field'], mappak = ind(input_pathpak, self.meta['field'], output_pathpak, threshold)
		with open(map_path, 'w') as fmap:
			json.dump(mappak, fmap, indent='\t')

		self.meta['extra']['.map'] = map_path
		for (key, val), output_path in zip(path_items, output_pathpak):
			val.path = output_path
		self.meta['log'].append('index threshold=%d' % threshold)

	def sample(self, file, expected_num):
		new_path = self._new_task()

		data_info = self.meta['data'][file]
		output_path = os.path.join(new_path, file)

		self.meta['data'][file] = sample(data_info.path, data_info, output_path, expected_num)
		self.meta['log'].append('sample file=%s, expected_num=%d' % (file, expected_num))

	def sample_out(self, file, file_out, expected_num):
		new_path = self._new_task()

		data_info = self.meta['data'][file]
		output_path = os.path.join(new_path, file_out)

		self.meta['data'][file_out] = sample(data_info.path, data_info, output_path, expected_num)
		self.meta['log'].append('sample file=%s, file-out=%s, expected_num=%d' % (file, file_out, expected_num))

	def split(self, file, *args):
		new_path = self._new_task()
		args = list(args) + [(file, None)]

		data_info = self.meta['data'][file]
		feed_args = [(os.path.join(new_path, new_file), subsize) for new_file, subsize in args]

		new_infos = split(data_info.path, data_info, *feed_args)
		for (key, _), info in zip(args, new_infos):
			self.meta['data'][key] = info
		self.meta['log'].append('split file=%s, %s' % (file, ' '.join([str(t) for t in args])))

	def nds(self, file, expected_ratio):
		new_path = self._new_task()

		data_info = self.meta['data'][file]
		output_path = os.path.join(new_path, file)

		self.meta['data'][file] = nds(data_info.path, data_info, output_path, expected_ratio)
		self.meta['log'].append('negative_down_sample file=%s, expected_ratio=1:%d' % (file, expected_ratio))

	def shuffle(self, file):
		new_path = self._new_task()

		data_info = self.meta['data'][file]
		output_path = os.path.join(new_path, file)
		shuffle(data_info.path, output_path)

		data_info.path = output_path
		self.meta['log'].append('shuffle file=%s' % file)

	def dump(self, path):
		os.makedirs(path, exist_ok=True)
		self.meta.dump(path)
		self.tmp_folder.__exit__(None, None, None)


def load(path):
	return PackageManager(path)

from ipinyoulib.lib import *
from ipinyoulib.metalib import *

def line_generator(path, cyclic):
	flag = True
	while flag:
		with open(path, 'r') as fi:
			for line in fi:
				yield line.strip('\n').split('\t')
		flag = cyclic


def checkpoint(epoch):
	while True:
		for _ in range(epoch - 1):
			yield False
		yield True


class DataManager:
	def __init__(self, fieldpak, selection):
		self._filter_list = []
		self._type_list = []
		self._offset_list = []
		self.intervals = []
		self.size = 0
		self.num = 0

		for field in fieldpak:
			if field['name'] in selection:
				self._filter_list.append(True)
				self._type_list.append(field['type'])
				if field['type'] == 'num':
					self._offset_list.append(None)
					self.intervals.append(None)
				elif field['type'] == 'cate' or field['type'] == 'set':
					self._offset_list.append(self.size)
					self.intervals.append((self.size, self.size + field['size']))
					self.size += field['size']
				self.num += 1
			else:
				self._filter_list.append(False)
				self._type_list.append(None)
				self._offset_list.append(None)

	def get(self, entry):
		output = []
		for item, selection, typ, offset in zip(entry, self._filter_list, self._type_list, self._offset_list):
			if selection:
				if typ == 'num':
					output.append(float(item))
				elif typ == 'cate':
					output.append(int(item) + offset)
				elif typ == 'set':
					output.append([int(element) + offset for element in item.split(',') if element != ''])
		return np.array(output, dtype=object)


class DataPack:
	def __init__(self, **kwargs):
		for key, val in kwargs.items():
			vars(self)[key] = val


class DataLoader:
	def __init__(self, path, **kwargs):
		self.meta = PackageInfo(path)
		self._keys = []
		self._managers = []
		for key, val in kwargs.items():
			manager = DataManager(self.meta['field'], val)
			self._keys.append(key)
			self._managers.append(manager)
			vars(self)[key] = manager

	def _entry_generator(self, file, cyclic):
		path = self.meta['data'][file].path
		for entry in line_generator(path, cyclic):
			yield [manager.get(entry) for manager in self._managers]

	def _batch_generator(self, file, batch_size, cyclic):
		batch = [[] for _ in self._keys]
		for check, entries in zip(checkpoint(batch_size), self._entry_generator(file, cyclic)):
			for key_entries, entry in zip(batch, entries):
				key_entries.append(entry)
			if check:
				yield DataPack(**{key: np.stack(key_entries) for key, key_entries in zip(self._keys, batch)})
				batch = [[] for _ in self._keys]

	def get(self, file, batch_size, cyclic):
		size = None if cyclic else (self.meta['data'][file]['size'] // batch_size)
		return size, self._batch_generator(file, batch_size, cyclic)


def load(path, **kwargs):
	return DataLoader(path, **kwargs)


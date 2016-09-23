from ipinyoulib.lib import *

class DataObjInfo(dict):
	def __init__(self, path, other):
		if 'file' in other:
			del other['file']
		dict.__init__(self, other)
		self.path = path

	def __missing__(self, key):
		if key in ['size', 'positive', 'negative']:
			size, positive, negative = 0, 0, 0
			with open(self.path, 'r') as fi:
				for line in fi:
					size += 1
					if is_positive(line):
						positive += 1
					else:
						negative += 1
			self['size'] = size
			self['positive'] = positive
			self['negative'] = negative
			return self[key]
		else:
			raise KeyError(key)

	def dump(self, file, path):
		shutil.copyfile(self.path, os.path.join(path, file))
		return dict(**self, file=file)


class DataPackageInfo(dict):
	def __init__(self, path, other):
		dict.__init__(self)
		for val in other:
			key = val['file']
			self[key] = DataObjInfo(os.path.join(path, key), val)

	def dump(self, path):
		return [val.dump(key, path) for key, val in self.items()]


class ExtraPackageInfo(dict):
	def __init__(self, path, other):
		dict.__init__(self)
		for val in other:
			self[val] = os.path.join(path, val)

	def dump(self, path):
		for key, val in self.items():
			shutil.copyfile(val, os.path.join(path, key))
		return [key for key in self]


class FieldObjInfo(dict):
	def __missing__(self, key):
		if key == 'size':
			raise KeyError('This is not a indexed data.')
		else:
			raise KeyError(key)


class FieldPackageInfo(list):
	def __init__(self, path, other):
		list.__init__(self, [FieldObjInfo(val) for val in other])

	def dump(self, path):
		return [dict(val) for val in self]


default_package_info = {
	'log': [],
	'field': [],
	'data': [],
	'extra': []
}


default_info_manager = lambda path, obj: obj


info_manager = {
	'data': DataPackageInfo,
	'extra': ExtraPackageInfo,
	'field': FieldPackageInfo
}


class PackageInfo(dict):
	def __init__(self, path):
		dict.__init__(self)
		info = dict(**default_package_info)
		with open(os.path.join(path, '.meta')) as fmeta:
			info.update(json.load(fmeta))
		for key, val in info.items():
			self[key] = info_manager.get(key, default_info_manager)(path, val)

	def dump(self, path):
		result = {}
		for key, val in self.items():
			if key in info_manager:
				result[key] = val.dump(path)
			else:
				result[key] = val
		with open(os.path.join(path, '.meta'), 'w') as fmeta:
			json.dump(result, fmeta, indent='\t')

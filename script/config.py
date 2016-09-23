class Maker():
	def __init__(self, **kwargs):
		for key, val in kwargs.items():
			self.__dict__[key] = val

identity = lambda x: [x]

makers = [
	Maker(
		name = 'click',
		names = ['click'],
		types = ['num'],
		make = identity
	),
	Maker(
		name = 'weekday',
		names = ['weekday'],
		types = ['cate'],
		make = identity
	),
	Maker(
		name = 'hour',
		names = ['hour'],
		types = ['cate'],
		make = identity
	),
	Maker(
		name = 'bidid',
		names = ['bidid'],
		types = ['cate'],
		make = identity
	),
	Maker(
		name = 'timestamp',
		names = ['time_day'],
		types = ['cate'],
		make = lambda val: [val[6:8]]
	),
	Maker(
		name = 'logtype',
		names = ['logtype'],
		types = ['cate'],
		make = identity
	),
	Maker(
		name = 'ipinyouid',
		names = ['ipinyouid'],
		types = ['cate'],
		make = identity
	),
	Maker(
		name = 'useragent',
		names = ['user_agent_os', 'user_agent_browser'],
		types = ['cate'] * 2,
		make = lambda val: val.split('_')
	),
	Maker(
		name = 'IP',
		names = ['IP%d' % i for i in range(3)],
		types = ['cate'] * 3,
		make = lambda val: val.split('.')[0:3]
	),
	Maker(
		name = 'region',
		names = ['region'],
		types = ['cate'],
		make = identity
	),
	Maker(
		name = 'city',
		names = ['city'],
		types = ['cate'],
		make = identity
	),
	Maker(
		name = 'adexchange',
		names = ['adexchange'],
		types = ['cate'],
		make = identity
	),
	Maker(
		name = 'domain',
		names = ['domain'],
		types = ['cate'],
		make = identity
	),
	Maker(
		name = 'url',
		names = ['url'],
		types = ['cate'],
		make = identity
	),
	Maker(
		name = 'urlid',
		names = ['urlid'],
		types = ['cate'],
		make = identity
	),
	Maker(
		name = 'slotid',
		names = ['slotid'],
		types = ['cate'],
		make = identity
	),
	Maker(
		name = 'slotwidth',
		names = ['slotwidth'],
		types = ['cate'],
		make = identity
	),
	Maker(
		name = 'slotheight',
		names = ['slotheight'],
		types = ['cate'],
		make = identity
	),
	Maker(
		name = 'slotvisibility',
		names = ['slotvisibility'],
		types = ['cate'],
		make = identity
	),
	Maker(
		name = 'slotformat',
		names = ['slotformat'],
		types = ['cate'],
		make = identity
	),
	Maker(
		name = 'slotprice',
		names = ['slotprice'],
		types = ['cate'],
		make = identity
	),
	Maker(
		name = 'creative',
		names = ['creative'],
		types = ['cate'],
		make = identity
	),
	Maker(
		name = 'bidprice',
		names = ['bidprice'],
		types = ['cate'],
		make = identity
	),
	Maker(
		name = 'payprice',
		names = ['payprice'],
		types = ['cate'],
		make = identity
	),
	Maker(
		name = 'keypage',
		names = ['keypage'],
		types = ['cate'],
		make = identity
	),
	Maker(
		name = 'advertiser',
		names = ['advertiser'],
		types = ['cate'],
		make = identity
	),
	Maker(
		name = 'usertag',
		names = ['usertag'],
		types = ['set'],
		make = identity
	)
]

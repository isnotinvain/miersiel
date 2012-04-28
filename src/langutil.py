#http://stackoverflow.com/users/7980/alec-thomas
class Enum(object):
	@classmethod
	def new(cls, *seq, **named):
		if len(seq) != len(set(seq)):
			raise ValueError("Duplicate keys in enum:" + str(seq))
		enums = dict(zip(seq, seq), **named)
		return type('Enum', (cls,), enums)
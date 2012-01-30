import util

class Environment(object):

	def __init__(self, simulation, SCREENHEIGHT, PPM=25.0):
		self.simulation = simulation
		self.tons = set()
		self.comms = {}

		self.SCREENHEIGHT = SCREENHEIGHT
		self.PPM = 25.0

	def writeComm(self, channelKey, ton, value):
		if channelKey not in self.comms:
			self.comms[channelKey] = {}
		channel = self.comms[channelKey]
		channel[ton] = value

	def readComm(self, channelKey, ton):
		if channelKey not in self.comms:
			return None
		if ton not in self.comms[channelKey]:
			return None
		return self.comms[channelKey][ton]

	def addTon(self, ton):
		self.tons.add(ton)

	def getTons(self):
		return self.tons

	def tonsInBox(self, leftTop, rightBottom):
		bodies = self.simulation.bodiesInRegion(leftTop, rightBottom)
		tons = set()
		for body in bodies:
			parent = body.userData['parent']
			if parent and parent in self.tons:
				tons.add(parent)
		return tons

	def tonsInCircle(self, center, radius):
		cx, cy = center
		left = cx - radius
		right = cx + radius
		top = cy + radius
		bottom = cy - radius

		inBox = self.tonsInBox((left, top), (right, bottom))
		return set(x for x in inBox if util.distance2(x.getCenter(), center) <= radius**2)
		return inBox

	@classmethod
	def _scToWorld(cls, scalar, PPM):
		return scalar / PPM

	def scToWorld(self, scalar):
		return self._scToWorld(scalar, self.PPM)

	@classmethod
	def _toWorld(cls, vec, PPM, SCREENHEIGHT):
		x, y = vec
		x /= PPM
		y = SCREENHEIGHT - y
		y /= PPM
		return x, y

	def toWorld(self, vec):
		return self._toWorld(vec, self.PPM, self.SCREENHEIGHT)

	@classmethod
	def _scToScreen(self, scalar, PPM):
		return scalar * PPM

	def scToScreen(self, scalar):
		return self._scToScreen(scalar, self.PPM)

	@classmethod
	def _toScreen(self, vec, PPM, SCREENHEIGHT):
		if not isinstance(vec, tuple):
			vec = vec.tuple()
		x, y = vec
		x *= PPM
		y *= PPM
		y = SCREENHEIGHT - y
		return x, y
	def toScreen(self, vec):
		return self._toScreen(vec, self.PPM, self.SCREENHEIGHT)

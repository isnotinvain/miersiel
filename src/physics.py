# miersiel (c) Alex Levenson 2011, All Rights Reserved
# method bodiesAtPoint modified from the Elements source (formerly: http://elements.linuxuser.at)
# Can't seem to find the Elements project online though, so I don't know how to properly attribute

import Box2D as box2d

class PhysicsSimulator(object):
	"""
	Encapsulates the Box2D simulation and
	provides useful physics related functions
	"""
	def __init__(self, game):
		self.game = game
		self.SCREENHEIGHT = game.screen.get_height()
		self.PPM = 25.0
		self.ITERATIONS = 20

		# set up box2D	
		worldAABB = box2d.b2AABB()
		worldAABB.lowerBound.Set(-10, -10)
		x, y = game.screen.get_size()
		x = (x / self.PPM) + 10
		y = (y / self.PPM) + 10
		worldAABB.upperBound.Set(x, y)
		gravity = (0, 0)
		self.world = box2d.b2World(worldAABB, gravity, True)

		self.timeStep = 1.0 / 60
		self.run = True

		# callbacks stored as {body id to watch : function to call}
		# function will be passed the contact type as a string, the contact point object, and the other body
		self.contactListener = ContactListener()
		self.world.SetContactListener(self.contactListener)

	def update(self):
		if self.run: self.world.Step(self.timeStep, self.ITERATIONS, self.ITERATIONS)

	def addBody(self, pos, parent, sleepFlag=True, isBullet=False, linearDamping=0.1, angularDamping=0.1):
		bodyDef = box2d.b2BodyDef()
		bodyDef.position.Set(*pos)
		bodyDef.sleepFlag = sleepFlag
		bodyDef.isBullet = isBullet
		bodyDef.linearDamping = linearDamping
		bodyDef.angularDamping = angularDamping
		body = self.world.CreateBody(bodyDef)
		body.userData = {'parent':parent, 'id': id(body)}
		return body

	def bodiesAtPoint(self, pt, include_static=False, include_sensor=False):
		# modified from the elements source
		# thanks guys!
		sx, sy = pt
		f = 0.01
		AABB = box2d.b2AABB()
		AABB.lowerBound.Set(sx - f, sy - f);
		AABB.upperBound.Set(sx + f, sy + f);
		amount, shapes = self.world.Query(AABB, 2)
		if amount == 0:
			return False
		else:
			bodylist = []
			for s in shapes:
				if s.IsSensor() and not include_sensor: continue
				body = s.GetBody()
				if not include_static:
					if body.IsStatic() or body.GetMass() == 0.0:
						continue

				if s.TestPoint(body.GetXForm(), (sx, sy)):
					bodylist.append(body)
			return bodylist

	def bodiesInRegion(self, leftTop, rightBottom, numBodies=1000):
		left, top = leftTop
		right, bottom = rightBottom

		aabb = box2d.b2AABB()
		aabb.lowerBound.Set(left, bottom)
		aabb.upperBound.Set(right, top)
		count, shapes = self.world.Query(aabb, numBodies)

		bodies = []
		for shape in shapes:
			bodies.append(shape.GetBody())
		return bodies

	def scToWorld(self, scalar):
		return scalar / self.PPM

	def toWorld(self, vec):
		x, y = vec
		x /= self.PPM
		y = self.SCREENHEIGHT - y
		y /= self.PPM
		return x, y

	def scToScreen(self, scalar):
		return scalar * self.PPM

	def toScreen(self, vec):
		if not isinstance(vec, tuple):
			vec = vec.tuple()
		x, y = vec
		x *= self.PPM
		y *= self.PPM
		y = self.SCREENHEIGHT - y
		return x, y

	def b2PolyToScreen(self, shape):
		points = []
		for i in xrange(shape.GetVertexCount()):
			pt = box2d.b2Mul(shape.GetBody().GetXForm(), shape.getVertex(i))
			pt = self.toScreen(pt)
			points.append(pt)
		return points

	def stopBody(self, body):
		zero = (0, 0)
		body.SetLinearVelocity(zero)
		body.SetAngularVelocity(0)

class ContactListener(box2d.b2ContactListener):
	def __init__(self):
		box2d.b2ContactListener.__init__(self)
		self.callbacks = {}

	def connect(self, body, cb):
		self.callbacks[body.GetUserData()['id']] = cb

	def disconnect(self, body):
		if self.callbacks[body.GetUserData()['id']]:
			del self.callbacks[body.GetUserData()['id']]

	def Add(self, point):
		b1 = point.shape1.GetBody().GetUserData()['id']
		b2 = point.shape2.GetBody().GetUserData()['id']

		if self.callbacks.has_key(b1):
			self.callbacks[b1]("Add", point)
		if self.callbacks.has_key(b2):
			self.callbacks[b2]("Add", point)

	def Persist(self, point):
		b1 = point.shape1.GetBody().GetUserData()['id']
		b2 = point.shape2.GetBody().GetUserData()['id']

		if self.callbacks.has_key(b1):
			self.callbacks[b1]("Persist", point)
		if self.callbacks.has_key(b2):
			self.callbacks[b2]("Persist", point)

	def Remove(self, point):
		b1 = point.shape1.GetBody().GetUserData()['id']
		b2 = point.shape2.GetBody().GetUserData()['id']

		if self.callbacks.has_key(b1):
			self.callbacks[b1]("Remove", point)
		if self.callbacks.has_key(b2):
			self.callbacks[b2]("Remove", point)

	def Result(self, point):
		b1 = point.shape1.GetBody().GetUserData()['id']
		b2 = point.shape2.GetBody().GetUserData()['id']

		if self.callbacks.has_key(b1):
			self.callbacks[b1]("Result", point)
		if self.callbacks.has_key(b2):
			self.callbacks[b2]("Result", point)
from math import *

class Ellipsoid(object):
	def __init__(self, a, b):
		self.a = a
		self.b = b
		self.e2 = (a**2 - b**2) / a**2
		self.et2 = (a**2 - b**2) / b**2

	def Kn(self, f):
		return self.a / sqrt(1 - self.e2 * sin(f)**2)

	def Kr(self, f):
		return self.a * (1 - self.e2) / pow((1 - self.e2 * sin(f)**2), 3/2)
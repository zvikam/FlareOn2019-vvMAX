#!/usr/bin/python3

import sys
import struct
import string
from itertools import product


DEBUG = True

class CPU():
	def __init__(self, memory = None):
		self.MEMORY = b'\x00\x11\x00\xff'
		self.IP = 0
		self.CALLTABLE = [
			(self.FUNC_17B0, 0),
			(self.FUNC_2300, 3),
			(self.FUNC_21E0, 3),
			(self.FUNC_3030, 3),
			(self.FUNC_2740, 3),
			(self.FUNC_1DD0, 3),
			(self.FUNC_2630, 2),
			(self.FUNC_1CB0, 3),
			(self.FUNC_2F10, 3),
			(self.FUNC_1950, 3),
			(self.FUNC_2BB0, 3),
			(self.FUNC_1A70, 3),
			(self.FUNC_2CD0, 3),
			(self.FUNC_1B90, 3),
			(self.FUNC_2DF0, 3),
			(self.FUNC_24E0, 3),
			(self.FUNC_2420, 2),
			(self.FUNC_2010, 1),
			(self.FUNC_2980, 3),
			(self.FUNC_20D0, 3),
			(self.FUNC_2A90, 3),
			(self.FUNC_2860, 3),
			(self.FUNC_1EF0, 3),
			(self.FUNC_2600, 0)
		]
		self.CALLTABLE_OFFSET = 0xC00
		self.RAM_OFFSET = 0x800
		if memory:
			with open(memory, 'rb') as fin:
					self.MEMORY = bytearray(fin.read())

	def _mask32bit(self, x):
		return x & 0xFFFFFFFF

	def _mask16bit(self, x):
		return x & 0xFFFF

	def _mask8bit(self, x):
		return x & 0xFF

	def _getBlock(self, addr):
		return self.MEMORY[addr:addr + 0x20]

	def _getRAMBlock(self, addr):
		addr1 = addr
		addr *= 0x20
		addr += self.RAM_OFFSET
		data = self._getBlock(addr)
		if DEBUG:
			print("read from %x" % addr1, [hex(x) for x in data])
		return data

	def _setBlock(self, addr, data):
		if DEBUG:
			print("store at %x" % addr, [hex(x) for x in data])
		addr *= 0x20
		addr += self.RAM_OFFSET	
		self.MEMORY[addr:addr + 0x20] = data[:0x20]

	def getFuncArgs(self, n):
		args = []
		self.IP += 1
		for i in range(n):
			arg1 = self.MEMORY[self.IP]
			self.IP += 1
			args.append(arg1)
		return args

	def run(self):
		while self.MEMORY[self.IP] != 0xFF:
			if DEBUG:
				#input("")
				print("===================================================================================================")
			inst = self.MEMORY[self.IP]
			func = self.CALLTABLE[inst]
			args = self.getFuncArgs(func[1])
			if DEBUG:
				print(hex(inst), [hex(a) for a in args])
			func[0](*args)

	def reverse(self):
		#self.FUNC_2A90(0x40, 0x14, 5)
		pass

	def verify(self):
		saddr = 0x2
		daddr = 0x14
		src = self._getRAMBlock(saddr)
		dst = self._getRAMBlock(daddr)
		if DEBUG:
			print(src)
			print(dst)
		return src[0:3] == dst[0:3]

	def result(self):
		saddr = 0x1
		daddr = 0x1F
		src = self._getRAMBlock(saddr)
		dst = self._getRAMBlock(daddr)
		return ''.join([chr(src[i] ^ dst[i]) for i in range(len(src))])
		#return [chr(src[i] ^ dst[i]) for i in range(len(src))]

	def FUNC_17B0(self):
		# this function prepares the VM memory. does nothing
		if DEBUG:
			print("memset 0000")
		pass
		
	def FUNC_1950(self, dst, ask, src):
		if DEBUG:
			print("vpaddw noIMPL")
		pass

	def FUNC_1A70(self, dst, src2, src1):
		if DEBUG:
			print("vpaddd")
		s1 = self._getRAMBlock(src1)
		s2 = self._getRAMBlock(src2)
		s1d = struct.unpack("<8L", s1)
		s2d = struct.unpack("<8L", s2)
		dd = [self._mask32bit(i + j) for i, j in zip(s1d, s2d)]
		d = struct.pack("<8L", *dd)
		self._setBlock(dst, d)
		pass

	def FUNC_1B90(self, dst, mask, src):
		if DEBUG:
			print("vpaddq noIMPL")
		pass

	def FUNC_1CB0(self, dst, src2, src1):
		if DEBUG:
			print("vpaddb")
		s1 = self._getRAMBlock(src1)
		s2 = self._getRAMBlock(src2)
		d = bytearray(self._mask8bit(i+j) for i, j in zip(s1, s2))
		self._setBlock(dst, d)
		pass

	def FUNC_1DD0(self, dst, src2, src1):
		if DEBUG:
			print("vpand")
		s1 = self._getRAMBlock(src1)
		s2 = self._getRAMBlock(src2)
		d = bytearray((i & j) for i, j in zip(s1, s2))
		self._setBlock(dst, d)
		pass

	def FUNC_1EF0(self, dst, src2, src1):
		if DEBUG:
			print("vpcmpeqb")
		s1 = self._getRAMBlock(src1)
		s2 = self._getRAMBlock(src2)
		d = bytearray(i == j for i, j in zip(s1, s2))
		self._setBlock(dst, d)
		pass

	def FUNC_2010(self, dst):
		data = self._getBlock(self.IP)
		self.IP += 0x20
		if DEBUG:
			print("store")
		self._setBlock(dst, data)
		pass

	def FUNC_20D0(self, dst, src, count):
		if DEBUG:
			print("vpslld")
		s = self._getRAMBlock(src)
		sd = struct.unpack("<8L", s)
		dd = [self._mask32bit(i << count) for i in sd]
		d = struct.pack("<8L", *dd)
		self._setBlock(dst, d)
		pass

	def FUNC_21E0(self, dst, src2, src1):
		if DEBUG:
			print("vpmaddwd")
		s1 = self._getRAMBlock(src1)
		s2 = self._getRAMBlock(src2)
		s1d = struct.unpack("<16H", s1)
		s2d = struct.unpack("<16H", s2)
		dd = []
		for i in range(0,16,2):
			dd.append(s1d[i]*s2d[i] + s1d[i+1]*s2d[i+1])
		d = struct.pack("<8L", *dd)
		self._setBlock(dst, d)
		pass

	def FUNC_2300(self, dst, src2, src1):
		if DEBUG:
			print("vpmaddubsw")
		s1 = self._getRAMBlock(src1)
		s2 = self._getRAMBlock(src2)
		s1d = struct.unpack("<32b", s1)
		s2d = struct.unpack("<32b", s2)
		dd = []
		for i in range(0,32,2):
			dd.append(s1d[i]*s2d[i] + s1d[i+1]*s2d[i+1])
		d = struct.pack("<16h", *dd)
		self._setBlock(dst, d)
		pass

	def FUNC_2420(self, dst, src):
		if DEBUG:
			print("memcpy noIMPL")
		pass

	def FUNC_24E0(self, dst, mask, src):
		if DEBUG:
			print("vpmuldq noIMPL")
		pass

	def FUNC_2600(self):
		if DEBUG:
			print("nop noIMPL")
		pass

	def FUNC_2630(self, dst, src):
		constant = '\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'
		if DEBUG:
			print("vpxor_constant noIMPL")
		pass

	def FUNC_2740(self, dst, src2, src1):
		if DEBUG:
			print("vpor")
		s1 = self._getRAMBlock(src1)
		s2 = self._getRAMBlock(src2)
		d = bytearray((i | j) for i, j in zip(s1, s2))
		self._setBlock(dst, d)
		pass

	def FUNC_2860(self, dst, src, mask):
		if DEBUG:
			print("vpermd")
		s = self._getRAMBlock(src)
		m = self._getRAMBlock(mask)
		sd = struct.unpack("<8L", s)
		md = struct.unpack("<8L", m)
		dd = [sd[i] if i != 0xffffffff else 0 for i in md]
		d = bytearray(struct.pack("<8L", *dd))
		self._setBlock(dst, d)
		pass

	def FUNC_2980(self, dst, src, count):
		if DEBUG:
			print("vpsrld")
		s = self._getRAMBlock(src)
		sd = struct.unpack("<8L", s)
		dd = [self._mask32bit(i >> count) for i in sd]
		d = struct.pack("<8L", *dd)
		self._setBlock(dst, d)
		pass

	def FUNC_2A90(self, dst, src, mask):
		if DEBUG:
			print("vpshufb")
		s = self._getRAMBlock(src)
		m = self._getRAMBlock(mask)
		d = bytearray([s[i & 0x0F] if i < 0x80 else 0 for i in m])
		self._setBlock(dst, d)
		pass

	def FUNC_2BB0(self, dst, mask, src):
		if DEBUG:
			print("vpsubw noIMPL")
		pass

	def FUNC_2CD0(self, dst, mask, src):
		if DEBUG:
			print("vpsubd noIMPL")
		pass

	def FUNC_2DF0(self, dst, mask, src):
		if DEBUG:
			print("vpsubq noIMPL")
		pass

	def FUNC_2F10(self, dst, mask, src):
		if DEBUG:
			print("vpsubb noIMPL")
		pass

	def FUNC_3030(self, dst, src2, src1):
		if DEBUG:
			print("vpxor")
		s1 = self._getRAMBlock(src1)
		s2 = self._getRAMBlock(src2)
		d = bytearray((i ^ j) for i, j in zip(s1, s2))
		self._setBlock(dst, d)
		pass


def main():
	#chars = string.ascii_letters + string.digits + '_'

	#for password in product(chars, repeat=4):
	#	password = str(password)
	for password in [None]:
		sys.stdout.write('\r%s' % password)
		cpu = CPU('VM_MEMORY.bin')
		if len(sys.argv) > 1:
			password = sys.argv[1].encode()

		if password:
			if len(password) < 0x20:
				password += '\x00' * (0x20 - len(password))
			cpu.MEMORY[0x25:0x25 + 0x20] = password

		# run program in memory
		cpu.run()

		if DEBUG:
			with open('VM_MEMORY_done.bin', 'wb') as fin:
				fin.write(bytearray(cpu.MEMORY))

		# let's verify the results
		r = cpu.verify()
		if r:
			print(cpu.result())
			return r
	return -1


if __name__ == '__main__': 
	sys.exit(main())

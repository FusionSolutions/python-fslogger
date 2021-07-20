# Builtin modules
import re, os, traceback
from abc import ABCMeta, abstractmethod
from glob import glob
from datetime import datetime
from functools import cmp_to_key
from typing import List, Any, Optional
# Third party modules
# Local modules
# Program
class STDErrModule:
	log:Any
	closed:bool
	buffer:str
	def __init__(self) -> None:
		self.log    = Logger("Standard").getChild("Error")
		self.closed = False
		self.buffer = ""
	def write(self, data:str) -> None:
		if data:
			self.buffer += data
		self.flush()
	def flush(self) -> None:
		while "\n" in self.buffer:
			pos = self.buffer.find("\n")
			self.log.error(self.buffer[:pos])
			self.buffer = self.buffer[pos+1:]
	def forceFlush(self) -> None:
		self.log.error(self.buffer)
		self.buffer = ""
	def close(self) -> None:
		self.closed = True

class STDOutModule:
	log:Any
	closed:bool
	buffer:str
	def __init__(self) -> None:
		self.log    = Logger("Standard").getChild("Output")
		self.closed = False
		self.buffer = ""
	def write(self, data:str) -> None:
		if data:
			self.buffer += data
		self.flush()
	def flush(self) -> None:
		while "\n" in self.buffer:
			pos = self.buffer.find("\n")
			self.log.info(self.buffer[:pos])
			self.buffer = self.buffer[pos+1:]
	def forceFlush(self) -> None:
		self.log.info(self.buffer)
		self.buffer = ""
	def close(self) -> None:
		self.closed = True

class ModuleBase(metaclass=ABCMeta):
	@abstractmethod
	def emit(self, data:str) -> None: pass
	@abstractmethod
	def close(self) -> None: pass

class STDOutStreamingModule(ModuleBase):
	stream:Any
	def __init__(self, stream:Any):
		self.stream = stream
	def emit(self, data:str) -> None:
		if self.stream:
			try:
				self.stream.write(data)
				self.stream.flush()
			except:
				pass
	def close(self) -> None:
		self.stream = None

class FileStream(ModuleBase):
	fullPath:str
	stream:Any
	def __init__(self, fullPath:str):
		self.fullPath = fullPath
		self.stream   = None
		self.open()
	def open(self) -> None:
		try:
			os.makedirs( os.path.dirname(self.fullPath), 0o755 , True)
		except:
			traceback.print_exc()
		try:
			self.stream = open(self.fullPath, "at")
		except:
			traceback.print_exc()
	def write(self, data:str) -> None:
		if self.stream is not None:
			try:
				self.stream.write(data)
				self.stream.flush()
			except:
				traceback.print_exc()
	def emit(self, message:str) -> None:
		self.write(message)
	def close(self) -> None:
		if self.stream is not None:
			self.stream.close()
		self.stream = None

class RotatedFileStream(FileStream):
	maxBytes:int
	rotateDaily:bool
	maxBackup:Optional[int]
	lastRotate:Optional[str]
	lastFileSize:Optional[int]
	def __init__(self, fullPath:str, maxBytes:int=0, rotateDaily:bool=False, maxBackup:Optional[int]=None):
		super().__init__(fullPath)
		self.maxBytes     = maxBytes
		self.rotateDaily  = rotateDaily
		self.maxBackup    = maxBackup
		self.lastRotate   = None
		self.lastFileSize = None
	def emit(self, message:str) -> None:
		if self.stream is not None:
			if self.shouldRotate(message):
				self.doRotate()
			super().emit(message)
	def shouldRotate(self, message:str) -> bool:
		if self.lastRotate is None:
			self.lastRotate = datetime.utcnow().strftime("%D")
			return True
		if self.maxBytes > 0:
			if self.lastFileSize is None:
				self.stream.seek(0, 2)
				self.lastFileSize = self.stream.tell()
			self.lastFileSize += len(message)
			if self.lastFileSize >= self.maxBytes:
				return True
		if self.rotateDaily:
			if self.lastRotate != datetime.utcnow().strftime("%D"):
				self.lastRotate = datetime.utcnow().strftime("%D")
				return True
		return False
	def doRotate(self) -> None:
		if self.stream is not None:
			self.stream.close()
			self.stream = None
		try:
			self.shiftLogFiles()
		except:
			traceback.print_exc()
		self.open()
	def shiftLogFiles(self) -> None:
		def sortFileNums(a:str, b:str) -> int:
			def parseFileNum(e:str) -> int:
				if not e:
					return 0
				r = re.findall(r'^.*[^\.]\.([0-9]*)$', e)
				if r:
					return int(r[0])
				else:
					return 0
			return -1 if parseFileNum(a) > parseFileNum(b) else 1
		if len(glob("%s" % self.fullPath)) == 0:
			return
		files:List[str] = [self.fullPath] + glob("{}.[0-9]*".format(self.fullPath))
		files.sort(key=cmp_to_key(sortFileNums))
		tmpFiles:List[str] = []
		for file in files:
			if os.stat(file).st_size > 0:
				os.rename(file, "{}_tmp".format(file))
				tmpFiles.append("{}_tmp".format(file))
			else:
				os.remove(file)
		for i, file in list(enumerate(tmpFiles[::-1])):
			if self.maxBackup is not None and ( self.maxBackup == 0 or self.maxBackup < i ):
				os.remove(file)
			else:
				os.rename(file, "{}.{}".format( self.fullPath, str(i+1).zfill(3) ))

class DailyFileStream(FileStream):
	path:str
	prefix:str
	postfix:str
	dateFormat:str
	lastRotate:Optional[str]
	def __init__(self, logPath:str, prefix:str="", postfix:str="", dateFormat:str="%Y-%m-%d"):
		self.path       = logPath
		self.prefix     = prefix
		self.postfix    = postfix
		self.dateFormat = dateFormat
		self.lastRotate = None
		super().__init__(self.buildPath())
	def buildPath(self) -> str:
		return "{}/{}{}{}".format(
			self.path,
			self.prefix,
			datetime.utcnow().strftime(self.dateFormat),
			self.postfix,
		)
	def emit(self, message:str) -> None:
		if self.stream is not None:
			if self.shouldRotate(message):
				self.doRotate()
			super().emit(message)
	def shouldRotate(self, message:str) -> bool:
		if self.lastRotate is None or self.lastRotate != datetime.utcnow().strftime("%D"):
			self.lastRotate = datetime.utcnow().strftime("%D")
			return True
		return False
	def doRotate(self) -> None:
		if self.stream is not None:
			self.stream.close()
			self.stream = None
		self.fullPath = self.buildPath()
		self.open()

# Finalizing imports
from .logger import Logger

# Builtin modules
import re, os, traceback
from abc import ABCMeta, abstractmethod
from glob import glob
from datetime import datetime
from functools import cmp_to_key
from time import time
from typing import List, Any, TextIO, Optional
# Local modules
# Program
class ModuleBase(metaclass=ABCMeta):
	@abstractmethod
	def emit(self, data:str) -> None: pass
	@abstractmethod
	def close(self) -> None: pass

class STDOutStreamingModule(ModuleBase):
	def __init__(self, stream:Any):
		self.stream:Any = stream
	def emit(self, data:str) -> None:
		if self.stream:
			try:
				self.stream.write(data)
				self.stream.flush()
			except:
				pass
	def close(self) -> None:
		if self.stream:
			self.stream.close()
		self.stream = None

class STDErrModule:
	def __init__(self) -> None:
		self.log:Any =Logger("Standard").getChild("Error")
		self.closed:bool = False
		self.buffer:str = ""
	def write(self, data:str) -> None:
		if data:
			self.buffer += data
		self.flush()
	def flush(self) -> None:
		i:int
		skipLastLine:bool = self.buffer[-1:] != "\n"
		lines:List[str] = self.buffer.splitlines()
		line:str
		for i, line in enumerate(lines):
			if i == len(lines)-1 and skipLastLine:
				self.buffer = line
				break
			self.log.error(line)
	def close(self) -> None:
		self.closed = True

class STDOutModule:
	def __init__(self) -> None:
		self.log:Any = Logger("Standard").getChild("Output")
		self.closed:bool = False
		self.buffer:str = ""
	def write(self, data:str) -> None:
		if data:
			self.buffer += data
		self.flush()
	def flush(self) -> None:
		i:int
		line:str
		skipLastLine:bool = self.buffer[-1:] != "\n"
		lines:List[str] = self.buffer.splitlines()
		for i, line in enumerate(lines):
			if i == len(lines)-1 and skipLastLine:
				self.buffer = line
				break
			self.log.info(line)
	def close(self) -> None:
		self.closed = True

class FileStream(ModuleBase):
	def __init__(self, fullPath:str):
		self.fullPath:str = fullPath
		self.stream:Any = None
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
	def __init__(self, fullPath:str, maxBytes:int=0, rotateDaily:bool=False, maxBackup:Optional[int]=None):
		super().__init__(fullPath)
		self.maxBytes:int = maxBytes
		self.rotateDaily:bool = rotateDaily
		self.maxBackup:Optional[int] = maxBackup
		self.lastRotate:Optional[str] = None
		self.lastFileSize:Optional[int] = None
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
			q:int = parseFileNum(a)
			w:int = parseFileNum(b)
			if q > w:
				return -1
			else:
				return 1
		if len(glob("%s" % self.fullPath)) == 0:
			return
		files:List[str] = [self.fullPath] + glob("{}.[0-9]*".format(self.fullPath))
		files.sort(key=cmp_to_key(sortFileNums))
		tmpFiles:List[str] = []
		file:str
		for file in files:
			if os.stat(file).st_size > 0:
				os.rename(file, "{}_tmp".format(file))
				tmpFiles.append("{}_tmp".format(file))
			else:
				os.remove(file)
		i:int
		for i, file in list(enumerate(tmpFiles[::-1])):
			if self.maxBackup is not None and ( self.maxBackup == 0 or self.maxBackup < i ):
				os.remove(file)
			else:
				os.rename(file, "{}.{}".format( self.fullPath, str(i+1).zfill(3) ))

class DailyFileStream(FileStream):
	def __init__(self, logPath:str, prefix:str="", postfix:str="", dateFormat:str="%Y-%m-%d"):
		self.path:str = logPath
		self.prefix:str = prefix
		self.postfix:str = postfix
		self.dateFormat:str = dateFormat
		self.lastRotate:Optional[str] = None
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

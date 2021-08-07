# Builtin modules
from __future__ import annotations
import re, os, traceback
from glob import glob
from datetime import datetime, timezone
from typing import List, Tuple, Any, Optional
# Third party modules
# Local modules
from .abcs import T_ModuleBase
from .logger import Logger
# Program
class STDErrModule:
	log:Logger
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
	log:Logger
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

class STDOutStreamingModule(T_ModuleBase):
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

class FileStream(T_ModuleBase):
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
	lastRotate:Optional[int]
	lastFileSize:Optional[int]
	def __init__(self, fullPath:str, maxBytes:int=0, rotateDaily:bool=False, maxBackup:Optional[int]=None,
	useUTCTimezone:bool=True):
		super().__init__(fullPath)
		self.maxBytes                    = maxBytes
		self.rotateDaily                 = rotateDaily
		self.maxBackup                   = maxBackup
		self.lastRotate                  = None
		self.lastFileSize                = None
		self.timezone:Optional[timezone] = timezone.utc if useUTCTimezone else None
	def emit(self, message:str) -> None:
		if self.stream is not None:
			if self.shouldRotate(message):
				self.doRotate()
			super().emit(message)
	def shouldRotate(self, message:str) -> bool:
		if self.lastRotate is None:
			self.lastRotate = datetime.now(self.timezone).day
			return True
		if self.maxBytes > 0:
			if self.lastFileSize is None:
				self.stream.seek(0, 2)
				self.lastFileSize = self.stream.tell()
			self.lastFileSize += len(message)
			if self.lastFileSize >= self.maxBytes:
				return True
		if self.rotateDaily:
			if self.lastRotate != datetime.now(self.timezone).day:
				self.lastRotate = datetime.now(self.timezone).day
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
		def sortFileNums(e:str) -> Tuple[int, str]:
			r = re.findall(r'^.*[^\.]\.([0-9]*)$', e)
			if r:
				return int(r[0]), e
			else:
				return 0, e
		if os.path.isdir(os.path.dirname(self.fullPath)):
			return
		files:List[Tuple[int, str]] = sorted(list(map(sortFileNums, glob(self.fullPath+"*"))), key=lambda x: x[0], reverse=True)
		for n, f in files:
			os.rename(f, "{}.{:>03}".format(self.fullPath, n+1))

class DailyFileStream(FileStream):
	path:str
	prefix:str
	postfix:str
	dateFormat:str
	lastRotate:Optional[int]
	def __init__(self, path:str, prefix:str="", postfix:str="", dateFormat:str="%Y-%m-%d", useUTCTimezone:bool=True):
		self.path                        = path
		self.prefix                      = prefix
		self.postfix                     = postfix
		self.dateFormat                  = dateFormat
		self.lastRotate                  = None
		self.timezone:Optional[timezone] = timezone.utc if useUTCTimezone else None
		super().__init__(self.buildPath())
	def buildPath(self) -> str:
		return os.path.join(
			self.path,
			"{}{}{}".format(
				self.prefix,
				datetime.now(self.timezone).strftime(self.dateFormat),
				self.postfix,
			)
		)
	def emit(self, message:str) -> None:
		if self.stream is not None:
			if self.shouldRotate(message):
				self.doRotate()
			super().emit(message)
	def shouldRotate(self, message:str) -> bool:
		if self.lastRotate is None or self.lastRotate != datetime.now(self.timezone).day:
			self.lastRotate = datetime.now(self.timezone).day
			return True
		return False
	def doRotate(self) -> None:
		if self.stream is not None:
			self.stream.close()
			self.stream = None
		self.fullPath = self.buildPath()
		self.open()
		return None

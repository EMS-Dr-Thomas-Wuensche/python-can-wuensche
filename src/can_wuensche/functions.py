"""
Definition of functions
"""

import ctypes
from packaging import version
from sys import platform, maxsize
from can import CanInterfaceNotImplementedError, CanOperationError
from .constants import CPC_ERR_ASSIGNING_FUNCTION, CPC_ERR_SERVICE_NOT_SUPPORTED
from .structures import CPC_MSG_T, CPC_CAN_PARAMS_T, CPC_CAN_MSG_T, CPC_CANFD_MSG_T, CPC_INIT_PARAMS_T
from .util import _cpcErrToStr

_cpclib_dll              = None            # Loaded cpclib
_cpclib_func_decorator   = None            # ctypes function decorator (depends on the OS)
_cpclib_required_version = None            # Minimum required cpclib version (may be None)
_cpclib_is_64bit         = maxsize > 2**32 # Convenience variable
_cpclib_cpcconf_paths    = ["cpcconf.ini"] # Fallback if CPC_CreateChannelListJSON is not available

# Try to load the library with ctypes
if platform.startswith('linux'):
	_cpclib_func_decorator   = ctypes.CFUNCTYPE
	_cpclib_required_version = None
	_cpclib_cpcconf_paths    = ["cpcconf.ini", "/etc/cpcconf.ini"]
	libpaths = []
	if _cpclib_is_64bit:
		libpaths = [
			"libcpc.so",
			"/usr/local/lib/lib64/libcpc.so", 
			"/usr/local/lib64/libcpc.so"
		]
	else:
		libpaths = [
			"libcpc.so",
			"/usr/local/lib/lib32/libcpc.so",
			"/usr/local/lib/libcpc.so"
		]
	firstException = None
	for libpath in libpaths:
		try:
			_cpclib_dll = ctypes.CDLL(libpath)
		except Exception as e:
			# Remember the first exception so we can rethrow it
			if firstException is None:
				firstException = e
		if _cpclib_dll is not None:
			break
	if _cpclib_dll is None:
		if firstException is not None:
			raise CanInterfaceNotImplementedError("Couldn't load libcpc.so. Please note that an installed cdkl is required for the can_wuensche plugin. python-can natively supports socketcan. If you want to use our devices with socketcan, then please refer to the python-can documentation on how to use it.") from firstException
		else:
			raise CanInterfaceNotImplementedError("Couldn't load libcpc.so. Please note that an installed cdkl is required for the can_wuensche plugin. python-can natively supports socketcan. If you want to use our devices with socketcan, then please refer to the python-can documentation on how to use it.")
elif platform in ["win32", "cygwin"]:
	_cpclib_func_decorator = ctypes.WINFUNCTYPE
	# Windows requires WRK/WDK version 6.x or higher
	_cpclib_required_version = version.parse("3.0.2.1")
	_cpclib_cpcconf_paths = ["cpcconf.ini", "C:\\WINDOWS\\cpcconf.ini"]
	firstException = None
	for libpath in ["cpcwin.dll", "C:\\Windows\\System32\\cpcwin.dll"]:
		try:
			_cpclib_dll = ctypes.WinDLL(libpath)
		except Exception as e:
			if firstException is None:
				firstException = e
		if _cpclib_dll is not None:
			break
	if _cpclib_dll is None:
		if firstException is not None:
			raise CanInterfaceNotImplementedError("Couldn't load cpcwin.dll. Please note that an installed WRK/WDK is required. You can download it from https://www.ems-wuensche.com") from firstException
		else:
			raise CanInterfaceNotImplementedError("Couldn't load cpcwin.dll. Please note that an installed WRK/WDK is required. You can download it from https://www.ems-wuensche.com")
	# TODO
	#elif sys.platform.startswith('freebsd'):
	#elif sys.platform.startswith('aix'):
	#elif sys.platform == 'emscripten':
	#elif sys.platform == 'wasi':
	#elif sys.platform == 'darwin':
else:
	raise CanInterfaceNotImplementedError("can_wuensche: Platform '"+platform+"' is currently not supported.")

################################################################################
#                                   FUNCTIONS                                  #
################################################################################
# Declare some helper functions
def __can_wuensche_assign_error(*args, **kwargs):
	return CPC_ERR_ASSIGNING_FUNCTION
def __can_wuensche_not_implemented_error(*args, **kwargs):
	raise CanOperationError(message="The requested function is currently not implemented in python.", error_code=CPC_ERR_SERVICE_NOT_SUPPORTED)
def __can_wuensche_load_func(func_dec, params):
	try:
		return func_dec(*params)
	except AttributeError:
		return __can_wuensche_assign_error

# library related functions
CPC_GetLibVersion         = __can_wuensche_load_func(_cpclib_func_decorator(ctypes.c_char_p),(                               ("CPC_GetLibVersion",         _cpclib_dll), None))
CPC_CreateChannelListJSON = __can_wuensche_load_func(_cpclib_func_decorator(ctypes.POINTER(ctypes.c_char), ctypes.POINTER(ctypes.c_int)),( ("CPC_CreateChannelListJSON", _cpclib_dll), ((1, "length"),)))
CPC_DeleteChannelListJSON = __can_wuensche_load_func(_cpclib_func_decorator(ctypes.c_int, ctypes.POINTER(ctypes.c_char)),(   ("CPC_DeleteChannelListJSON", _cpclib_dll), ((1, "str"),)))
# interface and channel related functions
CPC_OpenChannel           = __can_wuensche_load_func(_cpclib_func_decorator(ctypes.c_int, ctypes.c_char_p),(                 ("CPC_OpenChannel",           _cpclib_dll), ((1, "channel"),)))
CPC_OpenChannelJSON       = __can_wuensche_load_func(_cpclib_func_decorator(ctypes.c_int, ctypes.c_char_p),(                 ("CPC_OpenChannelJSON",       _cpclib_dll), ((1, "json"),)))
CPC_CloseChannel          = __can_wuensche_load_func(_cpclib_func_decorator(ctypes.c_int, ctypes.c_int),(                    ("CPC_CloseChannel",          _cpclib_dll), ((1, "handle"),)))
CPC_CANInit               = __can_wuensche_load_func(_cpclib_func_decorator(ctypes.c_int, ctypes.c_int, ctypes.c_ubyte),(    ("CPC_CANInit",               _cpclib_dll), ((1, "handle"), (1, "confirm"))))
CPC_CANExit               = __can_wuensche_load_func(_cpclib_func_decorator(ctypes.c_int, ctypes.c_int, ctypes.c_ubyte),(    ("CPC_CANExit",               _cpclib_dll), ((1, "handle"), (1, "confirm"))))
# synchronous functions
CPC_GetCANState           = __can_wuensche_load_func(_cpclib_func_decorator(ctypes.c_int, ctypes.c_int),(                    ("CPC_GetCANState",           _cpclib_dll), ((1, "handle"),)))
CPC_GetInfo               = __can_wuensche_load_func(_cpclib_func_decorator(ctypes.c_char_p, ctypes.c_int, ctypes.c_ubyte, ctypes.c_ubyte),(("CPC_GetInfo",_cpclib_dll), ((1, "handle"), (1, "source"), (1, "type"))))
CPC_GetInitParamsPtr      = __can_wuensche_load_func(_cpclib_func_decorator(ctypes.POINTER(CPC_INIT_PARAMS_T), ctypes.c_int),( ("CPC_GetInitParamsPtr",      _cpclib_dll), ((1, "handle"),)))
CPC_ClearMSGQueue         = __can_wuensche_load_func(_cpclib_func_decorator(ctypes.c_int, ctypes.c_int),(                    ("CPC_ClearMSGQueue",         _cpclib_dll), ((1, "handle"),)))
CPC_BufferClear           = CPC_ClearMSGQueue
CPC_ClearCMDQueue         = __can_wuensche_load_func(_cpclib_func_decorator(ctypes.c_int, ctypes.c_int, ctypes.c_ubyte),(    ("CPC_ClearCMDQueue",         _cpclib_dll), ((1, "handle"), (1, "confirm"))))
CPC_GetMSGQueueCnt        = __can_wuensche_load_func(_cpclib_func_decorator(ctypes.c_int, ctypes.c_int),(                    ("CPC_GetMSGQueueCnt",        _cpclib_dll), ((1, "handle"),)))
CPC_GetBufferCnt          = CPC_GetMSGQueueCnt
CPC_SendMsg               = __can_wuensche_load_func(_cpclib_func_decorator(ctypes.c_int, ctypes.c_int, ctypes.c_ubyte, ctypes.POINTER(CPC_CAN_MSG_T)),(("CPC_SendMsg",     _cpclib_dll), ((1, "handle"), (1, "confirm"), (1, "pCANMsg"))))
CPC_SendXMsg              = __can_wuensche_load_func(_cpclib_func_decorator(ctypes.c_int, ctypes.c_int, ctypes.c_ubyte, ctypes.POINTER(CPC_CAN_MSG_T)),(("CPC_SendXMsg",    _cpclib_dll), ((1, "handle"), (1, "confirm"), (1, "pCANMsg"))))
CPC_SendRTR               = __can_wuensche_load_func(_cpclib_func_decorator(ctypes.c_int, ctypes.c_int, ctypes.c_ubyte, ctypes.POINTER(CPC_CAN_MSG_T)),(("CPC_SendRTR",     _cpclib_dll), ((1, "handle"), (1, "confirm"), (1, "pCANMsg"))))
CPC_SendXRTR              = __can_wuensche_load_func(_cpclib_func_decorator(ctypes.c_int, ctypes.c_int, ctypes.c_ubyte, ctypes.POINTER(CPC_CAN_MSG_T)),(("CPC_SendXRTR",    _cpclib_dll), ((1, "handle"), (1, "confirm"), (1, "pCANMsg"))))
CPC_SendMsgFD             = __can_wuensche_load_func(_cpclib_func_decorator(ctypes.c_int, ctypes.c_int, ctypes.c_ubyte, ctypes.POINTER(CPC_CANFD_MSG_T)),(("CPC_SendMsgFD", _cpclib_dll), ((1, "handle"), (1, "confirm"), (1, "pCANMsg"))))
CPC_Control               = __can_wuensche_load_func(_cpclib_func_decorator(ctypes.c_int, ctypes.c_int, ctypes.c_ushort),(   ("CPC_Control",               _cpclib_dll), ((1, "handle"), (1, "value"))))
CPC_WaitForMType          = __can_wuensche_load_func(_cpclib_func_decorator(ctypes.POINTER(CPC_MSG_T), ctypes.c_int, ctypes.c_int),(("CPC_WaitForMType",     _cpclib_dll), ((1, "handle"), (1, "mtype"))))
#CPC_DecodeErrorMsg        = __can_wuensche_load_func(_cpclib_func_decorator(ctypes.c_char_p, ctypes.c_int),(                 ("CPC_DecodeErrorMsg",        _cpclib_dll), ((1, "error"),)))
CPC_DecodeErrorMsg        = _cpcErrToStr
# functions for the asynchronous interface
# TODO
##func_decorator(ctypes.c_voidp, ctypes.c_int, ctypes.POINTER(CPC_MSG)), "handle", "pCPCMsg"),
##func_decorator(ctypes.c_voidp, ctypes.c_int, ctypes.POINTER(CPC_MSG), ctypes.c_void_p), "handle", "pCPCMsg", "customPointer"),
##func_decorator(ctypes.c_int, ctypes.c_int), "handle", "handler"),
##func_decorator(ctypes.c_int, ctypes.c_int), "handle", "handler"),
CPC_AddHandler            = __can_wuensche_not_implemented_error
CPC_RemoveHandler         = __can_wuensche_not_implemented_error
CPC_AddHandlerEx          = __can_wuensche_not_implemented_error
CPC_RemoveHandlerEx       = __can_wuensche_not_implemented_error
##int   CALL_CONV CPC_AddHandler        (int handle, void (CALL_CONV *handler)(int handle, const CPC_MSG_T* pCPCMsg));
##int   CALL_CONV CPC_RemoveHandler     (int handle, void (CALL_CONV *handler)(int handle, const CPC_MSG_T* pCPCMsg));
##int   CALL_CONV CPC_AddHandlerEx      (int handle, void (CALL_CONV *handlerEx)(int handle, const CPC_MSG_T* pCPCMsg, void *customPointer), void *customPointer);
##int   CALL_CONV CPC_RemoveHandlerEx   (int handle, void (CALL_CONV *handlerEx)(int handle, const CPC_MSG_T* pCPCMsg, void *customPointer));
CPC_WaitForEvent          = __can_wuensche_load_func(_cpclib_func_decorator(ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_ubyte),( ("CPC_WaitForEvent",       _cpclib_dll), ((1, "handle"), (1, "timeout"), (1, "event"))))
CPC_Handle                = __can_wuensche_load_func(_cpclib_func_decorator(ctypes.POINTER(CPC_MSG_T), ctypes.c_int),( ("CPC_Handle",       _cpclib_dll), ((1, "handle"),)))
CPC_RequestCANParams      = __can_wuensche_load_func(_cpclib_func_decorator(ctypes.c_int, ctypes.c_int, ctypes.c_ubyte),( ("CPC_RequestCANParams",       _cpclib_dll), ((1, "handle"), (1, "confirm"))))
CPC_RequestCANState       = __can_wuensche_load_func(_cpclib_func_decorator(ctypes.c_int, ctypes.c_int, ctypes.c_ubyte),( ("CPC_RequestCANState",       _cpclib_dll), ((1, "handle"), (1, "confirm"))))
CPC_RequestInfo           = __can_wuensche_load_func(_cpclib_func_decorator(ctypes.c_int, ctypes.c_int, ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_ubyte),(("CPC_RequestInfo",_cpclib_dll), ((1, "handle"), (1, "confirm"), (1, "source"), (1, "type"))))
# currently not implemented
CPC_GetCANParams          = _cpclib_func_decorator(ctypes.POINTER(CPC_CAN_PARAMS_T), ctypes.c_int),( ("CPC_GetCANParams",       _cpclib_dll), (1, "handle"))
CPC_GetBusload            = _cpclib_func_decorator(ctypes.c_int, ctypes.c_int),(                 ("CPC_GetBusload",       _cpclib_dll), (1, "handle"))
CPC_ReadMsg               = _cpclib_func_decorator(ctypes.c_int, ctypes.c_int, ctypes.POINTER(CPC_CAN_MSG_T)),( ("CPC_ReadMsg",       _cpclib_dll), (1, "handle"), (2,"pCANMsg"))
CPC_Filter                = _cpclib_func_decorator(ctypes.c_int, ctypes.c_int, ctypes.c_short, ctypes.c_ushort, ctypes.c_ushort),( ("CPC_Filter", _cpclib_dll), (1, "handle"), (1), (1), (1))

#_RegisteredCPCHandlers = None
#_RegisteredCPCExHandlers = None

#def CPC_Handle(handle):
#	msg = CPC_Handle_func(handle)
#	if (not msg) or (not msg[0]):
#		return msg
#	if _RegisteredCPCHandlers is not None:
#		if handle in _RegisteredCPCHandlers:
#			for handler in _RegisteredCPCHandlers[handle]:
#				handler(handle, msg)
#	if _RegisteredCPCExHandlers is not None:
#		if handle in _RegisteredCPCExHandlers:
#			for handler, data in _RegisteredCPCExHandlers[handle]:
#				handler(handle, msg, data)
#	return msg

#def CPC_AddHandler(handle, handler):
#	global _RegisteredCPCHandlers
#	if _RegisteredCPCHandlers is None:
#		_RegisteredCPCHandlers = { handle : [handler] }
#	elif handle not in _RegisteredCPCHandlers:
#		_RegisteredCPCHandlers[handle] = [handler]
#	elif handler not in _RegisteredCPCHandlers[handle]:
#		_RegisteredCPCHandlers[handle].append(handler)
#	else:
#		return 0 # Already present
#	return 0 # Successfully added

#def CPC_RemoveHandler(handle, handler):
#	global _RegisteredCPCHandlers
#	if _RegisteredCPCHandlers is None:
#		return 0 # Nothing to do
#	elif handle not in _RegisteredCPCHandlers:
#		return 0 # Nothing to do
#	elif handler not in _RegisteredCPCHandlers[handle]:
#		return 0 # Nothing to do
#	else:
#		if len(_RegisteredCPCHandlers[handle]) > 1:
#			_RegisteredCPCHandlers[handle].remove(handler)
#		else:
#			_RegisteredCPCHandlers.remove(handle)
#	return 0 # Successfully removed

#def CPC_AddHandlerEx(handle, handler, customData):
#	global _RegisteredCPCExHandlers
#	if _RegisteredCPCExHandlers is None:
#		_RegisteredCPCExHandlers = { handle : [(handler, customData)] }
#	elif handle not in _RegisteredCPCExHandlers:
#		_RegisteredCPCExHandlers[handle] = [(handler, customData)]
#	else:
#		for h, d in _RegisteredCPCExHandlers[handle]:
#			if h == handler:
#				return 0 # Already present
#		_RegisteredCPCExHandlers[handle].append((handler, customData))
#		return 0 # Successfully added

#def CPC_RemoveHandlerEx(handle, handler, customData):
#	global _RegisteredCPCExHandlers
#	if _RegisteredCPCExHandlers is None:
#		return 0
#	elif handle not in _RegisteredCPCExHandlers:
#		return 0
#	else:
#		for h, d in _RegisteredCPCExHandlers[handle]:
#			if h == handler:
#				if len(_RegisteredCPCExHandlers[handle]) > 1:
#					_RegisteredCPCExHandlers[handle].remove((h, d))
#				else:
#					_RegisteredCPCExHandlers.remove(handle)
#				return 0
#	return 0 # Nothing to do

################################################################################
#                        Get and verify library version                        #
################################################################################
_cpclib_version_string = ""
_cpclib_version = None
if CPC_GetLibVersion == __can_wuensche_assign_error:
	# CPC_GetLibVersion might not be implemented on linux but must be implemented on windows
	#if platform in ["win32", "cygwin"]:
	if not platform.startswith('linux'):
		raise CanInterfaceNotImplementedError(message=_cpcErrToStr(error_code=CPC_ERR_ASSIGNING_FUNCTION), error_code=CPC_ERR_ASSIGNING_FUNCTION)
	elif _cpclib_required_version is not None:
		raise CanInterfaceNotImplementedError(message=_cpcErrToStr(error_code=CPC_ERR_ASSIGNING_FUNCTION), error_code=CPC_ERR_ASSIGNING_FUNCTION)
elif _cpclib_required_version is not None:
	# Get the library version.
	_cpclib_version_string = CPC_GetLibVersion()
	if not _cpclib_version_string:
		raise CanInterfaceNotImplementedError(message="Failed to aquire library version.")
	elif isinstance(_cpclib_version_string, int):
		raise CanInterfaceNotImplementedError(message="Failed to aquire library version. Error: " + _cpcErrToStr(error_code=_cpclib_version_string), error_code=_cpclib_version_string)

	_cpclib_version_string = _cpclib_version_string.decode("ascii")
	if (not _cpclib_version_string) or (len(_cpclib_version_string) < 1):
		raise CanInterfaceNotImplementedError(mesage="Failed to aquire library version. CPC_GetLibVersion returned an empty string.")
	if _cpclib_version_string.endswith("d"):
		# Older debug builds may contain a "d" at the end. This does not conform with PEP440.
		# To avoid this, we turn them into a local version (unless it's already one).
		if '+' not in _cpclib_version_string:
			_cpclib_version_string = _cpclib_version_string[:-1] + "+d"

	# Parse the version string
	try:
		_cpclib_version = version.parse(_cpclib_version_string)
	except Exception as e:
		raise CanInterfaceNotImplementedError("can_wuensche: Failed to parse version string from installed library: " + _cpclib_version_string) from e
	if _cpclib_version is None:
		raise CanInterfaceNotImplementedError("can_wuensche: Failed to parse version string from installed library: " + _cpclib_version_string)
	elif _cpclib_version < _cpclib_required_version:
		raise CanInterfaceNotImplementedError("can_wuensche: Installed runtime/development kit is too old: Library version is " + str(_cpclib_version) + " but required version is " + str(_cpclib_required_version) + ". Please visit https://www.ems-wuensche.com to download a newer version with python support.")

################################################################################
#                          Verify essential functions                          #
################################################################################
# Verify functions that must be available on all platforms
if __can_wuensche_assign_error in (
		CPC_OpenChannel, CPC_CloseChannel,
		CPC_GetInitParamsPtr, CPC_CANInit, CPC_Control, 
		CPC_Handle, CPC_SendMsg, CPC_SendMsgFD):
	raise CanInterfaceNotImplementedError(message=_cpcErrToStr(error_code=CPC_ERR_ASSIGNING_FUNCTION), error_code=CPC_ERR_ASSIGNING_FUNCTION)

"""
Definition of structures and unions
"""

# Global imports
import ctypes
from sys import platform

# Local imports
from .constants import CPC_MSG_LEN

class CPC_CAN_MSG(ctypes.Structure):
	_pack_ = 1
	_fields_ = [("id", ctypes.c_uint32),
				("length", ctypes.c_ubyte),
				("msg", ctypes.c_ubyte * 8)]
CPC_CAN_MSG_T = CPC_CAN_MSG

class CPC_CANFD_MSG(ctypes.Structure):
	_pack_ = 1
	_fields_ = [("id", ctypes.c_uint32),
				("length", ctypes.c_ubyte),
				("flags", ctypes.c_ubyte),
				("msg", ctypes.c_ubyte * 64)]
CPC_CANFD_MSG_T = CPC_CANFD_MSG

class CPC_SJA1000_PARAMS(ctypes.Structure):
	_pack_ = 1
	_fields_ = [("mode", ctypes.c_ubyte),
				("acc_code0", ctypes.c_ubyte),
				("acc_code1", ctypes.c_ubyte),
				("acc_code2", ctypes.c_ubyte),
				("acc_code3", ctypes.c_ubyte),
				("acc_mask0", ctypes.c_ubyte),
				("acc_mask1", ctypes.c_ubyte),
				("acc_mask2", ctypes.c_ubyte),
				("acc_mask3", ctypes.c_ubyte),
				("btr0", ctypes.c_ubyte),
				("btr1", ctypes.c_ubyte),
				("outp_contr", ctypes.c_ubyte)]
CPC_SJA1000_PARAMS_T = CPC_SJA1000_PARAMS

class CPC_LPC546XX_PARAMS(ctypes.Structure):
	_pack_ = 1
	_fields_ = [("dbtp", ctypes.c_uint32),
				("test", ctypes.c_uint32),
				("cccr", ctypes.c_uint32),
				("nbtp", ctypes.c_uint32),
				("psr", ctypes.c_uint32),
				("tdcr", ctypes.c_uint32),
				("gfc", ctypes.c_uint32),
				("sidfc", ctypes.c_uint32),
				("xidfc", ctypes.c_uint32),
				("xidam", ctypes.c_uint32),
				("cclk", ctypes.c_uint32)]
CPC_LPC546XX_PARAMS_T = CPC_LPC546XX_PARAMS

class CPC_GENERIC_BAUDRATE_PARAMS(ctypes.Structure):
	_pack_ = 1
	_fields_ = [("tseg1", ctypes.c_uint16),
				("tseg2", ctypes.c_uint16),
				("brp", ctypes.c_uint16),
				("sjw", ctypes.c_uint16)]
CPC_GENERIC_BAUDRATE_PARAMS_T = CPC_GENERIC_BAUDRATE_PARAMS

class CPC_GENERIC_PARAMS(ctypes.Structure):
	_pack_ = 1
	_fields_ = [("config", ctypes.c_uint32),
				("can_clk", ctypes.c_uint32),
				("n", CPC_GENERIC_BAUDRATE_PARAMS_T),
				("d", CPC_GENERIC_BAUDRATE_PARAMS_T),
				("reserved", ctypes.c_uint32 * 5)]
CPC_GENERIC_PARAMS_T = CPC_GENERIC_PARAMS

class CPC_M16C_BASIC_PARAMS(ctypes.Structure):
	_pack_ = 1
	_fields_ = [("con0",          ctypes.c_ubyte),
				("con1",          ctypes.c_ubyte),
				("ctrl0",         ctypes.c_ubyte),
				("ctrl1",         ctypes.c_ubyte),
				("clk",           ctypes.c_ubyte),
				("acc_std_code0", ctypes.c_ubyte),
				("acc_std_code1", ctypes.c_ubyte),
				("acc_ext_code0", ctypes.c_ubyte),
				("acc_ext_code1", ctypes.c_ubyte),
				("acc_ext_code2", ctypes.c_ubyte),
				("acc_ext_code3", ctypes.c_ubyte),
				("acc_std_mask0", ctypes.c_ubyte),
				("acc_std_mask1", ctypes.c_ubyte),
				("acc_ext_mask0", ctypes.c_ubyte),
				("acc_ext_mask1", ctypes.c_ubyte),
				("acc_ext_mask2", ctypes.c_ubyte),
				("acc_ext_mask3", ctypes.c_ubyte)]
CPC_M16C_BASIC_PARAMS_T = CPC_M16C_BASIC_PARAMS

class _CPC_CAN_PARAMS_PARAMS(ctypes.Union):
	_pack_ = 1
	_fields_ = [("m16c_basic", CPC_M16C_BASIC_PARAMS_T),
				("sja1000", CPC_SJA1000_PARAMS_T),
				("lpc546xx", CPC_LPC546XX_PARAMS_T),
				("generic", CPC_GENERIC_PARAMS_T)]

class CPC_CAN_PARAMS(ctypes.Structure):
	_pack_ = 1
	_fields_ = [("cc_type", ctypes.c_ubyte),
				("cc_params", _CPC_CAN_PARAMS_PARAMS)]
CPC_CAN_PARAMS_T = CPC_CAN_PARAMS

class CPC_CHAN_PARAMS(ctypes.Structure):
	_pack_ = 1
	_fields_ = [("fd", ctypes.c_int)]
CPC_CHAN_PARAMS_T = CPC_CHAN_PARAMS

_CPC_INIT_PARAMS_FIELDS_WIN = [("canparams", CPC_CAN_PARAMS_T)]
_CPC_INIT_PARAMS_FIELDS_LINUX = [("chanparams", CPC_CHAN_PARAMS_T), ("canparams", CPC_CAN_PARAMS_T)]

class CPC_INIT_PARAMS(ctypes.Structure):
	_pack_ = 1
	if platform in ["win32", "cygwin"]:
		_fields_ = _CPC_INIT_PARAMS_FIELDS_WIN
	elif platform.startswith('linux'):
		_fields_ = _CPC_INIT_PARAMS_FIELDS_LINUX
	else:
		# TODO
		_fields_ = _CPC_INIT_PARAMS_FIELDS_LINUX
CPC_INIT_PARAMS_T = CPC_INIT_PARAMS

class CPC_CONFIRM(ctypes.Structure):
	_pack_ = 1
	_fields_ = [("result", ctypes.c_ubyte),
				("pad", ctypes.c_ubyte * 3),
				("ts_sec", ctypes.c_uint),
				("ts_nsec", ctypes.c_uint)]
CPC_CONFIRM_T = CPC_CONFIRM

class CPC_INFO(ctypes.Structure):
	_pack_ = 1
	_fields_ = [("source", ctypes.c_ubyte),
				("type", ctypes.c_ubyte),
				("msg", ctypes.c_char * (CPC_MSG_LEN - 2))]
CPC_INFO_T = CPC_INFO

class CPC_OVERRUN(ctypes.Structure):
	_pack_ = 1
	_fields_ = [("event", ctypes.c_ubyte),
				("count", ctypes.c_ubyte)]
CPC_OVERRUN_T = CPC_OVERRUN

class CPC_SJA1000_CAN_ERROR(ctypes.Structure):
	_pack_ = 1
	_fields_ = [("ecc", ctypes.c_ubyte),
				("rxerr", ctypes.c_ubyte),
				("txerr", ctypes.c_ubyte)]
CPC_SJA1000_CAN_ERROR_T = CPC_SJA1000_CAN_ERROR

class CPC_LPC546XX_CAN_ERROR(ctypes.Structure):
	_pack_ = 1
	_fields_ = [("psr", ctypes.c_uint32),
				("ecr", ctypes.c_uint32)]
CPC_LPC546XX_CAN_ERROR_T = CPC_LPC546XX_CAN_ERROR

class _CPC_CAN_ERROR_REGS(ctypes.Union):
	_pack_ = 1
	_fields_ = [("sja1000", CPC_SJA1000_CAN_ERROR_T),
				("lpc546xx", CPC_LPC546XX_CAN_ERROR_T)]

class _CPC_CAN_ERROR_CC(ctypes.Structure):
	_pack_ = 1
	_fields_ = [("cc_type", ctypes.c_ubyte),
				("regs", _CPC_CAN_ERROR_REGS)]

class CPC_CAN_ERROR(ctypes.Structure):
	_pack_ = 1
	_fields_ = [("ecode", ctypes.c_ubyte),
				("cc", _CPC_CAN_ERROR_CC)]
CPC_CAN_ERROR_T = CPC_CAN_ERROR

class CPC_CAN_ERROR_COUNTER(ctypes.Structure):
	_pack_ = 1
	_fields_ = [("rx", ctypes.c_ubyte),
				("tx", ctypes.c_ubyte)]
CPC_CAN_ERROR_COUNTER_T = CPC_CAN_ERROR_COUNTER

class _CPC_MSG_MSG(ctypes.Union):
	_pack_ = 1
	_fields_ = [("generic", ctypes.c_ubyte * CPC_MSG_LEN),
				("canmsg", CPC_CAN_MSG_T),
				("canfdmsg", CPC_CANFD_MSG_T),
				("canparams", CPC_CAN_PARAMS_T),
				("confirmation", CPC_CONFIRM_T),
				("info", CPC_INFO_T),
				("overrun", CPC_OVERRUN_T),
				("error", CPC_CAN_ERROR_T),
				("err_counter", CPC_CAN_ERROR_COUNTER_T),
				("busload", ctypes.c_ubyte),
				("canstate", ctypes.c_ubyte)]

class CPC_MSG(ctypes.Structure):
	_pack_ = 1
	_fields_ = [("type", ctypes.c_ubyte),
				("length", ctypes.c_ubyte),
				("msgid", ctypes.c_ubyte),
				("ts_sec", ctypes.c_uint32),
				("ts_nsec", ctypes.c_uint32),
				("msg", _CPC_MSG_MSG)]
CPC_MSG_T = CPC_MSG

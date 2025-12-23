"""
"""

from math import ceil
from can import BitTiming, BitTimingFd
from .constants import *
from .structures import CPC_CAN_PARAMS_T

def _create_can_params_from_timing(timing : "BitTiming | BitTimingFd", controller : int = GENERIC_CAN_CONTR) -> CPC_CAN_PARAMS_T:
	if timing is None:
		raise ValueError("Can't create can parameters from timing: No timing given")
	elif isinstance(timing, BitTiming):
		if controller == GENERIC_CAN_CONTR:
			can_params = CPC_CAN_PARAMS_T()
			can_params.cc_type                   = GENERIC_CAN_CONTR
			can_params.cc_params.generic.config  = CPC_GENERICCONF_CLASSIC
			can_params.cc_params.generic.can_clk = timing.f_clock
			can_params.cc_params.generic.n.tseg1 = timing.tseg1
			can_params.cc_params.generic.n.tseg2 = timing.tseg2
			can_params.cc_params.generic.n.brp   = timing.brp
			can_params.cc_params.generic.n.sjw   = timing.sjw
			can_params.cc_params.generic.d.tseg1 = timing.tseg1
			can_params.cc_params.generic.d.tseg2 = timing.tseg2
			can_params.cc_params.generic.d.brp   = timing.brp
			can_params.cc_params.generic.d.sjw   = timing.sjw
			return can_params
		elif controller == SJA1000:
			if timing.f_clock != 8000000:
				timing = timing.recreate_with_f_clock(8000000)
			can_params = CPC_CAN_PARAMS_T()
			can_params.cc_type                      = SJA1000
			can_params.cc_params.sja1000.mode       = 0x00
			can_params.cc_params.sja1000.acc_code0  = 0x55
			can_params.cc_params.sja1000.acc_code1  = 0x55
			can_params.cc_params.sja1000.acc_code2  = 0x55
			can_params.cc_params.sja1000.acc_code3  = 0x55
			can_params.cc_params.sja1000.acc_mask0  = 0xFF
			can_params.cc_params.sja1000.acc_mask1  = 0xFF
			can_params.cc_params.sja1000.acc_mask2  = 0xFF
			can_params.cc_params.sja1000.acc_mask3  = 0xFF
			can_params.cc_params.sja1000.btr0       = timing.btr0
			can_params.cc_params.sja1000.btr1       = timing.btr1
			can_params.cc_params.sja1000.outp_contr = 0xDA
			return can_params
		elif controller == LPC546XX:
			can_params = CPC_CAN_PARAMS_T()
			can_params.cc_type                   = LPC546XX
			can_params.cc_params.lpc546xx.dbtp   = 0
			can_params.cc_params.lpc546xx.test   = 0
			can_params.cc_params.lpc546xx.cccr   = 0
			can_params.cc_params.lpc546xx.nbtp   = ((timing.tseg2-1) << 0) | ((timing.tseg1-1) << 8) | ((timing.brp-1) << 16) | ((timing.sjw-1) << 25)
			can_params.cc_params.lpc546xx.psr    = 0
			can_params.cc_params.lpc546xx.tdcr   = 0
			can_params.cc_params.lpc546xx.gfc    = 0
			can_params.cc_params.lpc546xx.sidfc  = 0
			can_params.cc_params.lpc546xx.xidfc  = 0
			can_params.cc_params.lpc546xx.xidam  = 0
			can_params.cc_params.lpc546xx.cclk   = timing.f_clock
			return can_params
		else:
			raise ValueError(_cpcErrToStr(CPC_ERR_WRONG_CONTROLLER_TYPE))
	elif isinstance(timing, BitTimingFd):
		if controller == GENERIC_CAN_CONTR:
			can_params = CPC_CAN_PARAMS_T()
			can_params.cc_type                   = GENERIC_CAN_CONTR
			can_params.cc_params.generic.config  = CPC_GENERICCONF_FD
			can_params.cc_params.generic.can_clk = timing.f_clock
			can_params.cc_params.generic.n.tseg1 = timing.nom_tseg1
			can_params.cc_params.generic.n.tseg2 = timing.nom_tseg2
			can_params.cc_params.generic.n.brp   = timing.nom_brp
			can_params.cc_params.generic.n.sjw   = timing.nom_sjw
			can_params.cc_params.generic.d.tseg1 = timing.data_tseg1
			can_params.cc_params.generic.d.tseg2 = timing.data_tseg2
			can_params.cc_params.generic.d.brp   = timing.data_brp
			can_params.cc_params.generic.d.sjw   = timing.data_sjw
			return can_params
		elif controller == LPC546XX:
			can_params = CPC_CAN_PARAMS_T()
			can_params.cc_type                   = LPC546XX
			can_params.cc_params.lpc546xx.dbtp   = ((timing.data_sjw-1) << 0) | ((timing.data_tseg2-1) << 4) | ((timing.data_tseg1-1) << 8) | ((timing.data_brp-1) << 16) | (1 << 23)
			can_params.cc_params.lpc546xx.test   = 0
			can_params.cc_params.lpc546xx.cccr   = CAN_CCCR_FDOE | CAN_CCCR_BRSE
			can_params.cc_params.lpc546xx.nbtp   = ((timing.nom_tseg2-1) << 0) | ((timing.nom_tseg1-1) << 8) | ((timing.nom_brp-1) << 16) | ((timing.nom_sjw-1) << 25)
			can_params.cc_params.lpc546xx.psr    = 0
			can_params.cc_params.lpc546xx.tdcr   = round((3 + timing.data_tseg1 + timing.data_tseg2) / 2) << 8
			can_params.cc_params.lpc546xx.gfc    = 0
			can_params.cc_params.lpc546xx.sidfc  = 0
			can_params.cc_params.lpc546xx.xidfc  = 0
			can_params.cc_params.lpc546xx.xidam  = 0
			can_params.cc_params.lpc546xx.cclk   = timing.f_clock
			return can_params
		elif controller == SJA1000:
			raise ValueError("Can't create can parameters: SJA1000 does not support CAN-FD.")
		else:
			raise ValueError(_cpcErrToStr(CPC_ERR_WRONG_CONTROLLER_TYPE))
	else:
		raise ValueError("Can't create can parameters from timing: timing must be an instance of BitTiming or BitTimingFd")

def _create_timing_from_can_params(can_params : CPC_CAN_PARAMS_T) -> "BitTiming | BitTimingFd":
	if can_params is None:
		raise ValueError("Can't create timing from can parameters: No can parameters given")
	elif _can_params_is_fd(can_params=can_params):
		if can_params.cc_type == GENERIC_CAN_CONTR:
			return BitTimingFd(
				f_clock    = can_params.cc_params.generic.can_clk,
				nom_tseg1  = can_params.cc_params.generic.n.tseg1,
				nom_tseg2  = can_params.cc_params.generic.n.tseg2,
				nom_brp    = can_params.cc_params.generic.n.brp,
				nom_sjw    = can_params.cc_params.generic.n.sjw,
				data_tseg1 = can_params.cc_params.generic.d.tseg1,
				data_tseg2 = can_params.cc_params.generic.d.tseg2,
				data_brp   = can_params.cc_params.generic.d.brp,
				data_sjw   = can_params.cc_params.generic.d.sjw
			)
		elif can_params.cc_type == LPC546XX:
			return BitTimingFd(
				f_clock    = can_params.cc_params.lpc546xx.cclk,
				nom_tseg1  = ((can_params.cc_params.lpc546xx.nbtp >>  8) & 0xff) + 1,
				nom_tseg2  = ((can_params.cc_params.lpc546xx.nbtp >>  0) & 0x7f) + 1,
				nom_brp    = ((can_params.cc_params.lpc546xx.nbtp >> 16) & 0x1ff)+ 1,
				nom_sjw    = ((can_params.cc_params.lpc546xx.nbtp >> 25) & 0x7f) + 1,
				data_tseg1 = ((can_params.cc_params.lpc546xx.dbtp >>  8) & 0x1f) + 1,
				data_tseg2 = ((can_params.cc_params.lpc546xx.dbtp >>  4) & 0x0f) + 1,
				data_brp   = ((can_params.cc_params.lpc546xx.dbtp >> 16) & 0x1f) + 1,
				data_sjw   = ((can_params.cc_params.lpc546xx.dbtp >>  0) & 0x0f) + 1
			)
		# SJA1000 does not support CAN-FD
		#elif can_params.cc_type == SJA1000:
		else:
			raise ValueError(_cpcErrToStr(CPC_ERR_WRONG_CONTROLLER_TYPE))
	else:
		if can_params.cc_type == GENERIC_CAN_CONTR:
			return BitTiming(
				f_clock = can_params.cc_params.generic.can_clk,
				tseg1   = can_params.cc_params.generic.n.tseg1,
				tseg2   = can_params.cc_params.generic.n.tseg2,
				brp     = can_params.cc_params.generic.n.brp,
				sjw     = can_params.cc_params.generic.n.sjw
			)
		elif can_params.cc_type == LPC546XX:
			return BitTiming(
				f_clock = can_params.cc_params.lpc546xx.cclk,
				tseg1   = ((can_params.cc_params.lpc546xx.nbtp >>  8) & 0xff) + 1,
				tseg2   = ((can_params.cc_params.lpc546xx.nbtp >>  0) & 0x7f) + 1,
				brp     = ((can_params.cc_params.lpc546xx.nbtp >> 16) & 0x1ff)+ 1,
				sjw     = ((can_params.cc_params.lpc546xx.nbtp >> 25) & 0x7f) + 1
			)
		elif can_params.cc_type == SJA1000:
			return BitTiming.from_registers(f_clock=8_000_000, btr0=can_params.cc_params.sja1000.btr0, btr1=can_params.cc_params.sja1000.btr1)
		else:
			raise ValueError(_cpcErrToStr(CPC_ERR_WRONG_CONTROLLER_TYPE))

def _create_can_params(controller : int = GENERIC_CAN_CONTR, **kwargs) -> CPC_CAN_PARAMS_T:
	timing = kwargs.get("timing", None)
	if timing is not None:
		return _create_can_params_from_timing(timing=timing, controller=controller)

	fd      = kwargs.get("fd", None)
	f_clock = kwargs.get("f_clock",     None)

	# FD
	if (fd is None) or (fd):
		nom_brp    = kwargs.get("nom_brp",    None)
		nom_tseg1  = kwargs.get("nom_tseg1",  None)
		nom_tseg2  = kwargs.get("nom_tseg2",  None)
		nom_sjw    = kwargs.get("nom_sjw",    None)
		data_brp   = kwargs.get("data_brp",   None)
		data_tseg1 = kwargs.get("data_tseg1", None)
		data_tseg2 = kwargs.get("data_tseg2", None)
		data_sjw   = kwargs.get("data_sjw",   None)
		# Try the normal constructor first
		try:
			timing = BitTimingFd(
				f_clock=f_clock, 
				nom_brp=nom_brp, 
				nom_tseg1=nom_tseg1, 
				nom_tseg2=nom_tseg2, 
				nom_sjw=nom_sjw, 
				data_brp=data_brp, 
				data_tseg1=data_tseg1, 
				data_tseg2=data_tseg2, 
				data_sjw=data_sjw
			)
		except (TypeError, ValueError):
			pass
		if timing is not None:
			return _create_can_params_from_timing(timing=timing, controller=controller)
		# Try from sample point
		nom_bitrate       = kwargs.get("nom_bitrate",       None)
		nom_sample_point  = kwargs.get("nom_sample_point",  None)
		data_bitrate      = kwargs.get("data_bitrate",      None)
		data_sample_point = kwargs.get("data_sample_point", None)
		try:
			timing = BitTimingFd.from_sample_point(
				f_clock=f_clock, 
				nom_bitrate=nom_bitrate, 
				nom_sample_point=nom_sample_point, 
				data_bitrate=data_bitrate, 
				data_sample_point=data_sample_point
			)
		except (TypeError, ValueError):
			pass
		if timing is not None:
			return _create_can_params_from_timing(timing=timing, controller=controller)
		# Try from bitrate and segments
		try:
			timing = BitTimingFd.from_bitrate_and_segments(
				f_clock=f_clock, 
				nom_bitrate=nom_bitrate, 
				nom_tseg1=nom_tseg1, 
				nom_tseg2=nom_tseg2, 
				nom_sjw=nom_sjw, 
				data_bitrate=data_bitrate, 
				data_tseg1=data_tseg1, 
				data_tseg2=data_tseg2, 
				data_sjw=data_sjw
			)
		except (TypeError, ValueError):
			pass
		if timing is not None:
			return _create_can_params_from_timing(timing=timing, controller=controller)
		# Try our default values
		try:
			timing = _baudToGenericTiming(
				f_clock=f_clock, 
				nom_bitrate=nom_bitrate, 
				data_bitrate=data_bitrate
			)
		except Exception:
			pass
		if timing is not None:
			return _create_can_params_from_timing(timing=timing, controller=controller)
	# NON-FD
	# Don't use "elif" (in case fd is None)
	if (fd is None) or (not fd):
		brp         = kwargs.get("brp",         None)
		tseg1       = kwargs.get("tseg1",       None)
		tseg2       = kwargs.get("tseg2",       None)
		sjw         = kwargs.get("sjw",         None)
		nof_samples = kwargs.get("nof_samples", 1)
		# Try the normal constructor first
		try:
			timing = BitTiming(
				f_clock=f_clock, 
				brp=brp, 
				tseg1=tseg1, 
				tseg2=tseg2, 
				sjw=sjw, 
				nof_samples=nof_samples
			)
		except (TypeError, ValueError) as e:
			pass
		if timing is not None:
			return _create_can_params_from_timing(timing=timing, controller=controller)
		# Try from sample point
		bitrate      = kwargs.get("bitrate",      None)
		sample_point = kwargs.get("sample_point", 69)
		try:
			timing = BitTiming.from_sample_point(
				f_clock=f_clock, 
				bitrate=bitrate, 
				sample_point=sample_point
			)
		except (TypeError, ValueError):
			pass
		if timing is not None:
			return _create_can_params_from_timing(timing=timing, controller=controller)
		# Try from bitrate and segments
		try:
			timing = BitTiming.from_bitrate_and_segments(
				f_clock=f_clock, 
				bitrate=bitrate, 
				tseg1=tseg1, 
				tseg2=tseg2, 
				sjw=sjw, 
				nof_samples=nof_samples
			)
		except (TypeError, ValueError):
			pass
		if timing is not None:
			return _create_can_params_from_timing(timing=timing, controller=controller)
		# Try from registers
		btr0 = kwargs.get("btr0", None)
		btr1 = kwargs.get("btr1", None)
		try:
			timing = BitTiming.from_registers(
				f_clock=f_clock, 
				btr0=btr0, 
				btr1=btr1
			)
		except (TypeError, ValueError):
			pass
		if timing is not None:
			return _create_can_params_from_timing(timing=timing, controller=controller)
		# Try our default values
		try:
			timing = _baudToSja1000Timing(
				f_clock=f_clock, 
				bitrate=bitrate
			)
		except Exception:
			pass
		if timing is not None:
			return _create_can_params_from_timing(timing=timing, controller=controller)
	raise ValueError("Can't create can params: No suitable arguments found.")

def _can_params_is_fd(can_params : CPC_CAN_PARAMS_T) -> bool:
	if can_params.cc_type == GENERIC_CAN_CONTR:
		if can_params.cc_params.generic.config & (CPC_GENERICCONF_FD | CPC_GENERICCONF_FD_BOSCH):
			return True
		else:
			return False
	elif can_params.cc_type == SJA1000:
		return False
	elif can_params.cc_type == LPC546XX:
		if can_params.cc_params.lpc546xx.cccr & CAN_CCCR_FDOE:
			return True
		else:
			return False
	else:
		raise ValueError(_cpcErrToStr(CPC_ERR_WRONG_CONTROLLER_TYPE))

def _can_params_get_listen_only(can_params : CPC_CAN_PARAMS_T) -> bool:
	if can_params.cc_type == GENERIC_CAN_CONTR:
		if can_params.cc_params.generic.config & CPC_GENERICCONF_LISTEN_ONLY:
			return True
		else:
			return False
	elif can_params.cc_type == SJA1000:
		if can_params.cc_params.sja1000.mode & 0x02:
			return True
		else:
			return False
	elif can_params.cc_type == LPC546XX:
		if can_params.cc_params.lpc546xx.cccr & CAN_CCCR_MON:
			return True
		else:
			return False
	else:
		raise ValueError(_cpcErrToStr(CPC_ERR_WRONG_CONTROLLER_TYPE))

def _can_params_set_listen_only(can_params : CPC_CAN_PARAMS_T, listen_only : bool = True) -> None:
	if can_params.cc_type == GENERIC_CAN_CONTR:
		if listen_only:
			can_params.cc_params.generic.config |= CPC_GENERICCONF_LISTEN_ONLY
		else:
			can_params.cc_params.generic.config &= (~CPC_GENERICCONF_LISTEN_ONLY)
	elif can_params.cc_type == SJA1000:
		if listen_only:
			can_params.cc_params.sja1000.mode |= 0x02
		else:
			can_params.cc_params.sja1000.mode &= (~0x02)
	elif can_params.cc_type == LPC546XX:
		if listen_only:
			can_params.cc_params.lpc546xx.cccr |= CAN_CCCR_MON
		else:
			can_params.cc_params.lpc546xx.cccr &= (~CAN_CCCR_MON)
	else:
		raise ValueError(_cpcErrToStr(CPC_ERR_WRONG_CONTROLLER_TYPE))

def _can_params_copy(dst : CPC_CAN_PARAMS_T, src : CPC_CAN_PARAMS_T) -> None:
	if src.cc_type == GENERIC_CAN_CONTR:
		dst.cc_type                      = GENERIC_CAN_CONTR
		dst.cc_params.generic.config     = src.cc_params.generic.config
		dst.cc_params.generic.can_clk    = src.cc_params.generic.can_clk
		dst.cc_params.generic.n.tseg1    = src.cc_params.generic.n.tseg1
		dst.cc_params.generic.n.tseg2    = src.cc_params.generic.n.tseg2
		dst.cc_params.generic.n.brp      = src.cc_params.generic.n.brp
		dst.cc_params.generic.n.sjw      = src.cc_params.generic.n.sjw
		dst.cc_params.generic.d.tseg1    = src.cc_params.generic.d.tseg1
		dst.cc_params.generic.d.tseg2    = src.cc_params.generic.d.tseg2
		dst.cc_params.generic.d.brp      = src.cc_params.generic.d.brp
		dst.cc_params.generic.d.sjw      = src.cc_params.generic.d.sjw
	elif src.cc_type == SJA1000:
		dst.cc_type                      = SJA1000
		dst.cc_params.sja1000.mode       = src.cc_params.sja1000.mode
		dst.cc_params.sja1000.acc_code0  = src.cc_params.sja1000.acc_code0
		dst.cc_params.sja1000.acc_code1  = src.cc_params.sja1000.acc_code1
		dst.cc_params.sja1000.acc_code2  = src.cc_params.sja1000.acc_code2
		dst.cc_params.sja1000.acc_code3  = src.cc_params.sja1000.acc_code3
		dst.cc_params.sja1000.acc_mask0  = src.cc_params.sja1000.acc_mask0
		dst.cc_params.sja1000.acc_mask1  = src.cc_params.sja1000.acc_mask1
		dst.cc_params.sja1000.acc_mask2  = src.cc_params.sja1000.acc_mask2
		dst.cc_params.sja1000.acc_mask3  = src.cc_params.sja1000.acc_mask3
		dst.cc_params.sja1000.btr0       = src.cc_params.sja1000.btr0
		dst.cc_params.sja1000.btr1       = src.cc_params.sja1000.btr1
		dst.cc_params.sja1000.outp_contr = src.cc_params.sja1000.outp_contr
	elif src.cc_type == LPC546XX:
		dst.cc_type                      = LPC546XX
		dst.cc_params.lpc546xx.dbtp      = src.cc_params.lpc546xx.dbtp
		dst.cc_params.lpc546xx.test      = src.cc_params.lpc546xx.test
		dst.cc_params.lpc546xx.cccr      = src.cc_params.lpc546xx.cccr
		dst.cc_params.lpc546xx.nbtp      = src.cc_params.lpc546xx.nbtp
		dst.cc_params.lpc546xx.psr       = src.cc_params.lpc546xx.psr
		dst.cc_params.lpc546xx.tdcr      = src.cc_params.lpc546xx.tdcr
		dst.cc_params.lpc546xx.gfc       = src.cc_params.lpc546xx.gfc
		dst.cc_params.lpc546xx.sidfc     = src.cc_params.lpc546xx.sidfc
		dst.cc_params.lpc546xx.xidfc     = src.cc_params.lpc546xx.xidfc
		dst.cc_params.lpc546xx.xidam     = src.cc_params.lpc546xx.xidam
		dst.cc_params.lpc546xx.cclk      = src.cc_params.lpc546xx.cclk
	else:
		raise ValueError(_cpcErrToStr(CPC_ERR_WRONG_CONTROLLER_TYPE))

def _isEMSHandleValid(handle: int) -> bool:
	return handle >= 0

def _cpcErrToStr(error_code: int) -> str:
	if error_code in __cpc_error_to_string:
		return __cpc_error_to_string[error_code]
	elif error_code >= CPC_ERR_NONE:
		return __cpc_error_to_string[CPC_ERR_NONE]
	else:
		return "Unknown CPC_ERR_ value (" + str(error_code) + ")"

def _getAllInfoSources() -> list[str]:
	retVar = []
	for key in __info_source_to_string:
		if key != CPC_INFOMSG_T_UNKNOWN_SOURCE:
			retVar.append(__info_source_to_string[key])
	return retVar

def _getAllInfoTypes() -> list[str]:
	retVar = []
	for key in __info_type_to_string:
		if key != CPC_INFOMSG_T_UNKNOWN_TYPE:
			retVar.append(__info_type_to_string[key])
	return retVar

def _infoSourceToString(info_source : int) -> "str | None":
	if info_source in __info_source_to_string:
		return __info_source_to_string[info_source]
	elif (info_source is None) or (not isinstance(info_source, int)):
		return None
	elif (info_source < 0) or (info_source > 255):
		return None
	else:
		return str(info_source)

def _infoTypeToString(info_type : int) -> "str | None":
	if info_type in __info_type_to_string:
		return __info_type_to_string[info_type]
	elif (info_type is None) or (not isinstance(info_type, int)):
		return None
	elif (info_type < 0) or (info_type > 255):
		return None
	else:
		return str(info_type)

def _stringToInfoSource(info_source : str) -> "int | None":
	if (info_source is None) or (len(info_source) == 0):
		return None
	for key in __info_source_to_string:
		if info_source == __info_source_to_string[key]:
			return key
	try:
		retVar = int(info_source)
		if (retVar < 0) or (retVar > 255):
			return None
		else:
			return retVar
	except:
		return None

def _stringToInfoType(info_type : str) -> "int | None":
	if (info_type is None) or (len(info_type) == 0):
		return None
	for key in __info_type_to_string:
		if info_type == __info_type_to_string[key]:
			return key
	try:
		retVar = int(info_type)
		if (retVar < 0) or (retVar > 255):
			return None
		else:
			return retVar
	except:
		return None

def _convert_timeout(timeout):
	if timeout is None:
		return 0xFFFFFFFF
	elif isinstance(timeout, float):
		return ceil(timeout*1000)
	elif isinstance(timeout, int):
		return timeout*1000
	else:
		try:
			return int(timeout) * 1000
		except Exception as e:
			return None

def _baudToSja1000Timing(bitrate : int, f_clock : int = 8_000_000) -> BitTiming:
	if bitrate not in __sja1000_baud_to_btr:
		raise ValueError("Invalid bitrate")
	# The btr values from the dictionary assume f_clock=8MHz.
	# Calculate the timing appropriately and convert later if needed
	btr = __sja1000_baud_to_btr[bitrate]
	timing = BitTiming.from_registers(f_clock=8_000_000, btr0=btr[0], btr1=btr[1])
	if (f_clock == 8_000_000) or (f_clock is None):
		return timing
	else:
		return timing.recreate_with_f_clock(f_clock=f_clock)

def _baudToGenericTiming(nom_bitrate : int, data_bitrate : int, f_clock : None = None) -> "BitTiming | BitTimingFd":
	# Only the nominal bitrate is given 
	if data_bitrate is None:
		
		if (f_clock == 8_000_000) or (fclock is None):
			if nom_bitrate not in __generic_nom_baud_to_segments:
				raise ValueError("Invalid nom_bitrate")
				
			nbtp_segs = __generic_nom_baud_to_segments[nom_bitrate]
			timing = BitTiming(
				f_clock	= 8_000_000,
				brp		= nbtp_segs[0],
				tseg1		= nbtp_segs[1],
				tseg2		= nbtp_segs[2],
				sjw		= nbtp_segs[3]
			)
			return timing
			
		else:
			if nom_bitrate not in __generic_baud_to_segments:
				raise ValueError("Invalid nom_bitrate")
			nbtp_segs = __generic_baud_to_segments[nom_bitrate]
			timing = BitTiming(
				f_clock	= 40_000_000,
				brp		= nbtp_segs[0],
				tseg1		= nbtp_segs[1],
				tseg2		= nbtp_segs[2],
				sjw		= nbtp_segs[3]
			)	
			
			if (f_clock == 40_000_000) or (f_clock is None):
				return timing
			else:
				return timing.recreate_with_f_clock(f_clock=f_clock)
				
	# Invalid data bitrate is given
	elif data_bitrate not in __generic_baud_to_segments:
		raise ValueError("Invalid data_bitrate")
		
	else:
		# Nominal and data bitrate are given
		# The dbtp values from the dictionary assume f_clock=40MHz
		# Calculate the timing appropriately and convert later if needed
		dbtp_segs  = __generic_baud_to_segments[data_bitrate]
		nbtp_segs  = __generic_baud_to_segments[nom_bitrate]
		timing = BitTimingFd(
			f_clock    = 40_000_000,
			nom_brp    = nbtp_segs[0],
			nom_tseg1  = nbtp_segs[1],
			nom_tseg2  = nbtp_segs[2],
			nom_sjw    = nbtp_segs[3],
			data_brp   = dbtp_segs[0],
			data_tseg1 = dbtp_segs[1],
			data_tseg2 = dbtp_segs[2],
			data_sjw   = dbtp_segs[3]
		)
		if (f_clock == 40_000_000) or (f_clock is None):
			return timing
		else:
			return timing.recreate_with_f_clock(f_clock=f_clock)

__info_source_to_string = {
	CPC_INFOMSG_T_UNKNOWN_SOURCE : "unknown",
	CPC_INFOMSG_T_INTERFACE      : "interface",
	CPC_INFOMSG_T_DRIVER         : "driver",
	CPC_INFOMSG_T_LIBRARY        : "library"
}

__info_type_to_string = {
	CPC_INFOMSG_T_UNKNOWN_TYPE : "unknown",
	CPC_INFOMSG_T_SERIAL       : "serial",
	CPC_INFOMSG_T_VERSION      : "version",
	CPC_INFOMSG_T_CANFD        : "canfd",
	CPC_INFOMSG_T_CHANNEL_NR   : "channel_nr"
}

# Only valid for f_clock=8Mhz
__sja1000_baud_to_btr = {
	1_000_000 : (0x00, 0x14),
	800_000   : (0x00, 0x16),
	500_000   : (0x00, 0x1C),
	250_000   : (0x01, 0x1C),
	125_000   : (0x03, 0x1C),
	100_000   : (0x04, 0x1C),
	50_000    : (0x09, 0x1C),
	20_000    : (0x18, 0x1C),
	10_000    : (0x31, 0x1C)
}

# Only valid for f_clock=40Mhz
# (brp, tseg1, tseg2, sjw)
__generic_baud_to_segments = {
	#10_000_000 : (1,  2, 1, 1),
	# 8_000_000 : (1,  3, 1, 1),
	 5_000_000 : (1,  5, 2, 1),
	 4_000_000 : (1,  7, 2, 1),
	 2_500_000 : (1, 11, 4, 3),
	 2_000_000 : (1, 15, 4, 3),
	 1_000_000 : (2, 15, 4, 3),
	   800_000 : (5,  7, 2, 1),
	   500_000 : (4, 15, 4, 3),
	   250_000 : (8, 15, 4, 3),
	   125_000 : (16, 15, 4, 3),
	   100_000 : (20, 15, 4, 3),
	    50_000 : (20, 31, 8, 7),
	    20_000 : (50, 31, 8, 7),
	    10_000 : (100, 31, 8, 7)
}

# Only valid for f_clock=8Mhz
# (brp, tseg1, tseg2, sjw)
__generic_nom_baud_to_segments = {
#	 1_000_000 : (2, 2, 1, 1),
	 1_000_000 : (1, 9, 4, 4),
	   800_000 : (2, 3, 1, 1),
	   500_000 : (2, 5, 2, 1),
	   250_000 : (4, 5, 2, 1),
	   125_000 : (8, 5, 2, 1),
	   100_000 : (8, 7, 2, 1),
	    50_000 : (8, 15, 4, 3),
	    20_000 : (10, 31, 8, 7),
	    10_000 : (20, 31, 8, 7)
}

__cpc_error_to_string = {
	CPC_ERR_NONE                  : "CPC_ERR_NONE: indicates success",
	CPC_ERR_NO_FREE_CHANNEL       : "CPC_ERR_NO_FREE_CHANNEL: no more free space within the channel array",
	CPC_ERR_CHANNEL_ALREADY_OPEN  : "CPC_ERR_CHANNEL_ALREADY_OPEN: the channel is already open",
	CPC_ERR_CHANNEL_NOT_ACTIVE    : "CPC_ERR_CHANNEL_NOT_ACTIVE: access to a channel not active failed",
	CPC_ERR_NO_DRIVER_PRESENT     : "CPC_ERR_NO_DRIVER_PRESENT: no driver at the location searched by the library",
	CPC_ERR_NO_INIFILE_PRESENT    : "CPC_ERR_NO_INIFILE_PRESENT: the library could not find the inifile",
	CPC_ERR_WRONG_PARAMETERS      : "CPC_ERR_WRONG_PARAMETERS: wrong parameters in the inifile",
	CPC_ERR_NO_INTERFACE_PRESENT  : "CPC_ERR_NO_INTERFACE_PRESENT: 1. The specified interface is not connected\n2. The interface (mostly CPC-USB) was disconnected upon operation",
	CPC_ERR_NO_MATCHING_CHANNEL   : "CPC_ERR_NO_MATCHING_CHANNEL: the driver couldn't find a matching channel",
	CPC_ERR_NO_BUFFER_AVAILABLE   : "CPC_ERR_NO_BUFFER_AVAILABLE: the driver couldn't allocate buffer for messages",
	CPC_ERR_NO_INTERRUPT          : "CPC_ERR_NO_INTERRUPT: the requested interrupt couldn't be claimed",
	CPC_ERR_NO_MATCHING_INTERFACE : "CPC_ERR_NO_MATCHING_INTERFACE: no interface type related to this channel was found",
	CPC_ERR_NO_RESOURCES          : "CPC_ERR_NO_RESOURCES: the requested resources could not be claimed",
	CPC_ERR_SOCKET                : "CPC_ERR_SOCKET: error concerning TCP sockets",
	CPC_ERR_WRONG_CONTROLLER_TYPE : "CPC_ERR_WRONG_CONTROLLER_TYPE: wrong CAN controller type within initialization",
	CPC_ERR_NO_RESET_MODE         : "CPC_ERR_NO_RESET_MODE: the controller could not be set into reset mode",
	CPC_ERR_NO_CAN_ACCESS         : "CPC_ERR_NO_CAN_ACCESS: the CAN controller could not be accessed",
	CPC_ERR_INVALID_CANPARAMS     : "CPC_ERR_INVALID_CANPARAMS: the CAN controller init params are invalid",
	CPC_ERR_CAN_WRONG_ID          : "CPC_ERR_CAN_WRONG_ID: the provided CAN id is too big",
	CPC_ERR_CAN_WRONG_LENGTH      : "CPC_ERR_CAN_WRONG_LENGTH: the provided CAN length is too long",
	CPC_ERR_CAN_NO_TRANSMIT_BUF   : "CPC_ERR_CAN_NO_TRANSMIT_BUF: the transmit buffer was occupied",
	CPC_ERR_CAN_TRANSMIT_TIMEOUT  : "CPC_ERR_CAN_TRANSMIT_TIMEOUT: The message could not be sent within a specified time",
	CPC_ERR_CAN_WRONG_FDFLAGS     : "CPC_ERR_CAN_WRONG_FDFLAGS: Wrong flags within a CAN FD message",
	CPC_ERR_SERVICE_NOT_SUPPORTED : "CPC_ERR_SERVICE_NOT_SUPPORTED: the requested service is not supported by the interface",
	CPC_ERR_IO_TRANSFER           : "CPC_ERR_IO_TRANSFER: a transmission error down to the driver occurred",
	CPC_ERR_TRANSMISSION_FAILED   : "CPC_ERR_TRANSMISSION_FAILED: a transmission error down to the interface occurred",
	CPC_ERR_TRANSMISSION_TIMEOUT  : "CPC_ERR_TRANSMISSION_TIMEOUT: a timeout occurred within transmission to the interface",
	CPC_ERR_OP_SYS_NOT_SUPPORTED  : "CPC_ERR_OP_SYS_NOT_SUPPORTED: the operating system is not supported",
	CPC_ERR_UNKNOWN               : "CPC_ERR_UNKNOWN: an unknown error ocurred (mostly IOCTL errors)",
	CPC_ERR_LOADING_DLL           : "CPC_ERR_LOADING_DLL: the library 'cpcwin.dll' could not be loaded",
	CPC_ERR_ASSIGNING_FUNCTION    : "CPC_ERR_ASSIGNING_FUNCTION: the specified function could not be assigned",
	CPC_ERR_DLL_INITIALIZATION    : "CPC_ERR_DLL_INITIALIZATION: the DLL was not initialized correctly",
	CPC_ERR_MISSING_LICFILE       : "CPC_ERR_MISSING_LICFILE: the file containing the licenses does not exist",
	CPC_ERR_MISSING_LICENSE       : "CPC_ERR_MISSING_LICENSE: a required license was not found",
}

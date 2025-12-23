"""
"""

# Global imports
import logging
import configparser
import json
from ctypes import c_int, byref
from typing import Tuple, List

# python-can imports
from can              import BitTiming, BitTimingFd
from can              import BusABC, BusState
from can              import CanTimeoutError, CanOperationError, CanInitializationError, CanInterfaceNotImplementedError
from can              import Message
from can.typechecking import AutoDetectedConfig, CanFilters

# Local imports
from .constants  import *
from .structures import *
from .functions  import *
from .functions  import _cpclib_cpcconf_paths
from .util       import _cpcErrToStr, _convert_timeout, _create_can_params, _can_params_copy, _can_params_is_fd, _can_params_get_listen_only, _can_params_set_listen_only, _isEMSHandleValid, _create_timing_from_can_params
from .util       import _getAllInfoSources, _infoSourceToString, _stringToInfoSource, _getAllInfoTypes, _infoTypeToString, _stringToInfoType

logger = logging.getLogger("can.can_wuensche")

class EMSWuenscheBus(BusABC):
	_cpc_handle   : int
	_can_params   : CPC_CAN_PARAMS_T
	_state        : BusState # Real bus-state. Can be overwritten by the device.
	_target_state : BusState # Bus-state that the user requested. Needed for #reset()
	_timing       : "BitTiming | BitTimingFd"
	_infomsg      : dict

	def __init__(
		self,
		channel = "CHAN00",
		state: BusState = BusState.ACTIVE,
		bitrate: int = 500_000,
		timing = None,
		req_infos = True,
		**kwargs,
	):
		"""EMS Dr. Thomas Wuensche CAN-to-PC interface.
		:param channel:
			Identifier for the CAN channel that should be openend.
			Each channel is usually defined in the system configuration file, which is 
			usually in 'C:\\Windows\\cpcconf.ini' or '/etc/cpcconf.ini' (OS-dependend).
			We recommend to edit the file with our configuration application. Please 
			see the WRK/WDK manual for more information.
			Newer versions may also allow the use of a JSON object/string.

		:param can.bus.BusState state:
			BusState that the device should get initialized to. Use ACTIVE for normal 
			operation or PASSIVE for listen-only mode (if supported).

		:param timing:
			Specify the bit timing that the device should use. Use a BitTiming object for 
			non-fd mode or a BitTimingFd object for fd. If specified then all other timing 
			related parameters will be ignored.

		:param req_infos:
			Request infos during the init process (non-blocking). Responses are getting 
			parsed during recv(). Depending on the device type, responses may be delayed.
			We recommend to wait a bit and call recv() at least once before trying to 
			access these informations.

		:param bool fd:
			Ignored if timing is set

		:param int f_clock:
			Ignored if timing is set. Will be passed to BitTimingFd and/or BitTiming

		:param int bitrate:
			Ignored if timing is set or fd=True. Will be passed to BitTiming.

		:param float sample_point:
			Ignored if timing is set or fd=True. Will be passed to BitTiming.
 
		:param int tseg1:
			Ignored if timing is set or fd=True. Will be passed to BitTiming

		:param int tseg2:
			Ignored if timing is set or fd=True. Will be passed to BitTiming.

		:param int sjw:
			Ignored if timing is set or fd=True. Will be passed to BitTiming.

		:param int brp:
			Ignored if timing is set or fd=True. Will be passed to BitTiming.

		:param int nom_bitrate:
			Ignored if timing is set or fd=False. Will be passed to BitTimingFd.

		:param float nom_sample_point:
			Ignored if timing is set or fd=False. Will be passed to BitTimingFd.
		
		:param int nom_tseg1:
			Ignored if timing is set or fd=False. Will be passed to BitTimingFd.

		:param int nom_tseg2:
			Ignored if timing is set or fd=False. Will be passed to BitTimingFd.

		:param int nom_sjw:
			Ignored if timing is set or fd=False. Will be passed to BitTimingFd.

		:param int nom_brp:
			Ignored if timing is set or fd=False. Will be passed to BitTimingFd.

		:param int data_bitrate:
			Ignored if timing is set or fd=False. Will be passed to BitTimingFd.

		:param float data_sample_point:
			Ignored if timing is set or fd=False. Will be passed to BitTimingFd.

		:param int data_tseg1:
			Ignored if timing is set or fd=False. Will be passed to BitTimingFd.

		:param int data_tseg2:
			Ignored if timing is set or fd=False. Will be passed to BitTimingFd.

		:param int data_sjw:
			Ignored if timing is set or fd=False. Will be passed to BitTimingFd.

		:param int data_brp:
			Ignored if timing is set or fd=False. Will be passed to BitTimingFd.
		"""
		self._cpc_handle   = CPC_ERR_NO_INTERFACE_PRESENT
		self._can_params   = None
		self._state        = BusState.ERROR
		self._target_state = state
		self._timing       = timing
		self._infomsg      = {}
		# Check desired state
		if state not in (BusState.ACTIVE, BusState.PASSIVE):
			raise ValueError("BusState must be Active or Passive")
		# Try to open the channel
		if channel is None:
			channel = "CHAN00"
		if isinstance(channel, str):
			channel = channel.strip()
			if len(channel) < 1:
				raise CanInterfaceNotImplementedError(message=_cpcErrToStr(error_code=CPC_ERR_NO_MATCHING_CHANNEL), error_code=CPC_ERR_NO_MATCHING_CHANNEL)
			# Try the normal version first
			self._cpc_handle = CPC_OpenChannel(channel.encode("ascii"))
			if _isEMSHandleValid(handle=self._cpc_handle):
				self.channel = channel
				self.channel_info = channel
			else:
				# Prepare to try the json version
				try:
					channel = json.loads(channel)
				except Exception:
					raise CanInterfaceNotImplementedError(message=_cpcErrToStr(error_code=self._cpc_handle), error_code=self._cpc_handle)
				# If json.loads worked then let the code below do the json handling
		# Try the json version
		if not _isEMSHandleValid(handle=self._cpc_handle):
			if "InterfaceType" in channel:
				self.channel = { "UNNAMED" : channel }
				self.channel_info = json.dumps(obj=self.channel, skipkeys=False, ensure_ascii=True, allow_nan=False)
				self._cpc_handle = CPC_OpenChannelJSON(self.channel_info.encode("ascii"))
			else:
				for key in channel:
					if "InterfaceType" in channel[key]:
						self.channel = { str(key) : channel[key] }
						self.channel_info = json.dumps(obj=self.channel, skipkeys=False, ensure_ascii=True, allow_nan=False)
						self._cpc_handle = CPC_OpenChannelJSON(self.channel_info.encode("ascii"))
						if _isEMSHandleValid(handle=self._cpc_handle):
							break
		# Verify that our handle is valid
		if not _isEMSHandleValid(handle=self._cpc_handle):
			raise CanInterfaceNotImplementedError(message="Failed to open channel: '" + self.channel_info + "': " + _cpcErrToStr(error_code=self._cpc_handle), error_code=self._cpc_handle)
		# Request infos before initializing the channel
		if req_infos:
			lib_string = _infoSourceToString(CPC_INFOMSG_T_LIBRARY)
			self._infomsg[lib_string] = {}
			for t in [CPC_INFOMSG_T_VERSION, CPC_INFOMSG_T_SERIAL, CPC_INFOMSG_T_CANFD, CPC_INFOMSG_T_CHANNEL_NR]:
				CPC_RequestInfo(self._cpc_handle, 0, CPC_INFOMSG_T_INTERFACE, t)
				CPC_RequestInfo(self._cpc_handle, 0, CPC_INFOMSG_T_DRIVER, t)
				lib_info = CPC_GetInfo(self._cpc_handle, CPC_INFOMSG_T_LIBRARY, t)
				if lib_info:
					self._infomsg[lib_string][_infoTypeToString(t)] = lib_info.decode("ascii")
			# Call receive to parse any received info messages (note: interface responses may 
			# need more time but we won't wait for them)
			self._recv_internal(None)
		# Try to initialize the controller with generic params
		try:
			self._can_params = _create_can_params(controller=GENERIC_CAN_CONTR, timing=timing, bitrate=bitrate, **kwargs)
			_can_params_set_listen_only(can_params=self._can_params, listen_only=state != BusState.ACTIVE)
			try:
				self.__apply_can_params()
			except CanOperationError as e:
				# Some devices may not support generic params yet
				if e.error_code == CPC_ERR_WRONG_CONTROLLER_TYPE:
					if _can_params_is_fd(can_params=self._can_params):
						self._can_params = _create_can_params(controller=LPC546XX, timing=timing, bitrate=bitrate, **kwargs)
					else:
						self._can_params = _create_can_params(controller=SJA1000, timing=timing, bitrate=bitrate, **kwargs)
					_can_params_set_listen_only(can_params=self._can_params, listen_only=state != BusState.ACTIVE)
					self.__apply_can_params()
				else:
					raise
		except:
			CPC_CloseChannel(self._cpc_handle)
			raise
		# Activate receive messages and CAN state
		result = CPC_Control(self._cpc_handle, CONTR_CAN_Message | CONTR_CONT_ON)
		if result != CPC_ERR_NONE:
			CPC_CloseChannel(self._cpc_handle)
			raise CanOperationError(message=_cpcErrToStr(error_code=result), error_code=result)
		result = CPC_Control(self._cpc_handle, CONTR_CAN_State   | CONTR_CONT_ON)
		if result != CPC_ERR_NONE:
			CPC_CloseChannel(self._cpc_handle)
			raise CanOperationError(message=_cpcErrToStr(error_code=result), error_code=result)
		result = CPC_Control(self._cpc_handle, CONTR_BusError    | CONTR_CONT_ON)
		if result != CPC_ERR_NONE:
			CPC_CloseChannel(self._cpc_handle)
			raise CanOperationError(message=_cpcErrToStr(error_code=result), error_code=result)
		super().__init__(channel=channel, state=state, bitrate=bitrate, timing=timing, **kwargs)
		
	# Send message
	def send(self, msg: Message, timeout: "float | None" = None) -> None:
		# Verify that our handle is valid
		if not _isEMSHandleValid(handle=self._cpc_handle):
			raise CanOperationError(message=_cpcErrToStr(error_code=self._cpc_handle), error_code=self._cpc_handle)
		# Sanity check the timeout value and convert it from float (sec) to int (msec)
		_timeout = _convert_timeout(timeout=timeout)
		if _timeout is None:
			raise ValueError("Failed to convert timeout value: Faulty value is: '"+ str(timeout) + "'")
		# Wait for buffer space
		result = CPC_WaitForEvent(self._cpc_handle, _timeout, EVENT_WRITE)
		if result < 0:
			raise CanOperationError(message=_cpcErrToStr(error_code=result), error_code=result)
		elif not (result & EVENT_WRITE):
			raise CanTimeoutError(message=_cpcErrToStr(error_code=CPC_ERR_IO_TRANSFER), error_code=CPC_ERR_IO_TRANSFER)
		# Send FD message
		if msg.is_fd:
			canmsg = CPC_CANFD_MSG_T()
			canmsg.id = msg.arbitration_id
			canmsg.length = msg.dlc
			canmsg.flags = 0
			if msg.is_extended_id:
				canmsg.type |= CPC_FDFLAG_XTD
				canmsg.id = canmsg.id & 0x1FFFFFFF
			else:
				canmsg.id = canmsg.id & 0x000007FF
			if msg.is_remote_frame:
				canmsg.type |= CPC_FDFLAG_RTR
			else:
				# Copy data if not rtr
				for i in range(msg.dlc):
					canmsg.msg[i] = msg.data[i]
			if not msg.is_fd:
				canmsg.type |= CPC_FDFLAG_NONCANFD_MSG
			if msg.is_error_frame:
				canmsg.type |= CPC_FDFLAG_ESI
			if msg.bitrate_switch:
				canmsg.type |= CPC_FDFLAG_BRS
			result = CPC_SendMsgFD(self._cpc_handle, 0, ctypes.byref(canmsg))
		# Send classic CAN message
		else:
			canmsg = CPC_CAN_MSG_T()
			canmsg.length = msg.dlc
			# Copy data (for non-rtr messages)
			if not msg.is_remote_frame:
				for i in range(msg.dlc):
					canmsg.msg[i] = msg.data[i]
			if not msg.is_extended_id:
				canmsg.id = msg.arbitration_id & 0x000007FF
				if not msg.is_remote_frame:
					result = CPC_SendMsg(self._cpc_handle, 0, ctypes.byref(canmsg))
				else:
					result = CPC_SendRTR(self._cpc_handle, 0, ctypes.byref(canmsg))
			else:
				canmsg.id = msg.arbitration_id & 0x1FFFFFFF
				if not msg.is_remote_frame:
					result = CPC_SendXMsg(self._cpc_handle, 0, ctypes.byref(canmsg))
				else:
					result = CPC_SendXRTR(self._cpc_handle, 0, ctypes.byref(canmsg))
		if result != CPC_ERR_NONE:
			raise CanOperationError(message="Failed to send: " + _cpcErrToStr(error_code=result), error_code=result)

	# Fetch a message from interface
	def _recv_internal(self, timeout: "float | None") -> Tuple["Message | None", bool]:
		# Verify that our handle is valid
		if not _isEMSHandleValid(handle=self._cpc_handle):
			raise CanOperationError(message=_cpcErrToStr(error_code=self._cpc_handle), error_code=self._cpc_handle)
		# Sanity check the timeout value and convert it from float (sec) to int (msec)
		_timeout = _convert_timeout(timeout=timeout)
		if _timeout is None:
			raise ValueError("Failed to convert timeout value: Faulty value is: '"+ str(timeout) + "'")
		# Wait for messages
		result = CPC_WaitForEvent(self._cpc_handle, _timeout, EVENT_READ)
		if result < 0:
			raise CanOperationError(message=_cpcErrToStr(error_code=result), error_code=result)
		elif (result & EVENT_READ) == 0:
			return None, False
		# Fetch message
		while True:
			msg = CPC_Handle(self._cpc_handle)
			if not msg:
				break
			msg = msg[0]
			if not msg:
				break
			logger.debug("Received a message with type: " + str(msg.type))
			if msg.type == CPC_MSG_T_CANFD:
				isExt = False
				isRTR = False
				isFD = False
				btrs = False
				isESI = False
				if msg.msg.canfdmsg.flags & CPC_FDFLAG_XTD:
					isExt = True
				if msg.msg.canfdmsg.flags & CPC_FDFLAG_RTR:
					isRTR = True
				if msg.msg.canfdmsg.flags & CPC_FDFLAG_ESI:
					isESI = True
				if not (msg.msg.canfdmsg.flags & CPC_FDFLAG_NONCANFD_MSG):
					isFD = True
					# baudrate switch is only available with CAN-FD
					if msg.msg.canfdmsg.flags & CPC_FDFLAG_BRS:
						btrs = True
				return Message(
					timestamp=msg.ts_sec + (msg.ts_nsec / 1_000_000_000.0),
					arbitration_id=msg.msg.canfdmsg.id,
					is_extended_id=isExt,
					is_remote_frame=isRTR,
					is_error_frame=False,
					dlc=msg.msg.canfdmsg.length,
					data=msg.msg.canfdmsg.msg[:msg.msg.canfdmsg.length],
					is_fd=isFD,
					bitrate_switch=btrs,
					error_state_indicator=isESI
				), False
			elif msg.type == CPC_MSG_T_CAN:
				return Message(
					timestamp=msg.ts_sec + (msg.ts_nsec / 1_000_000_000.0),
					arbitration_id=msg.msg.canmsg.id,
					is_extended_id=False,
					is_remote_frame=False,
					is_error_frame=False,
					dlc=msg.msg.canmsg.length,
					data=msg.msg.canmsg.msg[:msg.msg.canmsg.length],
					is_fd=False,
					bitrate_switch=False,
					error_state_indicator=False
				), False
			elif msg.type == CPC_MSG_T_XCAN:
				return Message(
					timestamp=msg.ts_sec + (msg.ts_nsec / 1_000_000_000.0),
					arbitration_id=msg.msg.canmsg.id,
					is_extended_id=True,
					is_remote_frame=False,
					is_error_frame=False,
					dlc=msg.msg.canmsg.length,
					data=msg.msg.canmsg.msg[:msg.msg.canmsg.length],
					is_fd=False,
					bitrate_switch=False,
					error_state_indicator=False
				), False
			elif msg.type == CPC_MSG_T_RTR:
				return Message(
					timestamp=msg.ts_sec + (msg.ts_nsec / 1_000_000_000.0),
					arbitration_id=msg.msg.canmsg.id,
					is_extended_id=False,
					is_remote_frame=True,
					is_error_frame=False,
					dlc=msg.msg.canmsg.length,
					data=[],
					is_fd=False,
					bitrate_switch=False,
					error_state_indicator=False
				), False
			elif msg.type == CPC_MSG_T_XRTR:
				return Message(
					timestamp=msg.ts_sec + (msg.ts_nsec / 1_000_000_000.0),
					arbitration_id=msg.msg.canmsg.id,
					is_extended_id=True,
					is_remote_frame=True,
					is_error_frame=False,
					dlc=msg.msg.canmsg.length,
					data=[],
					is_fd=False,
					bitrate_switch=False,
					error_state_indicator=False
				), False
			elif msg.type == CPC_MSG_T_INFO:
				if msg.length < 2:
					logger.debug("CPC_MSG_T_INFO: Invalid length!")
				else:
					info_src  = _infoSourceToString(msg.msg.info.source)
					if info_src is None:
						info_src = str(msg.msg.info.source)
					info_type = _infoTypeToString(msg.msg.info.type)
					if info_type is None:
						info_type = str(msg.msg.info.type)
					#
					if info_src not in self._infomsg:
						self._infomsg[info_src] = {}
					if msg.length > 2:
						self._infomsg[info_src][info_type] = msg.msg.info.msg[:msg.length-2].decode("ascii")
					else:
						self._infomsg[info_src][info_type] = ""
					logger.debug("CPC_MSG_T_INFO: len=" + str(msg.length) + " src=" + info_src + " type=" + info_type + " msg='" + self._infomsg[info_src][info_type] + "'")
			elif msg.type == CPC_MSG_T_CANSTATE:
				logger.debug("CPC_MSG_T_CANSTATE: " + str(msg.msg.canstate))
				if msg.msg.canstate & CPC_CAN_STATE_BUSOFF:
					self._state = BusState.ERROR
				elif self._state == BusState.ERROR:
					self._state = self._target_state
			elif msg.type == CPC_MSG_T_CANERROR:
				logger.debug("CPC_MSG_T_CANERROR")
				if msg.msg.error.ecode == CPC_CAN_ECODE_ERRFRAME:
					if msg.msg.error.cc.cc_type == SJA1000:
						# u8 ecc, rxerr, txerr -> 3 bytes in total
						data = bytes(msg.msg.error.cc.regs.sja1000)
						return Message(
							timestamp=msg.ts_sec + (msg.ts_nsec / 1_000_000_000.0),
							dlc=len(data),
							data=data,
							is_error_frame=True
						), False
					elif msg.msg.error.cc.cc_type == LPC546XX:
						# u32 psr, ecr -> 8 bytes in total
						data = bytes(msg.msg.error.cc.regs.lpc546xx)
						return Message(
							timestamp=msg.ts_sec + (msg.ts_nsec / 1_000_000_000.0),
							dlc=len(data),
							data=data,
							is_fd=False,
							is_error_frame=True
						), False
				return Message(
					timestamp=msg.ts_sec + (msg.ts_nsec / 1_000_000_000.0),
					is_error_frame=True
				), False
			elif msg.type == CPC_MSG_T_DISCONNECTED:
				logger.debug("CPC_MSG_T_DISCONNECTED")
				self.shutdown()
				raise CanOperationError(message=_cpcErrToStr(error_code=self._cpc_handle), error_code=self._cpc_handle)
			elif msg.type == CPC_MSG_T_CAN_PRMS:
				logger.debug("CPC_MSG_T_CAN_PRMS")
				self._timing = _create_timing_from_can_params(can_params=msg.msg.canparams)
				if not _can_params_get_listen_only(can_params=msg.msg.canparams):
					self._target_state = BusState.ACTIVE
				else:
					self._target_state = BusState.PASSIVE
				_can_params_copy(dst=self._can_params, src=msg.msg.canparams)
				if self._state != BusState.ERROR:
					self._state = self._target_state
			#else:
			#	logger.debug("Unhandled message type: "+str(msg.type))
		return None, False

	def flush_tx_buffer(self) -> None:
		super().flush_tx_buffer()
		if _isEMSHandleValid(handle=self._cpc_handle):
			CPC_ClearCMDQueue(self._cpc_handle)

	def shutdown(self) -> None:
		if _isEMSHandleValid(handle=self._cpc_handle):
			CPC_CloseChannel(self._cpc_handle)
			self._cpc_handle = CPC_ERR_NO_INTERFACE_PRESENT
		super().shutdown()

	#def _apply_filters(self, filters: "CanFilters | None") -> None:
	#	return super()._apply_filters(filters)

	@staticmethod
	def _detect_available_configs() -> List[AutoDetectedConfig]:
		channels : List[AutoDetectedConfig] = []
		################################
		# Ask the library for the channel list
		json_channels = {}
		json_string = ""
		json_string_raw = None
		json_length = c_int(0)
		try:
			json_string_raw = CPC_CreateChannelListJSON(byref(json_length))
			if json_string_raw:
				if json_length.value > 0:
					json_string = json_string_raw[:json_length.value].decode("ascii")
		finally:
			if json_string_raw:
				if json_length.value > 0:
					json_length = CPC_DeleteChannelListJSON(json_string_raw)
			json_string_raw = None
		try:
			json_channels = json.loads(json_string)
		except Exception:
			json_channels = {}
		for key in json_channels:
			channels.append(AutoDetectedConfig(interface='wuensche', channel={key : json_channels[key]}))
		if len(channels) > 0:
			return channels
		################################
		# Fallback implementation (CPC_CreateChannelListJSON is currently not implemented on unix)
		config = configparser.ConfigParser()
		for filePath in _cpclib_cpcconf_paths:
			if len(config.read(filePath)) > 0:
				break
		for key in config:
			if key != "DEFAULT":
				channels.append(AutoDetectedConfig(interface='wuensche', channel=key))
		return channels

	@property
	def timing(self) -> "BitTiming | BitTimingFd":
		if self._timing is None:
			try:
				self._timing = _create_timing_from_can_params(can_params=self._can_params)
			except Exception:
				pass
		return self._timing

	@timing.setter
	def timing(self, timing : "BitTiming | BitTimingFd"):
		if self._can_params:
			self._can_params = _create_can_params(controller=self._can_params.cc_type, timing=timing)
		else:
			self._can_params = _create_can_params(controller=GENERIC_CAN_CONTR, timing=timing)
		self._timing = timing
		self.__apply_can_params()

	@property
	def state(self) -> BusState:
		return self._state

	@state.setter
	def state(self, state):
		# We can't set the device to BusState.ERROR
		if state not in (BusState.ACTIVE, BusState.PASSIVE):
			raise ValueError("BusState must be Active or Passive")
		_can_params_set_listen_only(can_params=self._can_params, listen_only=state != BusState.ACTIVE)
		self._target_state = state
		self.__apply_can_params()

	def reset(self) -> None:
		if not _isEMSHandleValid(handle=self._cpc_handle):
			raise CanOperationError(message=_cpcErrToStr(error_code=self._cpc_handle), error_code=self._cpc_handle)
		result = CPC_ClearCMDQueue(self._cpc_handle, 0)
		if result != CPC_ERR_NONE:
			raise CanOperationError(message=_cpcErrToStr(error_code=result), error_code=result)
		result = CPC_ClearMSGQueue(self._cpc_handle)
		if result != CPC_ERR_NONE:
			raise CanOperationError(message=_cpcErrToStr(error_code=result), error_code=result)
		self.__apply_can_params()

	def __apply_can_params(self) -> None:
		if not _isEMSHandleValid(handle=self._cpc_handle):
			raise CanOperationError(message=_cpcErrToStr(error_code=self._cpc_handle), error_code=self._cpc_handle)
		# Get init params pointer. Do NOT use "is None" as that wouldn't catch NULL.
		initParams = CPC_GetInitParamsPtr(self._cpc_handle)
		if not initParams:
			raise CanOperationError(message="Failed to retrieve init parameters: " + _cpcErrToStr(error_code=CPC_ERR_UNKNOWN), error_code=CPC_ERR_UNKNOWN)
		#
		_can_params_copy(dst=initParams[0].canparams, src=self._can_params)
		#
		result = CPC_CANInit(self._cpc_handle, 0)
		if result != CPC_ERR_NONE:
			# TODO If the device was in BusState.ACTIVE before, could it be in BusState.ERROR now since init failed?
			#self._state = BusState.ERROR
			if result == CPC_ERR_INVALID_CANPARAMS:
				raise CanInitializationError(message=_cpcErrToStr(error_code=CPC_ERR_INVALID_CANPARAMS), error_code=CPC_ERR_INVALID_CANPARAMS)
			else:
				raise CanOperationError(message=_cpcErrToStr(error_code=result), error_code=result)
		self._state = self._target_state

	# Request info from device, driver or library
	def cpc_request_info(self, info_source : str, info_type : str) -> bool:
		if not _isEMSHandleValid(self._cpc_handle):
			return False
		s = _stringToInfoSource(info_source)
		if s is None:
			return False
		t = _stringToInfoType(info_type)
		if t is None:
			return False
		if s != CPC_INFOMSG_T_LIBRARY:
			result = CPC_RequestInfo(self._cpc_handle, 0, s, t)
			if result < 0:
				return False
			return True
		else:
			info_msg = CPC_GetInfo(self._cpc_handle, s, t)
			if info_msg:
				if info_source not in self._infomsg:
					self._infomsg[info_source] = {}
				self._infomsg[info_source][info_type] = info_msg.decode("ascii")
				return True
			return False

	# Read requested info
	def cpc_read_info(self, info_source : str, info_type : str) -> "str | None":
		if info_source in self._infomsg:
			if info_type in self._infomsg[info_source]:
				return self._infomsg[info_source][info_type]
		return None

	@staticmethod
	def get_info_sources() -> list[str]:
		return _getAllInfoSources()

	@staticmethod
	def get_info_types() -> list[str]:
		return _getAllInfoTypes()

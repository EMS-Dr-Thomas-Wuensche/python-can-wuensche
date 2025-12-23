"""
Definitions of constants and predefined values
"""

CPC_MSG_LEN = 70

CONTR_CAN_Message         = 0x04
CONTR_Busload             = 0x08
CONTR_CAN_State           = 0x0C
CONTR_SendAck             = 0x10
CONTR_Filter              = 0x14
CONTR_CmdQueue            = 0x18 # reserved, do not use
CONTR_BusError            = 0x1C

# Control Command Actions
CONTR_CONT_OFF               = 0
CONTR_CONT_ON                = 1
CONTR_SING_ON                = 2
# CONTR_SING_ON doesn't change CONTR_CONT_ON state, so it should be
# read as: transmit at least once

# defines for confirmed request
# DO_CONFIRM is a value in the range of 1..255. The value set will come back with
# a message of type CPC_MSG_T_CONFIRM. Implemented for the API functions CPC_Send...()
# and used with the CPC-USB/ARM7 v2.0 and later
DO_NOT_CONFIRM               = 0
DO_CONFIRM                   = 1

# event flags
EVENT_READ                = 0x01
EVENT_WRITE               = 0x02

# Messages from CPC to PC contain a message object type field.
# The following message types are sent by CPC and can be used in
# handlers, others should be ignored.
CPC_MSG_T_RESYNC           =   0 # Normally to be ignored
CPC_MSG_T_CAN              =   1 # standard CAN data frame
CPC_MSG_T_BUSLOAD          =   2 # Busload message
CPC_MSG_T_STRING           =   3 # Normally to be ignored
CPC_MSG_T_CONTI            =   4 # Normally to be ignored
CPC_MSG_T_MEM              =   7 # Normally not to be handled
CPC_MSG_T_RTR              =   8 # standard CAN remote frame
CPC_MSG_T_TXACK            =   9 # Send acknowledge
CPC_MSG_T_POWERUP          =  10 # Power-up message
CPC_MSG_T_CMD_NO           =  11 # Normally to be ignored
CPC_MSG_T_CAN_PRMS         =  12 # Actual CAN parameters
CPC_MSG_T_ABORTED          =  13 # Command aborted message
CPC_MSG_T_CANSTATE         =  14 # CAN state message
CPC_MSG_T_RESET            =  15 # used to reset CAN-Controller
CPC_MSG_T_XCAN             =  16 # extended CAN data frame
CPC_MSG_T_XRTR             =  17 # extended CAN remote frame
CPC_MSG_T_INFO             =  18 # information strings
CPC_MSG_T_CONTROL          =  19 # used for control of interface/driver behaviour
CPC_MSG_T_CONFIRM          =  20 # response type for confirmed requests
CPC_MSG_T_OVERRUN          =  21 # response type for overrun conditions
CPC_MSG_T_KEEPALIVE        =  22 # response type for keep alive conditions
CPC_MSG_T_CANERROR         =  23 # response type for bus error conditions
CPC_MSG_T_DISCONNECTED     =  24 # response type for a disconnected interface
CPC_MSG_T_ERR_COUNTER      =  25 # RX/TX error counter of CAN controller
CPC_MSG_T_CANFD            =  26 # CAN FD frame

CPC_MSG_T_FIRMWARE         = 100 # response type for USB firmware download
CPC_MSG_T_USER             = 120 # reserved for custom specific interface

# Messages from the PC to the CPC interface contain a command field
# Most of the command types are wrapped by the library functions and have therefore
# normally not to be used.
# However, programmers who wish to circumvent the library and talk directly
# to the drivers (mainly Linux programmers) can use the following
# command types:

CPC_CMD_T_CAN              =   1 # standard CAN data frame
CPC_CMD_T_CONTROL          =   3 # used for control of interface/driver behaviour
CPC_CMD_T_CAN_PRMS         =   6 # set CAN parameters
CPC_CMD_T_CLEAR_MSG_QUEUE  =   8 # clear CPC_MSG queue
CPC_CMD_T_INQ_CAN_PARMS    =  11 # inquire actual CAN parameters
CPC_CMD_T_FILTER_PRMS      =  12 # set filter parameter
CPC_CMD_T_RTR              =  13 # standard CAN remote frame
CPC_CMD_T_CANSTATE         =  14 # CAN state message
CPC_CMD_T_XCAN             =  15 # extended CAN data frame
CPC_CMD_T_XRTR             =  16 # extended CAN remote frame
CPC_CMD_T_RESET            =  17 # used to reset CAN-Controller
CPC_CMD_T_INQ_INFO         =  18 # miscellanous information strings
CPC_CMD_T_OPEN_CHAN        =  19 # open a channel
CPC_CMD_T_CLOSE_CHAN       =  20 # close a channel
CPC_CMD_T_INQ_MSG_QUEUE_CNT = 21 # inquires the count of elements in the message queue
CPC_CMD_T_INQ_ERR_COUNTER  =  25 # request the CAN controllers error counter
CPC_CMD_T_CANFD            =  26 # CAN FD frame
CPC_CMD_T_CLEAR_CMD_QUEUE  =  28 # clear CPC_CMD queue
CPC_CMD_T_FIRMWARE         = 100 # reserved, must not be used
CPC_CMD_T_USB_RESET        = 101 # reserved, must not be used
CPC_CMD_T_WAIT_NOTIFY      = 102 # reserved, must not be used
CPC_CMD_T_WAIT_SETUP       = 103 # reserved, must not be used
CPC_CMD_T_CAN_EXIT         = 200 # exit the CAN (disable interrupts; reset bootrate; reset output_cntr; mode = 1)

# definitions for CPC_MSG_T_INFO
# information sources
CPC_INFOMSG_T_UNKNOWN_SOURCE = 0
CPC_INFOMSG_T_INTERFACE      = 1
CPC_INFOMSG_T_DRIVER         = 2
CPC_INFOMSG_T_LIBRARY        = 3

# information types
CPC_INFOMSG_T_UNKNOWN_TYPE   = 0
CPC_INFOMSG_T_VERSION        = 1
CPC_INFOMSG_T_SERIAL         = 2
CPC_INFOMSG_T_CANFD          = 3
CPC_INFOMSG_T_CHANNEL_NR     = 4

# definitions for controller types
PCA82C200                    = 1 # Deprecated, do not use
SJA1000                      = 2 # NXP basic CAN controller
AN82527                      = 3 # Intel full CAN controller
M16C_BASIC                   = 4 # Deprecated, do not use
LPC546XX                     = 5 # NXP CAN FD controller
GENERIC_CAN_CONTR            = 6 # Generic controller

# channel open error codes
CPC_ERR_NONE                         =   0 # indicates success

CPC_ERR_NO_FREE_CHANNEL              =  -1 # no more free space within the channel array
CPC_ERR_CHANNEL_ALREADY_OPEN         =  -2 # the channel is already open
CPC_ERR_CHANNEL_NOT_ACTIVE           =  -3 # access to a channel not active failed
CPC_ERR_NO_DRIVER_PRESENT            =  -4 # no driver at the location searched by the library
CPC_ERR_NO_INIFILE_PRESENT           =  -5 # the library could not find the inifile
CPC_ERR_WRONG_PARAMETERS             =  -6 # wrong parameters in the inifile
CPC_ERR_NO_INTERFACE_PRESENT         =  -7 # 1. The specified interface is not connected
                                           # 2. The interface (mostly CPC-USB) was disconnected upon operation
CPC_ERR_NO_MATCHING_CHANNEL          =  -8 # the driver couldn't find a matching channel
CPC_ERR_NO_BUFFER_AVAILABLE          =  -9 # the driver couldn't allocate buffer for messages
CPC_ERR_NO_INTERRUPT                 = -10 # the requested interrupt couldn't be claimed
CPC_ERR_NO_MATCHING_INTERFACE        = -11 # no interface type related to this channel was found
CPC_ERR_NO_RESOURCES                 = -12 # the requested resources could not be claimed
CPC_ERR_SOCKET                       = -13 # error concerning TCP sockets

# init error codes
CPC_ERR_WRONG_CONTROLLER_TYPE        = -14 # wrong CAN controller type within initialization
CPC_ERR_NO_RESET_MODE                = -15 # the controller could not be set into reset mode
CPC_ERR_NO_CAN_ACCESS                = -16 # the CAN controller could not be accessed
CPC_ERR_INVALID_CANPARAMS            = -17 # the CAN controller init params are invalid

# transmit error codes
CPC_ERR_CAN_WRONG_ID                 = -20 # the provided CAN id is too big
CPC_ERR_CAN_WRONG_LENGTH             = -21 # the provided CAN length is too long
CPC_ERR_CAN_NO_TRANSMIT_BUF          = -22 # the transmit buffer was occupied
CPC_ERR_CAN_TRANSMIT_TIMEOUT         = -23 # The message could not be sent within a
                                           # specified time
CPC_ERR_CAN_WRONG_FDFLAGS            = -24 # Wrong flags within a CAN FD message


# other error codes
CPC_ERR_SERVICE_NOT_SUPPORTED        = -30 # the requested service is not supported by the interface
CPC_ERR_IO_TRANSFER                  = -31 # a transmission error down to the driver occurred
CPC_ERR_TRANSMISSION_FAILED          = -32 # a transmission error down to the interface occurred
CPC_ERR_TRANSMISSION_TIMEOUT         = -33 # a timeout occurred within transmission to the interface
CPC_ERR_OP_SYS_NOT_SUPPORTED         = -35 # the operating system is not supported
CPC_ERR_UNKNOWN                      = -40 # an unknown error ocurred (mostly IOCTL errors)

CPC_ERR_LOADING_DLL                  = -50 # the library 'cpcwin.dll' could not be loaded
CPC_ERR_ASSIGNING_FUNCTION           = -51 # the specified function could not be assigned
CPC_ERR_DLL_INITIALIZATION           = -52 # the DLL was not initialized correctly
CPC_ERR_MISSING_LICFILE              = -55 # the file containing the licenses does not exist
CPC_ERR_MISSING_LICENSE              = -56 # a required license was not found

# CAN state bit values. Ignore any bits not listed
CPC_CAN_STATE_BUSOFF      = 0x80
CPC_CAN_STATE_ERROR       = 0x40

# Mask to help ignore undefined bits
CPC_CAN_STATE_MASK        = 0xc0

CPC_FDFLAG_ESI            = 0x08
CPC_FDFLAG_RTR            = 0x10
CPC_FDFLAG_NONCANFD_MSG   = 0x20
CPC_FDFLAG_BRS            = 0x40
CPC_FDFLAG_XTD            = 0x80

CAN_CCCR_INIT        =      0x1 # Initialization mode
CAN_CCCR_ASM         =      0x4 # Restricted operation
CAN_CCCR_MON         =     0x20 # Bus monitoring mode
CAN_CCCR_DAR         =     0x40 # Disable automatic retransmission
CAN_CCCR_FDOE        =    0x100 # CAN FD operation enable
CAN_CCCR_BRSE        =    0x200 # Bit rate switch enable
CAN_CCCR_PXHD        =   0x1000 # Protocol exception handling disable
CAN_CCCR_EFBI        =   0x2000 # Edge filtering during bus integration
CAN_CCCR_TXP         =   0x4000 # Transmit pause
CAN_CCCR_NISO        =   0x8000 # ISO/BOSCH mode

CCLK16MHZ            =  16000000
CCLK20MHZ            =  20000000
CCLK32MHZ            =  32000000
CCLK40MHZ            =  40000000
CCLK80MHZ            =  80000000
CCLK160MHZ           = 160000000

# Generic config flags
#   can protocoll
CPC_GENERICCONF_CLASSIC        = 0x00000000
CPC_GENERICCONF_FD             = 0x00000001
CPC_GENERICCONF_FD_BOSCH       = 0x00000002
#   controller modes
CPC_GENERICCONF_LISTEN_ONLY    = 0x00000010
CPC_GENERICCONF_SINGLE_SHOT    = 0x00000020
#   version masks
CPC_GENERICCONF_VERSION_MASK_MINOR = 0x0F000000 # Devices will ignore new features if they're unsupported
CPC_GENERICCONF_VERSION_MASK_MAJOR = 0xF0000000 # Devices will fail if the version is unsupported

CPC_OVR_GAP               =   10

CPC_OVR_EVENT_CAN         = 0x01
CPC_OVR_EVENT_CANSTATE    = 0x02
CPC_OVR_EVENT_BUSERROR    = 0x04

# If the CAN controller lost a message
# we indicate it with the highest bit
# set in the count field.
CPC_OVR_HW                =  0x80

# structure for CAN error conditions
CPC_CAN_ECODE_ERRFRAME    = 0x01

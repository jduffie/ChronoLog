"""
Global constants and enumerations for the ChronoLog application.
"""

from enum import Enum


class CartridgeSource(Enum):
    """Cartridge source types"""
    FACTORY = "factory"
    CUSTOM = "custom"


class CartridgeType(Enum):
    """Common cartridge type designations"""
    SIX_MM_CREEDMOOR = "6mm Creedmoor"
    TWENTY_TWO_LR = "22LR" 
    SEVENTEEN_HMR = "17HMR"
    THREE_OH_EIGHT_WINCHESTER = ".308 Winchester"
    TWO_TWENTY_THREE_REMINGTON = ".223 Remington"
    THREE_HUNDRED_WIN_MAG = ".300 Win Mag"
    SIX_FIVE_CREEDMOOR = "6.5 Creedmoor"
    TWO_FORTY_THREE_WINCHESTER = ".243 Winchester"


class UserRole(Enum):
    """User role types"""
    USER = "user"
    ADMIN = "admin"


class UnitSystem(Enum):
    """Unit system preferences"""
    IMPERIAL = "Imperial"
    METRIC = "Metric"


class WeatherSourceType(Enum):
    """Weather source device types"""
    METER = "meter"
    STATION = "station"
    MANUAL = "manual"


class WeatherSourceMake(Enum):
    """Weather source manufacturers"""
    KESTREL = "Kestrel"
    DAVIS = "Davis"
    ACURITE = "AcuRite"
    AMBIENT = "Ambient Weather"


class ProcessingMode(Enum):
    """Data processing modes"""
    REAL_TIME = "Real-time"
    BACKGROUND = "Background"


class ImportStatus(Enum):
    """Import processing status"""
    STARTING = "starting"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class RangeStatus(Enum):
    """Range submission status"""
    UNDER_REVIEW = "Under Review"
    APPROVED = "Approved"
    REJECTED = "Rejected"


class SessionStatus(Enum):
    """Session status values"""
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


# CSV Structure Constants
class CSVStructure:
    """Constants for Kestrel CSV file structure"""
    DEVICE_NAME_ROW = 0
    DEVICE_MODEL_ROW = 1
    SERIAL_NUMBER_ROW = 2
    HEADERS_ROW = 3
    UNITS_ROW = 4
    DATA_START_ROW = 5


# Database Field Types
class FieldType(Enum):
    """Database field types for processing"""
    TEMPERATURE = "temperature"
    PRESSURE = "pressure" 
    ALTITUDE = "altitude"
    WIND_SPEED = "wind_speed"
    PERCENTAGE = "percentage"
    DEGREES = "degrees"
    TEXT = "text"


# Unit Types
class UnitType(Enum):
    """Measurement unit types"""
    FAHRENHEIT = "fahrenheit"
    CELSIUS = "celsius"
    FEET = "feet"
    METERS = "meters"
    MPH = "mph"
    MPS = "mps"
    INHG = "inhg"
    HPA = "hpa"
    NO_CONVERSION = "no_conversion"
    UNKNOWN = "unknown"
    TIMESTAMP = "timestamp"


# UI Constants
class UIConstants:
    """UI-related constants"""
    DEFAULT_BATCH_SIZE = 50
    BACKGROUND_BATCH_SIZE = 100
    MAX_LINE_LENGTH = 127
    DEFAULT_COMPLEXITY_THRESHOLD = 10
    
    # Colors
    SUCCESS_COLOR = "green"
    WARNING_COLOR = "orange"
    ERROR_COLOR = "red"
    INFO_COLOR = "blue"


# File Constants
class FileConstants:
    """File-related constants"""
    ALLOWED_CSV_EXTENSIONS = ["csv"]
    MAX_FILE_SIZE_MB = 100
    UPLOAD_TIMEOUT_SECONDS = 300
    
    # File paths
    KESTREL_UPLOAD_PATH = "{user_email}/kestrel/{filename}"
    GARMIN_UPLOAD_PATH = "{user_email}/garmin/{filename}"


# Validation Constants
class ValidationConstants:
    """Validation rules and limits"""
    MIN_USERNAME_LENGTH = 3
    MAX_USERNAME_LENGTH = 30
    MIN_PASSWORD_LENGTH = 8
    MAX_NAME_LENGTH = 100
    MAX_DESCRIPTION_LENGTH = 500
    MAX_NOTES_LENGTH = 1000
    
    # Regex patterns
    USERNAME_PATTERN = r'^[a-zA-Z0-9_-]+$'
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
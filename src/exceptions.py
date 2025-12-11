"""Custom exceptions for EAC3 Converter."""


class EAC3ConverterError(Exception):
    """Base exception for EAC3 Converter errors."""
    pass


class ConfigError(EAC3ConverterError):
    """Configuration-related errors."""
    pass


class ConversionError(EAC3ConverterError):
    """Audio conversion errors."""
    pass


class ConversionTimeoutError(ConversionError):
    """Timeout during audio conversion."""
    pass


class DiskSpaceError(ConversionError):
    """Insufficient disk space for conversion."""
    pass


class FileProcessingError(EAC3ConverterError):
    """File processing errors."""
    pass


class CacheError(EAC3ConverterError):
    """Cache-related errors."""
    pass

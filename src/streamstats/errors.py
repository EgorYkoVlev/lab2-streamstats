class StreamStatsError(Exception):
    pass

class InvalidEventError(StreamStatsError):
    pass

class MissingHeaderError(StreamStatsError):
    pass

class CLIConfigurationError(StreamStatsError):
    pass

class UnsupportedFormatError(InvalidEventError):
    pass

class InvalidLevelError(InvalidEventError):
    pass

class InvalidTimestampError(InvalidEventError):
    pass

class MissingRequiredFieldError(InvalidEventError):
    pass


# TODO: move to utils/maintenance 

"""User exceptions for Mathcha2TikZ."""

class Mathcha2TikZError(Exception):
    """Base class for all Mathcha2TikZ errors."""
    pass


class ParserError(Mathcha2TikZError):
    """Error during parsing input data."""
    pass


class DetectionError(Mathcha2TikZError):
    """Error during detection of figure type."""
    pass


class ProcessingError(Mathcha2TikZError):
    """Error during processing of figure."""
    pass


class RenderingError(Mathcha2TikZError):
    """Error during generation of TikZ code."""
    pass


class ConfigurationError(Mathcha2TikZError):
    """Error during configuration."""
    pass


# TODO: Реализовать использование или удалить лишние исключения ниже.
# class ValidationError(Mathcha2TikZError):
#     """Error during validation of input data or configuration."""
#     pass

# class UnsupportedFeatureError(Mathcha2TikZError):
#     """Unsupported feature used."""
#     pass

# class ResourceError(Mathcha2TikZError):
#     """Error during access to external resources."""
#     pass
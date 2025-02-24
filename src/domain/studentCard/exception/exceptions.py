class DomainException(Exception):
    pass


class StudentNotFoundException(DomainException):
    pass


class InvalidImageException(DomainException):
    pass


class OCRProcessingException(DomainException):
    pass


class BarcodeProcessingException(DomainException):
    pass

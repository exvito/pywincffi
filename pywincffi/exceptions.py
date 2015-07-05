"""
Exceptions
==========

Custom exceptions that ``pywincffi`` can throw.
"""

class PyWinCFFIError(Exception):
    """
    The base class for all custom exceptions that pywincffi can throw.
    """


class InputError(PyWinCFFIError):
    """
    A subclass of :class:`PyWinCFFIError` that's raised when invalid input
    is provided to a function.  Because we're passing inputs to C we have
    to be sure that the input(s) being provided are what we're expecting so
    we fail early and provide better error messages.
    """
    def __init__(self, name, value, expected_types):
        self.name = name
        self.value = value
        self.expected_types = expected_types
        self.message = "Expected type(s) %r for %s.  Got %s instead." % (
            self.expected_types, self.name, type(self.value)
        )
        super(InputError, self).__init__(self.message)


class WindowsAPIError(PyWinCFFIError):
    """
    A subclass of :class:`PyWinCFFIError` that's raised when there was a
    problem calling a Windows API function.
    """
    def __init__(
            self, api_function, api_error_message, code, expected_code,
            nonzero=False
    ):
        self.api_function = api_function
        self.api_error_message = api_error_message
        self.code = code
        self.expected_code = expected_code
        self.nonzero = nonzero

        if not self.nonzero:
            self.message = \
                "Error when calling %s, error was %r.  Received " \
                "return value %s when we expected %s." % (
                self.api_function, self.api_error_message, self.code,
                self.expected_code
            )
        else:
            self.message = \
                "Expected a non-zero result from %r but got zero instead.  " \
                "Message from windows API was %r" % (
                    self.api_function, self.api_error_message
                )

        super(WindowsAPIError, self).__init__(self.message)
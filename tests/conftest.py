import inspect
import os
import pytest


@pytest.fixture(scope='session')
def find_data_file():
    """
    This fixture provides a function that finds a test data file based on the
    filename. It will look in the data subfolder of the calling function's
    directory

    .. code-block:: python
        :caption: example usage

        test_file_path = find_data_file('my_data.json')
    """

    def _helper(filename):
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        return os.path.join(
            os.path.dirname(os.path.realpath(module.__file__)),
            'data',
            filename,
        )
    return _helper

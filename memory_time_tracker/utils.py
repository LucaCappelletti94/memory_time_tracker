"""Submodule providing a few useful helper methods to detect different types of crashes."""
import os


def get_last_line(path: str, number_of_lines_to_read: int = 1) -> str:
    """Return the last line of file at given path.

    Parameters
    ------------------------
    path: str
        The path from where to load the document.
    number_of_lines_to_read: int = 1
        Number of lines to read. By defauly, one.

    Implementation details
    ------------------------
    The implementation of this method is taken from
    StackOverflow, specifically here: https://stackoverflow.com/questions/66507206/how-to-quickly-get-the-last-line-of-a-huge-csv-file-48m-lines
    """
    with open(path, 'r') as file:

        # find the position of the end of the file: end of the file stream
        end_of_file = file.seek(0, 2)

        # set your stream at the end: seek the final position of the file
        file.seek(end_of_file)

        # trace back each character of your file in a loop
        n = 0
        for num in range(end_of_file+1):
            file.seek(end_of_file - num)

            # save the last characters of your file as a string: last_line
            last_line = file.read()

            # count how many '\n' you have in your string:
            # if you have 1, you are in the last line; if you have 2, you have the two last lines
            if last_line.count('\n') == number_of_lines_to_read:
                return last_line


def has_completed_successfully(path: str) -> bool:
    """Return whether the file at given path has completed successfully.

    Parameters
    --------------------
    path: str
        The path to the file to load.

    Raises
    --------------------
    ValueError
        If file does not exist.
    """
    if not os.path.exists(path):
        raise ValueError(
            "The file at the provided path {path} does not exist.".format(
                path=path
            )
        )
    return get_last_line() == "0,0"


def has_crashed_gracefully(path: str) -> bool:
    """Return whether the file at given path has crashed gracefully.

    This means that the crash was controlled and raised a "normal"
    Python exception, and was not caused by some other causes such
    as core dumps, OOM etc...

    Parameters
    --------------------
    path: str
        The path to the file to load.

    Raises
    --------------------
    ValueError
        If file does not exist.
    """
    if not os.path.exists(path):
        raise ValueError(
            "The file at the provided path {path} does not exist.".format(
                path=path
            )
        )
    return get_last_line() == "-1,-1"


def has_crashed_ungracefully(path: str) -> bool:
    """Return whether the file at given path has crashed ungracefully.

    Causes of ungraceful crashes may be, for instance, OOM and core dumps.

    Parameters
    --------------------
    path: str
        The path to the file to load.

    Raises
    --------------------
    ValueError
        If file does not exist.
    """
    if not os.path.exists(path):
        raise ValueError(
            "The file at the provided path {path} does not exist.".format(
                path=path
            )
        )
    return get_last_line() not in ("-1,-1", "0,0")

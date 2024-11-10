import os
from datetime import datetime

import imghdr
from werkzeug.utils import secure_filename
from mimetypes import MimeTypes


ALLOWED_EXTENSIONS = ["jpg", "gif", "jpeg", "png"]


def validate_image(stream):
    """
    Reads the first 512 bytes from the input stream and attempts to determine
    the image format.

    :param stream: binary stream - The input stream representing the image.

    :return: str - A file extension based on the detected image format.
    """
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)

    if not format:
        return None

    return format


def is_allowed_file(image_file):
    """
    Check if the provided image file has an allowed extension or is a valid
    image.

    :param image_file: werkzeug.datastructures.FileStorage - FileStorage object
    representing the uploaded image.

    :return: bool - True if the image has an allowed extension or is a valid
    image, False otherwise.
    """
    filename = image_file.filename
    if "." in filename:
        extension = filename.rsplit(".", 1)[1].lower()
        # Check if the extension is allowed or image is valid
        if extension in ALLOWED_EXTENSIONS or extension == validate_image(
            image_file.stream
        ):
            return True

        return False

    return False


def save_image(image_file, folder=None):
    """
    Save the provided image file to the specified folder.

    :param image_file: werkzeug.datastructures.FileStorage - The image file
    to be saved.

    :param folder: str, optional - The folder where the image will be saved. If
    not provided, the image will not be saved.

    :return (filename | None): str, optional - The full path to the saved image
    if successful, None otherwise.
    """
    if image_file and folder:
        if not os.path.exists(folder):
            os.makedirs(folder)

        filename = secure_filename(image_file.filename)
        image_path = os.path.join(folder, filename)
        image_file.save(image_path)

        return filename

    return None


def save_file(file, folder=None):
    """
    Save the provided file to the specified folder.

    :param file: werkzeug.datastructures.FileStorage - The file to be saved.

    :param folder: str, optional - The folder where the file will be saved.
    If not provided, the file will not be saved.

    :return filename: str | None - The full path to the saved file if
    successful, None otherwise.
    """
    if file and folder:
        if not os.path.exists(folder):
            os.makedirs(folder)

        filename = secure_filename(file.filename)
        file_path = os.path.join(folder, filename)
        file.save(file_path)

        return file_path

    return None


def allowed_file(filename, allowed_extensions=set()):
    """
    Checks if a filename has an allowed file extension.

    :param filename: str - The name of the file to be checked.
    :param allowed_extensions: set - A set of allowed extensions.

    :return: bool - True if the filename has an allowed extension, False
    otherwise.
    """
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in allowed_extensions
    )


def get_file_type_icon(filename):
    """
    Determines the icon type based on the file's MIME type.

    :param filename: str - The name of the file.

    :return: str - The type of icon ('image', 'pdf', 'zip', or 'file').
    """
    mime = MimeTypes()
    mime_type, _ = mime.guess_type(filename)
    if mime_type:
        if mime_type.startswith("image"):
            return "image"

        elif mime_type == "application/pdf":
            return "pdf"

        elif mime_type == "application/zip":
            return "zip"

    return "file"


def get_file_size(filename):
    """
    Retrieves the size of a file.

    :param filename: str - The name of the file.

    :return: int - The size of the file in bytes.
    """
    return os.path.getsize(filename)


def get_file_info(file_path):
    """
    Retrieves information about a file specified by its path.

    :param file_path: str - The path to the file.

    :return: dict - A dictionary containing information about the file.
    """
    file_stat = os.stat(file_path)
    upload_date = datetime.fromtimestamp(file_stat.st_ctime)
    modified_date = datetime.fromtimestamp(file_stat.st_mtime)
    file_size = get_file_size(file_path)

    return {
        "name": os.path.basename(file_path),
        "upload_date": upload_date,
        "modified_date": modified_date,
        "size": file_size,
    }


def get_folder_files(folder_path, file_type=""):
    """
    Retrieves the files from the specified folder and their properties.

    Description:
    This function lists all files in the specified top-level directory,
    retrieves their properties, and returns a list of these properties.

    :param folder_path: str - Path to the folder from which files are to be
        retrieved.
    :param file_type: str - The type to be assigned to each file.

    :return files: list - List of file properties.
    """
    # List all files in the top-level directory
    _files = [
        f
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f))
    ]

    # Retrieve file properties
    files = []
    for file in _files:
        file_path = os.path.join(folder_path, file)
        file_info = get_file_info(file_path)
        file_info["type"] = file_type
        files.append(file_info)

    return files


def delete_similar_files(directory, pattern):
    """
    Deletes files in the specified directory that match the given pattern.

    :param directory: str - Path to the directory to search for files.
    :param pattern: str - Pattern to match for deleting files.
    """
    for filename in os.listdir(directory):
        if filename.startswith(pattern):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)


def delete_file(path):
    """
    Deletes the file in the given path.

    :param path: str - Path of the file to be deleted.
    """
    if os.path.isfile(path):
        os.remove(path)

# Third-party suppliers
from django.core.files.storage import FileSystemStorage


class OverwriteStorage(FileSystemStorage):
    """
    Represents a custom overwrite storage.
    """

    def get_available_name(self, name, max_length=None):
        """
        Check if the file already exists and overwrite it.
        Otherwise, continue.
        """
        if self.exists(name):
            self.delete(name)
        return name

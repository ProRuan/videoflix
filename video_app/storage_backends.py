# Third-party suppliers
from django.core.files.storage import FileSystemStorage


class OverrideStorage(FileSystemStorage):
    """
    Class representing an override storage.

    Replaces existing files to avoid leftovers.
    """

    def get_available_name(self, name, max_length=None):
        """Get available file name."""
        if self.exists(name):
            self.delete(name)
        return name

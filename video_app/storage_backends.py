# Standard libraries

# Third-party suppliers
from django.core.files.storage import FileSystemStorage

# Local imports


class OverrideStorage(FileSystemStorage):
    """Storage that replaces existing files to avoid leftovers."""

    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            self.delete(name)
        return name

from django.core.files.storage import FileSystemStorage


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        # If the file already exists, remove it so we can overwrite
        if self.exists(name):
            self.delete(name)
        return name

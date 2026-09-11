from filesystem import FileSystem
from shell import run_shell

filesystem = FileSystem()

try:
    filesystem.load_from_storage("storage.json")

except (FileNotFoundError, SyntaxError):
    pass

run_shell(filesystem)








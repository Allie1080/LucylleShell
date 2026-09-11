from collections.abc import Iterable

import json


class FileSystem:
    # ends with / = directory, otherwise a file
    # or just check the value if its a string or dict actually..
    # whatever, i like the aesthetic

    RESERVED_NAMES = ("/", "DIRECTORY")
    ILLEGAL_CHARACTERS_STRING = "!@#$%^&*/\\~`"

    ERROR_INVALID_PATH = SyntaxError("No such file or directory")
    ERROR_ROOT_PATH = SyntaxError("Cannot perform operation in root directory")

    ERROR_NOT_A_FILE = SyntaxError("Not a file")
    ERROR_NOT_A_DIRECTORY = SyntaxError("Not a directory")
    
    ERROR_FILE_EXISTS = SyntaxError("File already exists")
    ERROR_DIRECTORY_EXISTS = SyntaxError("Directory already exists")

    ERROR_DIRECTORY_NOT_EMPTY= SyntaxError("Directory not empty")

    ERROR_ILLEGAL_CHARACTER = SyntaxError(f"The following characters are not allowed in directory/file naming: {ILLEGAL_CHARACTERS_STRING}")

    ERROR_CORRUPTED_FILE = SyntaxError("Storage file corrupted")
    ERROR_STORAGE_FILE_NOT_FOUND = SyntaxError("Storage file not found")

    ERROR_NOT_IMPLEMENTED_YET = SyntaxError("Not implemented yet lmao")

    def __init__(self):
        self._default_storage_name: str = "storage.json"
        
        self._working_directory_path: str = "/home/"
        self._root_directory_path: str = "/"

        self._file_system = {
            "/": {
                "home/": {
                    "documents/": {},
                    "scripts/": {
                        "addition.lush": "11 * 6 + 1"
                    }, 
                    "hello_world": "Hello, World!"
                }
            }
        }

        # self._time_to_destruction: float = None


    # def get_time_to_destruction(self) -> float:
    #     return self._time_to_destruction

    # def set_time_to_destruction(self, value: float) -> None:
    #     self._time_to_destruction = value

    def _parse_path_to_components(self, path: str) -> list[str]:
        base_components: list[str]
        provided_components: list[str]
        component: str

        if path.startswith("/"):
            base_components = []
        
            path = path.lstrip("/")
        
        else:
            working_directory_path = self._working_directory_path
        
            if working_directory_path == "/":
                base_components = []
        
            else:
                parts = working_directory_path.lstrip("/").split("/")

                # TODO: resolve "." for current directory or whatever
                base_components = [part for part in parts if part != ""]
            
            path = path.lstrip("/")

        # ignores empty strings from trailing or double "/"
        provided_components = [component for component in path.split("/") if component != ""]

        # resolves ".."s in the string 
        for component in provided_components:
            if component == "..":
                if base_components:
                    base_components.pop()
        
                else:
                    raise SyntaxError("No such file or directory (cannot go above root)")
        
            elif component == "." or component == "":
                continue
        
            else:
                base_components.append(component)

        return base_components


    def _get_parent_and_key_from_components(self, components: list[str]) -> tuple[dict, str]:
        # returns parent_dict, key_str so the path can be called using parent_dict[key_str]
        # returns str + "/" if key is a directory, otherwise it's just a file
        
        if not components:
            raise self.ERROR_ROOT_PATH

        final_component = components[-1]
        parent_components = components[:-1]

        current_directory = self._file_system[self._root_directory_path]

        for component in parent_components:
            directory_key = component + "/"

            if directory_key not in current_directory:
                raise self.ERROR_INVALID_PATH
            
            current_directory = current_directory[directory_key]

        final_key: str
        final_component_as_directory = final_component + "/"
        
        if final_component_as_directory in current_directory:
            final_key = final_component_as_directory
        
        elif final_component in current_directory:
            final_key = final_component
        
        else:
            raise self.ERROR_INVALID_PATH

        return current_directory, final_key

    def _get_directory_from_components(self, components: list[str]) -> dict:
        current_directory = self._file_system[self._root_directory_path]

        for component in components:
            directory_key = component + "/"

            if directory_key not in current_directory:
                raise self.ERROR_INVALID_PATH

            current_directory = current_directory[directory_key]

        return current_directory

    def verify_path(self, path: str) -> bool:
        try:
            components = self._parse_path_to_components(path)
            self._get_parent_and_key_from_components(components)
        
            return True
        
        except SyntaxError:
            return False

    def get_working_directory(self) -> str:
        return self._working_directory_path

    def change_directory(self, path: str) -> None:
        # side effects on self._working_directory_path
        components = self._parse_path_to_components(path)

        if not components:
            self._working_directory_path = self._root_directory_path
            return

        if not self._get_parent_and_key_from_components(components)[1].endswith("/"):
            raise self.ERROR_NOT_A_DIRECTORY

        self._working_directory_path = self._root_directory_path + "/".join(components) + "/"

    def make_directory(self, directory_name: str) -> None:
        # TODO: Gracefully and efficiently handle multiple directory creation, or dont

        components: list[str]
        parent_components: list[str]
        parent_directory: dict

        directory_name = directory_name.rstrip("/")

        if not directory_name:
            raise self.ERROR_INVALID_PATH
            # actually moreso, cannot create root "/"

        # TODO: check if the name ends in an extension like .lush and prevent it from being made?

        components = self._parse_path_to_components(directory_name)
        directory_name = components[-1]
        parent_components = components[:-1]

        parent_directory = self._get_directory_from_components(parent_components)

        if directory_name + "/" in parent_directory:
            raise self.ERROR_DIRECTORY_EXISTS
        
        elif directory_name in parent_directory:
            # Unix prevents files and directories with the same name in the same parent directory
            raise self.ERROR_FILE_EXISTS
        
        if not set(self.ILLEGAL_CHARACTERS_STRING).isdisjoint(directory_name):
            raise self.ERROR_ILLEGAL_CHARACTER

        parent_directory[directory_name+"/"] = {}

    def list_directory(self, path: str) -> Iterable[str]:
        directory: dict

        if not path or path == ".":
            directory = self._get_directory_from_components(self._parse_path_to_components(self._working_directory_path))

        else:
            raise self.ERROR_NOT_IMPLEMENTED_YET

        return directory.keys()

    def delete_empty_directory(self, directory_name: str) -> None:
        parent_directory, directory_key = self._get_parent_and_key_from_components(self._parse_path_to_components(directory_name))

        if not directory_key.endswith("/"):
            raise self.ERROR_NOT_A_DIRECTORY

        if parent_directory[directory_key]:
            raise self.ERROR_DIRECTORY_NOT_EMPTY

        parent_directory.pop(directory_key)

    def annihilate(self) -> None:
        self._working_directory_path = self._root_directory_path
        self._file_system[self._root_directory_path].clear()

    def create_file(self, filename: str) -> None:
        components: list[str]
        parent_components: list[str]
        parent_directory: dict
        
        components = self._parse_path_to_components(filename)
        filename = components[-1]
        parent_components = components[:-1]
        
        parent_directory = self._get_directory_from_components(parent_components)
        
        if filename in parent_directory:
            raise self.ERROR_FILE_EXISTS

        elif (filename + "/") in parent_directory:
            # Unix prevents files and directories with the same name in the same parent directory
            raise self.ERROR_DIRECTORY_EXISTS

        for character in self.ILLEGAL_CHARACTERS_STRING:
            if character in filename:
                raise self.ERROR_ILLEGAL_CHARACTER

        parent_directory[filename] = ""

    def write_to_file(self, text: str, filename: str) -> None:
        components: list[str]
        parent_directory: dict
        final_key: str
        
        components = self._parse_path_to_components(filename)
        parent_directory = self._get_directory_from_components(components[:-1])
        
        final_key = components[-1]

        if final_key not in parent_directory:
            self.create_file(filename)

        parent_directory[final_key] = text


    def append_to_file(self, text: str, filename: str) -> None:
        components: list[str]
        parent_directory: dict
        final_key: str

        components = self._parse_path_to_components(filename)
        parent_directory = self._get_directory_from_components(components[:-1])
        
        final_key = components[-1]

        if final_key not in parent_directory:
            self.create_file(filename)
            parent_directory[final_key] = text

        else:
            parent_directory[final_key] += '\n' + text

    def move_file(self, old_path_to_filename: str, new_path_to_filename: str) -> None:
        # also used to rename files
        old_components: list[str]
        old_parent: dict
        old_key: str
        
        new_components: list[str]
        new_parent: dict
        new_key: str

        old_components = self._parse_path_to_components(old_path_to_filename)
        old_parent, old_key = self._get_parent_and_key_from_components(old_components)

        new_components = self._parse_path_to_components(new_path_to_filename)
        new_parent = self._get_directory_from_components(new_components[:-1])
        new_key = new_components[-1]

        if old_key.endswith("/"):
            if new_key in new_parent:
                raise self.ERROR_FILE_EXISTS
            
            new_key += "/"

            if new_key in new_parent:
                raise self.ERROR_DIRECTORY_EXISTS

        else:
            if new_key in new_parent:
                raise self.ERROR_FILE_EXISTS

            if new_key + "/" in new_parent:
                raise self.ERROR_DIRECTORY_EXISTS

        moved_object = old_parent.pop(old_key)
        new_parent[new_key] = moved_object

    def view_file(self, filename: str) -> str:
        parent_directory, file_key = self._get_parent_and_key_from_components(
            self._parse_path_to_components(filename)
        )

        if file_key.endswith("/"):
            raise self.ERROR_NOT_A_FILE

        return parent_directory[file_key]

    def delete_file(self, filename: str) -> None:
        try:
            parent_directory, file_key = self._get_parent_and_key_from_components(
                self._parse_path_to_components(filename)
            )

        except SyntaxError:
            raise self.ERROR_INVALID_PATH

        if file_key.endswith("/"):
            raise self.ERROR_NOT_A_FILE

        parent_directory.pop(file_key)

    # saves to JSON
    def save_to_storage(self, storage_name: str) -> None:
        with open(storage_name, "w", encoding="utf-8") as file:
            json.dump(self._file_system, file, indent=4)

    def load_from_storage(self, storage_name: str) -> None:
        with open(storage_name, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)

            except json.JSONDecodeError:
                raise self.ERROR_CORRUPTED_FILE

            self._file_system = data
            self._working_directory_path = "/home/"


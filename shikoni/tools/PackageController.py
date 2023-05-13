import pip
import pathlib
import importlib


class PackageController:

    def __init__(self):
        self.molude_loaded = {}

    def base_package_file(self):
        return pathlib.Path().joinpath("requirements.txt")

    def read_package_list(self, base_requirements_file):
        return_list = []
        with open(base_requirements_file) as f:
            file_lines = f.readlines()
            for file_line in file_lines:
                file_line = file_line.strip()
                if file_line.startswith("#"):
                    continue
                file_line = file_line.split("<")[0].split(">")[0].split("=")[0]
                return_list.append(file_line.replace("\n", ""))
        return return_list

    def install_base_package(self):
        self.install_package(self.read_package_list(self.base_package_file()))


    def install_package(self,packages_to_check: list):
        for package_name in packages_to_check:
            pip.main(["install", package_name])


    def import_module(self, mpdule_to_import: list):
        for module_name in mpdule_to_import:
            self.molude_loaded[module_name] = importlib.import_module(module_name)

    def get_module_class(self, package_import_path: str, class_name: str):
        if package_import_path not in self.molude_loaded:
            self.import_module([package_import_path])
        return self.molude_loaded[package_import_path].__dict__[class_name]()


if __name__ == "__main__":
    pc = PackageController()
    pc.install_base_package()
    # install_base_package()

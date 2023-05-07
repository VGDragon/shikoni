import sys
import os
import subprocess
import pathlib
import json
import time


def get_package_list():
    root_folder = pathlib.Path(__file__).parent.parent.absolute()
    with open(root_folder.joinpath("packages_used.txt")) as f:
        packages = f.read().split("\n")
    while "" in packages:
        packages.remove("")
    return packages


def start_test(result_file="test_result.txt"):
    result_file_path = pathlib.Path(result_file)
    if result_file_path.exists():
        os.remove(result_file)
    temp = subprocess.Popen(["pipenv", "run", "python", '-m', 'unittest', 'discover'])
    temp.wait()
    if not result_file_path.exists():
        return False
    with open(result_file) as f:
        result_list = json.loads(f.read())
    for result_item in result_list:
        if result_item["type"] != "OK":
            return False
    return True


def install_package(package_name):
    subprocess.Popen(['pipenv', "install", "{0}".format(package_name)]).wait()


def install_package_version(package_name, version):
    subprocess.Popen(['pipenv', "install", "{0}=={1}".format(package_name, version)]).wait()


def remove_package(package_name):
    subprocess.Popen(['pipenv', "uninstall", "{0}".format(package_name)]).wait()


def test_package_version(package_name, versions, packages_version, packages_version_file, packages_error_version, packages_error_version_file):
    for version in versions:
        version = version.strip()
        if version in packages_version[package_name]:
            continue
        if version in packages_error_version[package_name]:
            continue
        remove_package(package_name)
        install_package_version(package_name, version)
        is_working = start_test()
        if is_working:
            packages_version[package_name].append(version)
            with open(packages_version_file, "w") as f:
                f.write(json.dumps(packages_version))
        else:
            packages_error_version[package_name].append(version)
            with open(packages_error_version_file, "w") as f:
                f.write(json.dumps(packages_error_version))


def get_package_versions(package_name):
    result = subprocess.Popen(['pipenv', "install", package_name + "=="],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = result.communicate()
    output_string = error.decode("UTF-8")
    output_string_split = output_string.split("(")
    if len(output_string_split) < 2:
        return None
    output_string_split = output_string_split[1].split(")")
    if len(output_string_split) < 2:
        return None
    output_string_split = output_string_split[0].split(":")
    if len(output_string_split) < 2:
        return None
    versions = output_string_split[1].split(",")
    versions = [item.replace("\n", "").replace("\r", "").strip() for item in versions]
    versions.reverse()
    return versions


def start_searching_versions():
    depentencies_to_remove = ["async"]
    packages_version_file = pathlib.Path("packages.json")
    packages_version = {}
    if packages_version_file.exists():
        with open(packages_version_file) as f:
            packages_version = json.loads(f.read())
    packages_error_version_file = pathlib.Path("packages_error.json")
    packages_error_version = {}
    if packages_error_version_file.exists():
        with open(packages_error_version_file) as f:
            packages_error_version = json.loads(f.read())

    packages = get_package_list()
    for package in packages:
        for reinstall_package in packages:
            remove_package(reinstall_package)
        for dependencie_package in depentencies_to_remove:
            remove_package(dependencie_package)
        for reinstall_package in packages:
            if package != reinstall_package:
                install_package(reinstall_package)
        if package not in packages_version:
            packages_version[package] = []
        if package not in packages_error_version:
            packages_error_version[package] = []
        versions = get_package_versions(package)
        if versions is None:
            continue
        if len(versions) < 2:
            continue
        test_package_version(package, versions, packages_version, packages_version_file, packages_error_version, packages_error_version_file)


if __name__ == "__main__":
    # TODO fix bugs - installing package error
    do_find_version = True
    do_script_test = False
    if do_script_test:
        remove_package("websockets")
        install_package_version("websockets", "11.0.2")
        install_package("websockets")
        time.sleep(1)
        remove_package("websockets")
        time.sleep(1)
        install_package("websockets")
        start_test()
    if do_find_version:
        start_searching_versions()

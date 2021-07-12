import json
from zipfile import ZipFile
from pathlib import Path
from typing import List
import os
import re


def find_new_icons_in_devicon_json(devicon_json_path: str, icomoon_json_path: str):
    """
    Find the newly added icons by finding the difference between
    the devicon.json and the icomoon.json.
    :param devicon_json_path, the path to the devicon.json.
    :param icomoon_json_path: a path to the iconmoon.json.
    :return: a list of the new icons as JSON objects.
    """
    devicon_json = get_json_file_content(devicon_json_path)
    icomoon_json = get_json_file_content(icomoon_json_path)

    new_icons = []
    for icon in devicon_json:
        if is_not_in_icomoon_json(icon, icomoon_json):
            new_icons.append(icon)

    return new_icons


def get_json_file_content(json_path: str):
    """
    Get the json content of the json_path.
    :param: json_path, the path to the json file.
    :return: a dict representing the file content.
    """
    with open(json_path) as json_file:
        return json.load(json_file)


def is_not_in_icomoon_json(icon, icomoon_json):
    """
    Checks whether the icon's name is not in the icomoon_json.
    :param icon: the icon object we are searching for.
    :param icomoon_json: the icomoon json object parsed from
    icomoon.json.
    :return: True if icon's name is not in the icomoon.json, else False.
    """
    pattern = re.compile(f"^{icon['name']}-")

    for font in icomoon_json["icons"]:
        if pattern.search(font["properties"]["name"]):
            return False
    return True


def get_svgs_paths(new_icons: List[dict], icons_folder_path: str, 
    icon_versions_only: bool=False, as_str: bool=True):
    """
    Get all the suitable svgs file path listed in the devicon.json.
    :param new_icons, a list containing the info on the new icons.
    :param icons_folder_path, the path where the function can find the
    listed folders.
    :param icon_versions_only, whether to only get the svgs that can be 
    made into an icon. 
    :param: as_str, whether to add the path as a string or as a Path.
    :return: a list of svg file paths that can be uploaded to Icomoon.
    """
    file_paths = []
    for icon_info in new_icons:
        folder_path = Path(icons_folder_path, icon_info['name'])

        if not folder_path.is_dir():
            raise ValueError(f"Invalid path. This is not a directory: {folder_path}.")

        if icon_versions_only:
            get_icon_svgs_paths(folder_path, icon_info, file_paths, as_str)
        else:
            get_all_svgs_paths(folder_path, icon_info, file_paths, as_str)
    return file_paths


def get_icon_svgs_paths(folder_path: Path, icon_info: dict,
    file_paths: List[str], as_str: bool):
    """
    Get only the svg file paths that can be made into an icon from the icon_info.
    :param: folder_path, the folder where we can find the icons.
    :param: icon_info, an icon object in the devicon.json.
    :param: file_paths, an array containing all the file paths found.
    :param: as_str, whether to add the path as a string or as a Path.
    """
    aliases = icon_info["aliases"]

    for font_version in icon_info["versions"]["font"]:
        # if it's an alias, we don't want to make it into an icon
        if is_alias(font_version, aliases):
            print(f"Skipping this font since it's an alias: {icon_info['name']}-{font_version}.svg")
            continue

        file_name = f"{icon_info['name']}-{font_version}.svg"
        path = Path(folder_path, file_name)

        if path.exists():
            file_paths.append(str(path) if as_str else path)
        else:
            raise ValueError(f"This path doesn't exist: {path}")


def get_all_svgs_paths(folder_path: Path, icon_info: dict,
    file_paths: List[str], as_str: bool):
    """
    Get all the svg file paths of an icon.
    :param: folder_path, the folder where we can find the icons.
    :param: icon_info, an icon object in the devicon.json.
    :param: file_paths, an array containing all the file paths found.
    :param: as_str, whether to add the path as a string or as a Path.
    """
    for font_version in icon_info["versions"]["svg"]:
        file_name = f"{icon_info['name']}-{font_version}.svg"
        path = Path(folder_path, file_name)

        if path.exists():
            file_paths.append(str(path) if as_str else path)
        else:
            raise ValueError(f"This path doesn't exist: {path}")


def is_alias(font_version: str, aliases: List[dict]):
    """
    Check whether the font version is an alias of another version.
    :return: True if it is, else False.
    """
    for alias in aliases:
        if font_version == alias["alias"]:
            return True
    return False


def extract_files(zip_path: str, extract_path: str, delete=True):
    """
    Extract the style.css and font files from the devicon.zip
    folder. Must call the gulp task "get-icomoon-files"
    before calling this.
    :param zip_path, path where the zip file returned
    from the icomoon.io is located.
    :param extract_path, the location where the function
    will put the extracted files.
    :param delete, whether the function should delete the zip file
    when it's done.
    """
    print("Extracting zipped files...")

    icomoon_zip = ZipFile(zip_path)
    target_files = ('selection.json', 'fonts/', 'fonts/devicon.ttf',
                    'fonts/devicon.woff', 'fonts/devicon.eot',
                    'fonts/devicon.svg', "style.css")
    for file in target_files:
        icomoon_zip.extract(file, extract_path)

    print("Files extracted")

    if delete:
        print("Deleting devicon zip file...")
        icomoon_zip.close()
        os.remove(zip_path)


def rename_extracted_files(extract_path: str):
    """
    Rename the extracted files selection.json and style.css.
    :param extract_path, the location where the function
    can find the extracted files.
    :return: None.
    """
    print("Renaming files")
    old_to_new_list = [
        {
            "old": Path(extract_path, "selection.json"),
            "new": Path(extract_path, "icomoon.json")
        },
        {
            "old": Path(extract_path, "style.css"),
            "new": Path(extract_path, "devicon.css")
        }
    ]

    for dict_ in old_to_new_list:
        os.replace(dict_["old"], dict_["new"])

    print("Files renamed")


def create_screenshot_folder(dir, screenshot_name: str="screenshots/"):
    """
    Create a screenshots folder in the dir.
    :param dir, the dir where we want to create the folder.
    :param screenshot_name, the name of the screenshot folder.
    :raise Exception if the dir provided is not a directory.
    :return the string name of the screenshot folder.
    """
    folder = Path(dir).resolve()
    if not folder.is_dir():
        raise Exception(f"This is not a dir: {str(folder)}. \ndir must be a valid directory")

    screenshot_folder = Path(folder, screenshot_name)
    try:
        os.mkdir(screenshot_folder)
    except FileExistsError:
        print(f"{screenshot_folder} already exist. Script will do nothing.")
    finally:
        return str(screenshot_folder)

def get_added_modified_svgs(files_added_json_path: str,
    files_modified_json_path: str):
    """
    Get the svgs added and modified from the files_changed_json_path.
    :param: files_added_json_path, the path to the files_added.json created by the gh-action-get-changed-files@2.1.4
    :param: files_modified_json_path, the path to the files_modified.json created by the gh-action-get-changed-files@2.1.4
    :return: a list of the svg file paths that were added/modified in this pr as Path. It will only return icons in /icons path (see https://github.com/devicons/devicon/issues/505)
    """
    files_added = get_json_file_content(files_added_json_path)
    files_modified = get_json_file_content(files_modified_json_path)

    svgs = []
    for file in files_added:
        path = Path(file)
        if path.suffix.lower() == ".svg" and path.as_posix().lower().startswith('icons/'):
            svgs.append(path)

    for file in files_modified:
        path = Path(file)
        if path.suffix.lower() == ".svg" and path.as_posix().lower().startswith('icons/'):
            svgs.append(path)
    
    return svgs


def write_to_file(path: str, value: any):
    """
    Write the value to a file.
    """
    with open(path, "w") as file:
        file.write(value)

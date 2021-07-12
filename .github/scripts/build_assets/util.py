import os
import re
from typing import List
import platform
import sys
import traceback


def exit_with_err(err: Exception):
    """
    Exit the current step and display the err.
    :param: err, the error/exception encountered.
    """
    traceback.print_exc()
    sys.exit(1)


def set_env_var(key: str, value: str, delimiter: str='~'):
    """
    Set the GitHub env variable of 'key' to 'value' using
    the method specified here:
    https://docs.github.com/en/free-pro-team@latest/actions/reference/workflow-commands-for-github-actions#setting-an-environment-variable
    Support both Windows and Ubuntu machines provided by GitHub Actions.

    :param: key, the name of the env variable.
    :param: value, the value of the env variable.
    :param: delimiter, the delimiter that you want to use
    to write to the file. Only applicable if the 'value' contains
    '\n' character aka a multiline string.
    """
    if platform.system() == "Windows":
        if "\n" in value:
            os.system(f'echo "{key}<<{delimiter}" >> %GITHUB_ENV%')
            os.system(f'echo "{value}" >> %GITHUB_ENV%')
            os.system(f'echo "{delimiter}" >> %GITHUB_ENV%')
        else:
            os.system(f'echo "{key}={value}" >> %GITHUB_ENV%')
    elif platform.system() == "Linux":
        if "\n" in value:
            os.system(f'echo "{key}<<{delimiter}" >> $GITHUB_ENV')
            os.system(f'echo "{value}" >> $GITHUB_ENV')
            os.system(f'echo "{delimiter}" >> $GITHUB_ENV')
        else:
            os.system(f'echo "{key}={value}" >> $GITHUB_ENV')
    else:
        raise Exception("This function doesn't support this platform: " + platform.system())


def find_object_added_in_pr(icons: List[dict], pr_title: str):
    """
    Find the icon name from the PR title. 
    :param icons, a list of the font objects found in the devicon.json.
    :pr_title, the title of the PR that this workflow was called on.
    :return a dictionary with the "name"
    entry's value matching the name in the pr_title.
    :raise If no object can be found, raise an Exception.
    """
    try:
        pattern = re.compile(r"(?<=^new icon: )\w+ (?=\(.+\))", re.I)
        icon_name = pattern.findall(pr_title)[0].lower().strip()  # should only have one match
        icon =  [icon for icon in icons if icon["name"] == icon_name][0]
        return icon
    except IndexError:  # there are no match in the findall()
        raise Exception("Couldn't find an icon matching the name in the PR title.")

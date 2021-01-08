from typing import List
import sys
import xml.etree.ElementTree as et
import time
from pathlib import Path


# pycharm complains that build_assets is an unresolved ref
# don't worry about it, the script still runs
from build_assets import filehandler, arg_getters
from build_assets import github_env


def main():
    """
    Check the quality of the svgs.
    If any error is found, set an environmental variable called ERR_MSGS
    that will contains the error messages.
    """
    args = arg_getters.get_check_svgs_args()
    new_icons = filehandler.find_new_icons(args.devicon_json_path, args.icomoon_json_path)

    if len(new_icons) == 0:
        sys.exit("No files need to be uploaded. Ending script...")

    # print list of new icons
    print("SVGs being checked:", *new_icons, sep = "\n", end='\n\n')

    time.sleep(1)  # do this so the logs stay clean
    try:
        # check the svgs
        svgs = filehandler.get_svgs_paths(new_icons, args.icons_folder_path, as_str=False)
        check_svgs(svgs)
        print("All SVGs found were good.\nTask completed.")
    except Exception as e:
        github_env.set_env_var("ERR_MSGS", str(e))
        sys.exit(str(e))


def check_svgs(svg_file_paths: List[Path]):
    """
    Check the width, height, viewBox and style of each svgs passed in.
    The viewBox must be '0 0 128 128'.
    If the svg has a width and height attr, ensure it's '128px'.
    The style must not contain any 'fill' declarations.
    If any error is found, they will be thrown.
    :param: svg_file_paths, the file paths to the svg to check for.
    """
    # batch err messages together so user can fix everything at once
    err_msgs = []
    for svg_path in svg_file_paths:
        tree = et.parse(svg_path)
        root = tree.getroot()
        namespace = "{http://www.w3.org/2000/svg}"
        err_msg = [f"{svg_path.name}:"]

        if root.tag != f"{namespace}svg":
            err_msg.append(f"-root is '{root.tag}'. Root must be an 'svg' element")

        if root.get("viewBox") != "0 0 128 128":
            err_msg.append("-'viewBox' is not '0 0 128 128' -> Set it or scale it using https://www.iloveimg.com/resize-image/resize-svg")

        acceptable_size = [None, "128px", "128"]
        if root.get("height") not in acceptable_size:
            err_msg.append("-'height' is present but is not '128' or '128px' -> Remove 'height' or set it to '128' or '128px'")

        if root.get("width") not in acceptable_size:
            err_msg.append("-'width' is present but is not '128' or '128px' -> Remove 'width' or set it to '128' or '128px'")

        if root.get("style") is not None and "enable-background" in root.get("style"):
            err_msg.append("-deprecated 'enable-background' in style attribute -> Remove it")

        if root.get("x") is not None:
            err_msg.append("-unneccessary 'x' attribute -> Remove it")

        if root.get("y") is not None:
            err_msg.append("-unneccessary 'y' attribute -> Remove it")

        style = root.findtext(f".//{namespace}style")
        if style != None and "fill" in style:
            err_msg.append("-contains style declaration using 'fill' -> Replace classes with the 'fill' attribute instead")

        if len(err_msg) > 1:
            err_msgs.append("\n".join(err_msg))

    if len(err_msgs) > 0:
        raise Exception("Errors found in these files:\n" + "\n\n".join(err_msgs))


if __name__ == "__main__":
    main()

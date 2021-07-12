from argparse import ArgumentParser
from build_assets.PathResolverAction import PathResolverAction


def get_selenium_runner_args(peek_mode=False):
    """
    Get the commandline arguments for the icomoon_peek.py and 
    icomoon_build.py.
    """
    parser = ArgumentParser(description="Upload svgs to Icomoon to create icon files.")

    parser.add_argument("--headless",
                        help="Whether to run the browser in headless/no UI mode",
                        action="store_true")

    parser.add_argument("geckodriver_path",
                        help="The path to the firefox executable file",
                        action=PathResolverAction)

    parser.add_argument("icomoon_json_path",
                        help="The path to the icomoon.json aka the selection.json created by Icomoon",
                        action=PathResolverAction)

    parser.add_argument("devicon_json_path",
                        help="The path to the devicon.json",
                        action=PathResolverAction)

    parser.add_argument("icons_folder_path",
                        help="The path to the icons folder",
                        action=PathResolverAction)

    parser.add_argument("download_path",
                        help="The download destination of the Icomoon files",
                        action=PathResolverAction)

    if peek_mode:
        parser.add_argument("--pr_title",
                            help="The title of the PR that we are peeking at")
    else:
        parser.add_argument("token",
                            help="The GitHub token to access the GitHub REST API.",
                            type=str)

    return parser.parse_args()


def get_check_svgs_on_pr_args():
    """
    Get the commandline arguments for the check_svgs_on_pr.py.
    """
    parser = ArgumentParser(description="Check the SVGs to ensure their attributes are correct. Run whenever a PR is opened")
    parser.add_argument("files_added_json_path",
                        help="The path to the files_added.json created by the gh-action-get-changed-files@2.1.4",
                        action=PathResolverAction)

    parser.add_argument("files_modified_json_path",
                        help="The path to the files_modified.json created by the gh-action-get-changed-files@2.1.4",
                        action=PathResolverAction)
    return parser.parse_args()


def get_release_message_args():
    """
    Get the commandline arguments for get_release_message.py.
    """
    parser = ArgumentParser(description="Create a text containing the icons and features added since last release.")
    parser.add_argument("token",
                        help="The GitHub token to access the GitHub REST API.",
                        type=str)
    return parser.parse_args()

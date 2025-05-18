"""
Handle labels in MS CodeOps repos
---------------------------------
Apply all labels to a new repo
Create a label for all repos
Edit a label for all repos
Delete a label for all repos
"""
import os
import argparse
import sys
import json
import re

import inquirer
import requests
from dotenv import load_dotenv

load_dotenv()

# Variables
PAT = os.environ.get("PAT")
GITHUB_BASE = "https://api.github.com/repos/equinor"
NO_HEX = "Expects hex code without leading #"


def create_all_labels(args) -> None:
    """Create all labels for new CodeOps repo"""
    # Get repo
    with open("repo_list.json", "r") as file:
        repo_list = json.load(file)

    if args.name:
        repo = args.name
    else:
        question = [inquirer.List(
            "repo",
            message="Select the repository to create labels in. Select 'Other' to add a new one",
            choices=repo_list + ["Other"],
            carousel=True,
        )]
        repo = inquirer.prompt(question)["repo"]
        if repo == "Other":
            question = [inquirer.Text(
                "new_repo",
                message="Enter the name of the new repository"
            )]
            repo = inquirer.prompt(question)["new_repo"]

    # Check if repo exists in GitHub
    url = f"{GITHUB_BASE}/{repo}"
    response = requests.get(url, headers={
        "Authorization": f"token {PAT}",
        "Accept": "application/vnd.github.v3+json"
    })
    if response.status_code == 404:
        raise Exception(f"Repository {repo} not found. Check for typos.")

    # Add repo to repo_list if not already in repo_list
    if repo not in repo_list:
        repo_list.append(repo)
        repo_list.sort(key=str.lower)
        with open("repo_list.json", "w") as file:
            json.dump(repo_list, file, indent=4)

    with open("label_list.json", "r") as file:
        label_list = json.load(file)

    # Create/update labels
    url = f"{GITHUB_BASE}/{repo}/labels"
    response = requests.get(url, headers={
        "Authorization": f"token {PAT}",
        "Accept": "application/vnd.github.v3+json"
    })
    repo_labels = [x["name"] for x in response.json()]

    for label in label_list:
        if label["name"] not in repo_labels:
            # Label does not exist, create it
            response = requests.post(url, headers={
                "Authorization": f"token {PAT}",
                "Accept": "application/vnd.github.v3+json"
            }, json=label)
            print(f"Created label {label['name']} in repo {repo}")
        else:
            # Label exists, update it
            response = requests.patch(url + f"/{label['name']}", headers={
                "Authorization": f"token {PAT}",
                "Accept": "application/vnd.github.v3+json"
            }, json=label)
            print(f"Updated label {label['name']} in repo {repo}")


def create_label(args) -> None:
    """Create a label for all CodeOps repos"""
    # Get label name, color and description
    questions = []
    answers = {}
    if args.name:
        answers["name"] = args.name
    else:
        questions.append(inquirer.Text(
            "name",
            message="What's the name of the new label?",
            validate=lambda _, x: x != ""
        ))
    if args.color:
        answers["color"] = args.color
    else:
        questions.append(inquirer.Text(
            "color",
            message=f"What's the color of the new label? {NO_HEX}",
            validate=lambda _, x: re.match(
                "^[a-fA-F0-9]{6}$", x),
        ))
    if args.desc:
        answers["description"] = args.desc
    else:
        questions.append(inquirer.Text(
            "description", message="What's the description of the new label?"))
    label = answers | inquirer.prompt(questions)

    # Remove from label_list if existing (by name), then add to label_list
    with open("label_list.json", "r") as file:
        label_list = json.load(file)
    label_list[:] = [i for i in label_list if i["name"] not in label["name"]]
    label_list.append(label)
    label_list.sort(key=lambda x: x["name"].lower())
    with open("label_list.json", "w") as file:
        json.dump(label_list, file, indent=4)

    # Loop through repo_list and create/update label for each
    with open("repo_list.json", "r") as file:
        repo_list = json.load(file)

    for repo in repo_list:
        url = f"{GITHUB_BASE}/{repo}/labels"
        response = requests.get(url + f"/{label['name']}", headers={
            "Authorization": f"token {PAT}",
            "Accept": "application/vnd.github.v3+json"
        })
        if response.status_code == 404:
            # Label does not exist, create it
            response = requests.post(url, headers={
                "Authorization": f"token {PAT}",
                "Accept": "application/vnd.github.v3+json"
            }, json=label)
            print(f"Created label {label['name']} in repo {repo}")
        elif response.status_code == 200:
            # Label exists, update it
            response = requests.patch(url + f"/{label['name']}", headers={
                "Authorization": f"token {PAT}",
                "Accept": "application/vnd.github.v3+json"
            }, json=label)
            print(f"Updated label {label['name']} in repo {repo}")


def edit_label(args) -> None:
    """Edit a label for all CodeOps repos"""
    # Get label
    with open("label_list.json", "r") as file:
        label_list = json.load(file)
        label_names = [x["name"] for x in label_list]

    if args.name:
        if args.name not in label_names:
            raise Exception((f"Label {args.name} not found. "
                             "Check for typos or add it to the label list."))
        label_name = args.name
    else:
        question = [inquirer.List(
            "label",
            message="Select label to edit",
            choices=label_names,
            carousel=True,
        )]
        label_name = inquirer.prompt(question)["label"]
    label_index = label_names.index(label_name)
    label = label_list[label_index]

    # Select value(s) to edit
    questions = []
    answers = {}
    if args.new_name:
        answers["name"] = args.new_name
    else:
        questions.append(inquirer.Text(
            "name",
            message=f"What's the new name of {label_name}?",
            default=label["name"],
        ))
    if args.color:
        answers["color"] = args.color
    else:
        questions.append(inquirer.Text(
            "color",
            message=f"What's the new color of {label_name}? {NO_HEX}",
            default=label["color"],
            validate=lambda _, x: re.match(
                "^[a-fA-F0-9]{6}$", x),
        ))
    if args.desc:
        answers["description"] = args.desc
    else:
        questions.append(inquirer.Text(
            "description",
            message=f"What's the new description of {label_name}?",
            default=label["description"],
        ))
    new_label = answers | inquirer.prompt(questions)

    # Ensure name is not empty, default to existing name
    if not new_label["name"]:
        new_label["name"] = label_name
    # If no changes, exit
    if new_label == label:
        raise Exception(f"No changes made for {label_name}. Aborting")

    # Save new label to label_list
    label_list[label_index] = new_label
    label_list.sort(key=lambda x: x["name"].lower())
    with open("label_list.json", "w") as file:
        json.dump(label_list, file, indent=4)

    # new_name if update, name if create
    new_label["new_name"] = new_label["name"]

    # Loop through repo_list and update label for each (if existing. If not, create)
    print(f"Editing label {label_name} to {new_label}")
    with open("repo_list.json", "r") as file:
        repo_list = json.load(file)

    for repo in repo_list:
        url = f"{GITHUB_BASE}/{repo}/labels"
        response = requests.get(url + f"/{label_name}", headers={
            "Authorization": f"token {PAT}",
            "Accept": "application/vnd.github.v3+json"
        })
        if response.status_code == 404:
            # Label does not exist, create it
            response = requests.post(url, headers={
                "Authorization": f"token {PAT}",
                "Accept": "application/vnd.github.v3+json"
            }, json=new_label)
            print(f"Created label {label_name} in repo {repo}")
        elif response.status_code == 200:
            # Label exists, update it
            response = requests.patch(url + f"/{label_name}", headers={
                "Authorization": f"token {PAT}",
                "Accept": "application/vnd.github.v3+json"
            }, json=new_label)
            print(f"Updated label {label_name} in repo {repo}")


def delete_label(args) -> None:
    """Delete a label from all CodeOps repos"""
    # Get labels
    with open("label_list.json", "r") as file:
        label_list = json.load(file)
        label_names = [x["name"] for x in label_list]

    if args.name:
        labels = [args.name]
    else:
        question = [inquirer.Checkbox(
            "label",
            message="Select labels to delete (use space to select)",
            choices=label_names,
            carousel=True,
        )]
        labels = inquirer.prompt(question)["label"]

    # Are you sure?
    if args.force:
        user_sure = True
    else:
        user_sure = inquirer.confirm(f"This will delete label(s) {labels}. "
                                     "Continue?", default=False)
    if not user_sure:
        print("Aborting...")
        return -1

    # Remove labels from label_list
    label_list[:] = [i for i in label_list if i["name"] not in labels]
    with open("label_list.json", "w") as file:
        json.dump(label_list, file, indent=4)

    # Loop through repo_list and delete labels for each (if existing)
    with open("repo_list.json", "r") as file:
        repo_list = json.load(file)

    for label in labels:
        for repo in repo_list:
            url = f"{GITHUB_BASE}/{repo}/labels/{label}"
            response = requests.delete(url, headers={
                "Authorization": f"token {PAT}",
                "Accept": "application/vnd.github.v3+json"
            })
            if response.status_code == 204:
                print(f"Deleted label {label} from repo {repo}")
            elif response.status_code == 404:
                print(f"Label {label} not found in repo {repo}")
            else:
                print(f"Error deleting label {label} from repo {repo}: "
                      f"{response.status_code}")


if __name__ == "__main__":
    # Set up command-line options, arguments, and subcommands
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=lambda prog: argparse.RawDescriptionHelpFormatter(
            prog, max_help_position=100, width=200))
    parser.add_argument("-d", "--debug",
                        action="store_true",
                        help="set flag to see full stack trace")
    subparsers = parser.add_subparsers(required=True,
                                       metavar="action")
    # Create all labels in new repo
    parser_repo = subparsers.add_parser("repo",
                                        help="create labels in new repo",
                                        aliases=["r"],
                                        description=create_all_labels.__doc__)
    parser_repo.add_argument("-n", "--name", help="Name of repository")
    parser_repo.set_defaults(func=create_all_labels)
    # Create new label in all repos
    parser_create = subparsers.add_parser("create",
                                          help="create new label",
                                          aliases=["c"],
                                          description=create_label.__doc__)
    parser_create.add_argument("-n", "--name", help="Name of new label")
    parser_create.add_argument(
        "-c", "--color", help="Color of new label (hex code without #)")
    parser_create.add_argument("-d", "--desc", help="Description of new label")
    parser_create.set_defaults(func=create_label)
    # Edit label in all repos
    parser_edit = subparsers.add_parser("edit",
                                        help="edit existing label",
                                        aliases=["e"],
                                        description=edit_label.__doc__)
    parser_edit.add_argument("-n", "--name", help="Name of label to edit")
    parser_edit.add_argument(
        "-nn", "--new-name", help="Name to change to")
    parser_edit.add_argument(
        "-c", "--color", help="Color to change to (hex code without #)")
    parser_edit.add_argument(
        "-d", "--desc", help="Description to change to")
    parser_edit.set_defaults(func=edit_label)
    # Delete label from all repos
    parser_delete = subparsers.add_parser("delete",
                                          help="create new label",
                                          aliases=["d"],
                                          description=delete_label.__doc__)
    parser_delete.add_argument("-n", "--name", help="Name of label to delete")
    parser_delete.add_argument("-f", "--force", help="Set flag to skip confirmation",
                               action="store_true",
                               default=False)
    parser_delete.set_defaults(func=delete_label)

    args = parser.parse_args()
    # Set tracebacklimit to 0 to hide traceback unless debug flag is set
    if not args.debug:
        sys.tracebacklimit = 0
    args.func(args)  # Run function based on subcommand

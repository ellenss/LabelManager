[![SCM Compliance](https://scm-compliance-api.radix.equinor.com/repos/equinor/MS-LabelManager/badge)](https://scm-compliance-api.radix.equinor.com/repos/equinor/MS-LabelManager/badge)

# MS LabelManager

When using a GitHub board with many different repositories, it might be an advantage for all of the repositories to have the same issue labels. This Label Manager will help you keep the labels in sync across the repos.

## Local Development

### Set up virtual environment

Run this command to create a venv (virtual environment): ```python -m venv ./.venv```

Run one of the following commands to activate the environment, depending on your system:

| Platform | Shell | Command |
| - | - | - |
| POSIX | bash/zsh | ```source <venv>/bin/activate``` |
| POSIX | fish | ```source <venv>/bin/activate.fish``` |
| POSIX | csh/tcsh | ```source <venv>/bin/activate.csh``` |
| POSIX | pwsh | ```<venv>/bin/Activate.ps1``` |
| WINDOWS | cmd.exe | ```<venv>\Scripts\activate.bat``` |
| WINDOWS | PowerShell | ```<venv>\Scripts\Activate.ps1``` |

### Install required packages

The necessary packages are listed in *requirements.txt*. To install them, run the command ```pip install -r requirements.txt```.

If these packages get updated or more are used, run the command ```pip freeze > requirements.txt``` to generate a new file.

The main external packages are **requests** to communicate with GitHub through the [GitHub API](https://docs.github.com/en/rest?apiVersion=2022-11-28) (mainly the */Issues/Labels* endpoints), and **inquirer** to communicate with the user (user input).

### Environment variables

The only environment variable used is your personal access token in GitHub, so that the requests sent to GitHub has the same permissions as your GitHub user. This means that you need to create a PAT [here](https://github.com/settings/tokens). Remember to authorize it for Equinor!

Create a .env file, with content that looks like this:
```PAT={your pat token}```

### Run the script

```py label.py -h```

## What This Script Does

This script contains four commands:
1. Create all existing labels in a repo.
2. Create a new label in all existing repos.
3. Edit an existing label in all existing repos.
4. Delete one or more labels in all existing repos.

To see the possible commands, run ```py label.py -h```. If you get an error under development that you don't understand, add the debug flag (-d or --debug) to get the full stack trace.

Note that whenever a reference is made to an "existing" or "new" repo or label, that is based on if it exists in *repo_list.json* and *label_list.json* respectively.

### Add all labels to a repo

Command: ```py label.py r```

Optional arguments:
- **-n/--name** to set the name of the repo to add the labels to.

If name is not given, you will be given a list of the repos in *repo_list.json* to choose from, in addition to the option of choosing a new repo. After choosing a repo, the script will check that it is a repo it can reach before adding it to *repo_list.json* if it's not already there.

It will then loop through all the existing labels to create the labels that does not exist in the repo, and update the ones that do.

### Create a new label

Command: ```py label.py c```

Optional arguments:
- **-n/--name** to set the name of the new label.
- **-c/--color** to set the color of the new label (hex code, without the hash).
- **-d/--desc** to set the description of the new label.

If any of the optional arguments are not given, the script will prompt you for the ones that are missing. It will then add the new label to *label_list.json*, or update it if it already exists. This means that this command could technically be used instead of the "edit" command if the name is not the field being updated.

Now it will loop through all the existing repos to create the new label if it does not already exists, and update it if it does.

### Edit an existing label

Command: ```py label.py e```

Optional arguments:
- **-n/--name** to set the name of the label to edit.
- **-nn/--new-name** to set the new name of the label.
- **-c/--color** to set the new color.
- **-d/--desc** to set the new description.

If any of the optional arguments are not given, the script will ask if you want to change any of them. Accept the default value (the current one) to not update a field.

If there are any changes, *label_list.json* will be updated with the new data before looping through the existing repos to update (or create) the label.

### Delete an existing label

Command: ```py label.py d```

Optional arguments:
- **-n/--name** to set name of the label to delete.
- **-f/--force** to skip confirmation.

If the optional argument for name is not given, you will be able to select one or more existing labels to delete. If the "force" flag is not set, you will get a confirmation check before it moves forward.

After you confirm (or if you set the "force" flag), the label will be removed from *label_list.json*. Then the script loops through the repos to delete the label from them.

## Contributing

Do you want to make this better? Great! For contributors outside the Equinor organization, the preferred way of submitting a contribution is by forking the project and making a pull request.

### Commit messages

We write our commit messages according to this guide:

- `feat:` a feature
- `fix:` a bugfix
- `wip:` work-in-progress, a code change that is not available/visible to the end user
- `build:` a change to build tool or external dependencies (npm, nuget, etc.)
- `ci:` a change to continuos integration/delivery setup (typically scripts and config files)
- `docs:` a change to documentation (content, for devops team and end users)
- `style:` a change that does not change behavior of code (whitespace, formatting, missing semi-colons etc.)
- `refactor:` a code change that neither fixes a bug nor adds/removes a feature
- `perf:` a code change that improves performance
- `test:` a change to tests/test tools
- `chore:` everything else

### Style

This project is following the [Python Style Guide](https://peps.python.org/pep-0008/). If contributing, make sure to follow it. Install the **autopep8** extension in VS Code for easy formatting.

prompt = (
    'Translate following text from english to belarusian: Rommel was a highly'
    ' decorated officer in World War I and was awarded the Pour le Mérite for'
    ' his actions on the Italian Front. In 1937, he published his classic'
    ' book on military tactics, Infantry Attacks, drawing on his experiences'
    ' in that war. In World War II, he commanded the 7th Panzer Division'
    ' during the 1940 invasion of France. His leadership of German and Italian'
    ' forces in the North African campaign established his reputation as one'
    ' of the ablest tank commanders of the war, and earned him the nickname'
    ' der Wüstenfuchs, "the Desert Fox". Among his British adversaries he had'
    ' a reputation for chivalry, and his phrase "war without hate" has been'
    ' uncritically used to describe the North African campaign.[2] A number'
    ' of[weasel words] historians have since rejected the phrase as a myth'
    ' and uncovered numerous examples of German war crimes and abuses towards'
    ' enemy soldiers and native populations in Africa during the conflict.[3]'
    ' Other historians note that there is no clear evidence Rommel was'
    ' involved or aware of these crimes,[4] with some pointing out that the'
    ' war in the desert, as fought by Rommel and his opponents, still came'
    ' as close to a clean fight as there was in World War II.[5] He later'
    ' commanded the German forces opposing the Allied cross-channel invasion'
    ' of Normandy in June 1944.'
)


import pathlib  # noqa
import os  # noqa
import re  # noqa


def print_directory_tree(
    directory_path,
    max_depth=float('inf'),
    show_hidden=False,
    ignored_files_regex=None,
):
    """
    Prints a beautiful tree structure of files and folders.

    Args:
    - directory_path (str): Path to the directory to visualize
    - max_depth (int): Maximum depth of tree to display (default: unlimited)
    - show_hidden (bool): Whether to show hidden files/folders (default: False)
    """
    if ignored_files_regex is None:
        ignored_files_regex = [
            r'\.pyc$',  # Python compiled files
            r'\.log$',  # Log files
            r'__pycache__',  # Python cache directories
            r'\.git',  # Git directories
            r'front',
            r'\.sql',
            r'translator.yml',
            r'\.txt',
            r'\.uml',
            r'test.py',
            r'README.md',
            r'insert_mock_reports.md',
            r'\.env',
            r'selfsigned',
        ]

    def _tree(directory, prefix='', depth=0) -> int:
        loc = 0

        if depth > max_depth:
            return loc

        # Convert to absolute path and get contents
        directory = pathlib.Path(directory).resolve()

        # Get contents, optionally filtering out hidden items
        try:
            contents = sorted(
                directory.iterdir(),
                key=lambda p: (not p.is_dir(), p.name.lower()),
            )
        except PermissionError:
            print(f'{prefix}🚫 Access denied')
            return loc

        # Filter out hidden files if show_hidden is False
        if not show_hidden:
            contents = [
                item for item in contents if not item.name.startswith('.')
            ]

        ignore_patterns = [
            re.compile(pattern) for pattern in ignored_files_regex
        ]
        # Iterate through contents
        for index, path in enumerate(contents):
            # Determine connector and branch style
            is_last = index == len(contents) - 1
            connector = '└── ' if is_last else '├── '

            # Create visual prefix
            if depth > 0:
                display_prefix = prefix + connector
            else:
                display_prefix = connector

            # Color and icon for different types
            if path.is_dir():
                if any(
                    pattern.search(path.name) for pattern in ignore_patterns
                ):
                    continue
                print(f'\033[1;34m{display_prefix}{path.name}/\033[0m')
                # Recursive call for subdirectories
                loc += _tree(
                    path, prefix + ('    ' if is_last else '│   '), depth + 1
                )
            else:
                if any(
                    pattern.search(path.name) for pattern in ignore_patterns
                ):
                    continue
                # Different color for files
                with open(path, 'r') as f:
                    file_LOC = len(f.readlines())
                    loc += file_LOC
                    print(
                        f'\033[0;32m{display_prefix}{path.name}\033[0m - {file_LOC}'
                    )
        return loc

    # Validate input directory
    if not os.path.exists(directory_path):
        print(f'Error: {directory_path} does not exist.')
        return 0

    # Print root directory
    print(f'\033[1;36m{directory_path}/\033[0m')

    # Start tree rendering
    print(f'Total LOC: {_tree(directory_path)}')


def get_matching_files(
    directory_path, file_exclude_regex, show_hidden=False
) -> list[str]:
    """
    Prints all filenames (relative paths) that match a given regex.

    Args:
        - directory_path (str): Path to the directory to search files in.
        - file_match_regex (str): Regex to match filenames.
        - show_hidden (bool): Whether to include hidden files/folders (default: False).
    """
    compiled_exclude_regex = re.compile(file_exclude_regex)

    def _search_files(directory, relative_prefix='') -> list[str]:
        directory = pathlib.Path(directory).resolve()
        file_paths = []
        try:
            contents = sorted(
                directory.iterdir(), key=lambda p: p.name.lower()
            )
        except PermissionError:
            print(f'Access denied: {directory}')
            return []

        for path in contents:
            if not show_hidden and path.name.startswith('.'):
                continue

            relative_path = os.path.join(relative_prefix, path.name)

            if compiled_exclude_regex.search(path.name):
                continue

            if path.is_dir():
                file_paths += _search_files(path, relative_path)
            else:
                file_paths.append(str(path.absolute()))
        return file_paths

    if not os.path.exists(directory_path):
        print(f'Error: {directory_path} does not exist.')
        return []

    print(
        f"Searching for files except for regex '{file_exclude_regex}' in "
        f"'{directory_path}':\n"
    )
    return _search_files(directory_path)


def print_files_for_applications():
    file_paths = get_matching_files(
        directory_path=os.path.curdir,
        file_exclude_regex=r'\.venv|__pycache__|front|.idea|.dockerignore|'
        r'\.env|\.local\.env|translator\.yml|юзкейс\.txt|'
        r'test\.py|insert_mock_reports\.py|vue-dev|'
        r'selfsigned|\.log'
        r'|contrib',
        show_hidden=True,
    )
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            # remove absolute prefix
            print(f'====={file_path[33:]}=====')
            print(f.read())


# print_directory_tree(
#     '/home/aleh/7-term/_curse/diploma',
# )
# print_files_for_applications()

import asyncio
from src.util.translator.classes import Gpt4freeTranslator

translator = Gpt4freeTranslator()
asyncio.run(translator.get_response({}))

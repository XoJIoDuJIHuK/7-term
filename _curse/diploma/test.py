import asyncio
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.database.models import Article, AIModel, StylePrompt, Language
from src.util.storage.classes import RedisHandler
from src.util.translator.classes import Gpt4freeTranslator

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

# import google.generativeai as genai
#
# genai.configure(api_key='AIzaSyBmKikk9iZfTFCzUL7wPLFY1lcJNNah4VM')
# model = genai.GenerativeModel("gemini-1.5-flash")
# response = model.generate_content(prompt)
#
# print(response.text)

# async def main():
#     async with get_session() as db:
#         article = (await db.execute(select(Article).filter_by(id=uuid.UUID('c10394b8-5cdd-4d88-9d25-0e654678ab64')))).scalars().first()
#         model = (await db.execute(select(AIModel).filter_by(id=1))).scalars().first()
#         prompt = (await db.execute(select(StylePrompt).filter_by(id=1))).scalars().first()
#         language = (await db.execute(select(Language).filter_by(id=5))).scalars().first()
#
#         await Gpt4freeTranslator().translate(
#             text='hello, it\'s me, Mario',
#             source_language=None,
#             target_language=language,
#             model=model,
#             prompt_object=prompt
#         )
# if __name__ == '__main__':
#     asyncio.run(main())

# from src.logger import get_logger
# logger = get_logger(__name__)
#
# logger.info('INFO')
# logger.warning('WARNING')
# logger.debug('DEBUG')
# logger.error('ERROR')
# logger.exception('EXCEPTION')


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
        LOC = 0

        if depth > max_depth:
            return LOC

        # Convert to absolute path and get contents
        directory = pathlib.Path(directory).resolve()

        # Get contents, optionally filtering out hidden items
        try:
            contents = sorted(
                directory.iterdir(),
                key=lambda p: (not p.is_dir(), p.name.lower())
            )
        except PermissionError:
            print(f"{prefix}🚫 Access denied")
            return LOC

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
                print(f"\033[1;34m{display_prefix}{path.name}/\033[0m")
                # Recursive call for subdirectories
                LOC += _tree(
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
                    LOC += file_LOC
                    print(f"\033[0;32m{display_prefix}{path.name}\033[0m - {file_LOC}")
        return LOC

    # Validate input directory
    if not os.path.exists(directory_path):
        print(f"Error: {directory_path} does not exist.")
        return 0

    # Print root directory
    print(f"\033[1;36m{directory_path}/\033[0m")

    # Start tree rendering
    print(f'Total LOC: {_tree(directory_path)}')


print_directory_tree(
    '/home/aleh/7-term/_curse/diploma',
)

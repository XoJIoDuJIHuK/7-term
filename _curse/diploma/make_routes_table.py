import os
import re
from pathlib import Path


def scan_routers(routers_path):
    results = []

    # Regular expressions
    prefix_pattern = r"prefix=(?:'([^']*)'|)"
    tags_pattern = r"tags=\[(?:'([^']*)'|)\]"
    tags_pattern = r"tags=\['([^']+)'\]"
    router_pattern = r"@router\.([a-z]+)\(\s*'([^']+)'"
    function_pattern = r"async def ([^\(]+)\("

    # Walk through all subdirectories in routers folder
    for root, dirs, files in os.walk(routers_path):
        for file in files:
            if file == 'views.py':
                file_path = os.path.join(root, file)

                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                    # Find prefix and controller (tags)
                    prefix_match = re.search(prefix_pattern, content)
                    tags_match = re.search(tags_pattern, content)

                    if prefix_match and tags_match:
                        prefix = prefix_match.group(1)
                        controller = tags_match.group(1)

                        # Find all router decorators and corresponding function names
                        router_matches = re.finditer(router_pattern, content)
                        function_matches = re.finditer(function_pattern,
                                                       content)

                        # Convert iterator to list for functions
                        functions = [m.group(1) for m in function_matches]

                        # Process router matches which now include both method and path
                        paths_and_methods = [(m.group(2), m.group(1).upper())
                                             for m in router_matches]

                        # Pair paths, methods with functions
                        for (path, method), func in zip(paths_and_methods,
                                                        functions):
                            results.append({
                                'prefix': prefix,
                                'path': path,
                                'method': method,
                                'controller': controller,
                                'function': func.strip()
                            })

    return results


def main():
    # Get absolute path to the routers directory
    # Assuming the script is in the project root
    routers_path = Path('/home/aleh/7-term/_curse/diploma/src/routers')

    # Scan all routers
    endpoints = scan_routers(routers_path)

    # Sort results by controller and path for better organization
    endpoints.sort(key=lambda x: (x['controller'], x['path']))

    # Create tab-separated output (easily pasteable into Word table)
    output = "Prefix\tPath\tMethod\tController\tFunction\n"
    for endpoint in endpoints:
        output += f"{endpoint['prefix'] or 'Нет'}\t{endpoint['path']}\t{endpoint['method']}\t{endpoint['controller']}\t{endpoint['function']}\n"

    # Write to output file
    output_path = Path(__file__).parent / 'endpoints_table.txt'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output)

    print(f"Table data has been written to {output_path}")
    print(
        "You can now copy the contents of this file and paste them into a Word table")


if __name__ == "__main__":
    main()

from configparser import ConfigParser
from pathlib import Path


def config(filename='database.ini', section='postgresql'):
    # Create a parser
    parser = ConfigParser()

    # Get the directory where this script is located
    config_dir = Path(__file__).parent
    config_path = config_dir / filename

    # Read config file
    parser.read(config_path)

    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(f"Section {section} not found in the {filename} file.")
    
    return db
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "file_path",
    nargs="?",
    help="The path to the HTML file to be processed.",
    type=str,
)
parser.add_argument(
    "--text",
    nargs="?",
    help="Converts the HTML file to text and exits."
)
parser.add_argument(
    "--local",
    nargs="?",
    help="Analyzes a file without calling the GPT-3.5 API."
)
parser.add_argument("--citation",
    nargs="?",
    help="Extracts citations and exits."
)
args = parser.parse_args()

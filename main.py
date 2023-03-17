from cli import args
from case_brief import text_argument, classify_firac


if __name__ == "__main__":
    if args.text is None:
        text = text_argument(args.file_path)
    else:
        text = args.text
    firac = classify_firac(text)

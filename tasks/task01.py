import asyncio
from pathlib import Path
import shutil
import logging
import argparse


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


async def read_folder(source: Path, output: Path):
    try:
        tasks = []
        entries = await asyncio.to_thread(list, source.iterdir())
        for entry in entries:
            if entry.is_file():
                tasks.append(copy_file(entry, output))
            elif entry.is_dir():
                tasks.append(read_folder(entry, output))
        await asyncio.gather(*tasks)
    except Exception as e:
        logging.error(f"Error while reading folder {source}: {e}")


async def copy_file(file: Path, output: Path):
    try:
        extension = file.suffix.lstrip('.').lower() or 'no_extension'
        target_folder = output / extension

        if not target_folder.exists():
            await asyncio.to_thread(target_folder.mkdir, parents=True, exist_ok=True)

        target_file = target_folder / file.name
        await asyncio.to_thread(shutil.copy, file, target_file)
        logging.info(f"File {file} copied successfully to {target_file}")
    except Exception as e:
        logging.error(f"Error copying file {file}: {e}")


async def main():
    parser = argparse.ArgumentParser(description='Files sorting by extensions')
    parser.add_argument('source', help='Source folder path')
    parser.add_argument('output', help='Destination folder path')
    args = parser.parse_args()

    source = Path(args.source).resolve()
    output = Path(args.output).resolve()

    if not source.exists() or not source.is_dir():
        logging.error("Source folder not found or is not a directory.")
        return

    if not output.exists():
        await asyncio.to_thread(output.mkdir, parents=True, exist_ok=True)

    await read_folder(source, output)


if __name__ == '__main__':
    asyncio.run(main())
    
"""
Download the MSHA data.
"""
import io
from zipfile import ZipFile

import requests

import local


def _get_url_contents(url, compressed=False):
    """Return a bytes object of url contents."""
    content = requests.get(url)
    if compressed:
        zip_file = ZipFile(io.BytesIO(content.content))
        file_name = zip_file.namelist()
        handle = zip_file.open(file_name[0])
        return handle.read()
    else:
        return content.content


if __name__ == "__main__":
    # first download data
    for name, url in local.msha_download_url.items():
        contents = _get_url_contents(url, compressed=True)
        with open(local.msha_raw_data_paths[name], 'wb') as fi:
            fi.write(contents)

    # then definitions
    for name, url in local.msha_defintion_url.items():
        contents = _get_url_contents(url)
        with open(local.msha_definition_paths[name], 'wb') as fi:
            fi.write(contents)

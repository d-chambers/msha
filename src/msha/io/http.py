"""
Dataset for downloading files with http
"""
import copy
import socket
from io import BytesIO
from typing import Any, Dict, Optional, Tuple, Union
from pathlib import Path

import pandas as pd
import requests
from requests.auth import AuthBase

from kedro.io.core import (
    AbstractDataSet,
    DataSetError,
    DataSetNotFoundError,
    deprecation_warning,
)


class CSVHTTPDataSet(AbstractDataSet):
    """
    ``CSVHTTPDataSet`` loads the data from HTTP(S), or saved path,
    and pareses into o Pandas dataframe.
    """

    def __init__(
        self,
        file_url: str,
        file_path: str = None,
        auth: Optional[Union[Tuple[str], AuthBase]] = None,
        load_args: Optional[Dict[str, Any]] = None,
        force_download: bool = False,
    ) -> None:
        """Creates a new instance of ``CSVHTTPDataSet`` pointing to a concrete
        csv file over HTTP(S).

        Args:
            fileurl: A URL to fetch the CSV file.
            auth: Anything ``requests.get`` accepts. Normally it's either
            ``('login', 'password')``, or ``AuthBase`` instance for more complex cases.
            load_args: Pandas options for loading csv files.
                Here you can find all available arguments:
                https://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_csv.html
                All defaults are preserved.
        """
        deprecation_warning(self.__class__.__name__)
        super().__init__()
        self._file_url = file_url
        self._file_path = file_path
        self._auth_backend = auth
        self._load_args = copy.deepcopy(load_args or {})
        self._force_download = force_download

    def _describe(self) -> Dict[str, Any]:
        return dict(fileurl=self._file_url, load_args=self._load_args)

    def _execute_request(self):
        try:
            response = requests.get(self._file_url, auth=self._auth_backend)
            response.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            if (
                exc.response.status_code
                == requests.codes.NOT_FOUND  # pylint: disable=no-member
            ):
                raise DataSetNotFoundError(
                    "The server returned 404 for {}".format(self._file_url)
                )
            raise DataSetError("Failed to fetch data")
        except socket.error:
            raise DataSetError("Failed to connect to the remote server")

        return response

    def _load(self) -> pd.DataFrame:
        if self._file_path is not None and Path(self._file_path).exists():
            df = pd.read_csv(self._file_path, **self._load_args)
        else:
            response = self._execute_request()
            df = pd.read_csv(BytesIO(response.content), **self._load_args)
        return df

    def _save(self, data=None) -> None:
        if self._file_path is None:
            msg = f"The parameter file_path must be defined to save."
            raise DataSetError(msg)

        # dataset already exists, simply do nothing.
        if Path(self._file_path).exists() and not self._force_download:
            return

        response = self._execute_request()
        with open(self._file_path, "wb") as fi:
            fi.write(response.content)

    def _exists(self) -> bool:
        if self._file_path is not None and Path(self._file_path).exists():
            return True
        try:
            response = self._execute_request()
        except DataSetNotFoundError:
            return False

        # NOTE: we don't access the actual content here, which might be large.
        return response.status_code == requests.codes.OK  # pylint: disable=no-member


class URLContentsDirectory(AbstractDataSet):
    """
    Given a dict of URL, download the contents and save each to a file (key).
    """

    def __init__(self, filepath=None):
        self.filepath = Path(filepath)

    def _load(self) -> Any:
        raise DataSetError("cant load this dataset")

    def _save(self, data: dict) -> None:
        """
        Save the contents of a dict to disk.
        """
        if self.filepath.exists():
            return
        for name, url in data.items():
            path = self.filepath / name
            path.parent.mkdir(exist_ok=True, parents=True)
            content = self.execute_request(url).content
            with path.open("wb") as fi:
                fi.write(content)

    @staticmethod
    def execute_request(url):
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            if (
                exc.response.status_code
                == requests.codes.NOT_FOUND  # pylint: disable=no-member
            ):
                raise ValueError("The server returned 404 for {}".format(url))
            raise ValueError("Failed to fetch data")
        except socket.error:
            raise ValueError("Failed to connect to the remote server")
        return response

    def _describe(self) -> Dict[str, Any]:
        return {}

    def _exists(self) -> bool:
        return self.filepath.exists()

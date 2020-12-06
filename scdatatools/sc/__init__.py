import io
import sys
import json
import shutil
import tempfile
from pathlib import Path

from rsi.launcher import LauncherAPI
from scdatatools.p4k import P4KFile
from scdatatools.forge import DataCoreBinary, DataCoreBinaryMMap

from .config import Profile
from .localization import SCLocalization

TRY_VERSION_FILES = ['f_win_game_client_release.id', 'c_hiload_crash_handler.id', 'c_hiload_crash_handler.id']


class StarCitizen:
    def __init__(self, game_folder, p4k_file='Data.p4k'):
        self.branch = self.build_time_stamp = self.config = self.version = None
        self.version_label = self.shelved_change = self.tag = None
        self._fetch_label_success = False

        self.game_folder = Path(game_folder).absolute()
        if not self.game_folder.is_dir():
            raise ValueError(f'{self.game_folder} is not a directory')

        self._p4k = None
        self.p4k_file = self.game_folder / p4k_file
        if not self.p4k_file.is_file():
            raise ValueError(f'Could not find p4k file {self.p4k_file}')

        self._datacore_tmp = self._datacore = None
        self._localization = self._profile = None

        for ver_file in TRY_VERSION_FILES:
            if (self.game_folder / ver_file).is_file():
                with (self.game_folder / ver_file).open('r') as f:
                    # try to read the version info out of the file
                    try:
                        data = json.loads(f.read())["Data"]
                        self.branch = data.get("Branch", None)
                        self.build_date_stamp = data.get("BuildDateStamp", None)
                        self.build_time_stamp = data.get("BuildTimeStamp", None)
                        self.config = data.get("Config", None)
                        self.version = data.get("RequestedP4ChangeNum", None)
                        self.shelved_change = data.get("Shelved_Change", None)
                        self.tag = data.get("Tag", None)
                        self.version_label = (
                            f"{self.branch}-{self.version}"  # better than nothing
                        )
                        break
                    except:  # noqa
                        pass
        else:
            sys.stderr.write(
                f"Warning: Unable to determine version of StarCitizen"
            )

    @property
    def localization(self):
        if self._localization is None:
            self._localization = SCLocalization(self.p4k)
        return self._localization

    @property
    def default_profile(self):
        if self._profile is None:
            self._profile = Profile(self, 'Data/Libs/Config/defaultProfile.xml')
        return self._profile

    @property
    def p4k(self):
        if self._p4k is None:
            self._p4k = P4KFile(self.p4k_file)
        return self._p4k

    @property
    def datacore(self):
        if self._datacore is None:
            dcb = self.p4k.search('*Game.dcb')
            if len(dcb) != 1:
                raise ValueError('Could not determine the location of the datacore')
            with self.p4k.open(dcb[0]) as f:
                self._datacore_tmp = tempfile.TemporaryFile()
                shutil.copyfileobj(f, self._datacore_tmp)
                self._datacore_tmp.seek(0)
                self._datacore = DataCoreBinary(DataCoreBinaryMMap(self._datacore_tmp))
        return self._datacore

    def gettext(self, key, language=None):
        return self.localization.gettext(key, language)

    def fetch_version_label(self, rsi_session, force=False) -> str:
        """ Try to get the version label from the launcher API for this version. This will only work for currently
        accessible versions. This will also set `self.version_label` to the fetched label.

        :param rsi_session: An authenticated `RSISession`
        :param force: Force update the version label even if it has successfully been fetched already.
        """
        if self._fetch_label_success and not force:
            return self.version_label

        launcher = LauncherAPI(session=rsi_session)
        try:
            for games in launcher.library["games"]:
                if games["id"] == "SC":
                    for version in games["channels"]:
                        if version.get("version", None) == self.version:
                            self.version_label = version["versionLabel"]
                            return self.version_label
            else:
                sys.stderr.write(
                    f"Could not determine version label for {self.version} "
                    f"from library {launcher.library}"
                )
                return ""
        except KeyError:
            return ""

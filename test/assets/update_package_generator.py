#!/usr/bin python3
# Copyright (c) 2017-2021, Mudita Sp. z.o.o. All rights reserved.
# For licensing, see https://github.com/mudita/MuditaOS/LICENSE.md

import os
import json
import tarfile
import shutil
from enum import Enum
from hashlib import md5
from download_asset import Getter
from tempfile import TemporaryDirectory


def get_0_versions():
    return {"boot.bin": "0.0.0",
            "updater.bin": "0.0.0", "ecoboot.bin": "0.0.0"}


def get_none_checksums():
    return {"boot.bin": None,
            "updater.bin": None, "ecoboot.bin": None}


def gen_version_json(workdir, versions, checksums=None):
    '''
    Create version.json in {workdir} for: boot.bin, updater.bin and ecoboot.bin if available in {workdir}
    - if no checksums provided, these will be calculated
    - if versions are not provided 0.0.0 versions are set
    '''
    version_json = {}
    # our dumb locations in json
    locations = {"boot.bin": "boot",
                 "updater.bin": "updater", "ecoboot.bin": "bootloader"}

    for file in os.listdir(workdir):
        if file in locations.keys():
            print(f"File to md5 {file}")
            if checksums is None or checksums[file] is None:
                with open(file, "rb") as f:
                    md5sum = md5(f.read()).hexdigest()
                    print(f"checksum: {md5sum}")
                    version_json[locations[file]] = {
                        "filename": file, "version": versions[file], "md5sum": md5sum}
    with open(workdir + "/version.json", "w") as f:
        print(f"saving version.json: {version_json}")
        f.write(json.dumps(version_json, indent=4, ensure_ascii=True))


def gen_deprecated_updater(workdir):
    '''
    first release of updater.bin is set to 0.0.1, defaults are 0.0.0 in gen_version
    therefore update of updater should not happen and update should fail
    TODO: discuss if we should fail update or i.e. do partial update.
          generally it's possible to update updater and boot.bin separatelly with separate package
          so this shouldn't be an issue
          on the other hand - if we want to not fail with partial update success - then
          it should make logic considerably more convoluted
    '''
    v = get_0_versions()
    gen_version_json(workdir, v)


def gen_same_updater(workdir, version: str):
    '''
    we should fail if software version is the same
    '''
    versions = get_0_versions()
    versions["updater.bin"] = version
    gen_version_json(workdir, versions)


def gen_too_big_updater(workdir, version: str):
    '''
    we can update only one version up
    '''
    versions = get_0_versions()
    version = version.split('.')
    if len(version) < 3:
        RuntimeError("Version has to be in format int.int.int <- three integers split with coma")
    # smallest version +1
    versions["updater.bin"] = version[2] + 2
    gen_version_json(workdir, versions)


class Version(Enum):
    Patch = 2
    Minor = 1
    Major = 0


def gen_version_up_updater(workdir, version: str, what: Version):
    '''
    we can update only one version up of version:
        - Patch, Minor and Major - all should be tested
    '''
    versions = get_0_versions()
    version = version.split('.')
    if len(version) < 3:
        RuntimeError("Version has to be in format int.int.int <- three integers split with coma")
    # smallest version +1
    versions["updater.bin"] = version[what.value] + 1
    gen_version_json(workdir, versions)


def gen_updater_bad_checksum(workdir):
    '''
    we can update only when checksum is proper
    '''
    checksums = get_none_checksums()
    checksums['updater.bin'] = "deadbeefdeadbeefdeadbeefdeadbeef"
    v = get_0_versions()
    gen_version_json(workdir, v, checksums)


def gen_updater_zero_checksum(workdir):
    '''
    we can update only when checksum is proper
    - 0 checksum is corner case check
    '''
    checksums = get_none_checksums()
    checksums['updater.bin'] = "0"
    v = get_0_versions()
    gen_version_json(workdir, v, checksums)


def gen_empty_json(workdir):
    '''
    empty json is still valid json - needs testing
    '''
    with open(workdir + "/version.json", "w") as f:
        print("saving version.json: {}")
        f.write(json.dumps({}, indent=4, ensure_ascii=True))


def gen_json_bad_key(workdir):
    '''
    if key is missing - then version json is valid json and
    we should check that update will fail with grace
    '''
    pass


def gen_existing_catalog():
    '''
    We allready check if we have existing file -as updater has to
    always exist - therefore testing update of updater tests
    overriting file

    This doesn't check overwritting catalog - therefore we have to
    test it too
    '''
    pass


class Args:
    tag = ""
    asset = ""
    assetRepoName = "PureUpdater_RT.bin"
    assetOutName = "updater.bin"
    workdir = ""


class WorkOnTmp:
    def __init__(self):
        self.current = os.getcwd()
        self.tempdir = TemporaryDirectory()
        os.chdir(self.tempdir.name)

    def __del__(self):
        os.chdir(self.current)

    def name(self):
        return self.tempdir.name

    def current(self):
        return self.current


if __name__ == "__main__":
    print("creating temp dir...")
    g = Getter()
    workdir = WorkOnTmp()
    g.repo = "PureUpdater"
    g.getReleases(None)
    version = g.releases[0]["tag_name"]
    args = Args()
    args.asset = "updater.bin"
    args.tag = version
    args.workdir = workdir.name()
    print(f"---> save file to: {workdir.name()}")
    g.downloadRelease(args)

    print("generating version json ...")
    gen_same_updater("./", version)

    print("writting update.tar ...")
    with tarfile.open(name="update.tar", mode='w') as tar:
        tar.add("version.json")
        tar.add("updater.bin")

    shutil.copyfile("update.tar", workdir.current + "/update.tar")

    print(f"package generation done and copied to: {workdir.current}!")
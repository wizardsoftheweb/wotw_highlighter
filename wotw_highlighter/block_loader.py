"""This file provides a class to load code"""
from os import devnull
from subprocess import CalledProcessError, check_call, check_output

import re

from wotw_highlighter.block_options import BlockOptions


class BlockLoader(BlockOptions):
    """
    This class provides a collection of methods to load a file from either a
    local or git tree
    """

    DEV_NULL = open(devnull, 'w+')

    working_directory = 'blob_working_directory'

    def validate_git_directory(self):
        """Ensures the blob_working_directory is a git repo"""
        try:
            check_call(
                ['git', 'status'],
                stdout=self.DEV_NULL,
                stderr=self.DEV_NULL,
            )
        except CalledProcessError:
            raise ValueError(
                "'%s' is not a git repo"
                % (
                    self.blob_working_directory,
                )
            )

    def validate_git_ref_name(self):
        """Ensures the provided ref name exists"""
        try:
            check_call(
                ['git', 'rev-parse', '--verify', self.git_ref_name],
                stdout=self.DEV_NULL,
                stderr=self.DEV_NULL,
            )
        except CalledProcessError:
            raise ValueError(
                "'%s' is not a valid git ref in %s"
                % (
                    self.git_ref_name,
                    self.blob_working_directory,
                )
            )

    def validate_git_hash(self, git_hash):
        """Ensures the provided hash exists"""
        try:
            check_call(
                ['git', 'rev-parse', '--verify', git_hash],
                stdout=self.DEV_NULL,
                stderr=self.DEV_NULL,
            )
        except CalledProcessError:
            raise ValueError(
                "'%s' is not a valid git hash in %s"
                % (
                    git_hash,
                    self.blob_working_directory,
                )
            )

    def validate(self):
        if self.git_ref_name or self.git_ref_hash or self.git_blob_hash:
            self.validate_git_directory()
        if self.git_ref_name:
            self.validate_git_ref_name()
        if self.git_ref_hash:
            self.validate_git_hash(self.git_ref_hash)
        if self.git_blob_hash:
            self.validate_git_hash(self.git_blob_hash)
        if (
                not self.raw and
                not self.blob_path and
                not self.git_ref_name and
                not self.git_ref_hash and
                not self.git_blob_hash
        ):
            raise ValueError('''\
Must specify an input string, file, or git ref\
''')
        if (
                (self.git_ref_name or self.git_ref_hash)
                and not self.git_blob_hash
                and not self.blob_path
                and not self.raw
        ):
            raise ValueError('''\
Cannot specify a ref name or hash without also specifying a blob path or hash''')

    def load_from_file(self):
        """Loads blob_path into blob"""
        blob_file = open(self.blob_path, 'r')
        self.blob = blob_file.read()

    def discover_blob_hash(self):
        """Discovers the git blob hash from all the git attributes"""
        if not self.git_blob_hash:
            git_ref = (
                self.git_ref_hash
                if self.git_ref_hash
                else self.git_ref_name
            )
            try:
                tree_output = check_output(
                    ['git', 'ls-tree', git_ref, self.blob_path]
                )
                self.git_blob_hash = re.compile(r'\s+').split(tree_output)[2]
            except (CalledProcessError, IndexError):
                raise ValueError(
                    'Ref %s does not contain blob %s'
                    % (
                        git_ref,
                        self.blob_path
                    )
                )
        return self.git_blob_hash

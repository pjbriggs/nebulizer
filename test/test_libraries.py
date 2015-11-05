#!/usr/bin/env python

import unittest
from nebulizer.libraries import split_library_path
from nebulizer.libraries import normalise_folder_path

class TestSplitLibraryPathFunction(unittest.TestCase):
    """
    Tests for the 'split_library_path' function

    """
    def test_library_name_only(self):
        self.assertEqual(split_library_path('TestLibrary'),
                         ('TestLibrary','/'))
    def test_library_name_leading_slash(self):
        self.assertEqual(split_library_path('/TestLibrary'),
                         ('TestLibrary','/'))
    def test_library_name_trailing_slash(self):
        self.assertEqual(split_library_path('TestLibrary/'),
                         ('TestLibrary','/'))
    def test_library_name_with_spaces(self):
        self.assertEqual(split_library_path('Test Library 2'),
                         ('Test Library 2','/'))
    def test_library_and_folder(self):
        self.assertEqual(split_library_path('Test Library 2/Run 11'),
                         ('Test Library 2','/Run 11'))
    def test_library_and_folder_trailing_slash(self):
        self.assertEqual(split_library_path('Test Library 2/Run 11/'),
                         ('Test Library 2','/Run 11'))
    def test_library_and_multiple_folders(self):
        self.assertEqual(
            split_library_path('Test Library 2/Run 11/Fastqs'),
            ('Test Library 2','/Run 11/Fastqs'))
    def test_library_and_multiple_folders_trailing_slash(self):
        self.assertEqual(
            split_library_path('Test Library 2/Run 11/Fastqs/'),
            ('Test Library 2','/Run 11/Fastqs'))

class TestNormaliseFolderPath(unittest.TestCase):
    """
    Tests for the 'normalise_folder_path' function

    """
    def test_empty_folder_path(self):
        self.assertEqual(normalise_folder_path(''),'/')
    def test_already_normalised_folder_path(self):
        self.assertEqual(normalise_folder_path('/path/to/folder'),
                         '/path/to/folder')
    def test_folder_path_without_leading_slash(self):
        self.assertEqual(normalise_folder_path('path/to/folder'),
                         '/path/to/folder')
    def test_folder_path_with_trailing_slash(self):
        self.assertEqual(normalise_folder_path('/path/to/folder/'),
                         '/path/to/folder')
    def test_folder_path_slashes_reversed(self):
        self.assertEqual(normalise_folder_path('path/to/folder/'),
                         '/path/to/folder')
    def test_folder_path_remove_multiple_slashes(self):
        self.assertEqual(normalise_folder_path('/path//to/folder///'),
                         '/path/to/folder')


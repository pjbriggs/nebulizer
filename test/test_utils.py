#!/usr/bin/env python

import unittest
import tempfile
import shutil
import os
from nebulizer.utils import size_to_bytes
from nebulizer.utils import bytes_to_size

class TestSizeToBytes(unittest.TestCase):
    def test_size_to_bytes(self):
        """
        size_to_bytes: check conversions from human-readable to bytes
        """
        # Bytes to bytes
        self.assertEqual(size_to_bytes('100'),100)
        # KB to bytes
        self.assertEqual(size_to_bytes('1KB'),1024)
        self.assertEqual(size_to_bytes('1K'),1024)
        self.assertEqual(size_to_bytes('1kb'),1024)
        self.assertEqual(size_to_bytes('1.0 KB'),1024)
        # MB to bytes
        self.assertEqual(size_to_bytes('1.5MB'),1572864)
        self.assertEqual(size_to_bytes('1.5M'),1572864)
        self.assertEqual(size_to_bytes('1.5mb'),1572864)
        self.assertEqual(size_to_bytes('1.5 MB'),1572864)
        # GB to bytes
        self.assertEqual(size_to_bytes('2.75GB'),2952790016)
        self.assertEqual(size_to_bytes('2.75G'),2952790016)
        self.assertEqual(size_to_bytes('2.75gb'),2952790016)
        self.assertEqual(size_to_bytes('2.75 GB'),2952790016)
        # TB to bytes
        self.assertEqual(size_to_bytes('1.1TB'),
                         int(1.1*1024.0*1024.0*1024.0*1024.0))
        self.assertEqual(size_to_bytes('1.1T'),
                         int(1.1*1024.0*1024.0*1024.0*1024.0))
        self.assertEqual(size_to_bytes('1.1tb'),
                         int(1.1*1024.0*1024.0*1024.0*1024.0))
        self.assertEqual(size_to_bytes('1.1 TB'),
                         int(1.1*1024.0*1024.0*1024.0*1024.0))

class TestBytesToSize(unittest.TestCase):
    def test_bytes_to_size(self):
        """
        bytes_to_size: check conversions from bytes to human-readable
        """
        # Bytes to bytes
        self.assertEqual(bytes_to_size(100),'100')
        # Bytes to KB
        self.assertEqual(bytes_to_size(1024),'1.0 KB')
        # Bytes to MB
        self.assertEqual(bytes_to_size(1572864),'1.5 MB')
        # Bytes to GB
        self.assertEqual(bytes_to_size(2952790016),'2.75 GB')
        # Bytes to TB
        self.assertEqual(bytes_to_size(int(1.1*1024.0*1024.0*1024.0*1024.0)),
                         '1.1 TB')

#!/usr/bin/env python

import unittest
from nebulizer.tables import DataTable

class TestDataTable(unittest.TestCase):
    """
    Tests for the 'DataTable' class
    """
    def test_load_data_table_data(self):
        table_data = { u'model_class': u'TabularToolDataTable',
                       u'name': u'bwa_indexes',
                       u'columns':
                       [u'value', u'dbkey', u'name', u'path'],
                       u'fields':
                       [[u'hg38_analysisSet',
                         u'hg38',
                         u'Human (hg38))',
                         u'/mnt/data-sets/hg38_analysisSet/hg38.fa'],
                        [u'hg19_random_chrM_hap',
                         u'hg19',
                         u'Human (hg19)',
                         u'/mnt/data-sets/hg19_GRCh37_random_chrM/hg19fa'],
                        [u'hg18_random_chrM',
                         u'hg18',
                         u'Human (hg18)',
                         u'/mnt/data-sets/hg18_random_chrM/hg18.fa'],
                        [u'mm10_random_chrM_chrUn',
                         u'mm10',
                         u'Mouse (mm10)',
                         u'/mnt/data-sets/mm10_random_chrM_chrUn/mm10.fa']
                       ] }
        data_table = DataTable(table_data)
        self.assertEqual(data_table.name,'bwa_indexes')
        self.assertEqual(data_table.columns,
                         ['value','dbkey','name','path'])
        self.assertEqual(len(data_table.fields),4)
        self.assertEqual(data_table.fields[0],
                         ['hg38_analysisSet',
                          'hg38',
                          'Human (hg38))',
                          '/mnt/data-sets/hg38_analysisSet/hg38.fa'])
        self.assertEqual(data_table.fields[1],
                         ['hg19_random_chrM_hap',
                          'hg19',
                          'Human (hg19)',
                          '/mnt/data-sets/hg19_GRCh37_random_chrM/hg19fa'])
        self.assertEqual(data_table.fields[2],
                         ['hg18_random_chrM',
                          'hg18',
                          'Human (hg18)',
                          '/mnt/data-sets/hg18_random_chrM/hg18.fa'])
        self.assertEqual(data_table.fields[3],
                         ['mm10_random_chrM_chrUn',
                          'mm10',
                          'Mouse (mm10)',
                          '/mnt/data-sets/mm10_random_chrM_chrUn/mm10.fa'])

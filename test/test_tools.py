#!/usr/bin/env python

import unittest
from nebulizer.tools import Tool
from nebulizer.tools import Repository
from nebulizer.tools import ToolPanelSection
from nebulizer.tools import handle_repository_spec
from nebulizer.tools import normalise_toolshed_url

class TestTool(unittest.TestCase):
    """
    Tests for the 'Tool' class

    """
    def test_load_tool_data(self):
        tool_data = { 'panel_section_name': 'NGS: Mapping',
                      'description': 'Reports on methylation status of reads mapped by Bismark',
                      'config_file': '/galaxy/shed_tools/toolshed.g2.bx.psu.edu/repos/bgruening/bismark/0f8646f22b8d/bismark/bismark_bowtie_wrapper.xml',
                      'name': 'Bismark Meth. Extractor',
                      'panel_section_id': 'solexa_tools',
                      'version': '0.10.2',
                      'link': '/galaxy_dev/tool_runner?tool_id=toolshed.g2.bx.psu.edu%2Frepos%2Fbgruening%2Fbismark%2Fbismark_methylation_extractor%2F0.10.2',
                      'min_width': -1,
                      'model_class': 'Tool',
                      'id': 'toolshed.g2.bx.psu.edu/repos/bgruening/bismark/bismark_methylation_extractor/0.10.2',
                      'target': 'galaxy_main'}
        tool = Tool(tool_data)
        self.assertEqual(tool.name,'Bismark Meth. Extractor')
        self.assertEqual(tool.description,
                         'Reports on methylation status of reads mapped by '
                         'Bismark')
        self.assertEqual(tool.version,'0.10.2')
        self.assertEqual(tool.panel_section,'NGS: Mapping')
        self.assertEqual(tool.id,
                         'toolshed.g2.bx.psu.edu/repos/bgruening/bismark/'
                         'bismark_methylation_extractor/0.10.2')
        self.assertEqual(tool.tool_repo,
                         'toolshed.g2.bx.psu.edu/bgruening/bismark')
        self.assertEqual(tool.tool_changeset,'0f8646f22b8d')

    def test_load_tool_data_no_config_file(self):
        tool_data = { 'panel_section_name': 'NGS: Mapping',
                      'description': 'Reports on methylation status of reads mapped by Bismark',
                      'name': 'Bismark Meth. Extractor',
                      'panel_section_id': 'solexa_tools',
                      'version': '0.10.2',
                      'link': '/galaxy_dev/tool_runner?tool_id=toolshed.g2.bx.psu.edu%2Frepos%2Fbgruening%2Fbismark%2Fbismark_methylation_extractor%2F0.10.2',
                      'min_width': -1,
                      'model_class': 'Tool',
                      'id': 'toolshed.g2.bx.psu.edu/repos/bgruening/bismark/bismark_methylation_extractor/0.10.2',
                      'target': 'galaxy_main'}
        tool = Tool(tool_data)
        self.assertEqual(tool.name,'Bismark Meth. Extractor')
        self.assertEqual(tool.description,
                         'Reports on methylation status of reads mapped by '
                         'Bismark')
        self.assertEqual(tool.version,'0.10.2')
        self.assertEqual(tool.panel_section,'NGS: Mapping')
        self.assertEqual(tool.id,
                         'toolshed.g2.bx.psu.edu/repos/bgruening/bismark/'
                         'bismark_methylation_extractor/0.10.2')
        self.assertEqual(tool.tool_repo,
                         'toolshed.g2.bx.psu.edu/bgruening/bismark')
        self.assertEqual(tool.tool_changeset,None)

    def test_load_tool_data_toolshed_has_prefix(self):
        tool_data = { 'panel_section_name': 'Local Toolshed',
                      'config_file': '/galaxy/shed_tools/192.168.60.164/toolshed/repos/pjbriggs/rnachipintegrator/2f0a1f1a5725/rnachipintegrator/rnachipintegrator_wrapper.xml',
                      'description': "Integrated analysis of 'gene' and 'peak' data",
                      'panel_section_id': 'local_toolshed',
                      'version': '1.0.1.0',
                      'link': '/galaxy_dev/tool_runner?tool_id=192.168.60.164%2Ftoolshed%2Frepos%2Fpjbriggs%2Frnachipintegrator%2Frnachipintegrator_wrapper%2F1.0.1.0',
                      'target': 'galaxy_main',
                      'min_width': -1,
                      'model_class': 'Tool',
                      'id': '192.168.60.164/toolshed/repos/pjbriggs/rnachipintegrator/rnachipintegrator_wrapper/1.0.1.0',
                      'name': 'RnaChipIntegrator'}
        tool = Tool(tool_data)
        self.assertEqual(tool.name,'RnaChipIntegrator')
        self.assertEqual(tool.description,
                         "Integrated analysis of 'gene' and 'peak' data")
        self.assertEqual(tool.version,'1.0.1.0')
        self.assertEqual(tool.panel_section,'Local Toolshed')
        self.assertEqual(tool.id,
                         '192.168.60.164/toolshed/repos/pjbriggs/'
                         'rnachipintegrator/rnachipintegrator_wrapper/1.0.1.0')
        self.assertEqual(tool.tool_repo,
                         '192.168.60.164/toolshed/pjbriggs/'
                         'rnachipintegrator')
        self.assertEqual(tool.tool_changeset,'2f0a1f1a5725')

    def test_load_tool_data_with_tool_shed_repository_data(self):
        tool_data = { 'panel_section_name': 'NGS: SAMtools',
                      'description': 'call variants',
                      'name': 'MPileup',
                      'labels': [],
                      'edam_operations': [],
                      'form_style': 'regular',
                      'edam_topics': [],
                      'panel_section_id': 'samtools',
                      'version': '2.1',
                      'link': '/tool_runner?tool_id=toolshed.g2.bx.psu.edu%2Frepos%2Fdevteam%2Fsamtools_mpileup%2Fsamtools_mpileup%2F2.1',
                      'min_width': -1,
                      'model_class': 'Tool',
                      'id': 'toolshed.g2.bx.psu.edu/repos/devteam/samtools_mpileup/samtools_mpileup/2.1',
                      'tool_shed_repository':
                      {'owner': 'devteam',
                       'changeset_revision':
                       '820754ab8901',
                       'name': 'samtools_mpileup',
                       'tool_shed': 'toolshed.g2.bx.psu.edu'},
                      'target': 'galaxy_main'}
        tool = Tool(tool_data)
        self.assertEqual(tool.name,'MPileup')
        self.assertEqual(tool.description,"call variants")
        self.assertEqual(tool.version,'2.1')
        self.assertEqual(tool.panel_section,'NGS: SAMtools')
        self.assertEqual(tool.id,
                         'toolshed.g2.bx.psu.edu/repos/devteam/'
                         'samtools_mpileup/samtools_mpileup/2.1')
        self.assertEqual(tool.tool_repo,
                         'toolshed.g2.bx.psu.edu/devteam/samtools_mpileup')
        self.assertEqual(tool.tool_changeset,'820754ab8901')

    def test_load_tool_data_not_from_toolshed(self):
        tool_data = { 'panel_section_name': 'Get Genomic Scores',
                      'config_file': '/galaxy/tools/filters/wiggle_to_simple.xml',
                      'description': 'converter',
                      'panel_section_id': 'scores',
                      'version': '1.0.0',
                      'link': '/galaxy_dev/tool_runner?tool_id=wiggle2simple1',
                      'target': 'galaxy_main',
                      'min_width': -1,
                      'model_class': 'Tool',
                      'id': 'wiggle2simple1',
                      'name': 'Wiggle-to-Interval' }
        tool = Tool(tool_data)
        self.assertEqual(tool.name,'Wiggle-to-Interval')
        self.assertEqual(tool.description,
                         'converter')
        self.assertEqual(tool.version,'1.0.0')
        self.assertEqual(tool.panel_section,'Get Genomic Scores')
        self.assertEqual(tool.id,'wiggle2simple1')
        self.assertEqual(tool.tool_repo,'')
        self.assertEqual(tool.tool_changeset,None)

class TestRepository(unittest.TestCase):
    """
    """
    def test_load_repo_data(self):
        repo_data = { 'tool_shed_status':
                      { 'latest_installable_revision': 'True',
                        'revision_update': 'False',
                        'revision_upgrade': 'False',
                        'repository_deprecated': 'False' },
                      'status': 'Installed',
                      'name': 'trimmomatic',
                      'deleted': False,
                      'ctx_rev': '2',
                      'error_message': '',
                      'installed_changeset_revision': 'a60283899c6d',
                      'tool_shed': 'toolshed.g2.bx.psu.edu',
                      'dist_to_shed': False,
                      'url': '/galaxy_dev/api/tool_shed_repositories/68b273cb7d2d6cff',
                      'id': '68b273cb7d2d6cff',
                      'owner': 'pjbriggs',
                      'uninstalled': False,
                      'changeset_revision': 'a60283899c6d',
                      'includes_datatypes': False }
        repo = Repository(repo_data)
        self.assertEqual(repo.name,'trimmomatic')
        self.assertEqual(repo.owner,'pjbriggs')
        self.assertEqual(repo.tool_shed,'toolshed.g2.bx.psu.edu')
        self.assertEqual(repo.id,
                         'toolshed.g2.bx.psu.edu/pjbriggs/trimmomatic')
        revisions = repo.revisions()
        self.assertEqual(len(revisions),1)
        self.assertEqual(revisions[0].revision_number,'2')
        self.assertEqual(revisions[0].changeset_revision,'a60283899c6d')
        self.assertEqual(revisions[0].installed_changeset_revision,
                         'a60283899c6d')
        self.assertEqual(revisions[0].status,'Installed')
        self.assertEqual(revisions[0].error_message,'')
        self.assertFalse(revisions[0].deleted)
        self.assertFalse(revisions[0].revision_update)
        self.assertFalse(revisions[0].revision_upgrade)
        self.assertTrue(revisions[0].latest_revision)
        self.assertEqual(revisions[0].revision_id,'2:a60283899c6d')

    def test_multiple_revisions(self):
        repo_data1 = { 'tool_shed_status':
                       { 'latest_installable_revision': 'True',
                         'revision_update': 'False',
                         'revision_upgrade': 'False',
                         'repository_deprecated': 'False' },
                       'status': 'Installed',
                       'name': 'trimmomatic',
                       'deleted': False,
                       'ctx_rev': '2',
                       'error_message': '',
                       'installed_changeset_revision': 'a60283899c6d',
                       'tool_shed': 'toolshed.g2.bx.psu.edu',
                       'dist_to_shed': False,
                       'url': '/galaxy_dev/api/tool_shed_repositories/68b273cb7d2d6cff',
                       'id': '68b273cb7d2d6cff',
                       'owner': 'pjbriggs',
                       'uninstalled': False,
                       'changeset_revision': 'a60283899c6d',
                       'includes_datatypes': False }
        repo_data2 = { 'tool_shed_status':
                       {'latest_installable_revision': 'False',
                        'revision_update': 'False',
                        'revision_upgrade': 'True',
                        'repository_deprecated': 'False' },
                       'status': 'Installed',
                       'name': 'trimmomatic',
                       'deleted': False,
                       'ctx_rev': '1',
                       'error_message': '',
                       'installed_changeset_revision': '3358c3d30143',
                       'tool_shed': 'toolshed.g2.bx.psu.edu',
                       'dist_to_shed': False,
                       'url': '/galaxy_dev/api/tool_shed_repositories/d6f760c242aa425c',
                       'id': 'd6f760c242aa425c',
                       'owner': 'pjbriggs',
                       'uninstalled': False,
                       'changeset_revision': '2bd7cdbb6228',
                       'includes_datatypes': False}
        repo = Repository(repo_data2)
        repo.add_revision(repo_data1)
        self.assertEqual(repo.name,'trimmomatic')
        self.assertEqual(repo.owner,'pjbriggs')
        self.assertEqual(repo.tool_shed,'toolshed.g2.bx.psu.edu')
        self.assertEqual(repo.id,
                         'toolshed.g2.bx.psu.edu/pjbriggs/trimmomatic')
        revisions = repo.revisions()
        # Most recent revision
        self.assertEqual(len(revisions),2)
        self.assertEqual(revisions[0].revision_number,'2')
        self.assertEqual(revisions[0].changeset_revision,'a60283899c6d')
        self.assertEqual(revisions[0].installed_changeset_revision,
                         'a60283899c6d')
        self.assertEqual(revisions[0].status,'Installed')
        self.assertEqual(revisions[0].error_message,'')
        self.assertFalse(revisions[0].deleted)
        self.assertFalse(revisions[0].revision_update)
        self.assertFalse(revisions[0].revision_upgrade)
        self.assertTrue(revisions[0].latest_revision)
        self.assertEqual(revisions[0].revision_id,'2:a60283899c6d')
        # Previous revision
        self.assertEqual(revisions[1].revision_number,'1')
        self.assertEqual(revisions[1].changeset_revision,'2bd7cdbb6228')
        self.assertEqual(revisions[1].installed_changeset_revision,
                         '3358c3d30143')
        self.assertEqual(revisions[1].status,'Installed')
        self.assertEqual(revisions[1].error_message,'')
        self.assertFalse(revisions[1].deleted)
        self.assertFalse(revisions[1].revision_update)
        self.assertTrue(revisions[1].revision_upgrade)
        self.assertFalse(revisions[1].latest_revision)
        self.assertEqual(revisions[1].revision_id,'1:2bd7cdbb6228')

class TestToolPanelSection(unittest.TestCase):
    """
    """
    def test_load_tool_panel_data_for_toolsection(self):
        tool_panel_data = { 'model_class': 'ToolSection',
                            'version': '',
                            'elems':
                            [{'panel_section_name': 'NGS: SAM Tools',
                              'description': 'call variants',
                              'name': 'MPileup',
                              'panel_section_id': 'ngs:_sam_tools',
                              'version': '2.0',
                              'link': '/galaxy_dev/tool_runner?tool_id=toolshed.g2.bx.psu.edu%2Frepos%2Fdevteam%2Fsamtools_mpileup%2Fsamtools_mpileup%2F2.0',
                              'min_width': -1,
                              'model_class': 'Tool',
                              'id': 'toolshed.g2.bx.psu.edu/repos/devteam/samtools_mpileup/samtools_mpileup/2.0',
                              'target': 'galaxy_main'}],
                            'name': 'NGS: SAM Tools',
                            'id': 'ngs:_sam_tools' }
        section = ToolPanelSection(tool_panel_data)
        self.assertEqual(section.name,'NGS: SAM Tools')
        self.assertEqual(section.id,'ngs:_sam_tools')
        self.assertEqual(section.model_class,'ToolSection')
        self.assertTrue(section.is_toolsection)
        self.assertFalse(section.is_tool)
        self.assertFalse(section.is_label)
        self.assertEqual(len(section.elems),1)
        self.assertEqual(section.elems[0].name,'MPileup')
        self.assertEqual(section.elems[0].id,'toolshed.g2.bx.psu.edu/repos/devteam/samtools_mpileup/samtools_mpileup/2.0')
        self.assertEqual(section.elems[0].model_class,'Tool')
        self.assertFalse(section.elems[0].is_toolsection)
        self.assertTrue(section.elems[0].is_tool)
        self.assertFalse(section.elems[0].is_label)
        self.assertEqual(len(section.elems[0].elems),0)

    def test_load_tool_panel_data_for_tool(self):
        tool_panel_data = { 'panel_section_name': None,
                            'config_file': '/mnt/galaxy/shed_tools/toolshed.g2.bx.psu.edu/repos/devteam/fastqc/3fdc1a74d866/fastqc/rgFastQC.xml',
                            'description': 'Read Quality reports',
                            'labels': [],
                            'name': 'FastQC',
                            'panel_section_id': None,
                            'version': '0.65',
                            'link': '/tool_runner?tool_id=toolshed.g2.bx.psu.edu%2Frepos%2Fdevteam%2Ffastqc%2Ffastqc%2F0.65',
                            'min_width': -1,
                            'model_class': 'Tool',
                            'id': 'toolshed.g2.bx.psu.edu/repos/devteam/fastqc/fastqc/0.65',
                            'target': 'galaxy_main' }
        section = ToolPanelSection(tool_panel_data)
        self.assertEqual(section.name,'FastQC')
        self.assertEqual(section.id,'toolshed.g2.bx.psu.edu/repos/devteam/fastqc/fastqc/0.65')
        self.assertEqual(section.model_class,'Tool')
        self.assertFalse(section.is_toolsection)
        self.assertTrue(section.is_tool)
        self.assertFalse(section.is_label)
        self.assertEqual(len(section.elems),0)

    def test_load_tool_panel_data_for_label(self):
        tool_panel_data = { 'model_class': 'ToolSectionLabel',
                            'version': '',
                            'id': 'deprecated',
                            'text': 'DEPRECATED' }
        section = ToolPanelSection(tool_panel_data)
        self.assertEqual(section.name,None)
        self.assertEqual(section.id,'deprecated')
        self.assertEqual(section.model_class,'ToolSectionLabel')
        self.assertFalse(section.is_toolsection)
        self.assertFalse(section.is_tool)
        self.assertTrue(section.is_label)
        self.assertEqual(len(section.elems),0)

class TestHandleRepositorySpec(unittest.TestCase):
    """
    Tests for the 'handle_repository_spec' function
    """
    def test_handle_repository_spec_full_url(self):
        self.assertEqual(
            handle_repository_spec(("https://toolshed.g2.bx.psu.edu/view/devteam/fastqc/e7b2202befea",)),
            ("toolshed.g2.bx.psu.edu",
             "devteam",
             "fastqc",
             "e7b2202befea"
            ))
        self.assertEqual(
            handle_repository_spec(("https://toolshed.g2.bx.psu.edu/view/devteam/fastqc",)),
            ("toolshed.g2.bx.psu.edu",
             "devteam",
             "fastqc",
             None
            ))
    def test_handle_repository_spec_full_url(self):
        self.assertEqual(
            handle_repository_spec(("https://local.org/toolshed/view/devteam/fastqc/e7b2202befea",)),
            ("local.org/toolshed",
             "devteam",
             "fastqc",
             "e7b2202befea"
            ))
    def test_handle_repository_spec_owner_slash_tool(self):
        self.assertEqual(
            handle_repository_spec(("devteam/fastqc",)),
            ("toolshed.g2.bx.psu.edu",
             "devteam",
             "fastqc",
             None
            ))
    def test_handle_repository_spec_owner_space_tool(self):
        self.assertEqual(
            handle_repository_spec(("devteam","fastqc",)),
            ("toolshed.g2.bx.psu.edu",
             "devteam",
             "fastqc",
             None
            ))
    def test_handle_repository_spec_space_separated(self):
        self.assertEqual(
            handle_repository_spec(("toolshed.g2.bx.psu.edu",
                                    "devteam","fastqc",)),
            ("toolshed.g2.bx.psu.edu",
             "devteam",
             "fastqc",
             None
            ))
        self.assertEqual(
            handle_repository_spec(("toolshed.g2.bx.psu.edu",
                                    "devteam","fastqc",
                                    "e7b2202befea",)),
            ("toolshed.g2.bx.psu.edu",
             "devteam",
             "fastqc",
             "e7b2202befea"
            ))
        self.assertEqual(
            handle_repository_spec(("toolshed.g2.bx.psu.edu",
                                    "devteam","fastqc",
                                    "3:e7b2202befea",)),
            ("toolshed.g2.bx.psu.edu",
             "devteam",
             "fastqc",
             "e7b2202befea"
            ))
    def test_handle_repository_spec_invalid_spec_raises_exception(self):
        self.assertRaises(
            Exception,
            handle_repository_spec,
            ("fastqc",))

class TestNormaliseToolshedUrl(unittest.TestCase):
    """
    Tests for the 'normalise_toolshed_url' function

    """
    def test_full_https_url(self):
        self.assertEqual(
            normalise_toolshed_url('https://toolshed.g2.bx.psu.edu'),
            'https://toolshed.g2.bx.psu.edu')
    def test_full_http_url(self):
        self.assertEqual(
            normalise_toolshed_url('http://127.0.0.1:9009'),
            'http://127.0.0.1:9009')
    def test_no_protocol(self):
        self.assertEqual(
            normalise_toolshed_url('127.0.0.1:9009'),
            'https://127.0.0.1:9009')

#!/usr/bin/env python

import unittest
from nebulizer.quotas import Quota
from nebulizer.quotas import handle_quota_spec

class TestQuota(unittest.TestCase):
    """
    Tests for the 'Quota' class

    """
    def test_load_quota_data_minimal(self):
        # Data returned from galaxy.quotas.QuotaClient(gi).get_quotas()
        quota_data = { u'model_class': u'Quota',
                       u'id': u'f2db41e1fa331b3e',
                       u'name': u'NGS analyst',
                       u'url': u'/api/quotas/f2db41e1fa331b3e' }
        quota = Quota(quota_data)
        self.assertEqual(quota.id,'f2db41e1fa331b3e')
        self.assertEqual(quota.name,'NGS analyst')
        self.assertEqual(quota.description,None)
        self.assertEqual(quota.operation,None)
        self.assertEqual(quota.bytes,None)
        self.assertEqual(quota.display_amount,None)
        self.assertEqual(quota.default_for,None)
        self.assertEqual(quota.list_users,[])
        self.assertEqual(quota.list_groups,[])
    def test_load_quota_data_full(self):
        # Data returned from galaxy.quotas.QuotaClient(gi).show_quota()
        quota_data = { u'users': [],
                       u'description': u'Quota for BCF',
                       u'default': [],
                       u'bytes': 536870912000,
                       u'display_amount': u'500.0 GB',
                       u'groups': [],
                       u'model_class': u'Quota',
                       u'operation': u'=',
                       u'id': u'a9a3a7ad1f6b4288',
                       u'name': 'BCF User' }
        quota = Quota(quota_data)
        self.assertEqual(quota.id,'a9a3a7ad1f6b4288')
        self.assertEqual(quota.name,'BCF User')
        self.assertEqual(quota.description,'Quota for BCF')
        self.assertEqual(quota.operation,'=')
        self.assertEqual(quota.bytes,536870912000)
        self.assertEqual(quota.display_amount,'500.0 GB')
        self.assertEqual(quota.default_for,None)
        self.assertEqual(quota.list_users,[])
        self.assertEqual(quota.list_groups,[])
    def test_load_quota_data_full_users_and_groups(self):
        # Data returned from galaxy.quotas.QuotaClient(gi).show_quota()
        quota_data = { u'users':
                       [
                           { u'model_class': u'UserQuotaAssociation',
                             u'user': { u'username': u'galaxy-user',
                                        u'total_disk_usage': 242167080660.0,
                                        u'deleted': False,
                                        u'nice_total_disk_usage': u'225.5 GB',
                                        u'email': u'galaxy.user@galaxy.org',
                                        u'last_password_change':
                                        u'2019-06-19T08:59:24.869868',
                                        u'active': True,
                                        u'model_class': u'User',
                                        u'id': '89b5001534959253' }
                           }
                       ],
                       u'description': u'Quota for BCF',
                       u'default': [],
                       u'bytes': 536870912000,
                       u'display_amount': u'500.0 GB',
                       u'groups':
                       [
                           { u'model_class': u'GroupQuotaAssociation',
                             u'group': { u'model_class': u'Group',
                                         u'id': u'568bb93d6fbfd316',
                                         u'name': u'BCF Staff' }
                           }
                       ],
                       u'model_class': u'Quota',
                       u'operation': u'=',
                       u'id': u'a9a3a7ad1f6b4288',
                       u'name': 'BCF User' }
        quota = Quota(quota_data)
        self.assertEqual(quota.id,'a9a3a7ad1f6b4288')
        self.assertEqual(quota.name,'BCF User')
        self.assertEqual(quota.description,'Quota for BCF')
        self.assertEqual(quota.operation,'=')
        self.assertEqual(quota.bytes,536870912000)
        self.assertEqual(quota.display_amount,'500.0 GB')
        self.assertEqual(quota.default_for,None)
        self.assertEqual([u.username for u in quota.list_users],
                         ['galaxy-user',])
        self.assertEqual([g.name for g in quota.list_groups],
                         ['BCF Staff',])

class TestHandleQuotaSpec(unittest.TestCase):
    """
    Tests for the 'handle_quota_spec' function
    """
    def test_handle_quota_spec(self):
        self.assertEqual(handle_quota_spec("=500GB"),
                         ('=','500GB'))
    def test_handle_quota_spec_no_operation(self):
        self.assertEqual(handle_quota_spec("500GB"),
                         ('=','500GB'))

        

#!/usr/bin/env python
#
# tables: functions for managing data tables
from bioblend import galaxy

class DataTable(object):
    """
    Class wrapping extraction of data table information

    Provides an interface for accessing data about a data
    table in a Galaxy instance, which has been retrieved
    via a call to the Galaxy API using bioblend.
    """
    def __init__(self,table_data):
        """
        Create a new DataTable instance

        ``table_data`` is a dictionary returned by a
        call to bioblend, for example:

        >>> for tbl in galaxy.tool_data.ToolDataClient(gi).get_data_tables():
        >>>    name = tbl['name']
        >>>    tbl_data = galaxy.tool_data.ToolDataClient(gi).show_data_table(name)
        >>>    print DataTable(tbl_data).name
        """
        self.name = table_data['name']
        self.columns = table_data['columns']
        self.fields = table_data['fields']

class DataTables(object):
    """
    Class wrapping extraction of data tables in Galaxy instance
    """
    def __init__(self,gi):
        """
        """
        self._tool_data_client = galaxy.tool_data.ToolDataClient(gi)
        self._table_names = [str(tbl['name']) for tbl in
                             self._tool_data_client.get_data_tables()]
        self._table_names.sort()

    @property
    def tables(self):
        """
        Return list of data table names
        """
        return [name for name in self._table_names]

    def get_table(self,name):
        """
        Fetch DataTable instance for a tool data table
        """
        return DataTable(self._tool_data_client.show_data_table(name))

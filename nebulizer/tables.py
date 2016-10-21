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
        tool_data_client = galaxy.tool_data.ToolDataClient(gi)
        self._tables = {}
        for tbl in tool_data_client.get_data_tables():
            name = str(tbl['name'])
            tbl_data = tool_data_client.show_data_table(name)
            self._tables[name] = DataTable(tbl_data)

    @property
    def tables(self):
        """
        Return list of DataTables
        """
        return sorted([self._tables[t] for t in self._tables],
                      key=lambda tbl: tbl.name)



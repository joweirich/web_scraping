"""
Tools for scraping homepages and saving results in Postgres DB
"""

import os
import re
import yaml
import lxml.html
import psycopg2

CONN_STR = """host='localhost' dbname='jowe_postgres'
                                   user='jowe_postgres'
                                   password='Rjjfdmko21'"""
import contextlib

@contextlib.contextmanager
def PostgreSQL_connect(conn_str=CONN_STR, commit=False):
  dbConnection = psycopg2.connect(conn_str)
  cursor = dbConnection.cursor()

  try:
      yield cursor
  except:
      dbConnection.rollback()
  else:
      if commit:
          dbConnection.commit()
          print('commit')
      else:
          print('no commit')

  finally:
      cursor.close()
      dbConnection.close()
      print('closing cursor and connection')

    
class PostgreSQLdb:
    """
    Wrapper class for PostgreSQL connection
    compare: https://stackoverflow.com/questions/38076220/python-mysqldb-connection-in-a-class
    """
    def __init__(self, conn_str=CONN_STR):
        self.conn_str = conn_str
        self.conn = psycopg2.connect(self.conn_str)
        self.cursor = None

    def __enter__(self):
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.conn.close()

    def query(self, sql_str):
        self.cursor.execute(sql_str)

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()


def sql_command(sql_str, conn_str=CONN_STR):
    conn = psycopg2.connect(conn_str)
    cur = conn.cursor()
    cur.execute(sql_str)
    #result = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return


def load_offsets(filename='offsets.yaml'):
    assert os.path.isfile(filename), 'file does not exist'
    with open(filename, 'r') as fsock:
        offsets = yaml.load(fsock, Loader=yaml.SafeLoader)
    return offsets


def save_offsets(offsets, filename='offsets.yaml'):
    with open(filename, 'w') as fsock:
        yaml.dump(offsets, fsock)


def parse_content(html_content, xpath):
    doc = lxml.html.fromstring(html_content)
    content_list = doc.xpath(xpath)
    return content_list


def format_content(content_list, indices=slice(0, 5, 1)):
    """
    Format content of input list
    """
    content_gen = (x.split()[0].replace(',', '.') for x in content_list[indices])
    float_check = re.compile(r'\d+\.\d+')
    content = [float(x) if float_check.match(x) else int(x)
               for x in content_gen]
    return content


def num_list_to_str(num_list):
    """
    Return a string corresponding to input list of numbers
    """
    return str(num_list).strip('[]')

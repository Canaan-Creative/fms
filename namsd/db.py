import sqlite3


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class DataBase():
    def __init__(self, addr, db_type='sqlite3', user=None, passwd=None):
        self.db_type = db_type
        self.addr = addr
        self.user = user
        self.passwd = passwd

        if db_type == 'sqlite3':
            self.holder = '?'
        elif db_type == 'mysql':
            self.holder = '%s'

    def connect(self):
        if self.db_type == 'sqlite3':
            self.conn = sqlite3.connect(self.addr)
            self.conn.row_factory = dict_factory
            self.cursor = self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def disconnect(self):
        self.cursor.close()
        self.conn.close()

    def _create(self, name, column_def, additional=None, suffix=None):
        self.query = 'CREATE TABLE IF NOT EXISTS `{}` ({}{}){}'.format(
            name,
            ', '.join('`{}` {}'.format(k, v)
                      for k, v in column_def.items()),
            ', {}'.format(additional) if additional else '',
            ' {}'.format(suffix) if suffix else ''
        )
        self.value = None

    def _insert(self, name, column, value):
        ignore = 'OR IGNORE'
        if self.db_type == 'mysql':
            ignore = 'IGNORE'

        self.query = 'INSERT {} INTO `{}` (`{}`) VALUES ({})'.format(
            ignore,
            name,
            '`, `'.join(column),
            ', '.join(self.holder for i in range(len(value)))
        )
        self.value = value

    def _update(self, name, column, value, condition):
        self.query = 'UPDATE `{}` SET `{}`={} WHERE `{}`={}'.format(
            name,
            ('`={}, '.format(self.holder)).join(column),
            self.holder,
            ('`={}, '.format(self.holder)).join(condition),
            self.holder,
        )
        self.value = value

    def _select(self, name, column=None, clause=None, value=None):
        self.query = 'SELECT {} FROM `{}`{}'.format(
            '`{}`'.format('`, `'.join(column)) if column else '*',
            name,
            ' WHERE {}'.format(clause) if clause else ''
        )
        self.value = value

    def _raw(self, query, value=None):
        self.query = query
        self.value = value

    def run(self, command, *args, **kwargs):
        if command == 'create':
            self._create(*args, **kwargs)
        elif command == 'insert':
            self._insert(*args, **kwargs)
        elif command == 'select':
            self._select(*args, **kwargs)
        elif command == 'update':
            self._select(*args, **kwargs)
        elif command == 'raw':
            self._raw(*args, **kwargs)
        else:
            return

        if self.value is None:
            self.cursor.execute(self.query)
        else:
            self.cursor.execute(self.query, self.value)
        return self.cursor.fetchall()

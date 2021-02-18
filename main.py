import logging
from typing import Generator, Dict

from sql_tokenizer import tokenizer

log = logging.getLogger(__name__)

SCHEMA = 'FOX'


class Field:
    def __init__(self, name: str):
        # log.debug('field %s', name)
        self.name = name
        self.type = '/* TODO */'
        self.is_pk = False
        self.is_null = False
        self.foreign_table = ''

    def __str__(self):
        if self.name.upper() == "ID" and self.type == 'integer' and self.is_pk:
            return '    "{}" serial primary key /* TODO or integer */'.format(self.name.upper())

        # todo self.foreign_table
        return '    "{}" {}{}{}'.format(
            self.name.upper(),
            self.type,
            ' primary key' if self.is_pk else '',
            ' not null' if self.is_pk and not self.is_pk else '')


# CREATE TABLE orders (
#     order_id integer PRIMARY KEY,
#     product_no integer REFERENCES products,
#     quantity integer
# );

class Table:
    def __init__(self, name):
        self.name = name
        self.fields: Dict[Field] = {}

    def __str__(self):
        return '\ncreate table "{}"."{}"\n(\n{}\n);'.format(
            SCHEMA,
            self.name.upper(),
            ',\n'.join(str(v) for v in self.fields.values())
        )


tables = {}


def table_field(t: Generator):
    types_map = {
        'number': 'integer',
    }
    token = next(t)
    field = Field(token)
    token = next(t)
    if token in types_map:
        field.type = types_map[token]
    elif token == 'numeric':
        token = next(t)
        if token != '(':
            raise ValueError(token)
        token = next(t)
        token = next(t)
        if token != ')':
            raise ValueError(token)
        field.type = 'integer'
    elif token == 'varchar2':
        token = next(t)
        if token != '(':
            raise ValueError(token)
        s = next(t)
        token = next(t)
        if token == 'char':
            token = next(t)
        if token != ')':
            raise ValueError(token)
        field.type = 'varchar({})'.format(s)
    else:
        raise NotImplementedError(token)

    token = next(t)
    if token in ',)':
        return field, token
    if token != 'not':
        raise ValueError(token)
    token = next(t)
    if token != 'null':
        raise ValueError(token)
    field.is_null = True
    token = next(t)
    return field, token


def create_table(t: Generator):
    token = next(t)
    if token in tables:
        raise ValueError(token)
    table = Table(token)
    token = next(t)
    if token != '(':
        raise ValueError
    while True:
        field, token = table_field(t)
        log.debug(field)
        table.fields[field.name] = field
        if token == ')':
            break
    token = next(t)
    if token != ';':
        raise ValueError
    return table


def main():
    with open('oracle.sql') as f:
        text = f.read()
    t = tokenizer(text)
    while True:
        token = next(t)
        if token == 'create':
            token = next(t)
            if token == 'table':
                table = create_table(t)
                log.debug(table)
                tables[table.name] = table
                continue
            else:
                log.error('%s', token)
        elif token == 'alter':
            token = next(t)
            if token == 'table':
                token = next(t)
                table = tables[token]
                token = next(t)
                if token == 'add':
                    token = next(t)
                    if token == 'constraint':
                        token = next(t)  # *_pk
                        token = next(t)
                        if token != 'primary':
                            raise ValueError(token)
                        token = next(t)  # 'key'
                        token = next(t)  # (
                        token = next(t)
                        table.fields[token].is_pk = True
                        token = next(t)  # )
                        token = next(t)  # ;
                        log.debug(table)
                        continue
                    else:
                        log.error('%s', token)
                else:
                    log.error('%s', token)
            else:
                log.error('%s', token)
        else:
            log.error('%s', token)
        log.error('%s', token)

    log.info('%s', tables)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s %(funcName)s():%(lineno)d: %(message)s',
                        level=logging.DEBUG)
    main()

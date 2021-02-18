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
        return '    "{}" {}{}{}{}'.format(
            self.name.upper(),
            self.type,
            ' primary key' if self.is_pk else '',
            ' not null' if self.is_null and not self.is_pk else '',
            ' references "{}"."{}"'.format(SCHEMA, self.foreign_table.upper()) if self.foreign_table else '',
        )


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
            raise ValueError(token)
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
                        if token == 'primary':
                            token = next(t)  # key
                            token = next(t)  # (
                            f = next(t)
                            table.fields[f].is_pk = True
                            token = next(t)  # )
                            token = next(t)  # ;
                            log.debug(table)
                            continue
                        elif token == 'foreign':
                            token = next(t)  # key
                            token = next(t)  # (
                            f = next(t)
                            token = next(t)  # )
                            token = next(t)  # references
                            tn = next(t)
                            table.fields[f].foreign_table = tn
                            token = next(t)  # (
                            token = next(t)  # *_id
                            token = next(t)  # )
                            token = next(t)  # ;
                            log.debug(table)
                            continue
                        raise ValueError(token)
                    else:
                        raise ValueError(token)
                else:
                    raise ValueError(token)
            else:
                raise ValueError(token)
        raise ValueError(token)

    log.info('%s', tables)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s %(funcName)s():%(lineno)d: %(message)s',
                        level=logging.DEBUG)
    try:
        main()
    except StopIteration:
        with open('pg.sql', 'w') as f:
            print('-- generated by oracle2pg', file=f)
            print('create schema if not exists "{}";'.format(SCHEMA), file=f)
            for i in tables.values():
                print(i, file=f)

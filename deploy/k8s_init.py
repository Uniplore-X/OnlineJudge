"""
目前仅判断pg数据库是否可用连接
"""
import os.path

import psycopg2


def get_env(name, default=""):
    return os.environ.get(name, default)


host = get_env("POSTGRES_HOST", "oj-postgres")
port = get_env("POSTGRES_PORT", "5432")
db_name = get_env("POSTGRES_DB")
user = get_env("POSTGRES_USER")
password = get_env("POSTGRES_PASSWORD")


def is_postgresql_connected():
    try:
        conn = psycopg2.connect(host=host, port=port, database=db_name, user=user, password=password)
        status = conn.status
        return status == psycopg2.extensions.STATUS_READY
    except psycopg2.Error as e:
        print(e)
        return False


if __name__ == '__main__':
    while True:
        if is_postgresql_connected():
            termination_message_path = get_env('terminationMessagePath')
            print(f"pg数据库正常：{host}:{port}, database={db_name}")
            if termination_message_path:
                with open(termination_message_path, 'w') as f:
                    f.write('ok')
            break

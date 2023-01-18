TEST_DB_NAME = "test_db"
database_dsn = (f'postgresql+asyncpg://postgres:'
                f'postgres@localhost:5432/{TEST_DB_NAME}')

COUNT_LINKS = 3
LINKS = [f'http://test_link{i}.ru' for i in range(COUNT_LINKS)]

ID_LINKS = {}

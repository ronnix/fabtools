import mock
import unittest


class TestRequirePostgresDatabase(unittest.TestCase):

    @mock.patch('fabtools.require.postgres._service_name')
    @mock.patch('fabtools.require.postgres.restarted')
    @mock.patch('fabtools.require.postgres.require_locale')
    @mock.patch('fabtools.require.postgres.create_database')
    @mock.patch('fabtools.require.postgres.run')
    @mock.patch('fabtools.require.postgres.database_exists')
    def test_params_respected(self, database_exists, run, create_database,
                              require_locale, restarted, service_name):
        """
        If require.database is called, ensure that the template,
        encoding and locale parameters are passed through to the
        underlying create_database call
        """
        from fabtools import require
        database_exists.return_value = False
        run.return_value = 'en-US.UTF-8\nde-DE.UTF-8'
        require.postgres.database('foo', 'bar', locale='some_locale',
                                  encoding='some_encoding',
                                  template='some_template')
        run.assert_called_with('locale -a')
        require_locale.assert_called_with('some_locale')
        create_database.assert_called_with('foo', 'bar', locale='some_locale',
                                           encoding='some_encoding',
                                           template='some_template')


class TestRequirePostgresUser(unittest.TestCase):

    @mock.patch('fabtools.require.postgres.create_user')
    @mock.patch('fabtools.require.postgres.user_exists')
    def test_require_user_exists(self, user_exists, create_user):
        user_exists.return_value = True
        from fabtools import require
        require.postgres.user('foo', 'bar')
        user_exists.assert_called_with('foo')
        self.assertEqual([], create_user.method_calls)

    @mock.patch('fabtools.require.postgres.create_user')
    @mock.patch('fabtools.require.postgres.user_exists')
    def test_require_user_with_default_options(self, user_exists, create_user):
        user_exists.return_value = False
        from fabtools import require
        require.postgres.user('foo', 'bar')
        create_user.assert_called_with('foo', 'bar', False, False, False, True,
                                       True, None, False)


class TestPostgresCreateUser(unittest.TestCase):

    @mock.patch('fabtools.postgres._run_as_pg')
    def test_create_user_with_no_options(self, _run_as_pg):
        from fabtools import postgres
        postgres.create_user('foo', 'bar')
        expected = (
            'psql -c "CREATE USER \\\\"foo\\\\" NOSUPERUSER NOCREATEDB NOCREATEROLE '
            'INHERIT LOGIN UNENCRYPTED PASSWORD \'bar\';"')
        self.assertEqual(expected, _run_as_pg.call_args[0][0])

    @mock.patch('fabtools.postgres._run_as_pg')
    def test_create_user_with_no_connection_limit(self, _run_as_pg):
        from fabtools import postgres
        postgres.create_user('foo', 'bar', connection_limit=-1)
        expected = (
            'psql -c "CREATE USER \\\\"foo\\\\" NOSUPERUSER NOCREATEDB NOCREATEROLE '
            'INHERIT LOGIN CONNECTION LIMIT -1 UNENCRYPTED PASSWORD \'bar\';"')
        self.assertEqual(expected, _run_as_pg.call_args[0][0])

    @mock.patch('fabtools.postgres._run_as_pg')
    def test_create_user_with_custom_options(self, _run_as_pg):
        from fabtools import postgres
        postgres.create_user('foo', 'bar', superuser=True, createdb=True,
                             createrole=True, inherit=False, login=False,
                             connection_limit=20, encrypted_password=True)
        expected = (
            'psql -c "CREATE USER \\\\"foo\\\\" SUPERUSER CREATEDB CREATEROLE '
            'NOINHERIT NOLOGIN CONNECTION LIMIT 20 '
            'ENCRYPTED PASSWORD \'bar\';"')
        self.assertEqual(expected, _run_as_pg.call_args[0][0])


class TestPostgresDropUser(unittest.TestCase):

    @mock.patch('fabtools.postgres._run_as_pg')
    def test_drop_user(self, _run_as_pg):

        from fabtools.postgres import drop_user

        drop_user('foo')

        _run_as_pg.assert_called_with('psql -c "DROP USER foo;"')


class TestPostgresDropDatabase(unittest.TestCase):

    @mock.patch('fabtools.postgres._run_as_pg')
    def test_drop_database(self, _run_as_pg):

        from fabtools.postgres import drop_database

        drop_database('foo')

        _run_as_pg.assert_called_with('dropdb foo')

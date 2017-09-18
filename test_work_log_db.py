"""Contains Unit Tests for work_log_db.py

Created by: Lawerence Lee, Sept 2017
"""
import datetime
import unittest
from unittest.mock import patch
from unittest import TestCase

from playhouse.test_utils import test_database
from peewee import *

import work_log_db
from work_log_db import Entry

pw_test_db = SqliteDatabase(':memory:')


def create_test_data():
    for num in range(10):
        Entry.create(
            name="Test Employee %d" % num,
            task="Testing Emplyee #%d" % num,
            time="%d" % num,
            note="Tester"
            )


def delete_tester():
    testers = Entry.select().where(
                  work_log_db.Entry.note == "Tester")
    for tester in testers:
        tester.delete_instance()


class TestInitDB(TestCase):

    @patch("work_log_db.init_db")
    def test_db_connection(self, init_db_mock):
        init_db_mock()
        self.assertTrue(init_db_mock.called)


class TestMain(TestCase):

    @patch("work_log_db.add_entry")
    def test_add_entry_option(self, add_mock):
        with patch("builtins.input", side_effect="a"):
            work_log_db.main()
        add_mock.assert_called_once

    @patch("work_log_db.search_menu")
    def test_search_menu_option(self, search_mock):
        with patch("builtins.input", side_effect="s"):
            work_log_db.main()
        search_mock.assert_called_once

    @patch("sys.exit")
    def test_entry_exit_option(self, exit_mock):
        with patch("builtins.input", side_effect="q"):
            work_log_db.main()
        exit_mock.assert_called_once

    @patch("work_log_db.search_menu")
    def test_entry_bad_option(self, search_mock):
        with patch("builtins.input", side_effect=["l", "s"]):
            work_log_db.main()
        search_mock.assert_called_once


class TestAddEntry(TestCase):

    @patch("work_log_db.db_insert")
    def test_add_entry_func_no_note(self, db_insert_mock):
        side_effects = ["Tester", "Add to DB", "45", ""]
        with patch("builtins.input", side_effect=side_effects):
            work_log_db.add_entry()
        db_insert_mock.assert_called_once_with("Tester", "Add to DB", "45", "")

    @patch("work_log_db.db_insert")
    def test_add_entry_func_with_note(self, db_insert_mock):
        side_effects = ["Tester", "Add to DB", "45", "y", "Added a Note"]
        with patch("builtins.input", side_effect=side_effects):
            work_log_db.add_entry()
        db_insert_mock.assert_called_once_with("Tester", "Add to DB",
                                               "45", "Added a Note")

    @patch("work_log_db.db_insert")
    def test_add_entry_func_bad_num(self, db_insert_mock):
        side_effects = ["Tester", "Add to DB", "fry", "", "23",
                        ""]
        with patch("builtins.input", side_effect=side_effects):
            work_log_db.add_entry()
        db_insert_mock.assert_called_once_with("Tester", "Add to DB",
                                               "23", "")

    def tearDown(self):
        delete_tester()


class TestDbInsertFunc(TestCase):

    @patch("work_log_db.main")
    @patch("work_log_db.db_insert")
    def pw_test_db_insert_func(self, db_insert_mock, main_mock):
        result = work_log_db.db_insert("Tester", "Flying", "10", "")
        self.assertTrue(result, main_mock)
        db_insert_mock.assert_called_once_with("Tester", "Flying", "10", "")
        delete_tester()


class TestSearchMenu(TestCase):

    def setUp(self):
        create_test_data()

    @patch("sys.exit")
    def test_search_menu_quit(self, exit_mock):
        with patch("builtins.input", side_effect="q"):
            work_log_db.search_menu()
        exit_mock.assert_called_once

    @patch("work_log_db.main")
    def test_search_menu_main_menu(self, main_mock):
        with patch("builtins.input", side_effect="m"):
            work_log_db.search_menu()
        main_mock.assert_called_once

    @patch("work_log_db.basic_search")
    def test_search_menu_name_search(self, search_mock):
        with patch("builtins.input", side_effect="n"):
            work_log_db.search_menu()
        search_mock.assert_called_once_with("N")

    @patch("work_log_db.basic_search")
    def test_search_menu_date_search(self, search_mock):
        with patch("builtins.input", side_effect="d"):
            work_log_db.search_menu()
        search_mock.assert_called_once_with("D")

    @patch("work_log_db.basic_search")
    def test_search_menu_range_search(self, search_mock):
        with patch("builtins.input", side_effect="r"):
            work_log_db.search_menu()
        search_mock.assert_called_once_with("R")

    @patch("work_log_db.basic_search")
    def test_search_menu_time_search(self, search_mock):
        with patch("builtins.input", side_effect="t"):
            work_log_db.search_menu()
        search_mock.assert_called_once_with("T")

    @patch("work_log_db.main")
    def test_entry_empty_db(self, main_mock):
        with test_database(pw_test_db, (Entry, )):
            with patch("builtins.input", side_effect="blah"):
                work_log_db.search_menu()
        main_mock.assert_called_once

    @patch("work_log_db.search_menu")
    def test_search_menu_bad_choice(self, search_menu_mock):
        with patch("builtins.input", side_effect="blah"):
            work_log_db.search_menu()
        search_menu_mock.assert_called_once

    @patch("work_log_db.targeted_search")
    def test_search_menu_targeted_search(self, target_search_mock):
        side_effects = ["k", "Apple"]
        with patch("builtins.input", side_effect=side_effects):
            work_log_db.search_menu()
        target_search_mock.assert_called_once_with("K", "Apple")

    def tearDown(self):
        delete_tester()


class TestBasicSearch(TestCase):

    @patch("work_log_db.targeted_search")
    def test_basic_search_by_name(self, verbose_mock):
        with patch("builtins.input", side_effect="0"):
            with test_database(pw_test_db, [Entry, ]):
                create_test_data()
                work_log_db.basic_search("N")
        verbose_mock.assert_called_once_with("N", "Test Employee 0")

    @patch("work_log_db.targeted_search")
    def test_basic_search_by_time(self, verbose_mock):
        with patch("builtins.input", side_effect="1"):
            with test_database(pw_test_db, [Entry, ]):
                create_test_data()
                work_log_db.basic_search("T")
        verbose_mock.assert_called_once_with("T", 1)

    @patch("work_log_db.targeted_search")
    def test_basic_search_by_date(self, verbose_mock):
        with patch("builtins.input", side_effect="0"):
            with test_database(pw_test_db, [Entry, ]):
                create_test_data()
                work_log_db.basic_search("D")
                todays_date = Entry.get(Entry.id == 1).date
        verbose_mock.assert_called_once_with("D", todays_date)

    @patch("work_log_db.targeted_search")
    def test_basic_search_by_range(self, verbose_mock):
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        side_effects = ["2016-05-12", today, "0"]
        with patch("builtins.input", side_effect=side_effects):
            with test_database(pw_test_db, [Entry, ]):
                create_test_data()
                work_log_db.basic_search("R")
                todays_date = Entry.get(Entry.id == 1).date
        verbose_mock.assert_called_once_with("R", todays_date)

    @patch("work_log_db.targeted_search")
    def test_basic_search_by_bad_range(self, verbose_mock):
        side_effects = ["2016-05-12", "2017-05-12", "blah",
                        "2016-05-12", "2017-12-12", "0"]
        with patch("builtins.input", side_effect=side_effects):
            with test_database(pw_test_db, [Entry, ]):
                create_test_data()
                work_log_db.basic_search("R")
                todays_date = Entry.get(Entry.id == 1).date
        verbose_mock.assert_called_once_with("R", todays_date)

    @patch("work_log_db.targeted_search")
    def test_basic_search_by_bad_range_input(self, verbose_mock):
        side_effects = ["2016-05-12", "2017", "blah",
                        "2016-05-12", "2017-12-12", "0"]
        with patch("builtins.input", side_effect=side_effects):
            with test_database(pw_test_db, [Entry, ]):
                create_test_data()
                work_log_db.basic_search("R")
                todays_date = Entry.get(Entry.id == 1).date
        verbose_mock.assert_called_once_with("R", todays_date)

    @patch("work_log_db.targeted_search")
    def test_basic_search_by_time_with_bad_choice(self, verbose_mock):
        side_effects = ["100", "blah", "3"]
        with patch("builtins.input", side_effect=side_effects):
            with test_database(pw_test_db, [Entry, ]):
                create_test_data()
                work_log_db.basic_search("T")
        verbose_mock.assert_called_once_with("T", 3)

    @patch("work_log_db.targeted_search")
    def test_basic_search_by_time_with_bad_value(self, verbose_mock):
        side_effects = ["five", "blah", "3"]
        with patch("builtins.input", side_effect=side_effects):
            with test_database(pw_test_db, [Entry, ]):
                create_test_data()
                work_log_db.basic_search("T")
        verbose_mock.assert_called_once_with("T", 3)


class TestTargetedSearch(TestCase):

    @patch("work_log_db.edit_entry")
    def test_targeted_goodKeyword_pageNav_editEntry(self, edit_mock):
        side_effects = ["f", "e"]
        with patch("builtins.input", side_effect=side_effects):
            with test_database(pw_test_db, [Entry, ]):
                create_test_data()
                work_log_db.targeted_search("K", "test")
        edit_mock.assert_called_once_with(2)

    @patch("work_log_db.search_menu")
    def test_targeted_badKeyword_pageNav_editEntry(self, search_menu_mock):
        with patch("builtins.input", side_effect=" "):
            with test_database(pw_test_db, [Entry, ]):
                create_test_data()
                work_log_db.targeted_search("K", "blah")
        search_menu_mock.assert_called_once

    @patch("work_log_db.search_menu")
    def test_targeted_name_pageNav_keyError_searchMenuReturn(
                                                    self, search_menu_mock):
        side_effects = ["F", " ", "S"]
        with patch("builtins.input", side_effect=side_effects):
            with test_database(pw_test_db, [Entry, ]):
                create_test_data()
                work_log_db.targeted_search("N", "Test Employee 9")
        search_menu_mock.assert_called_once

    @patch("work_log_db.search_menu")
    def test_targeted_time_noInput_pageNav_keyError_searchMenuReturn(
                                                    self, search_menu_mock):
        side_effects = ["BAD I/O", " ", "B", "KeyError", "S"]
        with patch("builtins.input", side_effect=side_effects):
            with test_database(pw_test_db, [Entry, ]):
                create_test_data()
                work_log_db.targeted_search("T", "1")
        search_menu_mock.assert_called_once

    @patch("work_log_db.edit_entry")
    def test_targeted_date_editEntry(self, edit_mock):
        side_effects = ["e"]
        with patch("builtins.input", side_effect=side_effects):
            with test_database(pw_test_db, [Entry, ]):
                create_test_data()
                todays_date = Entry.get(Entry.id == 1).date
                work_log_db.targeted_search("D", todays_date)
        edit_mock.assert_called_once_with(1)

    @patch("work_log_db.edit_entry")
    def test_targeted_date_editEntry(self, edit_mock):
        side_effects = ["e"]
        with patch("builtins.input", side_effect=side_effects):
            with test_database(pw_test_db, [Entry, ]):
                create_test_data()
                todays_date = Entry.get(Entry.id == 1).date
                work_log_db.targeted_search("R", todays_date)
        edit_mock.assert_called_once_with(1)


class TestEditEntry(TestCase):

    @patch("work_log_db.main")
    def test_edit_entry_delete_entry(self, main_mock):
        with patch("builtins.input", side_effect=["d", "ENTER"]):
            with test_database(pw_test_db, [Entry, ]):
                create_test_data()
                work_log_db.edit_entry(1)
        main_mock.assert_called_once

    @patch("work_log_db.main")
    def test_edit_entry_change_all_attributes(self, main_mock):
        side_effects = ["e", "Y", "2017-09-22", "y", "Kicking tires"
                        "y", "5", "y", "no cans kicked"]
        with patch("builtins.input", side_effect=side_effects):
            with test_database(pw_test_db, [Entry, ]):
                create_test_data()
                work_log_db.edit_entry(1)
        main_mock.assert_called_once

    @patch("work_log_db.main")
    def test_edit_entry_date_valueError_changeDate(self, main_mock):
        side_effects = ["e", "Y", "2017", "ValueError",
                        "2017-09-22", "N", "N", "N"]
        with patch("builtins.input", side_effect=side_effects):
            with test_database(pw_test_db, [Entry, ]):
                create_test_data()
                work_log_db.edit_entry(1)
        main_mock.assert_called_once

    @patch("work_log_db.main")
    def test_edit_entry_date_valueError_changeDate(self, main_mock):
        side_effects = ["e", "N", "Y", "Five", "ValueError", "5" "N"]
        with patch("builtins.input", side_effect=side_effects):
            with test_database(pw_test_db, [Entry, ]):
                create_test_data()
                work_log_db.edit_entry(1)
        main_mock.assert_called_once

if __name__ == "__main__":
    unittest.main()

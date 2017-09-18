"""Allows a user/Entry to add their completed
tasks to a Sqlite database using the Peewee ORM

Created by Lawerence Lee, Sept 2017
"""
from collections import OrderedDict
import datetime
import os
import sys


from peewee import *

db = SqliteDatabase('entries.db')


def clear():
    os.system("cls" if os.name == "nt" else "clear")

# PEEWEE CLASS & DATABASE
###############################################################################


class Entry(Model):
    date = DateField(default=datetime.date.today)
    name = CharField(max_length=50, null=True)
    task = TextField()
    time = IntegerField(default=0)
    note = TextField(null=True)

    class Meta:
        database = db


def init_db():
    db.connect()
    db.create_tables([Entry], safe=True)

# MAIN
###############################################################################


def main():
    """Menu to choose to create or view previous entries."""
    while True:
        clear()
        print('MAIN MENU')
        print('-'*9)
        print("\n-- Options --")
        for key, value in menu.items():
            print('{}) {}'.format(key, value.__doc__))
        print('Q) QUIT')
        choice = input('\nAction: ').upper().strip()

        if choice == "A":
            return add_entry()
        elif choice == "S":
            return search_menu()
        elif choice == "Q":
            clear()
            return sys.exit()

#  CREATING ENTRIES IN DATABASE
###############################################################################


def db_insert(name, task, time, note):
    """Creates entry in database"""
    Entry.create(name=name,
                 task=task,
                 time=time,
                 note=note)
    return main()


def add_entry():
    """Add Entry to database"""
    clear()
    name = input("Enter Full Name: ")
    task = input("Enter a task name: ")
    while True:
        try:
            time = input("Enter the minutes (ints only) to complete task: ")
            int(time)
        except ValueError:
            input("Be sure you are entering an integer. ")
        else:
            break
    quest = input("Would you like to add a note [N/y]: ").upper()
    note = ""
    if quest == "Y":
        print("Enter your note below.")
        note = input(":")
    return db_insert(name, task, time, note)

# EDITING DATABASE ENTRIES
###############################################################################


def edit_entry(table_id):
    """Prompts user to specify which values in a single database record they
    would like to replace."""

    print("\nWould you simply like to simply")
    edit_quest = input("[D]elete the record, or [E]dit it? ").upper()
    if edit_quest == 'D':
        Entry.get(Entry.id == table_id).delete_instance()
        clear()
        input('Entry has been deleted.\nPress ENTER to Continue. ')
        return main()
    else:
        clear()
        print("Do you wish to change the DATE of the task?")
        date_quest = input("[y/N] ").upper().strip()
        if date_quest == 'Y':
            while True:
                clear()
                print("Enter your task's new DATE using")
                edited_date = input("[YYYY-MM-DD]: ").strip()
                try:
                    task_dt = datetime.datetime.strptime(edited_date,
                                                         '%Y-%m-%d')
                except ValueError:
                    clear()
                    input("The format provided was not correct. Try Again ")
                else:
                    Entry.update(date=task_dt).where(
                                                        Entry.id ==
                                                        table_id).execute()
                    break

        clear()
        print("Do you wish to change the NAME of the task?")
        name_quest = input("[y/N] ").upper()
        if name_quest == 'Y':
            clear()
            edited_name = input('Enter your new task name: ')
            Entry.update(task=edited_name).where(
                            Entry.id == table_id).execute()

        clear()
        print("Do you wish to change the NUMBER")
        print("OF MINUTES TO COMPLETE the task?")
        minutes_quest = input("[y/N] ").upper().strip()
        if minutes_quest == 'Y':
            while True:
                try:
                    clear()
                    print("Enter the new number of minutes for your task")
                    edited_minutes = int(input(" (integers only): "))
                except ValueError:
                    clear()
                    input("The format provided was not correct. Try Again ")
                else:
                    Entry.update(time=edited_minutes).where(
                                    Entry.id == table_id).execute()
                    break

        clear()
        print("Would you like to edit your NOTE from this task?")
        note_quest = input("[y/N] ").upper().strip()
        if note_quest == 'Y':
            clear()
            edited_note = input('Enter your new note: ')
            Entry.update(note=edited_note).where(
                            Entry.id == table_id).execute()
    return main()

# SEARCH FOR & PRINT ENTRIES
###############################################################################


def print_records(records, page):
    clear()
    print("{}/{} Record".format(page+1, len(records)))
    print("DATE: {}".format(records[page].date
                            .strftime('%A %b %d,%Y')))
    print("NAME: {}".format(records[page].name))
    print("TASK: {}".format(records[page].task))
    print("COMPETION TIME: {} MINS".format(records[page].time))
    print("NOTE: {}".format(records[page].note))
    print("\n[B]ack | [F]orward | [S]earch Menu | [E]dit/Delete")


def targeted_search(choice, search_term):
    if choice == "K":
        records = OrderedDict(enumerate(Entry.select()
                              .where(Entry.task.contains(search_term) |
                              Entry.note.contains(search_term) |
                              Entry.name.contains(search_term))))
        if not records:
            clear()
            input("No records match the keyword '{}'. ".format(search_term))
            return search_menu()
    if choice == "N":
        records = OrderedDict(enumerate(Entry.select()
                              .where(Entry.name == search_term)))
    elif choice == "T":
        records = OrderedDict(enumerate(Entry.select()
                              .where(Entry.time == search_term)))
    elif choice == "D" or choice == "R":
        records = OrderedDict(enumerate(Entry.select()
                              .where(Entry.date == search_term)))

    page = 0
    print_records(records, page)
    while True:
        page_nav = input("Action: ").upper()
        if page_nav == "B":
            try:
                clear()
                page -= 1
                print_records(records, page)
            except KeyError:
                clear()
                page += 1
                print("You've reached the very first record.")
                input("\nPress Enter to view it. ")
                clear()
                print_records(records, page)
        elif page_nav == "F":
            try:
                clear()
                page += 1
                print_records(records, page)
            except KeyError:
                page -= 1
                clear()
                print("You've reached the very last record.")
                input("Press Enter to view it. ")
                clear()
                print_records(records, page)
        elif page_nav == "E":
            return edit_entry(records[page].id)
        elif page_nav == "S":
            return search_menu()
        else:
            clear()
            input("No menu option was selected ")
            clear()


def basic_search(choice):

    # CREATE ORDERED DICT BASED ON CHOICE ARG
    if choice != "R":
        if choice == "N":
            column = Entry.name
        elif choice == "T":
            column = Entry.time
        elif choice == "D":
            column = Entry.date

        q_dict = OrderedDict(enumerate(
                                Entry.select(column)
                                .order_by(column)
                                .distinct()))
    else:
        while True:
            clear()
            first_date = input("Enter your lower bound date in [YYYY-MM-DD]: ")
            end_date = input("Enter your upper bound date in [YYYY-MM-DD]: ")
            try:
                lower = datetime.datetime.strptime(first_date, "%Y-%m-%d")
                upper = datetime.datetime.strptime(end_date, "%Y-%m-%d")
                q_dict = OrderedDict(enumerate(Entry.select(Entry.date)
                                     .where(
                                     (lower < Entry.date) &
                                     (Entry.date < upper))
                                     .order_by(Entry.date).distinct()))
            except ValueError:
                input("The formatting used was not correct, please try again.")
            else:
                if q_dict:
                    break
                else:
                    input("There are no entries from that time span.")

    # PRINT UNIQUE ITEMS FROM ORDERED DICT
    while True:
        try:
            clear()
            for key, item in q_dict.items():
                if choice == "N":
                    print("{}) NAME: {}".format(key, item.name))

                elif choice == "T":
                    print("{}) {} MIN".format(key, item.time))

                elif choice == "D" or choice == "R":
                    print("{}) {}".format(key,
                                          item.date.strftime('%A %b %d,%Y')))

            # USER CHOOSES NUMBER OF A RECORD
            q_choice = int(input("\nChoice: "))
            if choice == "N":
                search_term = q_dict[q_choice].name
            elif choice == "T":
                search_term = q_dict[q_choice].time
            elif choice == "D" or choice == "R":
                search_term = q_dict[q_choice].date

        except KeyError:
            clear()
            print("The number entered does not match a menu choice.")
            input("Please Try Again")
        except ValueError:
            clear()
            print("The input provided was not an integer.")
            input("Please Try Again")
        else:
            return targeted_search(choice, search_term)

# SEARCH MENU (a.k.a search_menu)
###############################################################################


def search_menu():
    """Search Database Entries"""
    db_present = Entry.select()
    if not db_present:
        clear()
        print("The database in empty")
        input("Please create an entry first. ")
        return main()
    while True:
        clear()
        print('SEARCH MENU')
        print('-'*11)
        print("\n-- Search By: --")
        print("[N] : Name")
        print("[D] : Entry Date")
        print("[R] : Entry Date Range")
        print("[T] : Time Spent")
        print("[K] : Keyword or Employee Name")
        print("[M] : MAIN MENU")
        print("[Q] : QUIT")
        choice = input("\nAction: ").upper().strip()
        if choice not in ["N", "D", "R", "T", "K", "M", "Q"]:
            clear()
            input("That is not a valid menu choice.")
            return search_menu()
        if choice == "Q":
            return sys.exit()
        elif choice == "M":
            return main()
        elif choice != "K":
            return basic_search(choice)
        else:
            clear()
            search_term = input("Enter a keyword: ").strip()
            return targeted_search(choice, search_term)

###############################################################################

menu = OrderedDict([
    ("A", add_entry),
    ("S", search_menu)
])


if __name__ == "__main__":
    init_db()
    main()

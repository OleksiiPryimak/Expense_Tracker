# python (location)/expense_tracker.py report
# python (location)/expense_tracker.py add 5000 "Large amount"
# python (location)/expense_tracker.py import-csv (location)/expenses.csv
# python (location)/expense_tracker.py export-python

import csv
from dataclasses import dataclass
from pickle import load, dump
from typing import List
import sys

import click


BIG_EXPENSE_THRESHOLD = 1000
DB_FILENAME = 'budget.db'


@dataclass
class Expense:
    amount: int
    description: str
    id: int


    def __post_init__(self):
        if self.amount <= 0:
            raise ValueError('Amount cannot be zero or negative')
    

    def is_big(self) -> bool:
        return self.amount >= BIG_EXPENSE_THRESHOLD
    

def load_or_init_expenses() -> List[Expense]:
    try:
        with open(DB_FILENAME, 'rb') as stream:
         expenses = load(stream)
    except FileNotFoundError:
        expenses = []
    return expenses


def save_expances(expenses: List[Expense]) -> None:
    with open(DB_FILENAME, 'wb') as stream:
        expenses = dump(expenses, stream)


def find_new_id(expenses: List[Expense]) -> int:
    all_ids = {e.id for e in expenses}
    next_id = 1
    while next_id in all_ids:
        next_id += 1
    return next_id


def compute_total(expenses: List[Expense]) -> int:
    amounts = [e.amount for e in expenses]
    return sum(amounts)


def print_report(expenses: List[Expense], total: int) -> None:
    if expenses:
        print("--ID--  -AMOUNT-  -BIG?-  --DESC-----------")
        for expense in expenses:
            if expense.is_big():
                big = '(!)'
            else:
                big = ''
            print(f"{expense.id:6}  {expense.amount:8}  {big:^6}  {expense.description}")
        print(f"TOTAL: {total:8}")
    else:
        print("You haven't entered any expenses yet.")


@click.group()
def cli() -> None:
    pass


@cli.command()
def report() -> None:
    expenses = load_or_init_expenses()
    total = compute_total(expenses)
    print_report(expenses, total)


@cli.command()
@click.argument('amount', type=int)
@click.argument('desc')
def add(amount: int, desc: str) -> None:
    expenses = load_or_init_expenses()
    next_id = find_new_id(expenses)
    try:
        new_expense = Expense(amount=amount, description=desc, id=next_id)
    except ValueError as e:
        print("ERROR:", e.args[0])
        sys.exit(1)

    expenses.append(new_expense)
    save_expances(expenses)
    print("SUCCESS")


@cli.command()
@click.argument('csv_file')
def import_csv(csv_file: str) -> None:
    expenses = load_or_init_expenses()

    try:
        with open(csv_file) as stream:
            reader = csv.DictReader(stream)
            for row in reader:
                expense = Expense(
                    id=find_new_id(expenses),
                    description=row['description'],
                    amount=float(row['amount']),
                )
                expenses.append(expense)
    except FileNotFoundError:
        print("There is no such file")
        sys.exit(1)

    save_expances(expenses)
    print("Imported")


@cli.command()
def export_python() -> None:
    expenses = load_or_init_expenses()
    print(expenses)

if __name__ == "__main__":
    cli()
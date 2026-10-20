#!/bin/python3
from decktest import fnc
from decktest.tests import *

app = fnc.Application("./example.py")
example_section = TestSection("GeneralExampleTesting", full_test_name=True, log_completed=False)

Test("TestTestLol").expect("0\n").input("1 2").wrap_up(example_section)
Test("TestTestLol").expect("-1\n").input("1 -1").wrap_up(example_section)
Test("TestTestLol").expect("3\n").input("4 2").wrap_up(example_section)
Test("TestTestLol").expect("0\n").input("1 2").wrap_up(example_section)
Test("TestTestLol").expect_error(1, "Partial").input("1 0").wrap_up(example_section)

exit(example_section.run(app))
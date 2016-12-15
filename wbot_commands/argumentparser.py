#! /usr/bin/python3
import argparse


class ArgumentParserError(Exception):
    """Custom argparse ArgumentParser exception.
    """

class ThrowingArgumentParser(argparse.ArgumentParser):
    """An ArgumentParser that throws instead of printing and exiting.
    """
    def error(self, message):
        raise ArgumentParserError(message)


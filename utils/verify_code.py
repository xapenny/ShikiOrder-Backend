import string
import random
from datetime import datetime


class VerifyCode:
    code_A = 0
    code_B = 0
    date = datetime.now().date()

    @classmethod
    def get_code(cls, is_takeout):
        prefix = 'A' if is_takeout else 'B'
        return prefix + ''.join(random.choices(string.digits, k=4))

    @classmethod
    def get_code_old(cls, is_takeout: bool):
        if cls.date != datetime.now().date():
            cls.date = datetime.now().date()
            cls.code_A = 0
            cls.code_B = 0
        if cls.code_A > 9999:
            cls.code_A = 0
        if cls.code_B > 9999:
            cls.code_B = 0
        if is_takeout:
            cls.code_A += 1
            return f'A{cls.code_A:0>4}'
        else:
            cls.code_B += 1
            return f'B{cls.code_B:0>4}'

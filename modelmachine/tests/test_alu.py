# -*- coding: utf-8 -*-

"""Test case for arithmetic logic unit."""

from modelmachine.memory import RegisterMemory
from modelmachine.numeric import Integer
from modelmachine.alu import ArithmeticLogicUnit
from modelmachine.alu import ZF, CF, OF, SF, HALT, LESS, EQUAL, GREATER

BYTE_SIZE = 8

class TestArithmeticLogicUnit:

    """Test case for arithmetic logic unit."""

    registers = None
    alu = None
    max_int, min_int = None, None

    def setup(self):
        """Init state."""
        self.registers = RegisterMemory(BYTE_SIZE, ['R1', 'R2', 'S',
                                                    'FLAGS', 'IP'])
        self.alu = ArithmeticLogicUnit(BYTE_SIZE, self.registers)
        self.max_int = 2 ** (self.alu.operand_size - 1)
        self.min_int = -2 ** (self.alu.operand_size - 1)
        assert self.alu.registers is self.registers
        assert self.alu.operand_size == BYTE_SIZE
        assert self.registers.word_size == BYTE_SIZE

    def test_set_flags_negative(self):
        """Test set flags register algorithm with negative numbers."""
        for i in range(4 * self.min_int, 0):
            self.registers.put('S', i % 2 ** BYTE_SIZE, BYTE_SIZE)
            self.alu.set_flags(i, i)
            if i == 4 * self.min_int:
                assert self.registers.fetch('FLAGS', BYTE_SIZE) == OF | CF | ZF
            if 4 * self.min_int < i < 3 * self.min_int:
                assert self.registers.fetch('FLAGS', BYTE_SIZE) == OF | CF
            if i == 3 * self.min_int:
                assert self.registers.fetch('FLAGS', BYTE_SIZE) == OF | CF | SF
            if 3 * self.min_int < i < 2 * self.min_int:
                assert self.registers.fetch('FLAGS', BYTE_SIZE) == OF | CF | SF
            if i == 2 * self.min_int:
                assert self.registers.fetch('FLAGS', BYTE_SIZE) == OF | CF | ZF
            if 2 * self.min_int < i < self.min_int:
                assert self.registers.fetch('FLAGS', BYTE_SIZE) == OF | CF
            if self.min_int <= i < 0:
                assert self.registers.fetch('FLAGS', BYTE_SIZE) == SF | CF

    def test_set_flags_positive(self):
        """Test set flags register algorithm with positive numbers."""
        for i in range(0, 4 * self.max_int):
            self.registers.put('S', i % 2 ** BYTE_SIZE, BYTE_SIZE)
            self.alu.set_flags(i, i)
            if i == 0:
                assert self.registers.fetch('FLAGS', BYTE_SIZE) == ZF
            if 0 < i < self.max_int:
                assert self.registers.fetch('FLAGS', BYTE_SIZE) == 0
            if self.max_int <= i < self.max_int * 2:
                assert self.registers.fetch('FLAGS', BYTE_SIZE) == OF | SF
            if i == 2 * self.max_int:
                assert self.registers.fetch('FLAGS', BYTE_SIZE) == OF | CF | ZF
            if 2 * self.max_int < i < 3 * self.max_int:
                assert self.registers.fetch('FLAGS', BYTE_SIZE) == OF | CF
            if 3 * self.max_int <= i < 4 * self.max_int:
                assert self.registers.fetch('FLAGS', BYTE_SIZE) == OF | CF | SF

    def test_get_ops(self):
        """Test interaction with registers."""
        for i in range(self.min_int, self.max_int):
            self.registers.put('R1', i % 2 ** BYTE_SIZE, BYTE_SIZE)
            self.registers.put('R2', (-i - 1) % 2 ** BYTE_SIZE, BYTE_SIZE)
            signed = (Integer(i, BYTE_SIZE, True), Integer(-i-1, BYTE_SIZE, True))
            unsigned = (Integer(i % 2 ** BYTE_SIZE, BYTE_SIZE, False),
                        Integer((-i-1) % 2 ** BYTE_SIZE, BYTE_SIZE, False))
            assert self.alu.get_signed_ops() == signed
            assert self.alu.get_unsigned_ops() == unsigned

    def test_add(self):
        """Add must set flags and calc right result."""
        self.registers.put('R1', 0, BYTE_SIZE)
        self.registers.put('R2', 0, BYTE_SIZE)
        self.alu.add()
        assert self.registers.fetch('S', BYTE_SIZE) == 0
        assert self.registers.fetch('FLAGS', BYTE_SIZE) == ZF

        for i in range(1, self.max_int):
            self.registers.put('R1', i, BYTE_SIZE)
            self.registers.put('R2', -i % 2 ** BYTE_SIZE, BYTE_SIZE)
            self.alu.add()
            assert self.registers.fetch('S', BYTE_SIZE) == 0
            assert self.registers.fetch('FLAGS', BYTE_SIZE) == ZF | CF

            self.registers.put('R1', i, BYTE_SIZE)
            self.registers.put('R2', 10, BYTE_SIZE)
            self.alu.add()
            assert self.registers.fetch('S', BYTE_SIZE) == i + 10
            if i < self.max_int - 10:
                assert self.registers.fetch('FLAGS', BYTE_SIZE) == 0
            else:
                assert self.registers.fetch('FLAGS', BYTE_SIZE) == OF | SF

            self.registers.put('R1', -i % 2 ** BYTE_SIZE, BYTE_SIZE)
            self.registers.put('R2', -10 % 2 ** BYTE_SIZE, BYTE_SIZE)
            self.alu.add()
            assert self.registers.fetch('S', BYTE_SIZE) == (-i - 10) % 2 ** BYTE_SIZE
            if -i >= self.min_int + 10:
                assert self.registers.fetch('FLAGS', BYTE_SIZE) == SF | CF
            else:
                assert self.registers.fetch('FLAGS', BYTE_SIZE) == OF | CF

    def test_sub(self):
        """Substraction test."""
        self.registers.put('R1', 0, BYTE_SIZE)
        self.registers.put('R2', 0, BYTE_SIZE)
        self.alu.sub()
        assert self.registers.fetch('S', BYTE_SIZE) == 0
        assert self.registers.fetch('FLAGS', BYTE_SIZE) == ZF

        for i in range(1, self.max_int):
            self.registers.put('R1', i, BYTE_SIZE)
            self.registers.put('R2', i, BYTE_SIZE)
            self.alu.sub()
            assert self.registers.fetch('S', BYTE_SIZE) == 0
            assert self.registers.fetch('FLAGS', BYTE_SIZE) == ZF

            self.registers.put('R1', i, BYTE_SIZE)
            self.registers.put('R2', 10, BYTE_SIZE)
            self.alu.sub()
            assert self.registers.fetch('S', BYTE_SIZE) == (i - 10) % 2 ** BYTE_SIZE
            if i < 10:
                assert self.registers.fetch('FLAGS', BYTE_SIZE) == CF | SF
            elif i == 10:
                assert self.registers.fetch('FLAGS', BYTE_SIZE) == ZF
            else:
                assert self.registers.fetch('FLAGS', BYTE_SIZE) == 0

            self.registers.put('R1', -i % 2 ** BYTE_SIZE, BYTE_SIZE)
            self.registers.put('R2', 10, BYTE_SIZE)
            self.alu.sub()
            assert self.registers.fetch('S', BYTE_SIZE) == (-i - 10) % 2 ** BYTE_SIZE
            if -i >= self.min_int + 10:
                assert self.registers.fetch('FLAGS', BYTE_SIZE) == SF
            else:
                assert self.registers.fetch('FLAGS', BYTE_SIZE) == OF

    def test_mul(self):
        """Multiplication test."""
        self.registers.put('R1', 10, BYTE_SIZE)
        self.registers.put('R2', 15, BYTE_SIZE)
        self.alu.umul()
        assert self.registers.fetch('S', BYTE_SIZE) == 150
        assert self.registers.fetch('FLAGS', BYTE_SIZE) == SF | OF
        self.alu.smul()
        assert self.registers.fetch('S', BYTE_SIZE) == 150
        assert self.registers.fetch('FLAGS', BYTE_SIZE) == SF | OF


        self.registers.put('R1', 25, BYTE_SIZE)
        self.alu.umul()
        assert self.registers.fetch('S', BYTE_SIZE) == (25 * 15) % 2 ** BYTE_SIZE
        assert self.registers.fetch('FLAGS', BYTE_SIZE) == OF | CF

        self.registers.put('R1', -2 % 2 ** BYTE_SIZE, BYTE_SIZE)
        self.alu.smul()
        assert self.registers.fetch('S', BYTE_SIZE) == -30 % 2 ** BYTE_SIZE
        assert self.registers.fetch('FLAGS', BYTE_SIZE) == SF | CF

        self.registers.put('R1', -10 % 2 ** BYTE_SIZE, BYTE_SIZE)
        self.alu.smul()
        assert self.registers.fetch('S', BYTE_SIZE) == -150 % 2 ** BYTE_SIZE
        assert self.registers.fetch('FLAGS', BYTE_SIZE) == OF | CF

    def test_divmod(self):
        """Division test."""
        self.registers.put('R1', 27, BYTE_SIZE)
        self.registers.put('R2', 5, BYTE_SIZE)

        self.alu.udiv()
        assert self.registers.fetch('S', BYTE_SIZE) == 5
        assert self.registers.fetch('FLAGS', BYTE_SIZE) == 0
        self.alu.umod()
        assert self.registers.fetch('S', BYTE_SIZE) == 2
        assert self.registers.fetch('FLAGS', BYTE_SIZE) == 0
        self.alu.sdiv()
        assert self.registers.fetch('S', BYTE_SIZE) == 5
        assert self.registers.fetch('FLAGS', BYTE_SIZE) == 0
        self.alu.smod()
        assert self.registers.fetch('S', BYTE_SIZE) == 2
        assert self.registers.fetch('FLAGS', BYTE_SIZE) == 0

        self.registers.put('R1', -27 % 2 ** BYTE_SIZE, BYTE_SIZE)
        self.alu.sdiv()
        assert self.registers.fetch('S', BYTE_SIZE) == -5 % 2 ** BYTE_SIZE
        assert self.registers.fetch('FLAGS', BYTE_SIZE) == SF | CF
        self.alu.smod()
        assert self.registers.fetch('S', BYTE_SIZE) == -2 % 2 ** BYTE_SIZE
        assert self.registers.fetch('FLAGS', BYTE_SIZE) == SF | CF

    def test_jump(self):
        """Test jump instruction."""
        self.registers.put('R1', 15, BYTE_SIZE)
        self.alu.jump()
        assert self.registers.fetch('IP', BYTE_SIZE) == 15

        self.registers.put('R1', 12, BYTE_SIZE)
        self.registers.put('R2', 12, BYTE_SIZE)
        self.alu.sub()
        self.alu.cond_jump(signed=True, comparasion=EQUAL, equal=True)
        assert self.registers.fetch('IP', BYTE_SIZE) == 12


    def run_cond_jump(self, should_jump, first, second, *vargs, **kvargs):
        """Run one conditional jump test."""
        self.registers.put('R1', first % 2 ** BYTE_SIZE, BYTE_SIZE)
        self.registers.put('R2', second % 2 ** BYTE_SIZE, BYTE_SIZE)
        self.alu.sub()
        self.registers.put('IP', 1, BYTE_SIZE)
        self.registers.put('R1', 2, BYTE_SIZE)
        self.alu.cond_jump(*vargs, **kvargs)
        if should_jump:
            assert self.registers.fetch('IP', BYTE_SIZE) == 2
        else:
            assert self.registers.fetch('IP', BYTE_SIZE) == 1

    def test_cond_jump(self):
        """Tests for conditional jumps."""
        for signed in (False, True):
            self.run_cond_jump(False, 5, 10, signed, EQUAL, equal=True)
            self.run_cond_jump(True, 10, 10, signed, EQUAL, equal=True)
            self.run_cond_jump(False, 15, 10, signed, EQUAL, equal=True)

            self.run_cond_jump(True, 5, 10, signed, EQUAL, equal=False)
            self.run_cond_jump(False, 10, 10, signed, EQUAL, equal=False)
            self.run_cond_jump(True, 15, 10, signed, EQUAL, equal=False)

            self.run_cond_jump(True, 5, 10, signed, LESS, equal=False)
            self.run_cond_jump(False, 10, 10, signed, LESS, equal=False)
            self.run_cond_jump(False, 15, 10, signed, LESS, equal=False)

            self.run_cond_jump(True, 5, 10, signed, LESS, equal=True)
            self.run_cond_jump(True, 10, 10, signed, LESS, equal=True)
            self.run_cond_jump(False, 15, 10, signed, LESS, equal=True)

            self.run_cond_jump(False, 5, 10, signed, GREATER, equal=False)
            self.run_cond_jump(False, 10, 10, signed, GREATER, equal=False)
            self.run_cond_jump(True, 15, 10, signed, GREATER, equal=False)

            self.run_cond_jump(False, 5, 10, signed, GREATER, equal=True)
            self.run_cond_jump(True, 10, 10, signed, GREATER, equal=True)
            self.run_cond_jump(True, 15, 10, signed, GREATER, equal=True)

        self.run_cond_jump(False, -10, 10, False, LESS, equal=False)
        self.run_cond_jump(False, -10, 10, False, LESS, equal=True)
        self.run_cond_jump(True, -10, 10, True, LESS, equal=False)
        self.run_cond_jump(True, -10, 10, True, LESS, equal=True)

        self.run_cond_jump(True, 10, -10, False, LESS, equal=False)
        self.run_cond_jump(True, 10, -10, False, LESS, equal=True)
        self.run_cond_jump(False, 10, -10, True, LESS, equal=False)
        self.run_cond_jump(False, 10, -10, True, LESS, equal=True)

        self.run_cond_jump(True, -10, 10, False, GREATER, equal=False)
        self.run_cond_jump(True, -10, 10, False, GREATER, equal=True)
        self.run_cond_jump(False, -10, 10, True, GREATER, equal=False)
        self.run_cond_jump(False, -10, 10, True, GREATER, equal=True)

        self.run_cond_jump(False, 10, -10, False, GREATER, equal=False)
        self.run_cond_jump(False, 10, -10, False, GREATER, equal=True)
        self.run_cond_jump(True, 10, -10, True, GREATER, equal=False)
        self.run_cond_jump(True, 10, -10, True, GREATER, equal=True)

    def test_halt(self):
        """Very easy and important test."""
        assert self.registers.fetch('FLAGS', BYTE_SIZE) & HALT == 0
        self.alu.halt()
        assert self.registers.fetch('FLAGS', BYTE_SIZE) & HALT != 0

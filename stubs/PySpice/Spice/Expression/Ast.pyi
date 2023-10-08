from _typeshed import Incomplete

class StatementList:
    def __init__(self, *statements) -> None: ...
    def __nonzero__(self): ...
    def __iter__(self): ...
    def add(self, statement) -> None: ...

class Program(StatementList): ...

class Variable:
    def __init__(self, name) -> None: ...
    @property
    def name(self): ...

class Constant:
    def __init__(self, value) -> None: ...

class IntConstant(Constant):
    def __int__(self) -> int: ...

class FloatConstant(Constant):
    def __float__(self) -> float: ...

class Expression:
    NUMBER_OF_OPERANDS: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...
    def iter_on_operands(self): ...
    @property
    def operand(self): ...
    @property
    def operand1(self): ...
    @property
    def operand2(self): ...
    @property
    def operand3(self): ...

class UnaryExpression(Expression):
    NUMBER_OF_OPERANDS: int

class BinaryExpression(Expression):
    NUMBER_OF_OPERANDS: int

class TernaryExpression(Expression):
    NUMBER_OF_OPERANDS: int

class OperatorMetaclass(type):
    def __new__(meta, class_name, base_classes, attributes): ...
    @classmethod
    def register_prefix(meta, cls) -> None: ...
    @classmethod
    def operator_iter(cls): ...
    @classmethod
    def get_unary(cls, operator): ...
    @classmethod
    def get_binary(cls, operator): ...

class OperatorMixin(metaclass=OperatorMetaclass):
    OPERATOR: Incomplete

class UnaryOperator(UnaryExpression, OperatorMixin): ...
class BinaryOperator(BinaryExpression, OperatorMixin): ...

class Assignation(BinaryExpression):
    @property
    def variable(self): ...
    @property
    def value(self): ...

class Negation(UnaryOperator):
    OPERATOR: str
    PRECEDENCE: int

class Not(UnaryOperator):
    OPERATOR: str
    PRECEDENCE: int

class power(BinaryOperator):
    OPERATOR: str
    PRECEDENCE: int

class Multiplication(BinaryOperator):
    OPERATOR: str
    PRECEDENCE: int

class Division(BinaryOperator):
    OPERATOR: str
    PRECEDENCE: int

class Modulo(BinaryOperator):
    OPERATOR: str
    PRECEDENCE: int

class IntegerDivision(BinaryOperator):
    OPERATOR: str
    PRECEDENCE: int

class Addition(BinaryOperator):
    OPERATOR: str
    PRECEDENCE: int

class Subtraction(BinaryOperator):
    OPERATOR: str
    PRECEDENCE: int

class Equal(BinaryOperator):
    OPERATOR: str
    PRECEDENCE: int

class NotEqual(BinaryOperator):
    OPERATOR: str
    PRECEDENCE: int

class LessEqual(BinaryOperator):
    OPERATOR: str

class GreaterEqual(BinaryOperator):
    OPERATOR: str
    PRECEDENCE: int

class Less(BinaryOperator):
    OPERATOR: str
    PRECEDENCE: int

class Greater(BinaryOperator):
    OPERATOR: str
    PRECEDENCE: int

class And(BinaryOperator):
    OPERATOR: str
    PRECEDENCE: int

class Or(BinaryOperator):
    OPERATOR: str
    PRECEDENCE: int

class If:
    PRECEDENCE: int
    def __init__(self, condition, then_expression, else_expression) -> None: ...
    @property
    def condition(self): ...
    @property
    def then_expression(self): ...
    @property
    def else_expression(self): ...

class Function(Expression):
    def __init__(self, name, *args) -> None: ...
    @property
    def name(self): ...

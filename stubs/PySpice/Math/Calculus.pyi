from PySpice.Math import odd as odd

def compute_exact_finite_difference_coefficients(derivative_order, grid, x0: int = ...): ...
def compute_finite_difference_coefficients(derivative_order, grid): ...
def get_finite_difference_coefficients(derivative_order, accuracy_order, grid_type): ...
def simple_derivative(x, values): ...
def derivative(x, values, derivative_order: int = ..., accuracy_order: int = ...): ...

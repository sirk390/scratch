
def newton(fct, x=0, eps=0.01):
    last_x = None
    while (last_x is None or (abs(x - last_x) > eps)):
        y = fct(x)
        dx = (y - fct(x-eps)) / eps
        last_x = x
        x -= y / dx   
    return x


def newton2(fct, x=0, eps=0.01):
    last_x = x
    last_y = fct(last_x)
    dx1 = 1
    while True:
        y = fct(x)
        dx = (y - fct(x-eps)) / eps
        last_x = x
        x -= y / dx   
    return x


def sqrt(x):
    def cost_sqrt(sqrt_x):
        return (sqrt_x * sqrt_x) - x
    return newton(cost_sqrt, x, eps=0.000001)

if __name__ == "__main__":
    import math
    print sqrt(200)
    print math.sqrt(200)
    #newton(lambda x: 2*x, 8)
    
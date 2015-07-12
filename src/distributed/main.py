
def p1():
    g1 = Group("group1", secret="efzfzezfeezf")
    g2 = Group("group2")
    a = Variable()
    a.share("a", group="group1", permissions="r")
    a.assign(5)
    b = g2.variable("b")

def p2():
    def handle(event):
        print event
    context = distpy.Context(, secret="efzfzezfeezf")
    a = context.Variable("A")
    a.ON_CHANGED.subscribe(handle)

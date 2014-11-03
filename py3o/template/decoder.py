import ast


class Callable(object):
    def __init__(self, c):
        self.ast = c

    def get_func_str(self):
        func_name = self.ast.func.id
        args = ', '.join([a.id for a in self.ast.args])
        kwargs = ', '.join(
            ['%s=%s' % (k.arg, k.value.id) for k in self.ast.keywords]
        )
        if kwargs:
            kwargs = ', ' + kwargs
        return func_name + '(' + args + kwargs + ')'


class Attribute(object):
    def __init__(self, a):
        self.ast = a

    def __recur_construct_str(self, value):
        if isinstance(value, ast.Attribute):
            return self.__recur_construct_str(value.value) + '.' + value.attr
        return value.id

    def get_attr_str(self):
        return self.__recur_construct_str(self.ast)


class ForDecoder(object):
    def __init__(self, ast_for):
        self.ast = ast_for

    def get_variables(self):
        target = self.ast.target
        if not target:
            return None
        if isinstance(target, ast.Name):
            return target.id
        if isinstance(target, ast.Tuple):
            return tuple(name.id for name in target.elts)

    def get_iterables(self):
        it = self.ast.iter
        if not it:
            return None
        if isinstance(it, ast.Name):
            return it.id
        if isinstance(it, ast.Call):
            return Callable(it)
        if isinstance(it, ast.Attribute):
            return Attribute(it)


class Decoder(object):
    def __init__(self):
        self.instruction = None
        self.body = None
        self.vars = None
        self.iters = None

    def decode_py3o_instruction(self, instruction):
        # We convert py3o for loops into valid python for loop
        inst_str = "for " + instruction.split('"')[1] + ": pass\n"
        return self.decode(inst_str)

    def decode(self, instruction):
        # We attempt to compile 'instruction' and decode it
        self.instruction = instruction
        module = ast.parse(instruction)
        bodies = module.body
        if not bodies:
            return

        self.body = bodies[0]
        #TODO: Manage other instructions
        if isinstance(self.body, ast.For):
            obj = ForDecoder(self.body)
            self.vars = obj.get_variables()
            self.iters = obj.get_iterables()
            return {self.vars: self.iters}
        else:
            raise NotImplementedError()

    def get_variables(self):
        return self.vars

    def get_iterables(self):
        return self.iters
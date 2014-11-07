import ast
import json


class Callable(object):
    def __init__(self, c):
        self.ast = c

    def __str__(self):
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
        self._str = self.__recur_construct_str(a)
        self._list = self._str.split('.')

    def __recur_construct_str(self, value):
        if isinstance(value, ast.Attribute):
            return self.__recur_construct_str(value.value) + '.' + value.attr
        return value.id

    def __str__(self):
        return self._str

    def get_root(self):
        return self._list[0]


class ForList(object):
    def __init__(self, name, var_from):
        self.name = name
        self.childs = []
        self.attrs = []
        self._parent = None
        self.var_from = var_from

    def add_child(self, child):
        if not isinstance(child, ForList):
            raise Exception()
        child.parent = self
        self.childs.append(child)

    def add_attr(self, attr):
        self.attrs.append(attr)

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent

    @staticmethod
    def __recur_jsonify(forlist, data_dict, res):
        """ Recursive function that fill up the disctionary
        """
        # First we go through all attrs from the ForList and add respective
        #  keys on the dict.
        for a in forlist.attrs:
            a_list = a.split('.')
            if a_list[0] in data_dict:
                tmp = res
                for i in a_list[1:-1]:
                    if not i in tmp:
                        tmp[i] = {}
                    tmp = tmp[i]
                tmp[a_list[-1]] = reduce(getattr, a_list[1:], data_dict[a_list[0]])
        # Then create a list for all children, modify the datadict to fit the new child
        #  and call myself
        for c in forlist.childs:
            it = c.name.split('.')
            res[it[1]] = []
            for i, val in enumerate(reduce(getattr, it[1:], data_dict[it[0]])):
                new_data_dict = {c.var_from: val}
                res[it[1]].append({})
                ForList.__recur_jsonify(c, new_data_dict, res[it[1]][i])

    def jsonify(self, data_dict):

        """
        This function construct a json dump of our ForList object.
        :param data_dict: a dictionary with {key: browsable struct}
        :return: json representation of the datastruct
        """
        res = {}
        # The first level is a little bit special
        for a in self.attrs:
            a_list = a.split('.')
            if not a_list[0] in res:
                res[a_list[0]] = {}
            tmp = res[a_list[0]]
            for i in a_list[1:-1]:
                if not i in tmp:
                    tmp[i] = {}
                tmp = tmp[i]
            tmp[a_list[-1]] = reduce(getattr, a_list[1:], data_dict[a_list[0]])
        for c in self.childs:
            it = c.name.split('.')
            if not it[0] in res:
                res[it[0]] = {}
            res[it[0]][it[1]] = []
            for i, val in enumerate(reduce(getattr, it[1:], data_dict[it[0]])):
                new_data_dict = {c.var_from: val}
                res[it[0]][it[1]].append({})
                ForList.__recur_jsonify(c, new_data_dict, res[it[0]][it[1]][i])
        return json.dumps(res)



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
        if isinstance(it, ast.Attribute):
            return Attribute(it)

    def get_mapping(self):
        it = self.ast.iter
        target = self.ast.target

        # If a callable is found, only enumerate will be treated for now
        if isinstance(it, ast.Call):
            if (it.func.id == 'enumerate' and
                    len(it.args) == 1 and
                    isinstance(target, ast.Tuple) and
                    len(target.elts) == 2):
                attr = (
                    it.args[0].id
                    if isinstance(it.args[0], ast.Name)
                    else Attribute(it.args[0])
                )
                return target.elts[1].id, attr
            else:
                raise Exception()
        return self.get_variables(), self.get_iterables()


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
        # TODO: Manage other instructions
        if isinstance(self.body, ast.For):
            obj = ForDecoder(self.body)
            self.vars, self.iters = obj.get_mapping()
            return {self.vars: self.iters}
        else:
            raise NotImplementedError()

    def get_variables(self):
        return self.vars

    def get_iterables(self):
        return self.iters
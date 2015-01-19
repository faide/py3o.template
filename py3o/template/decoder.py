# -*- encoding: utf-8 -*-
import ast
# noinspection PyUnresolvedReferences
from six.moves import reduce


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
        self.name = str(name)
        self.childs = []
        self.attrs = []
        self._parent = None
        self.var_from = var_from

    def __eq__(self, other):
        return self.name == other.name

    def add_child(self, child):
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
    def __recur_to_dict(forlist, data_dict, res):
        """Recursive function that fills up the dictionary
        """
        # First we go through all attrs from the ForList and add respective
        #  keys on the dict.
        for a in forlist.attrs:
            a_list = a.split('.')
            if len(a_list) == 1:
                res = data_dict[a_list[0]]
                return res
            if a_list[0] in data_dict:
                tmp = res
                for i in a_list[1:-1]:
                    if not i in tmp:
                        tmp[i] = {}
                    tmp = tmp[i]
                if len(a_list) == 1:
                    tmp[a_list[0]] = data_dict[a_list[0]]
                else:
                    tmp[a_list[-1]] = reduce(
                        getattr,
                        a_list[1:],
                        data_dict[a_list[0]]
                    )
        # Then create a list for all children,
        # modify the datadict to fit the new child
        # and call myself
        for c in forlist.childs:
            it = c.name.split('.')
            res[it[-1]] = []
            for i, val in enumerate(
                    reduce(getattr, it[1:], data_dict[it[0]])
            ):
                new_data_dict = {c.var_from: val}
                if len(res[it[-1]]) <= i:
                    res[it[-1]].append({})
                res[it[-1]] = ForList.__recur_to_dict(
                    c, new_data_dict, res[it[-1]][i]
                )

        return res

    @staticmethod
    def to_dict(for_lists, global_vars, data_dict):
        """ Construct a dict object from a list of ForList object

        :param for_lists: list of for_list
        :param global_vars: list of global vars to add
        :param data_dict: data from an orm-like object (with dot notation)
        :return: a dict representation of the ForList objects
        """
        res = {}

        # The first level is a little bit special
        # Manage global variables
        for a in global_vars:
            a_list = a.split('.')
            tmp = res
            for i in a_list[:-1]:
                if not i in tmp:
                    tmp[i] = {}
                tmp = tmp[i]
            tmp[a_list[-1]] = reduce(getattr, a_list[1:], data_dict[a_list[0]])
        # Then manage for lists recursively
        for for_list in for_lists:
            it = for_list.name.split('.')
            tmp = res
            for i in it[:-1]:
                if not i in tmp:
                    tmp[i] = {}
                tmp = tmp[i]
            if not it[-1] in tmp:
                tmp[it[-1]] = []
            tmp = tmp[it[-1]]
            if not it[0] in data_dict:
                continue
            if len(it) == 1:
                loop = enumerate(data_dict[it[0]])
            else:
                loop = enumerate(reduce(getattr, it[-1:], data_dict[it[0]]))
            for i, val in loop:
                new_data_dict = {for_list.var_from: val}
                # We append a new dict only if we need
                if len(tmp) <= i:
                    tmp.append({})
                # Call myself with new context, and get result
                tmp[i] = ForList.__recur_to_dict(
                    for_list, new_data_dict, tmp[i]
                )

        return res


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
            return obj.get_mapping()
        else:
            raise NotImplementedError()

    def get_variables(self):
        return self.vars

    def get_iterables(self):
        return self.iters

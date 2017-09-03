#!/usr/bin/env python
###############################################################################
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program. If not, see <http://www.gnu.org/licenses/>.        #
#                                                                             #
###############################################################################

__author__ = "Ben Woodcroft, Joel Boyd"
__copyright__ = "Copyright 2017"
__credits__ = ["Ben Woodcroft"]
__license__ = "GPL3+"
__maintainer__ = "Joel Boyd"
__email__ = "joel.boyd3 near uq.edu.au"
__status__ = "Development"

###############################################################################
# Imports

import re

###############################################################################

class ModuleDescription:

    def __init__(self, module_description_string):
        self.module_description_string = module_description_string
        self.parsed_module = ModuleDescriptionParser().parse_module_string(
            module_description_string)

        if isinstance(self.parsed_module, ModuleDescriptionOrRelation):
            new_and = ModuleDescriptionAndRelation()
            new_and.relations = [self.parsed_module]
            self.parsed_module = new_and

    def amount_of_pathway_covered(self, ko_list):
        pass #FIXME self._global_steps = module_description_string.split(' ')

    def kos(self):
        '''Return an iterable over the total list of KOs in the module'''
        r = re.compile('(K\d+)')
        return re.findall(r, self.module_description_string)

    def num_steps(self):
        if isinstance(self.parsed_module, ModuleDescriptionAndRelation):
            return len(self.parsed_module.relations)
        else:
            raise Exception("Cannot work with non-AND type modules")

    def num_covered_steps(self, ko_set):
        if isinstance(self.parsed_module, ModuleDescriptionAndRelation):
            step_cov = 0
            path_cov = 0 
            for m in self.parsed_module.relations:
                step_passed, step_counts = m.satisfied_with(ko_set)
                if step_passed:
                    step_cov+=1
                    path_cov+=step_counts
            return step_cov, path_cov
        
        else:
            raise Exception("Cannot work with non-AND type modules")

class ModuleDescriptionAndRelation:
    def satisfied_with(self, set_of_kos):
        
        counts      = 0
        step_passed = False
        founds      = []
        
        for r in self.relations:
            found, count = r.satisfied_with(set_of_kos)
            if found:
                founds.append(1)
                counts += count
        
        step_passed = len(self.relations) == sum(founds)
        
        return step_passed, counts

class ModuleDescriptionOrRelation:
    def satisfied_with(self, set_of_kos):
        counts      = 0
        step_passed = False
        
        for r in self.relations:
            found, count = r.satisfied_with(set_of_kos)
            if found:
                step_passed = True
                return step_passed, counts
        
        return step_passed, counts

class ModuleDescriptionPlusRelation(ModuleDescriptionAndRelation): pass

class ModuleDescriptionKoEntry:
    def __init__(self, ko):
        self.ko = ko

    def satisfied_with(self, set_of_kos):
        found = self.ko in set_of_kos
        count = (1 if found else 0)
        return found, count


class ParserHelper: pass

class ModuleDescriptionParser:
    
    def correct_substrings(self, substring_list):
        fixed_substrings = []
        for substring in substring_list:
            # Omit optional enzyme (e.g. M00372) 
            # or undefined KO group (e.g. M00079)
            if substring.startswith('-'):
                continue 
            # Remove redundant and definitions
            substring=substring.replace(', ', ',')
            fixed_substrings.append(substring)
        return fixed_substrings
        
    def parse_module_string(self, string):

        frags1 = self.split_on_space(string)
        frags1 = self.correct_substrings(frags1) 

        if len(frags1) == 1:
            # rare if ever, I think
            frags1 = self.split_on_comma(frags1[0])
            master_relation = ModuleDescriptionOrRelation()
        else:
            master_relation = ModuleDescriptionAndRelation()
            
        current = ParserHelper()
        current.top_relation = master_relation
        current.understuff = frags1
        stack = list([current])
        while len(stack) > 0:
            current = stack.pop()
            new_stuff = []
            for e in current.understuff:
                if isinstance(e, str):
                    if re.match('^K\d+$', e):
                        new_stuff.append(ModuleDescriptionKoEntry(e))
                    else:
                        #TOREMOVE frags = self.split_on_space(e)
                        frags = self.split_on_comma(e)
                        if len(frags) == 1:
                            topush = ParserHelper()
                            #TOREMOVE comma_splits = self.split_on_comma(e)
                            comma_splits = self.split_on_space(e)
                            m = None
                            if len(comma_splits) == 1:
                                plus_splits = self.split_on_plus(e)
                                minus_splits = self.split_on_minus(e)
                                if len(plus_splits)>1:
                                    m = ModuleDescriptionPlusRelation()
                                    topush.understuff = plus_splits
                                elif len(minus_splits)>1:
                                    m = ModuleDescriptionAndRelation()
                                    topush.understuff = minus_splits[:1]
                                else:
                                    raise Exception("Parse exception on %s" % string)
                            else:
                                #m = ModuleDescriptionOrRelation()
                                m = ModuleDescriptionAndRelation()
                                topush.understuff = comma_splits
                            topush.top_relation = m
                            stack.append(topush)
                            new_stuff.append(m)
                        else:
                            #m = ModuleDescriptionAndRelation()                            
                            m = ModuleDescriptionOrRelation()
                            topush = ParserHelper()
                            topush.top_relation = m
                            topush.understuff = frags
                            stack.append(topush)
                            new_stuff.append(m)
                else:
                    new_stuff.append(e)
            current.top_relation.relations = new_stuff
        return master_relation


    def split_on(self, string, characters):
        bracket_counter = 0
        fragments = []
        current = []
        remove_end_brackets = True
        for i in xrange(len(string)):
            c = string[i]
            if c == '(':
                current += c
                bracket_counter += 1
            elif c == ')':
                current += c
                bracket_counter -= 1
                if bracket_counter == 0 and i < len(string)-1:
                    remove_end_brackets = False
            elif c in characters and bracket_counter == 0:
                fragments.append(''.join(current))
                current = ''
            else:
                current += c
        fragments.append(''.join(current))

        if remove_end_brackets and string[0] == '(':
            if string[-1] != ')': raise Exception("Parse error")
            return self.split_on(string[1:-1], characters)
        return fragments

    def split_on_space(self, string):
        return(self.split_on(string, ' '))

    def split_on_plus(self, string):
        return(self.split_on(string, '+'))

    def split_on_comma(self, string):
        return(self.split_on(string, ','))

    def split_on_minus(self, string):
        return(self.split_on(string, '-'))
#!/usr/bin/python3.3
# Copyright (C) 2014 Harold Grovesteen
#
# This file is part of SATK.
#
#     SATK is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     SATK is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with SATK.  If not, see <http://www.gnu.org/licenses/>.

# This module utilizes a finite state machine in conjunction with the lexer.py module
# to implement a parser.  It is built from the basic finite state machine support
# provide by the fsm.py module.

# Python imports: None
# SATK imports:
import fsm        # Access the generic finite state machine.
import lexer      # Access the lexical analyzer.

this_module="fsmparser.py"

# This FSM provides parsing services based upon the SATK lexical analyzer.
#
# Instance Arguments:
#   lex        Lexical analyzer used for parsing.
#   external   External object providing assistance.  Defaults to None.
#   init       Specify the initial FSMState instance name of the FSM.  
#              Defaults to 'init'.
#   trace      Enable (True) or disable (False) tracing of state actions.  Defaults to 
#              False.
# Instance methods:
#   stack      Allows a previously processed token to be placed on a LIFO stack
#   unstack    Removes a previously processed token from the LIFO stack
class FSMParser(fsm.FSM):
    def __init__(self,lex,scls=None,external=None,init="init",trace=False):
        super().__init__(trace=trace)
        if not isinstance(lex,lexer.Lexer):
            cls_str="%s - %s.__init__() -" % (this_module,self.__class__.__name__)
            raise ValueError("%s 'lex' argument must be an instance of "
                "lexer.Lexer: %s" % (cls_str,lex))

        self.lex=lex              # Lexical analyzer used for parsing
        self.scopecls=scls        # Class to create for my scope
        self.external=external    # External assistance object
        self._stack=[]            # A holding place for potential look aheads
        self._unstacked=None      # Queued token from stack for input to FSM

        self.init(init)
     
    # Uses the FSM to recognize a string converting it into lexical tokens.
    # Returns the global scope object constructed during the parse.
    def parse(self,string,scope=None,fail=False,lines=False,line=1):
        if self.scopecls is not None:
            scop=self.scopecls()
            scop.init()
        else:
            scop=scope   # If not defined with the parser, use the one supplied here.
        self.start(scope=scop)
        done=False
        for token in self.lex.tokenize(string,pos=0,fail=fail,lines=lines,line=line):
            #print("fsmparser.parse - token: %s" % token)
            while self._unstacked is not None:
                inp=self._unstacked
                self._unstacked=None
                done=self.machine(inp)
                if done:
                    break
            if not done:
                done=self.machine(token)
            #print("fsmparser.parse - done: %s" % done)
            if done:
                self.lex.stop()
        return self.scope()
     
    # Saves a previously presented token on a pushdown stack
    def stack(self,token,trace=None):
        if trace is not None:
            print("FSM:%s input token stacked: %s" % (trace,token))  
        self._stack.append(token)

    # Overrides to super class
    def start(self,scope=None):
        super().start(scope=scope)
        self._stack=[]

    # Queues a token from the pushdown stack for input to the FSM
    def unstack(self,trace=None):
        if len(self._stack)==0:
            cls_str="%s - %s.unstack():" % (this_module,self.__class__.__name__)
            raise ValueError("%s stack is empty" % cls_str)
        if self._unstacked is not None:
            cls_str="%s - %s.unstack():" % (this_module,self.__class__.__name__)
            raise ValueError("%s ustacked token already queued for machine" % cls_str)
        self._unstacked=self._stack.pop(-1)
        if trace is not None:
            print("FSM:%s token unstacked: %s" % (trace,token))
        return

# This class facilitates the management of scope within the FSM.  It  is recommended
# that this class or a subclass be used at least to manage global  FSM processing scope.
# This ensures the separation of FSM processor global name space from the FSM
# class and its states.
#
# The base class simply provides an alternative attribute name space.  A subclass
# may add language specific methods and an init() method for initialization.
class PScope(object):
    def __init__(self):
        self.init()     # Initialize myself

    # Optional initialization method.  If used, the subclass must provide it.
    def init(self): pass

class PState(fsm.FSMState):
    def __init__(self,name,end=False):
        super().__init__(name,end=end,fsm=True)

    # Must match the method signature of FSMState.ActID() method.
    def ActID(self,value,reg=False):
        if reg:
            if not isinstance(value,(lexer.Type,lexer.Unrecognized)):
                cls_str="%s - %s.ActID() -" % (this_module,self.__class__.__name__)
                raise ValueError("%s 'value' argument must be an instance of "
                    "lexer.Type: %s" % (cls_str,value))
        else:
            if not isinstance(value,lexer.Token):
                cls_str="%s - %s.ActID() -" % (this_module,self.__class__.__name__)
                raise ValueError("%s 'value' argument must be an instance of "
                    "lexer.Type: %s" % (cls_str,value))
        return value.tid
        
    # Returns the global PScope object of the parser.
    def scope(self):
        return self.fsm.scope()

if __name__ == "__main__":
    raise NotImplementedError("%s - intended for import use only" % this_module)
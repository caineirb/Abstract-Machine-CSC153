#!/usr/bin/env python3

from machine import readcode, assemble, initstate, meval

# Main program
def runMachine():
  codestr      = readcode()          # read the code from stdin
  code         = assemble(codestr)   # code is list of pair of instruction and parameter
  initialstate = initstate(code)     # return a state: pair of code and stack (empty) (code, stack)
  finalstate   = meval(initialstate)
  _, stack, memory  = finalstate
  print(stack, memory)

  #print(finalstate)
  #print(finalstate[1][0])               # The second part is stack

# (Code, Stack, Memory) = state
#    0     1     2

if __name__ == "__main__":
  runMachine()

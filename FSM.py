import re

class FSM:

    rule_pattern = re.compile(r'\((\d+),(\w+),\(((\d+,)*\d+)\)\)')
    #despite a few checks fsm could still be invalid after this
    def file_init(self, f):
        try:
            self.num_states = int(f.readline())
            self.start_state = 0
            self.accept_state = self.num_states-1
            self.states = [dict() for i in range(self.num_states)]
            num_rules = int(f.readline())

            for i in range(num_rules):
                matches = FSM.rule_pattern.match(f.readline())
                if matches==None:
                    raise ValueError
                state_n = int(matches.group(1))
                if state_n >= self.num_states:
                    raise ValueError
                symbol = matches.group(2)

                #not sure which is nicer looking, maybe I shouldn't call
                #eval unnecessarily but it's so much fun

                #to_states {int(x) for x in matches.group(3).split(",")}
                to_states = eval("{"+matches.group(3)+"}")
                for new_state_n in to_states:
                    if new_state_n >= self.num_states:
                        raise ValueError

                self.states[state_n][symbol] = to_states
        except IOError:
            print("Could not read file "+f.name)
            raise
        except ValueError:
            print("Invalid file "+f.name)
            raise

    def string_init(self, s):

        if not s:
            self.states = [{}]
            self.num_states = 1
            self.start_state = 0
            self.accept_state = 0
            return
        elif len(s) == 1:
            self.states = [ {s: {1}}, {}]
            self.num_states = 2 
            self.start_state = 0
            self.accept_state = 1
            return
        else:
            raise ValueError

#         rgp = RegExParser(s)

#        try:
#            self = rgp.parse()
#        except ValueError:
#            print("Invalid regular expression")
#            raise

    def __init__(self, o):
        if type(o) is file:
            self.file_init(o)
            
        elif type(o) is str:
            self.string_init(o)
        else:
            print("Argument must be file or string")
            raise ValueError

    def nextState(self):
        self.states.append(dict())
        self.num_states += 1
        return self.num_states -1

    def close(self):
        new_start = self.nextState()
        new_accept = self.nextState()

        self.insertEdges('EPSILON',new_start,{self.start_state,new_accept})
        self.insertEdges('EPSILON',self.accept_state,{self.start_state,new_accept})
        self.start_state = new_start
        self.accept_state = new_accept

    def unionize(self, other):
        new_states = list(other.states)
        new_states = [ {edge: {n+self.num_states for n in state_ns} for (edge,state_ns) in state.items()  } for state in new_states ] 
        self.states.extend(new_states)

        self.insertEdge('EPSILON',self.start_state,other.start_state+self.num_states)    
        self.insertEdge('EPSILON',other.accept_state+self.num_states,self.accept_state)
         
        self.num_states += other.num_states
      
    def concatenate(self, other):
        new_states = list(other.states)
        new_states = [ {edge: {n+self.num_states for n in state_ns} for (edge,state_ns) in state.items()  } for state in new_states ] 
        self.states.extend(new_states)

        self.insertEdge('EPSILON',self.accept_state,other.start_state+self.num_states)        

        self.accept_state = other.accept_state + self.num_states
        self.num_states += other.num_states

    def insertEdge(self, t, from_s, to_s):
        if t in self.states[from_s]:
            self.states[from_s][t].add(to_s)
        else:
            self.states[from_s][t] = {to_s}

    def insertEdges(self, t, from_s, to_s):
        if t in self.states[from_s]:
            self.states[from_s][t] |= to_s
        else:
            self.states[from_s][t] = to_s

    def exportToGraph(self, f):
        try:
            f.write("digraph fsm {\n")
            f.write("rankdir=\"LR\"\n")
            f.write("start [shape=\"plaintext\",label=\"start\"]\n")
    
            for i in range(len(self.states)):
                if i == self.accept_state:
                    f.write(str(i) + " [shape=\"doublecircle\"]\n")
                else:
                    f.write(str(i) + " [shape=\"circle\"]\n")   

            f.write("start->"+str(self.start_state)+"\n")
            for state_n,state in enumerate(self.states):
                for symbol,to_states in state.items():  
                    for new_state_n in to_states:
                        f.write(str(state_n)+"->"+str(new_state_n)+" [label=\""+symbol+"\"]\n")
            
            f.write("}\n")  
        except IOError:
            print("Could not write to file "+f.name)

    def simulate(self, string):
        current_state_ns = {self.start_state}
        new_state_ns = current_state_ns
        for c in string:

            #calculate EPSILON transitions
            while new_state_ns:
                add_state_ns = set()
                for state_n in new_state_ns:
                    state = self.states[state_n]    
                    if "EPSILON" in state:
                        add_state_ns |= (state["EPSILON"] - current_state_ns)
                new_state_ns = add_state_ns
                current_state_ns |= add_state_ns

            #calculate set of states after transition on c
            for state_n in current_state_ns:
                state = self.states[state_n]
                if c in state:
                    new_state_ns |= state[c]

            if not new_state_ns:
                return False
            current_state_ns = new_state_ns
        

        #calculate final EPSILON transitions
        while new_state_ns:
            add_state_ns = set()
            for state_n in new_state_ns:
                state = self.states[state_n]    
                if "EPSILON" in state:
                    add_state_ns |= (state["EPSILON"] - current_state_ns)
            new_state_ns = add_state_ns
            current_state_ns |= add_state_ns

        return self.accept_state in current_state_ns


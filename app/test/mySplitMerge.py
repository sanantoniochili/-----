import math
import os


from dispel4py.examples.graph_testing import testing_PEs as t
from dispel4py.workflow_graph import WorkflowGraph
from dispel4py.core import GenericPE, NAME, TYPE, GROUPING
from dispel4py.base import SimpleFunctionPE, IterativePE, BasePE
from dispel4py.provenance import *


def read_in(filename):
    nos = []
    # open file
    with open(filename) as f:
        # read numbers and convert to int
        for line in f:
            nos += [int(x) for x in line.split()]
        f.close()
    return nos


class DataInGranuleType(ProvenanceType):

    def extractItemMetadata(self, data, port):
        return [{port:str(data)}]

class splitPE(GenericPE):
    '''
    PE to split list of numbers to sublists and perform
    actions on the sublists in parallel
    '''
    INPUT_NAME = 'input'

    def __init__(self, num_outputs=0):
        GenericPE.__init__(self)

        self._add_input(splitPE.INPUT_NAME)

        # read input from file
        self.nos = [1, 2, 3, 4, 5, 6, 7, 4, 5, 9, 10, 300]

        # create output chunk dict
        self.num_outputs = num_outputs
        for i in range(num_outputs):
            name = '%s%s' % (BasePE.OUTPUT_NAME, i)
            self.outputconnections['output%s' % i] = {
                NAME: 'output%s' % i, TYPE: ['number']}
        self.outputnames = list(self.outputconnections.keys())

    def _process(self, inputs):

        # split into sublists of about same length
        n = math.ceil(len(self.nos) / self.num_outputs)
        n = int(n)
        self.chunks = [self.nos[x:x+n] for x in range(0, len(self.nos), n)]

        result = {}
        count = 0
        # for every expected output split into chunks
        for output in self.outputnames:
            result[output] = self.chunks[count]
            count += 1
        self.log("Writing out %s" % result)
        return result


def mult(input):
    '''
    Simple multiplication of list elements with number 2
    '''
    return [i*2 for i in input]


class mergePE(GenericPE):
    '''
    PE to merge input lists from different nodes
    into one bigger list
    '''
    result = []
    counter = 0

    def __init__(self, num_inputs=0):
        GenericPE.__init__(self)

        # form expected input dict
        self.num_inputs = num_inputs
        for i in range(num_inputs):
            self.inputconnections['input%s' % i] = {
                NAME: 'input%s' % i, TYPE: ['number']}
        self.outputconnections = {'output': {NAME: 'output', TYPE: ['result']}}

    def _process(self, inputs):
        # combine different input lists into one
        for inp in self.inputconnections:
            if inp in inputs:
                self.result += inputs[inp]
                self.counter += 1

        if self.counter == self.num_inputs:
            self.counter=0
            out=self.result.copy()
            self.result=[]
            return {'output': out}


class fwritePE(GenericPE):
    '''
    Write input to file
    '''
    INPUT_NAME = 'input'
    OUTPUT_NAME = 'output'

    def __init__(self):
        GenericPE.__init__(self)
        self._add_input(fwritePE.INPUT_NAME)
        self._add_output(fwritePE.OUTPUT_NAME)

    def _process(self, inputs):
        # write result input to file 'output.txt'
        data = inputs[fwritePE.INPUT_NAME]

        with open('output.txt','w') as f:
            for item in data:
                f.write("%s " % item)
            f.close()
        self.write("output",data,location="output.txt",metadata={'results':data})


def testSplitMerge():
    '''
    Creates the split/merge graph with 4 nodes.
    '''
    graph = WorkflowGraph()
    split = splitPE(3)
    mult1 = SimpleFunctionPE(mult)
    mult2 = SimpleFunctionPE(mult)
    mult3 = SimpleFunctionPE(mult)
    merge = mergePE(3)
    test = fwritePE()

    graph.connect(split, 'output0', mult1, 'input')
    graph.connect(split, 'output1', mult2, 'input')
    graph.connect(split, 'output2', mult3, 'input')
    graph.connect(mult1, 'output', merge, 'input0')
    graph.connect(mult2, 'output', merge, 'input1')
    graph.connect(mult3, 'output', merge, 'input2')
    graph.connect(merge, 'output', test, 'input')

    return graph


''' important: this is the graph_variable '''
graph = testSplitMerge()



#provenance configuration:
prov_config =  {
                'provone:User': "aspinuso",
                's-prov:description' : "API demo",
                's-prov:workflowName': "splitMerge",
                's-prov:workflowType': "dare:Thing",
                's-prov:workflowId'  : "splitmerge",
                's-prov:save-mode'   : 'service',
                's-prov:WFExecutionInputs':  [],
                # defines the Provenance Types and Provenance Clusters for the Workflow Components
                's-prov:componentsType' :
                                   {'mergePE': {'s-prov:type':(AccumulateFlow,DataInGranuleType,)},
                #                                 's-prov:prov-cluster':'seis:Processor'},
                                    'splitPE': {'s-prov:type':(DataInGranuleType,)}},
                #                                 's-prov:prov-cluster':'seis:Processor'},
                #                    'StoreStream':    {'s-prov:prov-cluster':'seis:DataHandler',
                #                                       's-prov:type':(SeismoPE,)},
                's-prov:sel-rules': None
                }

#rid='DARE_SPLITMERGE_'+getUniqueId()

#provenance storage endpoint:
ProvenanceType.REPOS_URL='http://'+os.getenv('SPROV_SERVICE_HOST')+':'+os.getenv('SPROV_SERVICE_PORT')+'/workflowexecutions/insert'
ProvenanceType.BULK_SIZE=5

# Finally, provenance enhanced graph is prepared:
configure_prov_run(graph,
                    provImpClass=(ProvenanceType,),
                    input=prov_config['s-prov:WFExecutionInputs'],
                    username=prov_config['provone:User'],
                    runId=os.getenv('RUN_ID'),
                    description=prov_config['s-prov:description'],
                    workflowName=prov_config['s-prov:workflowName'],
                    workflowType=prov_config['s-prov:workflowType'],
                    workflowId=prov_config['s-prov:workflowId'],
                    save_mode=prov_config['s-prov:save-mode'],
                    componentsType=prov_config['s-prov:componentsType'],
                    sel_rules=prov_config['s-prov:sel-rules']
                    )

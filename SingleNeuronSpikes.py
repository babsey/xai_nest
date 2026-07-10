from argparse import ArgumentParser
from xai_components.base import SubGraphExecutor, InArg, OutArg, Component, xai_component, parse_bool
from xai_components.xai_nest.nest_components import NESTCreate, NESTResetKernel, NESTSimulate, NESTSetKernelStatus, NESTConnect, NESTGetStatus

@xai_component(type='xircuits_workflow')
class SingleNeuronSpikes(Component):
    output: OutArg[any]

    def __init__(self, id: str=None):
        super().__init__()
        self.__id__ = id
        self.__start_nodes__ = []
        self.c_0 = NESTResetKernel()
        self.c_0.__id__ = 'aca8893e-0279-473a-885e-d6943eb2ccd2'
        self.c_1 = NESTSetKernelStatus()
        self.c_1.__id__ = '3a2e9655-fd92-4ca2-ba63-0f971f71ce2c'
        self.c_2 = NESTConnect()
        self.c_2.__id__ = '6d844a6b-3164-4419-a7da-c683d1f6da80'
        self.c_3 = NESTSimulate()
        self.c_3.__id__ = 'd8564572-23cb-4473-8c7e-d9fbbff307b2'
        self.c_4 = NESTGetStatus()
        self.c_4.__id__ = '9e16dbb7-7502-42eb-9898-fa2a9547b1d6'
        self.c_5 = NESTCreate()
        self.c_5.__id__ = 'faf7fee3-222b-4ed4-83bb-e23d1591987a'
        self.c_6 = NESTCreate()
        self.c_6.__id__ = 'bb8225ba-ca22-48ae-967b-91f392b43994'
        self.c_1.resolution.value = 1
        self.c_2.pre.connect(self.c_6.value)
        self.c_2.post.connect(self.c_5.value)
        self.c_3.t.value = 1000
        self.c_4.nodes_or_conns.connect(self.c_5.value)
        self.c_4.keys.value = ['events']
        self.c_5.model.value = 'spike_recorder'
        self.c_6.model.value = 'iaf_psc_alpha'
        self.c_6.params.value = {'I_e': 376}
        self.output.connect(self.c_4.value)
        self.c_0.next = self.c_1
        self.c_1.next = self.c_6
        self.c_2.next = self.c_3
        self.c_3.next = self.c_4
        self.c_4.next = None
        self.c_5.next = self.c_2
        self.c_6.next = self.c_5

    def execute(self, ctx):
        for node in self.__start_nodes__:
            if hasattr(node, 'init'):
                node.init(ctx)
        SubGraphExecutor(self.c_0).do(ctx)

def main(args):
    import pprint
    ctx = {}
    ctx['args'] = args
    flow = SingleNeuronSpikes()
    flow.next = None
    flow.do(ctx)
    print('output:')
    pprint.pprint(flow.output.value)
if __name__ == '__main__':
    parser = ArgumentParser()
    args, _ = parser.parse_known_args()
    main(args)
    print('\nFinished Executing')
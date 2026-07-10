from xai_components.base import InArg, OutArg, InCompArg, Component, BaseComponent, xai_component, SubGraphExecutor, \
    dynalist
import nest


@xai_component(color='orange')
class NESTConnect(Component):
    """Connect `pre` nodes to `post` nodes.

    Nodes in `pre` and `post` are connected using the specified connectivity
    (`all-to-all` by default) and synapse type (`static_synapse` by default).
    Details depend on the connectivity rule.

    Lists of synapse models and connection rules are available as
    ``nest.synapse_models`` and ``nest.connection_rules``, respectively.

    Parameters
    ----------
    pre : NodeCollection (or array-like object)
        Presynaptic nodes, as object representing the IDs of the nodes
    post : NodeCollection (or array-like object)
        Postsynaptic nodes, as object representing the IDs of the nodes
    conn_spec : str or dict, optional
        Specifies connectivity rule, see below
    syn_spec : str or dict, optional
        Specifies synapse model, see below
    return_synapsecollection: bool
        Specifies whether or not we should return a `SynapseCollection` of pre
        and post connections

    Notes
    -----
    It is possible to connect NumPy arrays of node IDs one-to-one by passing
    the arrays as `pre` and `post`, specifying `'one_to_one'` for `conn_spec`.
    In that case, the arrays may contain non-unique IDs. You may also specify
    weight, delay, and receptor type for each connection as NumPy arrays in the 
    `syn_spec` dictionary.
    This feature is currently not available when MPI is used; trying to connect 
    arrays with more than one MPI process will raise an error.

    If pre and post have spatial positions, a `mask` can be specified as a
    dictionary. The mask define which nodes are considered as potential targets
    for each source node. Connections with spatial nodes can also use 
    `nest.spatial_distributions` as parameters, for instance for the 
    probability `p`.

    **Connectivity specification (conn_spec)**

    Available rules and associated parameters::

     - 'all_to_all' (default)
     - 'one_to_one'
     - 'fixed_indegree', 'indegree'
     - 'fixed_outdegree', 'outdegree'
     - 'fixed_total_number', 'N'
     - 'pairwise_bernoulli', 'p'
     - 'symmetric_pairwise_bernoulli', 'p'
     - 'pairwise_poisson', 'pairwise_avg_num_conns'

    See `conn_rules` for more details, including example usage.

    **Synapse specification (syn_spec)**

    The synapse model and its properties can be given either as a string
    identifying a specific synapse model (default: `static_synapse`) or
    as a dictionary specifying the synapse model and its parameters.

    Available keys in the synapse specification dictionary are::

     - 'synapse_model'
     - 'weight'
     - 'delay'
     - 'receptor_type'
     - any parameters specific to the selected synapse model.

    See `synapse_spec` for details, including example usage.

    All parameters are optional and if not specified, the default values
    of the synapse model will be used. The key 'synapse_model' identifies the
    synapse model, this can be one of NEST's built-in synapse models
    or a user-defined model created via `nest.CopyModel`.

    If `synapse_model` is not specified the default model `static_synapse`
    will be used.

    Distributed parameters can be defined through NEST's different 
    parametertypes. NEST has various random parameters, spatial parameters and
    distributions (only accessible for nodes with spatial positions), logical
    expressions and mathematical expressions, which can be used to define node
    and connection parameters.

    To see all available parameters, see documentation defined in
    distributions, logic, math, random and spatial modules.

    See Also
    ---------
    `connectivity_concepts`
    """

    pre: InCompArg[any]
    post: InCompArg[any]
    conn_spec: InArg[dict]
    syn_spec: InArg[dict]
    return_synapsecollection: InArg[bool]
    value: OutArg[dict]
    
    def execute(self, ctx) -> None:
        self.value.value = nest.Connect(
            self.pre.value, 
            self.post.value, 
            self.conn_spec.value,
            self.syn_spec.value,
            self.return_synapsecollection.value
        )

@xai_component(color='orange')
class NESTCreate(Component):
    """Create one or more nodes.

    Generates `n` new network objects of the supplied model type. If `n` is not
    given, a single node is created. Note that if setting parameters of the
    nodes fail, the nodes will still have been created.

    Note
    ----
    If `Create()` is called with two arguments and the second argument (`n`) is
    a dictionary, this dictionary will be intepreted as `params` for backward 
    compatibility.

    During network construction, create all nodes representing model neurons 
    first, then all nodes representing devices (generators, recorders, or 
    detectors), or all devices first and then all neurons. Otherwise, network 
    connection can be slow, especially in parallel simulations of networks
    with many devices.

    Parameters
    ----------
    model : str
        Name of the model to create
    n : int, optional
        Number of nodes to create
    params : dict or list, optional
        Parameters for the new nodes. Can be any of the following:

        - A dictionary with either single values or lists of size n.
          The single values will be applied to all nodes, while the lists will
          be distributed across the nodes. Both single values and lists can be
          given at the same time.
        - A list with n dictionaries, one dictionary for each node.

        Values may be `Parameter` objects. If omitted,
        the model's defaults are used.
    positions: `grid` or `free` object, optional
        Object describing spatial positions of the nodes. If omitted, the nodes
        have no spatial attachment.

    Returns
    -------
    NodeCollection:
        Object representing the IDs of created nodes, see `NodeCollection` for
        more.

    Raises
    ------
    NESTError
        If setting node parameters fail. However, the nodes will still have
        been created.
    TypeError
        If the positions object is of wrong type.
    """

    model: InCompArg[str]
    n: InArg[int]
    params: InArg[dict]
    positions: InArg[any]
    value: OutArg[any]

    def __init__(self):
        super().__init__()
        self.n.value = 1
        self.params.value = None
        self.positions.value = None
    
    def execute(self, ctx) -> None:
        self.value.value = nest.Create(
            self.model.value, 
            self.n.value, 
            self.params.value,
            self.positions.value
        )

@xai_component(color='orange')
class NESTGetStatus(Component):
    """Get parameters from nodes or connections.

        Parameters
        ----------
        nodes_or_conns: NodeCollection or SynapseCollection
            `NodeCollection` of nodes or `SynapseCollection` of connections.
        keys : str or list, optional
            Parameters to get from the nodes. It must be one of the following:

            - A single string.
            - A list of strings.
            - One or more strings, followed by a string or list of strings.
              This is for hierarchical addressing.
        output : str, ['pandas','json'], optional
             If the returned data should be in a Pandas DataFrame or in a
             JSON string format.

        Returns
        -------
        int or float:
            If there is a single node in the `NodeCollection`, and a single
            parameter in params.
        array_like:
            If there are multiple nodes in the `NodeCollection`, and a single
            parameter in params.
        dict:
            If there are multiple parameters in params. Or, if no parameters
            are specified, a dictionary containing aggregated parameter-values
            for all nodes is returned.
        DataFrame:
            Pandas Data frame if output should be in pandas format.

        Raises
        ------
        TypeError
            If the input params are of the wrong form.
        KeyError
            If the specified parameter does not exist for the nodes.
    """

    nodes_or_conns: InCompArg[any] 
    keys: InArg[list]
    output: InArg[str]
    value: OutArg[any]
    
    def execute(self, ctx) -> None:
        # try: 
        self.value.value = nest.GetStatus(
            self.nodes_or_conns.value, 
            self.keys.value, 
            self.output.value
        )
        # except:
        #     self.value.value = self.nodes_or_conns.value.get(keys, output)

@xai_component(color='orange')
class NESTResetKernel(Component):
    """Reset the simulation kernel.

    This will destroy the network as well as all custom models created with
    `nest.CopyModel`. Calling this function is equivalent to restarting NEST.

    In particular,

    * all network nodes
    * all connections
    * all user-defined neuron and synapse models

    are deleted, and

    * time
    * random generators

    are reset. All dynamically loaded modules (via `nest.Install()`) are
    unloaded.

    """
    
    def execute(self, ctx) -> None:
        nest.ResetKernel()

@xai_component(color='orange')
class NESTSetKernelStatus(Component):
    """Set parameters for the simulation kernel.

    See the documentation of `sec_kernel_attributes` for a valid list of
    params.

    Parameters
    ----------

    params : dict
        Dictionary of parameters to set.

    See Also
    --------

    GetKernelStatus

    """

    local_num_threads: InArg[int]
    resolution: InArg[float]
    rng_seed: InArg[int]
    
    def __init__(self):
        super().__init__()
        self.local_num_threads.value = 1
        self.resolution.value = 0.1
        self.rng_seed.value = 1

    def execute(self, ctx) -> None:        
        nest.SetKernelStatus({
            'local_num_threads': self.local_num_threads.value,
            'resolution': self.resolution.value,
            'rng_seed': self.rng_seed.value
        })

@xai_component(color='orange')
class NESTSimulate(Component):
    """Simulate the network for `t` milliseconds.

    `Simulate(t)` runs `Prepare()`, `Run(t)`, and `Cleanup()` in this order.

    Parameters
    ----------
    t : float
        Time to simulate in ms

    See Also
    --------
    RunManager, Prepare, Run, Cleanup

    """

    t: InCompArg[int]
    
    def execute(self, ctx) -> None:        
        nest.Simulate(self.t.value)

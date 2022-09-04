# GO WECC
The grid operations (GO) model of the U.S. Western Interconnection is developed to address weather and water dynamics, and associated vulnerabilities in this bulk power system. It is created through the IM3 program at Pacific Northwest National Laboratory and NC State University. GO model includes 28 balancing authorities (BA) and 12 states.
GO model is written by using Pyomo package in Python. It utilizes [10,000 nodal topology dataset of U.S. Western Interconnection created by Texas A&M University](https://electricgrids.engr.tamu.edu/electric-grid-test-cases/activsg10k/). The current optimization solver is Gurobi but users can select another solver to run the model.

GO model allows users to choose:
* Number of nodes to retain in the system
* Mathematical formulation (users can choose to formulate the problem as linear programming (LP) or mixed interger linear prograaming (MILP))
* Transmission line limit scaling factors
* BA to BA hurdle rate scaling factors

## Running GO WECC Model
Running GO model includes two main steps:
### Preprocessing of data
1. The first step is to use mapper script in Model_setup folder. This script selects a prespecified number of nodes to retain from Texas A&M University synthetic network. Outputs of this script are “excluded_nodes.csv” and “selected_nodes.csv” files for each model configuration. Those outputs are saved into Selected_nodes folder.

2. Selected nodes are used in Arizona State University network reduction algorithm script. This algorithm simplifies the WECC network and reduces the number of nodes, transmission lines, and generators in the model to decrease computational requirements. Output of this algorithm (Results_Excluded_Nodes.xlsx) provides detailed information about the retained nodes, which is used in the next steps. 

 Results from ASU Network Reduction Algorithm are utilized in “reduced_etwork_data_allocation.py” script to create model files such as thermal generator parameters, available hourly wind, and solar power at each node, hourly demand at each node, etc. This script also creates different folders for each model configuration and populates those with relevant scripts and data to run the model. 









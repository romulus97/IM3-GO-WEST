# GO WECC
The grid operations (GO) model of the U.S. Western Interconnection is developed to address weather and water dynamics, and associated vulnerabilities in this bulk power system. It is created through the IM3 program at Pacific Northwest National Laboratory and NC State University. GO model includes 28 balancing authorities (BA) and 12 states.
GO model is written by using Pyomo package in Python. It utilizes [10,000 nodal topology dataset of U.S. Western Interconnection created by Texas A&M University](https://electricgrids.engr.tamu.edu/electric-grid-test-cases/activsg10k/). The current optimization solver is Gurobi but users can select another solver to run the model.

GO model allows users to choose:
* Number of nodes to retain in the system
* Mathematical formulation (users can choose to formulate the problem as linear programming (LP) or mixed interger linear prograaming (MILP))
* Transmission line limit scaling factors
* BA to BA hurdle rate scaling factors





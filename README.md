# GO WEST
The grid operations model of the U.S. Western Interconnection (GO WEST) is created through the IM3 program at Pacific Northwest National Laboratory and NC State University. It is developed to address weather and water dynamics, and associated vulnerabilities in this bulk power system. It is a security-constrained unit commitment and economic dispatch (UC/ED) model, and covers 28 balancing authorities (BA) and 12 states.
GO WEST model is written by using Pyomo package in Python. It utilizes [10,000 nodal topology dataset of U.S. Western Interconnection](https://electricgrids.engr.tamu.edu/electric-grid-test-cases/activsg10k/) created by Texas A&M University (TAMU). The current optimization solver is Gurobi but users can select another solver to run the model.

GO WEST model allows users to choose:
* Number of nodes to retain in the system
* Mathematical formulation (users can choose to formulate the problem as linear programming (LP) or mixed integer linear programming (MILP))
* Transmission line capacity scaling factors
* BA to BA hurdle rate scaling factors

## Running GO WEST Model
Running GO WEST model includes two main steps:
### Preprocessing of data
1. The first step is to use "mapper.py" script in Model_setup folder. This script selects a prespecified number of nodes to retain from TAMU synthetic network. Outputs of this script are "excluded_nodes.csv" and "selected_nodes.csv" files for each model configuration. Those outputs are saved in "Selected_nodes" folder.

2. Selected nodes are used in Arizona State University (ASU) network reduction algorithm. This algorithm simplifies the network and reduces the number of nodes, transmission lines, and generators in the model to decrease computational requirements. Output of this algorithm ("Results_Excluded_Nodes.xlsx") provides detailed information about the retained nodes, which is used in the next steps. 

3. Results from ASU network reduction algorithm are utilized in “reduced_etwork_data_allocation.py” script to create model files such as generator parameters, available hourly solar and wind power at each node, and hourly demand at each node, etc. This script also creates different folders for each model configuration and populates those with relevant scripts and data to run the model. 

### Starting the simulation
In "Simulation_folders", the script named "WECCDataSetup.py" is used to merge all relevant data into "WECC_data.dat" file, which is interpreted by Pyomo. Finally, "wrapper.py" is run to call the optimization solver and start the simulation. The process of running GO model is illustrated in the figure below. 

![GO_process](https://user-images.githubusercontent.com/56842236/188332405-580e2386-7796-43f2-97c2-d591eec76197.png)

For reference, the files in the "Simulation_folders" and their purpose is explained in the table below.

| File Name      | Description |
| ----------- | ----------- |
| BA_to_BA_hurdle_scaled.csv | Scaled hurdle rates between BAs |
| BA_to_BA_transmission_matrix.csv   | Binary file showing which lines are connected to which BAs |
| data_genparams.csv | Names and parameters of generators |
| gen_outage_cat.npy | Generator capacity categories and names for outage modeling |
| Fuel_prices.csv | Daily coal and natural gas prices identified for each generator |
| gen_mat.csv | Binary file showing which generators are connected to which buses |
| Hydro_max.csv | Maximum hourly hydropower availability at each node |
| Hydro_min.csv | Minimum hourly hydropower availability at each node |
| Hydro_total.csv | Daily total hydropower availability at each node |
| line_params.csv | Thermal limits and reactances of each transmission line |
| line_to_bus.csv | Binary file showing which lines are connected to which buses |
| must_run.csv | Available nodal must-run generation (from nuclear generators) |
| nodal_load.csv | Hourly electricity demand at each node |
| nodal_solar.csv | Hourly available solar power generation at each node |
| nodal_wind.csv | Hourly available wind power generation at each node |
| thermal_gens.csv | Names and parameters of just thermal generators |
| west_YYYY_lostcap.csv | Hourly capacity on outage for each generator capacity categories |
| WECCDataSetup.py | Python script that creates "WECC_data.dat" file which includes all data above in a format accessible by Pyomo |
| WECC_LP_coal.py | This is only present if user selects to include only coal power plants in the unit commitment (UC) process. This contains the LP problem formulation of GO WEST model. |
| WECC_LP_coal_gas.py | This is only present if user selects to include both natural gas and coal power plants in the unit commitment (UC) process. This contains the LP problem formulation of GO WEST model. |
| WECC_MILP_coal.py | This is only present if user selects to include only coal power plants in the unit commitment (UC) process. This contains the MILP problem formulation of GO WEST model. |
| WECC_MILP_coal_gas.py | This is only present if user selects to include both natural gas and coal power plants in the unit commitment (UC) process. This contains the MILP problem formulation of GO WEST model. |
| WECC_simple.py | This is only present if user selects to skip unit commitment (UC) process and model only economic dispatch (ED) process. This contains the LP problem formulation of GO WEST model. |
| wrapper_coal.py | This is only present if user selects to include only coal power plants in the unit commitment (UC) process. This script calls an optimization solver, starts the simulations and returns the model outputs. |
| wrapper_coal_gas.py | This is only present if user selects to include both natural gas and coal power plants in the unit commitment (UC) process. This script calls an optimization solver, starts the simulations and returns the model outputs. |
| wrapper_simple.py | This is only present if user selects to skip unit commitment (UC) process and model only economic dispatch (ED) process. This script calls an optimization solver, starts the simulations and returns the model outputs. |

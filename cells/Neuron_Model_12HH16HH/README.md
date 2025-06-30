# Neuron Model Mutations

## Instructions for incoporating mutations into the layer 5 pyramidal neuron model.

For Nav1.2 and Nav1.6, the L5PN model takes two mechanisms for each to represent each gene having two alleles.

Since we are primarily interested in Nav1.2 mutations, we will replace one allele with a mutant mechanism to
create a heterzygous neuron (1 WT allele + 1 mutant allele).

To achieve this we will change the parameter values in na12_mut.txt to reflect the variant's biophysical properties,
then incorporate the mechanism into the model.

## First change the model arguments to accept a different (mutant) param file: 
1. In Na12HH_Model_TF.py line 15, change: 
    
    ```python
    mut_name = 'na12annaTFHH2' to 'na12_mut'


2. In NeuronModelClass.py line 23, make a similar change:
    
    ```python
    na12mut_name = 'na12annaTFHH2' to 'na12_mut'


## Update the params in the param file:
3. The params file will need to be updated. The current file path is:

    ./Neuron_Model_12HH16HH/params/na12_mut.txt

4. You can use the following function to update the na12_mut.txt file

        ```python

        def modify_dict_file(filename, changes):
        ## Modifies values in a dictionary stored in a text file.
        ## filename: The name of the text file containing the dictionary.
        ## changes: A dictionary containing mutant params.

        try:
            with open(filename, "r") as file:
            content = file.read()

            # Try to load the content as a dictionary
            try:
            data = eval(content)
            except (NameError, SyntaxError):
            raise ValueError("Invalid dictionary format in the file.")

            # Modify values based
            for key, value in changes.items():
            if key not in data:
                print(f"Warning: Key '{key}' not found in the dictionary, skipping.")
            else:
                data[key] = value

            with open(filename, "w") as file:
            file.write(json.dumps(data, indent=2))

        except IOError as e:
            raise ValueError(f"Error opening or writing file: {e}")

        ## Example usage

        filename = ./Neuron_Model_12HH16HH/params/na12_mut.txt ##File name

        changes = {"Rd": 0.023204006298533603, "Rg": 0.015604498120126004, "Rb": 0.0925081211054913, "Ra": 0.23933332265451177, "a0s": 0.0005226303768198727, "gms": 0.14418575154491814, "hmin": 0.008449935591049326, "mmin": 0.01193016441163175, "qinf": 5.7593653647578105, "q10": 2.1532859986639186, "qg": 1.2968193480468215, "qd": 0.661199851452832, "qa1": 4.492758160759386, "smax": 3.5557932199839737, "sh": 8.358558450280716, "thinf": -47.8194205612529, "thi2": -79.6556083820085, "thi1": -62.40165437813537, "tha": -33.850064879126805, "vvs": 1.4255479951467982, "vvh": -55.33213046147061, "vhalfs": -40.89976480829731, "zetas": 13.403615755952343} ## example dictionary of parameters.

        modify_dict_file(filename, changes) ## run the function
        
        ```

5. You can loop through many mutations by assigning a single variable a dictionary of dictionaries.

        ```python

        multiple_variants = {
            "F257I":{"Rd": 0.028485318424710374, "Rg": 0.018420814026814298, "Rb": 0.05777962337521357, "Ra": 0.21341303335597034, "a0s": 0.00046381351100748496, "gms": 0.1341164855099387, "hmin": 0.006864146828635849, "mmin": 0.007621368015226187, "qinf": 6.486459886532015, "q10": 2.561051746368186, "qg": 1.3943995618682714, "qd": 0.797072687262635, "qa1": 6.540179485338942, "smax": 5.751234160342341, "sh": 9.898965372911075, "thinf": -42.299802571430824, "thi2": -64.0747495998566, "thi1": -48.0852551990378, "tha": -30.139992632180743, "vvs": 0.8468560048684934, "vvh": -53.739541326283735, "vhalfs": -42.22939001512733, "zetas": 12.811495608869796},

            "R1319G":{"Rd": 0.01821017957894782, "Rg": 0.015835927879902578, "Rb": 0.08669778691261865, "Ra": 0.25222138069588795, "a0s": 0.0005998602174497901, "gms": 0.15734865667490094, "hmin": 0.003049022325449447, "mmin": 0.009227432163769297, "qinf": 7.542037850663156, "q10": 1.3991326492121134, "qg": 0.11658354700541385, "qd": 0.41022807889968216, "qa1": 6.23800810747929, "smax": 2.297618044174789, "sh": 9.225725362157418, "thinf": -46.09023665760313, "thi2": -57.0320710747067, "thi1": -62.70708396987019, "tha": -29.27378295119758, "vvs": 0.25717057711770985, "vvh": -58.74304862555019, "vhalfs": -31.258170795759927, "zetas": 10.786789360357215},

            "K1480E":{"Rd": 0.017988222179818, "Rg": 0.014526835880098123, "Rb": 0.032287886870504066, "Ra": 0.20374071568963156, "a0s": 0.00043332968046547453, "gms": 0.2506541588105391, "hmin": 0.003724133667885614, "mmin": 0.022703936878165614, "qinf": 8.056557948665372, "q10": 2.1947359595099254, "qg": 1.607903072936985, "qd": 0.9369754615041643, "qa1": 6.825173338201797, "smax": 9.756858258324922, "sh": 9.29652730203526, "thinf": -44.454878232047506, "thi2": -78.8896576923306, "thi1": -61.97876376872753, "tha": -25.286365983599477, "vvs": 0.665802756552117, "vvh": -45.45240491205891, "vhalfs": -18.50057219270583, "zetas": 11.579233310014331}
            }


        for mutname,dict in multiple_variants.items():
            modify_dict_file(filename,dict)
            print(f"Mutant name is {mutname}")
            print(f"It's corresponding dictionary is {dict}")

            # Do other things...

        ```

## Alternative method to update params
6. If for some reason you want to have a unique txt file for each mutant, place each file in the ./Neuron_Model_12HH16HH/params folder
and change the arguments in the same way as steps 1 and 2 to accept the new txt file name (minus .txt extension) in the mutant allele (mut_name and na12mut_name).



##################################
### Modifying the Dendritic Nav1.2
To change dendritic Nav1.2 density, alter the value of the dend_nav12 argmument when calling the model. Dendritic Nav1.2 can be reduced fairly dramatically before changes are noticed at the soma. 


## General workflow
-Na12Model_TF (in Na12HH_Model_TF.py) contains the main arguments of the model and passes those arguments to NeuronModel (in NeuronModelClass.py) when called. A few important arguments are:
1. na12name - WT param file name minus the .txt extension. (e.g. na12annaTFHH2.txt)
2. mut_name - param file name but for mutant allele minust the .txt extension (e.g. na12_mut.txt)
3. na12mechs - mechanism .mod file suffix. Must match exactly to mod file suffix.
4. na16name - same as na12name but for na16
5. na16mut_name - same as mut_name but for na16
6. na16mechs - na16 mechanism .mod file suffixes
7. params_folder - contains .txt files of params. These params update the mod file params in their respective files.
8. update - make sure this is set to True. This will run the update section in NeuronModelClass.py that uses the param txt files to update the mod files. This will also update the AIS gbars and other param values appropriately.

-NeuronModel (in NeuronModelClass.py) sets multiple parameters and updates the mechanisms with new parameters. The "if update:" section (line 177-249) is very important and will take the param files that you give in the arguments
and use them to update the mechanism files of the specific suffixes contained in na12mechs or na16mechs.

-One way that we run the model is by using a "run.py" file (here, run_TF.py). This sets up the simulation configuration for where to read from in sim_config_soma. It then calls the model in simwt where parameters can be altered if 
desired. This also sets which param files to use for updating your mechanisms (.mod files). Raw stimulation data is recorded in get_stim_raw_data. Then, those variables of voltage and time are used for plotting functions to plot
the action potentials, dvdt, and FI curves.
# Mondrian_K-Anonymity
Implementation of the Mondrian Multidimensional K-anonymity paper [1]

# Usage

-Clone this repository and go to the main folder<br/>
-Execute the code as follow :<br/>
```$ python Mondrian.py [K] [input_file] [qid_names] [algo_type] [output_file]```

All parameters are mandatory !

K : Integer value for the K-anonymity algorithm<br/>
input_file : Path to the input file (must be .csv)<br/>
qid_names : Quasi-identifiers columns names to anonymize, separated by ',' (eg name1,name2,...)<br/>
algo_type : Variant of the Mondrian algorithm, either 'relaxed' or 'strict'<br/>
output_file : Path to the output_file (also .csv)<br/>


# Data & tests

The data provided in the DATA folder can be found here:<br/>
-https://archive.ics.uci.edu/ml/datasets/Contraceptive+Method+Choice<br/>
-https://archive.ics.uci.edu/ml/datasets/adult<br/>
-https://archive.ics.uci.edu/ml/machine-learning-databases/00519/<br/>

Please note that for the "adult" dataset, a header was added and a blank line was removed.

You can test on this data with those commands :
```
$ python Mondrian.py 200 DATA/adult.csv sex,education,job strict adult_out.csv
$ python Mondrian.py 10 DATA\heart_failure.csv age,sex,DEATH_EVENT strict heart_out.csv
$ python Mondrian.py 30 DATA/contraceptive.csv wife_age,wife_religion,cm_used relaxed contraceptive_out.csv
```

### Project
Made by Raphael Garnier (5355495) for the DPP course

# Source

[1] K. LeFevre, D. J. DeWitt, R. Ramakrishnan. Mondrian Multidimensional K-Anonymity ICDE '06: Proceedings of the 22nd International Conference on Data Engineering, IEEE Computer Society, 2006, 25

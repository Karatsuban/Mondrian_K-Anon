#coding:utf-8

# made by Raphael Garnier (5355495)
# for the DPP course


import csv
import argparse
import os


TABLE = [] # content of the .csv input file
QIDS = [] # QID indexes
PARTITIONS = []
PARTITIONS_OUT = [] # anonymized content of the table
HEADER = []


def load_data():
	"""Load data from the file and put it in TABLES"""
	global PARAMS, TABLE, QIDS, HEADER

	if not os.path.isfile(PARAMS["input_file"]):
		print("Input file not found !")
		exit()

	with open(PARAMS["input_file"], "r") as file:
		reader = csv.reader(file)
		HEADER = next(reader)

		for idx, qid in enumerate(HEADER):
			if qid.strip() in PARAMS['qid_names']: # save the QID idx of the chosen column
				QIDS.append(idx)

		for row in reader:
			TABLE.append(tuple(row))


def save_data():
	"""Store data from the PARTITIONS_OUT in the .csv output file"""
	global PARAMS, PARTITIONS_OUT, HEADER
	with open(PARAMS["output_file"], "w") as file:
		file.write(",".join(HEADER))
		file.write("\n")

		for line in PARTITIONS_OUT:
			file.write(", ".join([str(k) for k in line]))
			file.write("\n")



def anonymize(table, quasids):
	"""First part of the anonymization process"""
	global PARTITIONS, PARAMS
	# check upper bound on data size and on end of recursion

	if len(table) < 2*PARAMS['K'] or len(quasids) == 0:
		return table # cannot split

	best_dim, best_dom = choose_dimension(table, quasids) # find best dimension
	freqs = frequency_set(table, best_dim, best_dom) # find frequencies for each value of the best dimension domain
	median, splitVal = find_median(freqs) # find the value on wich to split

	if PARAMS['algo_type'] == "strict":
		if splitVal == best_dom[-1]: # can't split if the value is the last one
			n_quasids = quasids[:]
			n_quasids.remove(best_dim)
			return anonymize(table, n_quasids)

	lhs, rhs = partition(best_dim, best_dom, table, splitVal) # create partitions


	if len(set(lhs)) < PARAMS['K'] or len(set(rhs)) < PARAMS['K']:
		# the size of either is less than K ==> Remove the current best QID and try another dimension
		n_quasids = quasids[:]
		n_quasids.remove(best_dim)
		return anonymize(table, n_quasids)

	# add anonymize applied on the partitions to the partitions list
	PARTITIONS.append(anonymize(lhs, QIDS))
	PARTITIONS.append(anonymize(rhs, QIDS))



def choose_dimension(table, quasids):
	#Choose the best dimension on which to split, ie the dimension with the most number of unique values
	best_dim = 0
	best_dim_length = 0
	best_dim_dom = []

	for qid_idx in quasids: # for each qid
	
		dom = set()
		for line in table:
			dom.add(line[qid_idx])


		if len(dom) >= best_dim_length: # look at the dimension with the most number of unique values
			best_dim_length = len(dom)
			best_dim_dom = dom
			best_dim = qid_idx

	best_dim_dom = list(best_dim_dom)

	return best_dim, best_dim_dom


def frequency_set(table, qid_idx, dim_dom):
	"""Compute the frequency of every unique value of the qid_idx dimension"""
	freqs = {k:0 for k in dim_dom} # initialize the frequencies of the values
	for line in table:
		value = line[qid_idx]
		freqs[value] += 1 # update the frequency
	return freqs


def find_median(fs):
	"""Find the median in the frequency set given"""
	keys = list(fs.keys()) # gets the keys (ordered)
	median = sum(list(fs.values()))/2 # find the median value

	idx = -1
	cumul = 0
	median_val = keys[idx]

	while median > cumul: # iterates until median_val found
		idx += 1
		cumul += fs[keys[idx]]
		median_val = keys[idx]

	return median, median_val


def partition(dim_idx, dim_dom, table, splitVal):
	"""Partition the table given the split value and the relax/strict algo"""
	global PARAMS
	lhs = []
	rhs = []
	median_idx = dim_dom.index(splitVal)
	relax_counter = 0

	for line in table:
		
		# append either to one or the other partition
		if dim_dom.index(line[dim_idx]) < median_idx:
			lhs.append(line)
		if dim_dom.index(line[dim_idx]) > median_idx:
			rhs.append(line)
		if dim_dom.index(line[dim_idx]) == median_idx:
			if PARAMS["algo_type"] == "strict":
				lhs.append(line) # add to one partition
			else:
				# distribute equally the values in the partitions
				if relax_counter % 2 == 0:
					lhs.append(line)
				else:
					rhs.append(line)
				relax_counter += 1

	return lhs, rhs


def summarize(partition):
	"""Second part of the anonymization process : apply the phi functions"""
	global QIDS

	summaries = []
	
	for qids in QIDS:  # for each QID
		values = set()
		for line in partition: # for each line
			values.add(line[qids])
		values = list(values) # get the list of unique values for this qid


		if len(values) > 1:
			if values[0].isnumeric():
				values = [eval(k) for k in values] # replace by their numerical values
				values.sort()
				values = [values[0],values[-1]] # get only the min and max
			summaries.append(values) # append the values

		else:
			if values[0].isnumeric():
				values = [eval(values[0])] # get the numerical value
			summaries += values # add the values


	out_partition = []
	for line in partition:
		out_list = list(line)

		for i, qid in enumerate(QIDS): # for each qid
			out_list[qid] = summaries[i] # replace the value by its summary
		out_partition.append(out_list)

	return out_partition


def main():
	"""Main function"""
	global PARAMS, QIDS, TABLE, PARTITIONS, PARTITIONS_OUT
	is_error = False

	load_data()

	anonymize(TABLE, QIDS) # 

	for partition in PARTITIONS: # anonymize the partition with all the dataset
		if partition != None and len(partition) != 0: # rules out wrong partitions
			summarized = summarize(partition)
			if len(summarized) < PARAMS['K']: # Error in the process
				print("Partition with size < K !")
				return 1

			PARTITIONS_OUT += summarized

	if len(PARTITIONS_OUT) == 0:
		return 1
	else:
		save_data()

	return


# Adding arguments to parse


parser = argparse.ArgumentParser()

parser.add_argument("K", help="K value for the K-anonymity Mondrian algorithm", type=int)
parser.add_argument("input_file", help="Path to the .csv input file", type=str)
parser.add_argument("qid_names", help="Name of the columns of the .csv file to anonymize", type=str)
parser.add_argument("algo_type", help="Variant of the Mondrian algorithm, either relaxed or strict", choices=["relaxed", "strict"])
parser.add_argument("output_file", help="Path to the .csv output file", type=str)


args = parser.parse_args()
PARAMS = vars(args)

PARAMS["qid_names"] = list(map(str, PARAMS["qid_names"].split(','))) # Transforms the string in a list of string
if not ".csv" in PARAMS["output_file"]:
	PARAMS["output_file"] += ".csv"


# Launch the programm

result = main()

if result is None:
	print("All done !")
else:
	print("The data could not be anonymized properly with the current parameters !")
	print("Please verify and change the input parameters.")


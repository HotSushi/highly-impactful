product = 'firefox'
# We consider a crash-type to be of high priority if at least
# one of its associated bugs has a severity level either 
# “critical”, “major”, or “blocker”.
# • When the highest severity level of the associated bugs
# is “normal”, we consider the priority of the crash-type
# to be “medium”.
# • When the highest severity level of the associated bugs
# is “trivial”, we consider the priority of the crash-type
# to be “very low”.
# • Otherwise the priority of the crash-type is considered
# “low”.

compute_similarity <- function(data)
{	
	size <- length(data[, 1])
	total_high <- 0L
	total_moderate <- 0L
	total_skewed <- 0L
	total_low <- 0L
	matched_high <- 0L
	matched_moderate <- 0L
	matched_skewed <- 0L
	matched_low <- 0L
	
	# for(i in 1:size){
	# 	if(data[i, 'severity'] == 'critical' || data[i, 'severity'] == 'major' || data[i, 'severity'] == 'blocker'){
	# 		total_high <- total_high + 1
	# 		if(data[i, 'region'] == 'high'){
	# 			matched_high <- matched_high + 1
	# 		}
	# 	}
	# 	else if(data[i, 'severity'] == 'normal'){
	# 		total_skewed <- total_skewed + 1
	# 		if(data[i, 'region'] == 'skewed'){
	# 			matched_skewed <- matched_skewed + 1
	# 		}
	# 	}
	# 	else if(data[i, 'severity'] == 'trivial'){
	# 		total_moderate <- total_moderate + 1
	# 		if(data[i, 'region'] == 'isolated'){
	# 			matched_moderate <- matched_moderate + 1
	# 		}
	# 	}
	# 	else {
	# 		total_low <- total_low + 1
	# 		if(data[i, 'region'] == 'moderate'){
	# 			matched_low <- matched_low + 1
	# 		}
	# 	}
	# }

	for(i in 1:size){
		if(data[i, 'region'] == 'high'){
			total_high <- total_high + 1
			if(data[i, 'severity'] == 'critical' || data[i, 'severity'] == 'major' || data[i, 'severity'] == 'blocker'){
				matched_high <- matched_high + 1
			}
		}
		else if(data[i, 'region'] == 'skewed'){
			total_skewed <- total_skewed + 1
			if(data[i, 'severity'] == 'normal'){
				matched_skewed <- matched_skewed + 1
			}
		}
		else if(data[i, 'region'] == 'moderate'){
			total_moderate <- total_moderate + 1
			if(data[i, 'severity'] == 'minor'){
				matched_moderate <- matched_moderate + 1
			}
		}
		else {
			total_low <- total_low + 1
			if(data[i, 'severity'] == 'trivial'){
				matched_low <- matched_low + 1
			}
		}
	}
	#	output data
	print(paste('Similarity high:', matched_high/ total_high))
	print(paste('Similarity skewed:', matched_skewed/ total_skewed))
	print(paste('Similarity moderate:', matched_moderate/ total_moderate))
	print(paste('Similarity low:', matched_low/ total_low))
}


data <- read.csv(sprintf('metrics/%s_metrics_machine.csv', product), header = TRUE)

print('Similarity')
compute_similarity(data)

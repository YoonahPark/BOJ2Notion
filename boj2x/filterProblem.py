
def is_valid(problem, filter):
    
    if "language" in filter:
        if problem["solution"]["language"] not in filter["language"]:
            return False
        
    if "level" in filter:
        if problem["level"] not in filter["level"]:
            return False
        
    if "algorithm" in filter:
        algorithm_filter = filter["algorithm"]
        
        if algorithm_filter[0]=="and":
            for tag in algorithm_filter[1:]:
                if tag not in problem["tags"]:
                    return False         
        else:
            for tag in algorithm_filter[1:]:
                if tag in problem["tags"]:
                    return True
                
    return True
                
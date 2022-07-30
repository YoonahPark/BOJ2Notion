from notion.client import *
from notion.block import *
from notion.collection import *
from notion.store import *

from getBojData import get_problem, create_user_profile_text


def add_problem_info_to_github(repo, user_id, filt_dic, create_profile):
    
    # create readme.md for user profile
    if create_profile["github"]:
        try:
            contents = repo.get_contents("README.md")
            repo.update_file(contents.path, "update user profile", create_user_profile_text(user_id), contents.sha, branch="main")
        except:
            repo.create_file("README.md", "create user profile", create_user_profile_text(user_id), branch="main")
    
    # put data
    count, problems = get_problem(user_id, **filt_dic)
    
    print("\n깃허브에 올리는 중")
    
    for problem in problems:
        
        # put data
        solution_id = str(problem['solution']['solution_id'])
        problem_id = str(problem['problem_id'])
        language = problem['solution']['language']
        source_code = problem['solution']['source_code']
        
        # select file extension
        if "C++" in language:
            extension = "cpp"
        elif "Python" in language:
            extension = "py"
        else:
            extension = "txt"
    
        try:
            file_name = problem_id+"."+extension
            repo.create_file(file_name, "Create "+file_name, source_code, branch="main")
            
        except:
            # pass if same title exists
            pass
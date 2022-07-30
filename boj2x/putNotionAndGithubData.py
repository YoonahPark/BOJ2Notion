import datetime

from notion.client import *
from notion.block import *
from notion.collection import *
from notion.store import *

from getBojData import get_problem, create_user_profile_text
from putNotionData import get_collection_schema, add_row_to_notion


def add_problem_info_to_notion_and_github(client, page, repo, github_url, user_id, view_types, filt_dic, create_profile):
    
    # set page title as user id [notion]
    page.title = user_id
    
    # remove original blocks [notion]
    print("Agree to remove all original block? y/n")
    if input()=="y":
        for block in page.children:
            block.remove()
    else:
        for block in page.children:
            print("Agree to remove original block? y/n")
            print("--------------------------------------------------------------")
            print(block.title)
            print("--------------------------------------------------------------")
            if input()=="y":
                block.remove()
    
    # create text block for user profile [notion]
    if create_profile["notion"]:
        child_text = page.children.add_new(TextBlock)
        child_text.title =  create_user_profile_text(user_id)
    
    # create readme.md for user profile [github]
    if create_profile["github"]:
        try:
            contents = repo.get_contents("README.md")
            repo.update_file(contents.path, "update user profile", create_user_profile_text(user_id), contents.sha, branch="main")
        except:
            repo.create_file("README.md", "create user profile", create_user_profile_text(user_id), branch="main")
    
    # create collection view block for problem view[notion]
    child_page = page.children.add_new(CollectionViewBlock)
    schema = get_collection_schema()
    schema["github_url"] = {"name" : "github_url", "type" : "url"}
    child_page.collection = client.get_collection(
        client.create_record('collection', parent=child_page, schema=schema)
    )
    child_page.title = "BOJ Problem Solving" +"  ver."+str(datetime.datetime.now().strftime("%Y-%m-%d"))
    
    # put data [notion] [github]
    count, problems = get_problem(user_id, **filt_dic)
    
    print("\n노션 및 깃허브에 올리는 중")
    
    for problem in problems:
        
        # put data [github]
        solution_id = str(problem['solution']['solution_id'])
        problem_id = str(problem['problem_id'])
        language = problem['solution']['language']
        source_code = problem['solution']['source_code']
        
        # select file extension [github]
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
            # pass if same title exists [github]
            pass
        
        # put data [notion]
        add_row_to_notion(child_page, problem, github_url+file_name)
            
        print(".", end="")
            
    # set notion views [notion]
    for view_type in view_types:
        view = child_page.views.add_new(view_type=view_type)
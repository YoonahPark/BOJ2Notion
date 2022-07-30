from random import choice
from datetime import datetime

from notion.client import *
from notion.block import *
from notion.collection import *
from notion.store import *

from getBojData import *
         
def add_new_multi_select_value(collection, prop, value):
    colors = [
        "default",
        "gray",
        "brown",
        "orange",
        "yellow",
        "green",
        "blue",
        "purple",
        "pink",
        "red",
    ]
    
    collection_schema = collection.get(["schema"])
    prop_schema = next((v for k, v in collection_schema.items() if v["name"] == prop), None)
    
    if not prop_schema:
        raise ValueError(
            f'"{prop}" property does not exist on the collection!')
    if prop_schema["type"] != "multi_select":
        raise ValueError(f'"{prop}" is not a multi select property!')

    '''dupe = next((o for o in prop_schema["options"] if o["value"] == value), None)
    if dupe:
        raise ValueError(f'"{value}" already exists in the schema!')'''
    
    prop_schema["options"].append({"id": str(uuid1()), "value": value, "color" : choice(colors)})
    collection.set("schema", collection_schema)
    
 
def get_collection_schema():
    schema = {
        "problem_id" : {"name" : "problem_id", "type" : "number"},
        "problem_url" : {"name" : "problem_url", "type" : "url"},
        "title" : {"name" : "title", "type" : "text"},
        "level" : {"name" : "level", "type" : "number"},
        "tier" : {
            "name" : "tier", 
            "type" : "multi_select",
            "options" : []
            },
        "algorithm" : {
            "name" : "algorithm", 
            "type" : "multi_select",
            "options" : []
            },
        "solution_id" : {"name" : "solution_id" , "type" : "number"},
        "solution_url" : {"name" : "solution_url" , "type" : "url"},
        "memory" : {"name" : "memory", "type" : "number"},
        "time" : {"name" : "time", "type" : "number"},
        "language" : {"name" : "language", "type" : "text"},
        "solved_at" : {"name" : "solved_at", "type" : "date"},
        "source_code" : {"name" : "source_code", "type" : "text"}
    }
    return schema
    
def add_row_to_notion(child_page, problem, github_url=None):
    row = child_page.collection.add_row()
    
    if github_url is not None:
        row.github_url = github_url
        
    row.problem_id = problem['problem_id']
    row.problem_url = problem['problem_url']
    row.title = problem['title']
    row.level = problem['level']
    
    tier = problem['tier']
    add_new_multi_select_value(child_page.collection, "tier", tier)
    row.tier = tier

    for tag in problem['tags']:
        add_new_multi_select_value(child_page.collection, "algorithm", tag)
    row.algorithm = problem['tags']

    row.solution_id = int(problem['solution']['solution_id'])
    row.solution_url = problem['solution']['solution_url']
    row.memory = int(problem['solution']['memory'])
    row.time = int(problem['solution']['time'])
    row.language = problem['solution']['language']
    row.solved_at = problem['solution']['solved_at']
    row.source_code = problem['solution']['source_code']
    
    print(".", end="")
    
    
def add_problem_info_to_notion(client, page, user_id, view_types, filt_dic, create_profile):
    # set page title as user id
    page.title = user_id
    
    # remove original blocks
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
    
    # create text block for user profile
    if create_profile["notion"]:
        child_text = page.children.add_new(TextBlock)
        child_text.title =  create_user_profile_text(user_id)
    
    # create collection view block for problem view
    child_page = page.children.add_new(CollectionViewBlock)
    child_page.collection = client.get_collection(
        client.create_record('collection', parent=child_page, schema=get_collection_schema())
    )
    child_page.title = "BOJ Problem Solving" +"  ver."+str(datetime.now().strftime("%Y-%m-%d"))
    
    # put data to notion (or also to github)
    count, problems = get_problem(user_id, **filt_dic)
    print("\n노션에 올리는 중")

    for problem in problems:
        add_row_to_notion(child_page, problem)
            
    # set notion views
    for view_type in view_types:
        view = child_page.views.add_new(view_type=view_type)
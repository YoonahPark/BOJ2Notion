from github import Github
from execute import execute_boj2github, execute_boj2notion, execute_boj2notionNgithub

# set personal informations
user_id = ""

token_v2 = ""
url = ""

github_access_key = ""
g = Github(github_access_key)
repo_name = ""


# set filtering or sorting dic

sort = "level" # id, level, title, solved
direction = "desc" # asc, desc
limit = False

create_profile = {}
create_profile["github"] = True
create_profile["notion"] = True

language = ["Python 3", "C++17"]
level = [] #[4, 5, 6]
algorithm = ["or", "문자열", "조합론"] # and, or
filter = {
    #"language" : language, 
    #"level" : level, 
    #"algorithm" : algorithm
    }

filt_dic = {}
if sort: 
    filt_dic["sort"] = sort
if direction:
    filt_dic["direction"] = direction
if limit:
    filt_dic["limit"] = limit

if filter:
    filt_dic["filter"] = filter
    
view_types = ["table", "board", "list", "timeline", "calendar"]

# execute
#execute_boj2notion(user_id, token_v2, url, view_types, filt_dic, create_profile)
#execute_boj2github(g, repo_name, user_id, filt_dic, create_profile)
execute_boj2notionNgithub(user_id, g, repo_name, token_v2, url, view_types, filt_dic, create_profile)

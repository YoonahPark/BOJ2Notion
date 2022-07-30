from notion.client import *
from notion.block import *
from notion.collection import *
from notion.store import *

from setNotion import set_notion
from putNotionData import add_problem_info_to_notion
from putGithubData import add_problem_info_to_github
from putNotionAndGithubData import add_problem_info_to_notion_and_github

def execute_boj2notion(user_id, token_v2, url, view_types, filt_dic, create_profile):
    
    # get pages on notion
    set_notion()
    client = NotionClient(token_v2 = token_v2)
    page = client.get_block(url)
    
    add_problem_info_to_notion(client, page, user_id, view_types, filt_dic, create_profile)


def execute_boj2github(g, repo_name, user_id, filt_dic, create_profile):
    
    # get repo on github
    repo = g.get_repo(repo_name)
    
    add_problem_info_to_github(repo, user_id, filt_dic, create_profile)
    
def execute_boj2notionNgithub(user_id, g, repo_name, token_v2, url, view_types, filt_dic, create_profile):
    
    # get pages on notion
    set_notion()
    client = NotionClient(token_v2 = token_v2)
    page = client.get_block(url)
    
    # get repo on github
    repo = g.get_repo(repo_name)
    github_url = "https://github.com/%s/blob/main/"%repo_name
    
    add_problem_info_to_notion_and_github(client, page, repo, github_url, user_id, view_types, filt_dic, create_profile)
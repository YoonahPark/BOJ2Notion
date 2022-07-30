from github import Github
import requests
from bs4 import BeautifulSoup
import time
from getBojData import get_source, create_user_profile_text

def get_next_page(url):
    # get next page url
    
    base_url = "https://www.acmicpc.net"
    cookie = {
            "OnlineJudge": "aa1vnhhn0udsupp4lhj7u1rln5"
        }
    
    try:
        # maintain session
        s = requests.session()
        req = s.get(url, cookies = cookie)
        soup = BeautifulSoup(req.text, "html.parser")
        
        # move on to next page
        next_page = soup.select_one("#next_page")['href']
        result = base_url + next_page
        
        print(" 페이지 넘기는 중")
        return result
    
    # stop moving page when exception occurs
    except Exception as e:
        return False


def post_source_code_on_repo(repo, user_id, sort="level", direction="desc", limit=None, **kwargs):
    # get source code and create file on github repo
    
    url = f"https://www.acmicpc.net/status?user_id=%s&result_id=4&sort={sort}&direction={direction}"%user_id
    s = requests.session()
    cookie = {
        "OnlineJudge": "aa1vnhhn0udsupp4lhj7u1rln5"
    }
    
    try:
        contents = repo.get_contents("README.md")
        repo.update_file(contents.path, "update user profile", create_user_profile_text(user_id), contents.sha, branch="main")
    except:
        repo.create_file("README.md", "create user profile", create_user_profile_text(user_id), branch="main")
    
    print("코드 올리는 중")
    
    cnt = 0;
    while True:
        # get problems solved by user
        req = s.get(url, cookies = cookie)
        soup = BeautifulSoup(req.text, "html.parser")
        elements = soup.find("tbody").find_all("td")

        # get source code and create file on github repo from one page
        for i in range(0, len(elements), 9):
            
            if limit:
                if cnt>limit:
                    break
                
            element = elements[i]
            
            solution_id = element.get_text()
            problem_id = elements[i+2].get_text()[1:]
            language = soup.select(f"#solution-{solution_id} > td > a:nth-child(1)")[1].get_text()
            source_code = get_source(problem_id, solution_id)
            
            # select file extension
            if "C++" in language:
                extension = "cpp"
            elif "Python" in language:
                extension = "py"
            else:
                extension = "txt"
        
            try:
                repo.create_file(problem_id+"."+extension, problem_id, source_code, branch="main")
                cnt += 1
            except:
                # pass if same title exists
                pass
            
            print(".", end="")
        
        # move on to next page
        url = get_next_page(url)
        if url == False:
            break
        
        time.sleep(0.5)
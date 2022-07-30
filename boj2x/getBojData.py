from django.forms import ValidationError
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from filterProblem import is_valid
    
def create_tier_string(level):
    # create tier string from level number
    if level==31: 
        return "Master"
    
    material_dic = {
        0 : "Bronze",
        1 : "Silver",
        2 : "Gold",
        3 : "Platinum",
        4 : "Diamond",
        5 : "Ruby",
    }
    
    material = material_dic[int((level-1)/5)]
    level = 5-(level-1)%5
    
    return material+" "+str(level)


def create_tags_list(item):
    # create tag list from item HTML doc
    tags_list = []
    
    for tag in item.get("tags"):
        tags_list.append(tag['displayNames'][1].get("name"))
        
    return tags_list


def get_source(problem_id, solution_id):
    # get source code from solution link
    
    try:
        url = f"https://www.acmicpc.net/submit/%s/%s"%(problem_id, solution_id)
        s = requests.session()
        cookie = {
            "OnlineJudge": "vkno0icfkn3sutfgmhq2f3g389"
        }
        
        req = s.get(url, cookies = cookie, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(req.text, "html.parser")
        source_code = soup.select("#source")[0].get_text()
        
        return source_code
    
    except:
        print("소스코드를 불러오는 중에 예상치 못한 오류가 발생했습니다.")


def get_solution(problem_id, user_id):
    # get solution information from problem link
    
    url = f"https://www.acmicpc.net/status?user_id=%s&problem_id=%s&result_id=4&from_mine=1"%(user_id, problem_id)
    s = requests.session()
    cookie = {
        "OnlineJudge": "vkno0icfkn3sutfgmhq2f3g389"
    }

    req = s.get(url, cookies = cookie, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(req.text, "html.parser")
    
    # get only latest solution solved
    element = soup.find_all("tbody")[0]
    
    solution_id = element.find("td").get_text()
    memory = soup.select_one(f"#solution-{solution_id} > td.memory").get_text() 
    time = soup.select_one(f"#solution-{solution_id} > td.time").get_text() 
    language = soup.select(f"#solution-{solution_id} > td > a:nth-child(1)")[1].get_text() 
    solved_at = soup.select(f"#solution-{solution_id} > td > a:nth-child(1)")[2].get("title")
    source_code = get_source("2557", solution_id)
    
    return {
        "solution_id" : int(solution_id),
        "solution_url" : "https://www.acmicpc.net/submit/"+problem_id+"/"+solution_id,
        "memory" : int(memory),
        "time" : int(time),
        "language" : language,
        "solved_at" : datetime.strptime(solved_at, '%Y-%m-%d %H:%M:%S'),
        "source_code" : source_code,
    }


def get_problem(user_id, sort="level", direction="desc", limit=None, filter={}, **kwargs):
    # get information of problems solved by user
    
    url = f"https://solved.ac/api/v3/search/problem?query=solved_by%3A{user_id}&sort={sort}&direction={direction}"
    
    r_solved = requests.get(url)
    
    if r_solved.status_code == requests.codes.ok:
        solved = json.loads(r_solved.content.decode('utf-8'))
        
        count = solved.get("count")
        items = solved.get("items")
        
        # make solved problem list
        solved_problems = []
        print("문제 정보 불러오는 중")
        
        cnt = 0
        for item in items:
            
            if limit:
                if cnt>=limit:
                    break
                
            problem = {
                    'problem_id': item.get("problemId"),
                    'problem_url' : "https://www.acmicpc.net/problem/"+str(item.get("problemId")),
                    'title': item.get("titleKo"),
                    'level': int(item.get("level")),
                    'tier' : create_tier_string(int(item.get("level"))),
                    'tags' : create_tags_list(item),
                    'solution' : get_solution(str(item.get("problemId")), user_id)
                }
            if is_valid(problem, filter):
                solved_problems.append(problem)
                cnt+=1
                
            print(".", end="")
            
    else:
        print("문제를 불러오는 중에 예상치 못한 오류가 발생했습니다.")
        
    return count, solved_problems


def get_profile(user_id):
    # get user information
    
    url = f"https://solved.ac/api/v3/user/show?handle={user_id}"
    r_profile = requests.get(url)
    
    if r_profile.status_code == requests.codes.ok:
        
        profile = json.loads(r_profile.content.decode('utf-8'))
        profile = {
        "tier" : profile.get("tier"),
        "rank" : profile.get("rank"),
        "solvedCount" : profile.get("solvedCount"),
        "rating" : profile.get("rating"),
        "class" : profile.get("class"),
        "exp" : profile.get("exp"),
        "maxStreak" : profile.get("maxStreak")
        }
        
    else:
        print("프로필 요청 실패")
        
    return profile


def get_count_by_level(user_id):
    # get problem count by level
    
    url = f"https://solved.ac/api/v3/user/problem_stats?handle={user_id}"
    r_count_by_level = requests.get(url)
    
    if r_count_by_level.status_code == requests.codes.ok:
        count_by_level = json.loads(r_count_by_level.content.decode('utf-8'))
        filted_count_by_level = [ {"level":dict_['level'], 
                                   "total":dict_['total'], 
                                   "solved":dict_['solved'],} for dict_ in count_by_level if dict_.get('solved') != 0 ]
        filted_count_by_level = sorted(filted_count_by_level, key=lambda x:x['level'], reverse=True)
        
    else:
        print("레벨별, 전체 문제수, 푼 문제수  요청 실패")
        
    return filted_count_by_level

def create_user_profile_text(user_id):
    profile = get_profile(user_id)
    count_by_level = get_count_by_level(user_id)
    
    profile_text = ""
    profile_text += "* 티어 : "+create_tier_string(profile["tier"])+"\n"
    profile_text += "* 풀어낸 문제 수 : "+str(profile["solvedCount"])+"\n"
    profile_text += "* 레이팅 : "+str(profile["rating"])+"\n"
    profile_text += "* 클래스 : "+str(profile["class"])+"\n"
    profile_text += "* 랭크 : "+str(profile["rank"])+"\n"
    profile_text += "* exp : "+str(profile["exp"])+"\n"
    profile_text += "* 연속 풀이한 최대 일수 : "+str(profile["maxStreak"])+"\n\n"
    
    for level_dic in count_by_level:
        profile_text += "- "+create_tier_string(int(level_dic["level"]))
        profile_text += " | 합계 : "+str(level_dic["total"])
        profile_text += " | 풀어낸 문제 수 : "+str(level_dic["solved"])+"\n"
        
    return profile_text
    
    
    
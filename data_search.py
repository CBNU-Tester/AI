import time
import os
import csv
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# 필요한 예외 처리 추가
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException

# XPath를 계산하는 함수 정의
def get_xpath(element):
    script = """
    function getElementXPath(elt) {
        var path = '';
        for (; elt && elt.nodeType == 1; elt = elt.parentNode) {
            idx = getElementIdx(elt);
            xname = elt.tagName.toLowerCase();
            if (idx > 1) xname += '[' + idx + ']';
            path = '/' + xname + path;
        }
        return path;
    }
    function getElementIdx(elt) {
        var count = 1;
        for (var sib = elt.previousSibling; sib; sib = sib.previousSibling) {
            if(sib.nodeType == 1 && sib.tagName == elt.tagName) count++;
        }
        return count;
    }
    return getElementXPath(arguments[0]);
    """
    try:
        return element._parent.execute_script(script, element)
    except StaleElementReferenceException:
        return None

# Chrome 옵션 설정
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)

# URL 리스트 설정
urls = [
    # 포털 사이트
    'https://www.naver.com',  # 네이버
    'https://www.daum.net',  # 다음
    'https://www.google.com',  # 구글
    'https://www.yahoo.com',  # 야후
    'https://www.bing.com',  # 빙 (Bing)

    # 소셜 미디어
    'https://www.facebook.com',  # 페이스북
    'https://www.instagram.com',  # 인스타그램
    'https://www.twitter.com',  # 트위터
    'https://www.linkedin.com',  # 링크드인
    'https://www.tiktok.com',  # 틱톡

    # 온라인 커머스 및 쇼핑몰
    'https://www.coupang.com',  # 쿠팡
    'https://www.11st.co.kr',  # 11번가
    'https://www.gmarket.co.kr',  # 지마켓
    'https://www.auction.co.kr',  # 옥션

    # 뉴스 사이트
    'https://www.joongang.co.kr',  # 중앙일보
    'https://www.chosun.com',  # 조선일보
    'https://www.donga.com',  # 동아일보
    'https://www.hani.co.kr',  # 한겨레
    'https://www.yna.co.kr',  # 연합뉴스

    # 정보 및 지식 공유 사이트
    'https://www.wikipedia.org',  # 위키백과
    'https://terms.naver.com',  # 네이버 지식백과
    'https://www.quora.com',  # Quora
    'https://www.reddit.com',  # 레딧 (Reddit)
    'https://stackoverflow.com',  # 스택 오버플로우

    # 음악 및 비디오 스트리밍
    'https://www.youtube.com',  # 유튜브
    'https://www.netflix.com',  # 넷플릭스
    'https://www.melon.com',  # 멜론
    'https://www.spotify.com',  # 스포티파이
    'https://music.apple.com',  # 애플뮤직

    # 여행 및 숙박
    'https://www.airbnb.com',  # 에어비앤비
    'https://www.tripadvisor.com',  # 트립어드바이저
    'https://www.agoda.com',  # 아고다
    'https://www.expedia.com',  # 익스피디아
    'https://www.booking.com',  # 부킹닷컴


]


# 검색할 용어 (포함되는 id, class, role을 찾기 위해)
search_term = 'search'  # 원하는 검색어로 변경 가능

# 데이터 폴더가 없으면 생성
output_dir = './data'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# CSV 파일 설정
csv_file_path = os.path.join(output_dir, 'data_search.csv')

# 이미 처리된 요소의 XPath를 추적하기 위한 세트
processed_xpaths = set()

# CSV 파일 작성
with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Tag', 'HTML', 'XPath', 'ParentXPath', 'Input', 'Result', 'Important', 'Type']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for url in urls:
        driver.get(url)
        time.sleep(2)  # 페이지 로딩 대기

        # 검색할 id, class, role 속성에 search_term이 포함된 요소를 XPath로 찾기
        xpath_expression = f"//*[contains(@id, '{search_term}') or contains(@class, '{search_term}') or contains(@role, '{search_term}')]"
        elements = driver.find_elements(By.XPATH, xpath_expression)

        # 중복된 요소를 제거하기 위해 XPath를 사용
        unique_elements = []
        unique_xpaths = set()
        for elem in elements:
            try:
                xpath = get_xpath(elem)
                if xpath and xpath not in unique_xpaths:
                    unique_elements.append(elem)
                    unique_xpaths.add(xpath)
            except StaleElementReferenceException:
                continue

        # 각 요소와 모든 하위 요소를 가져옴
        for element in unique_elements:
            elements_queue = [(element, None)]  # (element, parent_xpath)
            while elements_queue:
                try:
                    current_element, parent_xpath = elements_queue.pop(0)
                    current_xpath = get_xpath(current_element)
                    if not current_xpath or current_xpath in processed_xpaths:
                        continue
                    processed_xpaths.add(current_xpath)

                    # 현재 요소의 태그만 가져오기
                    outer_html = current_element.get_attribute('outerHTML')
                    # 정규식을 사용하여 시작 태그만 추출
                    match = re.match(r'<[^>]+?>', outer_html)
                    if match:
                        element_only_html = match.group()
                    else:
                        element_only_html = f'<{current_element.tag_name}>'

                    # 현재 요소 처리
                    tag_name = current_element.tag_name
                    input_field = ''
                    result_field = ''
                    important_field = ''
                    type_field = ''

                    # input 태그 데이터 처리
                    if tag_name == 'input':
                        name_attr = current_element.get_attribute('name')
                        id_attr = current_element.get_attribute('id')
                        if name_attr and search_term in name_attr.lower():
                            input_field = 'input_text'
                        elif id_attr and search_term in id_attr.lower():
                            input_field = 'input_text'

                    # a 태그나 버튼의 Result 처리
                    if tag_name == 'a':
                        href = current_element.get_attribute('href')
                        if href:
                            result_field = href
                    elif tag_name == 'button':
                        onclick = current_element.get_attribute('onclick')
                        if onclick:
                            result_field = onclick
                    else:
                        onclick = current_element.get_attribute('onclick')
                        if onclick:
                            result_field = onclick

                    row = {
                        'Tag': tag_name,
                        'HTML': element_only_html,
                        'XPath': current_xpath,
                        'ParentXPath': parent_xpath if parent_xpath else '',
                        'Input': input_field,
                        'Result': result_field,
                        'Important': important_field,
                        'Type': type_field
                    }

                    # 빈 필드를 None으로 설정
                    for key in row:
                        if not row[key]:
                            row[key] = None

                    writer.writerow(row)

                    # 자식 요소들을 큐에 추가
                    child_elements = current_element.find_elements(By.XPATH, './*')
                    for child in child_elements:
                        elements_queue.append((child, current_xpath))

                except StaleElementReferenceException:
                    continue
                except Exception as e:
                    print(f"Error processing element: {e}")
                    continue

# 드라이버 종료
driver.quit()

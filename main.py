import asyncio
import aiohttp
import logging
import json

from config import parser

neis_key = parser.get('DEFAULT', 'token')
training_data1 = list(json.loads(parser.get('training_data', 'training1')))
training_data2 = list(json.loads(parser.get('training_data', 'training2')))
training_data3 = list(json.loads(parser.get('training_data', 'training3')))
training_data4 = list(json.loads(parser.get('training_data', 'training4')))
training_data5 = list(json.loads(parser.get('training_data', 'training5')))
training_data6 = list(json.loads(parser.get('training_data', 'training6')))

log = logging.getLogger()
log.setLevel(logging.INFO)

logging_format = logging.Formatter('[%(asctime)s | %(name)s | %(levelname)s]: %(message)s', "%Y-%m-%d %p %I:%M:%S")

console = logging.StreamHandler()
console.setFormatter(logging_format)

log.addHandler(console)


async def main():
    count = 1
    with open("training_data_exam.json", "r", encoding='utf8') as f:
        data = json.load(f)

    # 급식 정보를 학습 시키는 구간
    log.info("급식 intent의 발화 데이터를 추가하고 있습니다.")
    data['taggedSentenceList'][0]['ask.school_meal'] = list()
    training_data1.append(str())
    training_data2.append(str())
    for d1 in training_data1:
        for d2 in training_data2:
            for d3 in training_data3:
                for d4 in training_data6:
                    data['taggedSentenceList'][0]['ask.school_meal'].append('%s%s%s%s' % (d1, d2, d3, d4))
                    
    # 시간표 정보를 학습 시키는 구간
    log.info("시간표 intent의 발화 데이터를 추가하고 있습니다.")
    data['taggedSentenceList'][0]['ask.timetable'] = list()
    training_data4.append(str())
    training_data5.append(str())
    for d1 in training_data1:
        for d2 in training_data2:
            for d3 in training_data4:
                for d4 in training_data5:
                    for d5 in training_data6:
                        data['taggedSentenceList'][0]['ask.timetable'].append('%s%s%s%s시간표%s' % (d1, d2, d3, d4, d5))

    # 학교 정보를 삽입하는 구간.
    school_num = 0
    log.info("학교 정보를 불러옵니다.")
    total_deleted_data = 0
    registered_data = 0
    async with aiohttp.ClientSession() as session:
        while True:
            params = {
                "Type": "json",
                "KEY": neis_key,
                "pSize": 1000,
                "pIndex": count
            }

            async with session.get("https://open.neis.go.kr/hub/schoolInfo", params=params) as resp:
                text = await resp.text()
                json_data = json.loads(text)

            RESULT = json_data.get("RESULT")
            if RESULT is not None:
                if RESULT.get('CODE') == "INFO-200":
                    log.info(f"더 이상의 학교 데이터가 존재하지 않습니다. 총 검색된 학교 갯수: {school_num}개")
                    break
            count += 1
            deleted_data = 0
            school_num += len(json_data.get('schoolInfo')[1]['row'])
            for i in json_data.get('schoolInfo')[1]['row']:
                # 공동 실습소, 해외 한인 학교, 평생학교의 경우 필터링하여, 데이터에 등록하지 않았음. (1차)
                # 초등학교, 중학교, 고등학교, 특수학교만 등재하는 방식으로 변경 (2차)
                if not (i['SCHUL_KND_SC_NM'] == "초등학교" or i['SCHUL_KND_SC_NM'] == "중학교" or
                        i['SCHUL_KND_SC_NM'] == "고등학교" or i['SCHUL_KND_SC_NM'] == "특수학교"):
                    deleted_data += 1
                    total_deleted_data += 1
                    continue
                registered_data += 1

                #변환 과정 중에 에러가 발생한 단어
                school_nm = i['SCHUL_NM'].replace('・', '')
                data['userDictList'][0]['SCHOOL_NAME'][school_nm] = list()

                # 초등학교에 알맞는 동의어 추가
                if school_nm.endswith("초등학교"):
                    data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("초등학교", "초교"))
                    data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("초등학교", "초"))

                # 중학교에 알맞는 동의어 추가
                if school_nm.endswith("중학교"):
                    data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("중학교", "중교"))
                    data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("중학교", "중"))
                    
                    if school_nm.endswith("여자중학교"):
                        data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("여자중학교", "여중"))
                        data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("여자중학교", "여중교"))
                    elif school_nm.endswith("남자중학교"):
                        data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("남자중학교", "남중"))
                        data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("남자중학교", "남중교"))
                    elif school_nm.endswith("예술중학교"):
                        data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("예술중학교", "예중"))
                        data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("예술중학교", "예중교"))
                    elif school_nm.endswith("체육중학교"):
                        data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("체육중학교", "체중"))
                        data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("체육중학교", "체중교"))

                # 고등학교에 알맞는 동의어 추가
                if school_nm.endswith("고등학교"):
                    data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("고등학교", "고교"))
                    data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("고등학교", "고"))

                    if school_nm.endswith("여자고등학교"):
                        data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("여자고등학교", "여고"))
                        data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("여자고등학교", "여고교"))
                    elif school_nm.endswith("남자고등학교"):
                        data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("남자고등학교", "남고"))
                        data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("남자고등학교", "남고고교"))
                    elif school_nm.endswith("예술고등학교"):
                         data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("예술고등학교", "예고"))
                         data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("예술고등학교", "예고교"))
                    elif school_nm.endswith("체육고등학교"):
                        data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("체육고등학교", "체고"))
                        data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("체육고등학교", "체고교"))
                    #elif school_nm.endswith("국제고등학교"):
                    #elif school_nm.endswith("마이스터고등학교"):
                    elif school_nm.endswith("외국어고등학교"):
                        data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("외국어고등학교", "외고"))
                        data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("외국어고등학교", "외고교"))
                    elif school_nm.endswith("과학고등학교"):
                        data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("과학고등학교", "과고"))
                        data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("과학고등학교", "과고교"))
                    elif school_nm.endswith("상업고등학교"):
                        data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("상업고등학교", "상고"))
                        data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("상업고등학교", "상고교"))
                    elif school_nm.endswith("공업고등학교"):
                        data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("공업고등학교", "공고"))
                        data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("공업고등학교", "공고교"))

                # 특수학교에 알맞는 동의어 추가
                if i['SCHUL_KND_SC_NM'] == "특수학교":
                    data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("학교", "교"))

                # 영재학교에 알맞는 동의어 추가
                if school_nm.endswith("영재학교"):
                    data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("영재학교", "영교"))
                    data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("영재학교", "영재교"))

                # 창작학교에 알맞는 동의어 추가
                if school_nm.endswith("창작학교"):
                    data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("창작학교", "창교"))

                # 학교(분교장)에 알맞는 동의어 추가
                if school_nm.endswith("분교장"):
                    data['userDictList'][0]['SCHOOL_NAME'][school_nm].append(school_nm.replace("분교장", "분교"))

            log.info(f"{count}번째, {len(json_data.get('schoolInfo')[1]['row'])}개의 학교 데이터를 불러왔습니다. 삭제된 데이터의 양: {deleted_data}개")
    log.info(f"등록된 학교의 수: {registered_data}개/ 총 삭제된 학교의 수: {total_deleted_data} 개")
    # 값을 json 형태로 저장함.
    log.info("알맞게 json 형태의 데이터로 추출하고 있습니다.")
    with open('training_data_final.json', 'w', encoding='UTF8') as f:
        final = json.dumps(data, indent=4, ensure_ascii=False)
        f.write(final)
    return

asyncio.run(main())

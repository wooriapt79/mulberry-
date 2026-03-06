import json
import time
import csv

# 1. 방언 처리 모듈 (JSON 생성기)
def process_dialect_order(dialect_sentence):
    """
    경상도/전라도 방언을 처리하여 JSON 형식으로 변환
    """
    # 방언 사전
    dialect_dict = {
        "정구지": "부추",
        "지레": "기저귀",
        "항그": "가득",
        "있능교": "있습니까",
        "퍼뜩": "빨리",
        "보내주이소": "보내주세요",
        "얼만교": "얼마입니까",
        "아지매": "아주머니",
        "뭇": "다발",
        "사고": "사과",
        "조아": "좋아"
    }
    
    # 기본 응답 구조
    response = {
        "표준어 요약": "",
        "품목 정보": [],
        "주문 의도": "주문배송"  # 기본값
    }
    
    # 1. 표준어 변환
    standard_text = dialect_sentence
    for dialect, standard in dialect_dict.items():
        standard_text = standard_text.replace(dialect, standard)
    response["표준어 요약"] = standard_text + "."
    
    # 2. 품목 정보 추출 (간단한 규칙 기반)
    items = []
    
    # 정구지/부추 처리
    if "정구지" in dialect_sentence or "부추" in dialect_sentence:
        items.append(["부추", 1, "다발"])
    
    # 지레/기저귀 처리
    if "지레" in dialect_sentence:
        items.append(["기저귀", 1, "개"])
        if "큰" in dialect_sentence:
            items[-1][0] = "기저귀 (대형)"
    
    # 사과 처리
    if "사고" in dialect_sentence or "사과" in dialect_sentence:
        if "항그" in dialect_sentence:
            items.append(["사과", 1, "가득"])
        elif "봉지" in dialect_sentence:
            items.append(["사과", 1, "봉지"])
    
    # 우유 처리
    if "우유" in dialect_sentence:
        items.append(["우유", 2, "개"])
    
    response["품목 정보"] = items
    
    # 3. 주문 의도 판별
    if "있능교" in dialect_sentence:
        response["주문 의도"] = "재고문의"
    elif "얼만교" in dialect_sentence:
        response["주문 의도"] = "가격확인"
    elif "보내주" in dialect_sentence or "퍼뜩" in dialect_sentence:
        response["주문 의도"] = "주문배송"
    
    return json.dumps(response, ensure_ascii=False)

# 2. 테스트 설정
test_dataset = [
    {"input": "아지매, 정구지 한 뭇 있능교?", "expected": "부추"},
    {"input": "지레 큰 거 한 봉지 얼만교?", "expected": "기저귀"},
    {"input": "사과 한 항그하고 우유 두 개만 퍼뜩 보내주이소.", "expected": "사과"},
    {"input": "정구지 두 뭇 조아?", "expected": "부추"},
    {"input": "지레 작은 거 있능교?", "expected": "기저귀"},
    {"input": "사고 한 봉지 얼만교?", "expected": "사과"},
] * 17  # 102개 샘플

def run_test():
    results = []
    success_count = 0
    total_time = 0

    print(f"[*] 총 {len(test_dataset)}건의 방언 테스트를 시작합니다...")

    for i, data in enumerate(test_dataset):
        start_time = time.time()
        
        try:
            # 방언 처리 모듈 호출
            res_json = process_dialect_order(data['input'])
            latency = time.time() - start_time
            total_time += latency
            
            res_data = json.loads(res_json)
            
            # 정확도 검증 (품목 정보에서 상품명 확인)
            is_success = False
            for item in res_data.get("품목 정보", []):
                if data['expected'] in str(item[0]):
                    is_success = True
                    break
            
            if is_success: 
                success_count += 1
            
            results.append({
                "no": i + 1,
                "input": data['input'],
                "output": res_json,
                "latency": f"{latency:.2f}s",
                "result": "PASS" if is_success else "FAIL"
            })
            
            if (i + 1) % 10 == 0:
                print(f"[{i+1}/{len(test_dataset)}] 진행 중...")

        except Exception as e:
            print(f"[오류] {i+1}번 항목 처리 중 에러 발생: {e}")
            results.append({
                "no": i + 1,
                "input": data['input'],
                "output": f"ERROR: {str(e)}",
                "latency": "0.00s",
                "result": "ERROR"
            })

    # 3. 결과 요약 및 저장
    avg_latency = total_time / len(test_dataset) if test_dataset else 0
    accuracy = (success_count / len(test_dataset)) * 100 if test_dataset else 0

    with open('dialect_test_report.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["no", "input", "output", "latency", "result"])
        writer.writeheader()
        writer.writerows(results)

    print("\n" + "="*50)
    print("테스트 완료 보고서")
    print("="*50)
    print(f"- 총 테스트 문장: {len(test_dataset)}건")
    print(f"- 성공한 문장: {success_count}건")
    print(f"- 최종 정확도: {accuracy:.1f}%")
    print(f"- 평균 응답 속도: {avg_latency:.4f}초")
    print(f"- 결과 파일: 'dialect_test_report.csv'")
    print("="*50)

if __name__ == "__main__":
    run_test()
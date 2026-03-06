import json
import time
import csv
import re

# 1. 향상된 방언 처리 모듈
def process_dialect_order(dialect_sentence):
    """
    경상도/전라도 방언을 처리하여 JSON 형식으로 변환
    """
    # 확장된 방언 사전
    dialect_dict = {
        "정구지": "부추", "정구지는": "부추는", "정구지가": "부추가",
        "지레": "기저귀", "지레는": "기저귀는", "지레가": "기저귀가",
        "항그": "가득", "항그한": "가득한",
        "있능교": "있습니까", "있능가": "있습니까",
        "퍼뜩": "빨리", "퍼뜩이": "빨리",
        "보내주이소": "보내주세요", "보내주이써": "보내주세요",
        "얼만교": "얼마입니까", "얼만가": "얼마입니까",
        "아지매": "아주머니", "아지매는": "아주머니는",
        "뭇": "다발", "뭇은": "다발은",
        "사고": "사과", "사고는": "사과는", "사고가": "사과가",
        "조아": "좋아", "조아요": "좋아요",
        "하고": "과", "랑": "과",
        "거": "것", "거는": "것은", "거가": "것이"
    }
    
    # 기본 응답 구조
    response = {
        "표준어 요약": "",
        "품목 정보": [],
        "주문 의도": "주문배송"
    }
    
    # 원본 저장
    original_sentence = dialect_sentence
    
    # 1. 표준어 변환 (더 정확한 변환)
    standard_text = dialect_sentence
    # 우선순위가 높은 패턴부터 처리
    for dialect, standard in sorted(dialect_dict.items(), key=lambda x: -len(x[0])):
        standard_text = standard_text.replace(dialect, standard)
    
    # 문장 부호 정리
    if not standard_text.endswith(('.', '!', '?', '요', '다')):
        if '?' in standard_text or '입니까' in standard_text:
            standard_text += '?'
        else:
            standard_text += ' 주세요.'
    
    response["표준어 요약"] = standard_text
    
    # 2. 품목 정보 추출 (향상된 규칙 기반)
    items = []
    
    # 수량 추출 패턴
    quantity_patterns = [
        (r'한\s*(뭇|다발|박스|봉지|개|항그|가득)', 1),
        (r'두\s*(뭇|다발|박스|봉지|개|항그|가득)', 2),
        (r'세\s*(뭇|다발|박스|봉지|개|항그|가득)', 3),
        (r'(\d+)\s*(뭇|다발|박스|봉지|개|항그|가득)', lambda m: int(m.group(1))),
    ]
    
    # 단위 매핑
    unit_mapping = {
        '뭇': '다발', '다발': '다발',
        '항그': '가득', '가득': '가득',
        '봉지': '봉지', '박스': '박스',
        '개': '개'
    }
    
    # 품목 검출 로직
    product_patterns = [
        (r'(정구지|부추)', '부추'),
        (r'(지레|기저귀)', '기저귀'),
        (r'(사고|사과)', '사과'),
        (r'우유', '우유'),
    ]
    
    for pattern, product_name in product_patterns:
        matches = list(re.finditer(pattern, original_sentence))
        for match in matches:
            # 해당 품목 주변에서 수량과 단위 찾기
            start_pos = match.start()
            surrounding_text = original_sentence[max(0, start_pos-20):min(len(original_sentence), start_pos+20)]
            
            # 수량 추출
            quantity = 1  # 기본값
            unit = '개'   # 기본값
            
            for q_pattern, q_value in quantity_patterns:
                q_match = re.search(q_pattern, surrounding_text)
                if q_match:
                    if callable(q_value):
                        quantity = q_value(q_match)
                    else:
                        quantity = q_value
                    
                    # 단위 추출
                    for unit_key in unit_mapping:
                        if unit_key in q_match.group():
                            unit = unit_mapping[unit_key]
                            break
                    break
            
            # 기저귀 크기 처리
            final_product_name = product_name
            if product_name == '기저귀':
                if '큰' in surrounding_text or '대형' in surrounding_text:
                    final_product_name = '기저귀 (대형)'
                elif '작은' in surrounding_text or '소형' in surrounding_text:
                    final_product_name = '기저귀 (소형)'
            
            # 이미 추가된 품목인지 확인
            exists = False
            for item in items:
                if item[0] == final_product_name and item[2] == unit:
                    exists = True
                    break
            
            if not exists:
                items.append([final_product_name, quantity, unit])
    
    response["품목 정보"] = items
    
    # 3. 주문 의도 판별 (향상된 로직)
    lower_sentence = original_sentence.lower()
    
    if any(keyword in lower_sentence for keyword in ['있능교', '있습니까', '있나', '있나요']):
        response["주문 의도"] = "재고문의"
    elif any(keyword in lower_sentence for keyword in ['얼만교', '얼마', '얼마입니까', '가격']):
        response["주문 의도"] = "가격확인"
    elif any(keyword in lower_sentence for keyword in ['보내주', '배송', '퍼뜩', '빨리']):
        response["주문 의도"] = "주문배송"
    
    return json.dumps(response, ensure_ascii=False, indent=2)

# 2. 확장된 테스트 데이터셋
test_dataset = [
    # 재고문의
    {"input": "아지매, 정구지 한 뭇 있능교?", "expected": "부추"},
    {"input": "지레 작은 거 있능교?", "expected": "기저귀"},
    {"input": "사고 있능교?", "expected": "사과"},
    {"input": "우유 있능가?", "expected": "우유"},
    
    # 가격확인
    {"input": "지레 큰 거 한 봉지 얼만교?", "expected": "기저귀"},
    {"input": "사고 한 봉지 얼만교?", "expected": "사과"},
    {"input": "정구지 두 뭇 얼만가?", "expected": "부추"},
    
    # 주문배송
    {"input": "사과 한 항그하고 우유 두 개만 퍼뜩 보내주이소.", "expected": "사과"},
    {"input": "정구지 두 뭇 조아?", "expected": "부추"},
    {"input": "지레 큰 거 두 개 보내주이써.", "expected": "기저귀"},
    
    # 복합 주문
    {"input": "사과 한 박스랑 우유 세 개 얼만교?", "expected": "사과"},
    {"input": "정구지 한 뭇하고 지레 한 개 보내주이소.", "expected": "부추"},
    
    # 다양한 수량
    {"input": "정구지 세 뭇 있능교?", "expected": "부추"},
    {"input": "우유 다섯 개 퍼뜩 보내주이소.", "expected": "우유"},
] * 7  # 14 * 7 = 98개 (+2개 추가로 100개)

def run_test():
    results = []
    success_count = 0
    total_time = 0
    detailed_results = []

    print(f"[*] 총 {len(test_dataset)}건의 방언 테스트를 시작합니다...")
    print("="*60)

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
            found_items = []
            
            for item in res_data.get("품목 정보", []):
                if data['expected'] in str(item[0]):
                    is_success = True
                    found_items.append(f"{item[0]} {item[1]}{item[2]}")
            
            if is_success: 
                success_count += 1
            
            result_entry = {
                "no": i + 1,
                "input": data['input'],
                "output": res_json,
                "latency": f"{latency:.4f}s",
                "result": "PASS" if is_success else "FAIL"
            }
            results.append(result_entry)
            
            # 상세 결과 저장
            detailed_results.append({
                "no": i + 1,
                "input": data['input'],
                "expected": data['expected'],
                "found_items": ", ".join(found_items) if found_items else "없음",
                "standard_summary": json.loads(res_json).get("표준어 요약", ""),
                "intent": json.loads(res_json).get("주문 의도", ""),
                "latency": latency,
                "result": "PASS" if is_success else "FAIL"
            })
            
            if (i + 1) % 10 == 0:
                print(f"[{i+1:3d}/{len(test_dataset)}] 진행 중... 정확도: {success_count/(i+1)*100:.1f}%")

        except Exception as e:
            print(f"[오류] {i+1}번 항목 처리 중 에러 발생: {e}")
            results.append({
                "no": i + 1,
                "input": data['input'],
                "output": f"ERROR: {str(e)}",
                "latency": "0.0000s",
                "result": "ERROR"
            })

    # 3. 결과 요약 및 저장
    avg_latency = total_time / len(test_dataset) if test_dataset else 0
    accuracy = (success_count / len(test_dataset)) * 100 if test_dataset else 0

    # CSV 파일 저장
    with open('dialect_test_report.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["no", "input", "output", "latency", "result"])
        writer.writeheader()
        writer.writerows(results)

    # 상세 보고서 저장
    with open('dialect_detailed_report.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "no", "input", "expected", "found_items", 
            "standard_summary", "intent", "latency", "result"
        ])
        writer.writeheader()
        writer.writerows(detailed_results)

    # 통계 계산
    intents_count = {}
    for result in detailed_results:
        intent = result.get("intent", "")
        if intent in intents_count:
            intents_count[intent] += 1
        else:
            intents_count[intent] = 1

    print("\n" + "="*60)
    print("방언 처리 시스템 테스트 완료 보고서")
    print("="*60)
    print(f"📊 성능 통계")
    print(f"  - 총 테스트 문장: {len(test_dataset):4d}건")
    print(f"  - 성공한 문장:    {success_count:4d}건")
    print(f"  - 최종 정확도:    {accuracy:6.1f}%")
    print(f"  - 평균 응답 속도: {avg_latency:.4f}초")
    print(f"  - 최대 응답 속도: {max([r.get('latency', 0) for r in detailed_results if isinstance(r.get('latency'), (int, float))]):.4f}초")
    print(f"  - 최소 응답 속도: {min([r.get('latency', 0) for r in detailed_results if isinstance(r.get('latency'), (int, float))]):.4f}초")
    
    print(f"\n🎯 의도 분류 통계")
    for intent, count in intents_count.items():
        percentage = (count / len(detailed_results)) * 100
        print(f"  - {intent:10s}: {count:3d}건 ({percentage:5.1f}%)")
    
    print(f"\n💾 출력 파일")
    print(f"  - 간략 보고서: 'dialect_test_report.csv'")
    print(f"  - 상세 보고서: 'dialect_detailed_report.csv'")
    print("="*60)
    
    # 실패한 케이스 표시 (있는 경우)
    failed_cases = [r for r in detailed_results if r.get("result") == "FAIL"]
    if failed_cases:
        print(f"\n❌ 실패한 케이스 ({len(failed_cases)}건):")
        for case in failed_cases[:5]:  # 최대 5개만 표시
            print(f"  [{case['no']:3d}] 입력: {case['input']}")
            print(f"       기대: {case['expected']}, 발견: {case['found_items']}")
    
    return accuracy, avg_latency

if __name__ == "__main__":
    accuracy, avg_latency = run_test()
    
    # 성능 기준 평가
    print(f"\n📈 시스템 평가:")
    if accuracy >= 95:
        print(f"  ✅ 정확도: 우수 (95% 이상)")
    elif accuracy >= 85:
        print(f"  ⚠️  정확도: 보통 (85-94%)")
    else:
        print(f"  ❌ 정확도: 개선 필요 (85% 미만)")
    
    if avg_latency <= 0.01:
        print(f"  ✅ 응답속도: 매우 빠름 (0.01초 미만)")
    elif avg_latency <= 0.05:
        print(f"  ⚠️  응답속도: 빠름 (0.01-0.05초)")
    else:
        print(f"  ❌ 응답속도: 개선 필요 (0.05초 초과)")
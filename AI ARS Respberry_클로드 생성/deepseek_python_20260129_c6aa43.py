import json
import time
import csv
import re
import os
import sys

# 현재 디렉토리 확인
print(f"현재 작업 디렉토리: {os.getcwd()}")
print("="*60)

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
    
    # 1. 표준어 변환
    standard_text = dialect_sentence
    for dialect, standard in sorted(dialect_dict.items(), key=lambda x: -len(x[0])):
        standard_text = standard_text.replace(dialect, standard)
    
    if not standard_text.endswith(('.', '!', '?', '요', '다')):
        if '?' in standard_text or '입니까' in standard_text:
            standard_text += '?'
        else:
            standard_text += ' 주세요.'
    
    response["표준어 요약"] = standard_text
    
    # 2. 품목 정보 추출
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
            start_pos = match.start()
            surrounding_text = original_sentence[max(0, start_pos-20):min(len(original_sentence), start_pos+20)]
            
            quantity = 1
            unit = '개'
            
            for q_pattern, q_value in quantity_patterns:
                q_match = re.search(q_pattern, surrounding_text)
                if q_match:
                    if callable(q_value):
                        quantity = q_value(q_match)
                    else:
                        quantity = q_value
                    
                    for unit_key in unit_mapping:
                        if unit_key in q_match.group():
                            unit = unit_mapping[unit_key]
                            break
                    break
            
            final_product_name = product_name
            if product_name == '기저귀':
                if '큰' in surrounding_text or '대형' in surrounding_text:
                    final_product_name = '기저귀 (대형)'
                elif '작은' in surrounding_text or '소형' in surrounding_text:
                    final_product_name = '기저귀 (소형)'
            
            exists = False
            for item in items:
                if item[0] == final_product_name and item[2] == unit:
                    exists = True
                    break
            
            if not exists:
                items.append([final_product_name, quantity, unit])
    
    response["품목 정보"] = items
    
    # 3. 주문 의도 판별
    lower_sentence = original_sentence.lower()
    
    if any(keyword in lower_sentence for keyword in ['있능교', '있습니까', '있나', '있나요']):
        response["주문 의도"] = "재고문의"
    elif any(keyword in lower_sentence for keyword in ['얼만교', '얼마', '얼마입니까', '가격']):
        response["주문 의도"] = "가격확인"
    elif any(keyword in lower_sentence for keyword in ['보내주', '배송', '퍼뜩', '빨리']):
        response["주문 의도"] = "주문배송"
    
    return json.dumps(response, ensure_ascii=False)

# 2. 테스트 데이터셋
test_dataset = [
    {"input": "아지매, 정구지 한 뭇 있능교?", "expected": "부추"},
    {"input": "지레 작은 거 있능교?", "expected": "기저귀"},
    {"input": "사고 있능교?", "expected": "사과"},
    {"input": "우유 있능가?", "expected": "우유"},
    {"input": "지레 큰 거 한 봉지 얼만교?", "expected": "기저귀"},
    {"input": "사고 한 봉지 얼만교?", "expected": "사과"},
    {"input": "정구지 두 뭇 얼만가?", "expected": "부추"},
    {"input": "사과 한 항그하고 우유 두 개만 퍼뜩 보내주이소.", "expected": "사과"},
    {"input": "정구지 두 뭇 조아?", "expected": "부추"},
    {"input": "지레 큰 거 두 개 보내주이써.", "expected": "기저귀"},
] * 10  # 100개 샘플

def run_test():
    results = []
    success_count = 0
    total_time = 0

    print(f"[*] 총 {len(test_dataset)}건의 방언 테스트를 시작합니다...")

    for i, data in enumerate(test_dataset):
        start_time = time.time()
        
        try:
            res_json = process_dialect_order(data['input'])
            latency = time.time() - start_time
            total_time += latency
            
            res_data = json.loads(res_json)
            
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
                "output": res_json[:100] + "..." if len(res_json) > 100 else res_json,
                "latency": f"{latency:.4f}s",
                "result": "PASS" if is_success else "FAIL"
            })
            
            if (i + 1) % 20 == 0:
                print(f"[{i+1}/{len(test_dataset)}] 진행 중...")

        except Exception as e:
            print(f"[오류] {i+1}번 항목 처리 중 에러 발생: {e}")
            results.append({
                "no": i + 1,
                "input": data['input'],
                "output": f"ERROR: {str(e)}",
                "latency": "0.0000s",
                "result": "ERROR"
            })

    # 3. 결과 저장 (명시적 경로 지정)
    base_dir = os.getcwd()
    csv_path = os.path.join(base_dir, 'dialect_test_report.csv')
    detailed_path = os.path.join(base_dir, 'dialect_detailed_report.csv')
    
    print(f"\n파일 저장 경로:")
    print(f"1. {csv_path}")
    print(f"2. {detailed_path}")
    
    try:
        # 간략 보고서 저장
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["no", "input", "output", "latency", "result"])
            writer.writeheader()
            writer.writerows(results)
        print(f"✓ CSV 파일 저장 성공: {csv_path}")
        
        # 상세 보고서 저장 (간단한 버전)
        with open(detailed_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['테스트 번호', '입력 문장', '품목 발견', '정확도'])
            for result in results:
                writer.writerow([
                    result['no'],
                    result['input'],
                    '예' if result['result'] == 'PASS' else '아니오',
                    result['result']
                ])
        print(f"✓ 상세 보고서 저장 성공: {detailed_path}")
        
    except Exception as e:
        print(f"✗ 파일 저장 실패: {e}")
        # 대체 저장 위치 시도
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'dialect_test_report.csv')
        try:
            with open(desktop_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=["no", "input", "output", "latency", "result"])
                writer.writeheader()
                writer.writerows(results)
            print(f"✓ 대체 경로에 저장 성공: {desktop_path}")
        except Exception as e2:
            print(f"✗ 대체 경로 저장도 실패: {e2}")
            # 콘솔에 출력
            print("\n콘솔에 결과 출력:")
            for result in results[:5]:  # 처음 5개만 출력
                print(f"{result['no']}: {result['input']} -> {result['result']}")

    # 4. 결과 요약
    avg_latency = total_time / len(test_dataset) if test_dataset else 0
    accuracy = (success_count / len(test_dataset)) * 100 if test_dataset else 0

    print("\n" + "="*60)
    print("테스트 완료 보고서")
    print("="*60)
    print(f"- 총 테스트 문장: {len(test_dataset)}건")
    print(f"- 성공한 문장: {success_count}건")
    print(f"- 최종 정확도: {accuracy:.1f}%")
    print(f"- 평균 응답 속도: {avg_latency:.4f}초")
    
    # 파일 존재 확인
    if os.path.exists(csv_path):
        file_size = os.path.getsize(csv_path)
        print(f"- 생성된 파일 크기: {file_size} bytes")
        print(f"- 파일 위치: {csv_path}")
    else:
        print(f"- 파일 생성 실패: {csv_path} 경로 확인 필요")

if __name__ == "__main__":
    run_test()
    
    # 추가 확인
    print("\n" + "="*60)
    print("생성된 파일 목록 (현재 디렉토리):")
    current_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    if current_files:
        for file in current_files:
            file_path = os.path.join(os.getcwd(), file)
            size = os.path.getsize(file_path)
            print(f"  - {file} ({size} bytes)")
    else:
        print("  - CSV 파일이 없습니다.")
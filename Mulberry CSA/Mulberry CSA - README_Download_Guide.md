# Mulberry CSA - README_Download_Guide

## 📦 패키지 개요

이 패키지는 **Mulberry Project CSA 계약서 템플릿**을 GitHub 및 로컬 환경에서 쉽게 사용하고 관리할 수 있도록 구성되어 있습니다.  

- 계약서 01~05 (영문 EN)  
- Markdown(MD) + Word(DOCX) 버전 포함  
- Flowchart / Mermaid Diagram 포함  
- 법무 주석 포함

---

## 📁 디렉토리 구조

```
Mulberry_CSA/
┣ contracts/
┃  ├─ 01_AI_Agent_Delegation/
┃  ├─ 02_Automated_Commerce/
┃  ├─ 03_AP2_Smart_Mandate/
┃  ├─ 04_Agent_Sponsorship/
┃  └─ 05_Performance_Linked_Investment/
┣ governance/
┃  └─ Agent_Passport_Governance.md
┣ summaries/
┃  ├─ Municipality_2Page_Summary_EN.pdf
┣ pitch/
┃  └─ VC_Pitch_Contract_Structure_Slides.pdf
└ README_Download_Guide.md
```

---

## 📄 contracts/ 설명

| 번호  | 계약서명             | MD  | DOCX | 용도                   |
| --- | ---------------- | --- | ---- | -------------------- |
| 01  | AI Agent 운영·위임   | ✅   | ✅    | AI Agent 운영 권한/책임 규정 |
| 02  | 자동화 상거래 대행       | ✅   | ✅    | 공동구매/매장주문 자동화        |
| 03  | AP2 스마트 위임 결제    | ✅   | ✅    | 조건부 결제 실행 약정         |
| 04  | AI Agent 후원·사회지원 | ✅   | ✅    | 후원금/사회적 가치 흐름        |
| 05  | 성과연동 투자          | ✅   | ✅    | 투자금/수익 배분 구조         |

> MD: GitHub 열람 및 버전 관리 용  
> DOCX: 법무 검토, PDF 변환, 회의·행정 제출용

---

## 🛠 사용 안내

### 1️⃣ Markdown → DOCX 변환

- Pandoc, Typora, Word 사용 가능
- Mermaid Diagram은 PNG 등 그림으로 변환 후 DOCX에 삽입
- 예:  
  
  ```bash
  pandoc 01_AI_Agent_Delegation_Template_EN.md -o 01_AI_Agent_Delegation_Template_EN.docx
  ```

### 2️⃣ GitHub 업로드

```bash
git checkout -b mulberry_csa_upload
git add Mulberry_CSA/
git commit -m "Add CSA contract templates (EN MD + DOCX)"
git push origin mulberry_csa_upload
```

- PR 생성 → 팀/법무 검토 → 메인 브랜치 병합

### 3️⃣ Mermaid / Flowchart 처리

- MD 코드 블록 그대로 GitHub에서 확인 가능
- DOCX/회의용은 PNG로 변환 후 삽입

---

## ⚠️ 주의 사항

- 모든 계약서 EN 버전은 **영문 기반 템플릿**입니다
- KR 버전은 **별도 번역 후 업로드**  
- DOCX 저장 전 반드시 **법무 주석 확인**  
- ZIP 압축 전 전체 구조 확인

---

## 📥 ZIP 패키지 안내

1. 로컬에서 Mulberry_CSA/ 폴더 전체 선택  
2. 마우스 오른쪽 → **압축(zip) 생성**  
3. GitHub 업로드 시 **폴더 구조 그대로 유지**  
4. 필요 시 팀 공유 및 백업용

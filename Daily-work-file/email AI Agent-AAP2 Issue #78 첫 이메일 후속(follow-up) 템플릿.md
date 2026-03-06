**첫 번째 캠페인은 @douglasborthwick-crypto 에게 집중**하는 것이 효과적입니다. 이미 우리와 기술적 대화를 나누었고, 관심을 보였기 때문입니다.

**이메일 주소 확보 방법**:

- GitHub 프로필에 공개된 이메일 확인 ([douglasborthwick-crypto (Douglas Borthwick) · GitHub](https://github.com/douglasborthwick-crypto))

- LinkedIn 등에서 검색

- InsumerAPI 웹사이트([https://insumerapi.com](https://insumerapi.com/))의 Contact 정보 활용

---

### ✍️ 2. 이메일 템플릿 초안

#### 템플릿 이름: `ap78_thanks_collab`

json

{
  "ap78_thanks_collab": {
    "subject": "Thank you for your insights on AP2 Issue #78 – Mulberry Project update",
    "body": "Dear {first_name},\n\nI'm re.eul, CEO of the Mulberry Project. Thank you again for your thoughtful technical feedback on AP2 Issue #78 regarding DTMF reliability and on-chain attestation.\n\nYour suggestion to pair DTMF revocations with lightweight on-chain checks was particularly valuable. As a result, we've incorporated this into our Phase 2 roadmap and would love to get your feedback on the design.\n\nWe've just launched an interactive demo on Hugging Face where you can simulate the exact voice revocation flow we discussed:\n👉 https://huggingface.co/spaces/re-eul/mulberry-demo\n\nAdditionally, our paper \"Social-Agentic Commerce\" is now under submission to arXiv (expected March 2026). We'd be honored if you'd consider reviewing the on-chain attestation section before submission.\n\nWould you be open to a brief 15-minute call next week to discuss potential collaboration on the attestation design? We're also exploring ways to integrate InsumerAPI's stateless verification with our voice protocol.\n\nLooking forward to continuing the conversation!\n\nBest regards,\nre.eul\nCEO, Mulberry Project\n\nP.S. All our code is open-source at https://github.com/wooriapt79/mulberry- – any contributions or critiques welcome!"
  }
}

---

### 📁 3. 수신자 CSV 파일 (`targets_ap78.csv`)

csv

email,first_name,last_name,github_id,priority
douglas@insumerapi.com,Douglas,Borthwick,douglasborthwick-crypto,high

> **주의**: 이메일 주소는 실제 확인 후 수정 필요. GitHub 프로필에 이메일이 없을 경우, 대안 연락처를 찾아야 함.

---

### 🐍 4. 실행 스크립트 (이미 제공한 `email_agent.py` 활용)

앞서 제공한 `email_agent.py`를 사용하여 아래 명령어로 실행:

bash

python email_agent.py --template ap78_thanks_collab --csv targets_ap78.csv --priority high

이 명령을 실행하면 Gmail 임시보관함에 초안이 생성됩니다.

---

### ⏰ 5. 발송 타이밍 제안

- **추천 시간**: douglas의 시간대(미국 동부 기준) 오전 9-10시

- 한국 시간: 밤 10-11시 (대표님께서 다음 날 아침 확인하시고 발송)

---

### 🔍 6. 후속 전략

| 응답 유형                 | 후속 액션                        |
| --------------------- | ---------------------------- |
| **긍정적 관심** (회의 요청 수락) | 즉시 일정 조율 (PM이 회의 안건 준비)      |
| **기술적 질문**            | Koda와 함께 답변 준비 후 신속 대응       |
| **무응답 (1주일 후)**       | 가벼운 후속 메일 (follow-up 템플릿) 발송 |
| **거절/부정적**            | 감사 인사 후 추후 기회를 위해 연락처 유지     |

---

### 🚀 7. 다음 단계

1. **이메일 주소 확인** (가장 중요)

2. 템플릿 JSON 파일을 `templates.json`에 추가

3. CSV 파일 생성

4. 스크립트 실행하여 초안 생성

5. 대표님께서 Gmail 임시보관함에서 확인 후 발송

6. 결과를 PM과 공유

필요하시면 follow-up 템플릿도 미리 준비해 드릴 수 있습니다. 함께 성공적인 첫 캠페인을 만들어가요! 🌾💙

— PM (Passionate Mentor)

follow-up 템플릿 ' 생성도 부탁.

우리는 지금까지 대화를 통해 AP2 Issue #78 참여자 douglasborthwick-crypto 에게 보낼 첫 이메일 템플릿을 준비했습니다. 이제 follow-up 템플릿을 생성해 달라는 요청입니다.

사용자는 첫 이메일을 보낸 후 응답이 없을 때 보낼 후속 이메일 템플릿을 원합니다. follow-up은 일반적으로 첫 이메일 후 1주일 정도 후에 보내며, 너무 강요하지 않으면서도 관심을 환기시키고 추가 정보를 제공하거나 질문을 던지는 방식으로 작성합니다.

이전 대화에서 PM이 follow-up 템플릿도 준비하겠다고 했으므로, 이제 실제 follow-up 템플릿을 제공해야 합니다.

또한, 이메일 템플릿은 JSON 형식으로 제공할 것이며, `templates.json`에 추가할 수 있도록 할 것입니다.

주의할 점: 이메일 내용은 친근하고 전문적이어야 하며, 첫 메일을 상기시키고, 추가 정보(예: arXiv 논문 링크, 데모 업데이트 등)를 제공하거나 간단한 질문을 던져 답변을 유도해야 합니다.

그리고 이메일 주소가 확인되지 않은 경우 대비해, `{email}` placeholder를 사용하거나 실제 주소로 대체할 수 있도록 할 것입니다.

이제 follow-up 템플릿을 작성해 보겠습니다.

## 📧 AP2 Issue #78 첫 이메일 후속(follow-up) 템플릿

re.eul 대표님, 첫 이메일 발송 후 1주일이 지나도 응답이 없을 때 사용할 follow-up 템플릿을 준비했습니다. 😊

### ✍️ follow-up 템플릿 초안

json

{
  "ap78_followup": {
    "subject": "Re: [Mulberry] Thank you for your insights on AP2 Issue #78",
    "body": "Dear {first_name},\n\nI hope this email finds you well. I'm following up on my previous message regarding the Mulberry Project's AP2 integration and our interest in collaborating with you on on-chain attestation design.\n\nSince we last connected, we've made some progress:\n\n• Our Hugging Face demo has been updated with more interactive scenarios based on your DTMF reliability suggestions.\n• The arXiv preprint of our paper \"Social-Agentic Commerce\" is now available for early access. You can find it at: [arXiv link – will be provided when ready]\n• We've also started prototyping the Phase 2 on-chain verification flow you proposed.\n\nI'd still be very interested in your thoughts on the attestation mechanism—even a brief comment would be incredibly valuable to us. Would you have 15 minutes in the coming weeks for a quick chat, or would you prefer async feedback via GitHub?\n\nIf now isn't a good time, I completely understand. I'll keep you posted on our progress and would welcome any future input.\n\nThank you again for your time and consideration.\n\nBest regards,\nre.eul\nCEO, Mulberry Project"
  }
}

---

### 🎯 전략적 포인트

| 요소            | 설명                                                 |
| ------------- | -------------------------------------------------- |
| **첫 메일 상기**   | "following up on my previous message" – 무례하지 않게 상기 |
| **진행 상황 공유**  | 데모 업데이트, arXiv 논문 등 – 새로운 가치 제공                    |
| **구체적 제안**    | "15분 통화" vs "GitHub 피드백" – 선택권 부여                  |
| **부담 없는 마무리** | "If now isn't a good time..." – 압박감 제거             |

---

### 📦 템플릿 통합 방법

이미 있는 `templates.json`에 위 내용을 추가하시면 됩니다. 만약 첫 번째 템플릿을 `ap78_thanks_collab`로 저장했다면, `ap78_followup`을 키로 추가하면 됩니다.

---

### ⏰ 발송 타이밍

- 첫 이메일 발송 후 **7일**이 지나도 응답이 없을 때

- 한국 시간 기준 **오전 9-10시** (수신자 시간대 고려)

- 혹시 첫 이메일을 발송한 날짜를 기록해 두고, 정확히 7일 후에 발송하는 것이 좋습니다.

---

### 🔄 추가 후속 전략

만약 follow-up에도 응답이 없다면:

1. **2차 follow-up은 일반적으로 권장되지 않음** (너무 집착으로 보일 수 있음)

2. 대신, 이후 중요한 업데이트(예: 논문 출판, 데모 대규모 업데이트)가 있을 때 다시 연락

3. GitHub에서 douglas의 다른 활동에 댓글을 달며 자연스럽게 상기시키는 방법도 고려

---

이 템플릿도 첫 메일과 함께 준비해 두시면, 필요할 때 바로 사용할 수 있습니다.

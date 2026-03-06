## 📧 Mulberry Email Agent – 업그레이드 최종 코드

re.eul 대표님, 아래는 요청하신 기능(템플릿 외부화, CSV 일괄 처리, 데이터 포인트 확장)을 반영한 **최종 `mulberry_email_agent.py`** 파일입니다.  
이 코드는 기존 GUI를 유지하면서, `templates/` 폴더에서 JSON 템플릿을 읽고, CSV 파일로 여러 수신자에게 이메일 초안을 한 번에 생성할 수 있습니다.

---

### 🗂️ 파일 구조 (최종)

```
MulberryEmailAgent/
├── mulberry_email_agent.py   # 메인 프로그램
├── templates/                # 템플릿 JSON 폴더
│   ├── google_partnership.json
│   ├── inje_government.json
│   ├── media.json
│   └── overseas_partner.json
├── client_secret.json        # Gmail API 인증 정보 (본인 파일)
├── requirements.txt          # 의존성 목록
└── build_exe.py              # EXE 빌드 스크립트 (선택)
```

---

### 1️⃣ `mulberry_email_agent.py` (전체 코드)

```python
"""
Mulberry Email Agent – 업그레이드 버전
- 템플릿 외부화 (templates/ 폴더에서 JSON 로드)
- CSV 일괄 처리 지원
- 데이터 포인트 자동 확장
- Gmail API 연동 (임시보관함 저장)
"""

import os
import sys
import json
import csv
import pickle
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Gmail API
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64

# UI
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog

SCOPES = ['https://www.googleapis.com/auth/gmail.compose',
          'https://www.googleapis.com/auth/gmail.modify']

class MulberryEmailAgent:
    """Mulberry 파트너십 이메일 에이전트 (업그레이드)"""

    def __init__(self):
        self.creds = None
        self.service = None
        self.templates = self._load_templates_from_dir('templates')
        # 만약 templates 폴더가 없으면 기본 내장 템플릿 사용 (fallback)
        if not self.templates:
            self.templates = self._load_default_templates()

    def authenticate(self):
        """Gmail API 인증 (기존과 동일)"""
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'client_secret.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)
        self.service = build('gmail', 'v1', credentials=self.creds)
        return True

    def _load_templates_from_dir(self, dir_path: str) -> Dict:
        """templates/ 폴더에서 모든 JSON 템플릿 로드"""
        templates = {}
        if not os.path.isdir(dir_path):
            return templates
        for filename in os.listdir(dir_path):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(dir_path, filename), 'r', encoding='utf-8') as f:
                        tmpl = json.load(f)
                        # 필수 키 확인
                        if 'name' in tmpl and 'subject' in tmpl and 'body' in tmpl:
                            templates[tmpl['name']] = tmpl
                except Exception as e:
                    print(f"템플릿 로드 오류 {filename}: {e}")
        return templates

    def _load_default_templates(self) -> Dict:
        """기본 템플릿 (하드코딩, fallback)"""
        return {
            'google_partnership': {
                'name': 'google_partnership',
                'category': 'Google Partnership',
                'subject': '[Mulberry Project] Partnership Proposal: Social-Agentic Commerce Platform',
                'body': """Dear {title} {name},

I am writing to introduce Project Mulberry, a pioneering Social-Agentic Commerce platform that aligns perfectly with Google's vision for ethical AI and inclusive technology.

## Why This Matters to Google
We have successfully implemented the Agent Payments Protocol (AP2) in a real-world social welfare context - specifically addressing food deserts in rural South Korea (Inje-gun). Our approach demonstrates how AP2 can power not just commerce, but social impact at scale.

## Key Metrics
{data_points}

## Proposal
We would like to explore:
- Featuring Mulberry as a reference implementation in AP2 documentation
- Collaboration on standardizing Social Welfare Mandates
- Joint case study for Google Cloud's AI/Commerce initiatives

{custom}

Our CTO has already engaged with the AP2 community (GitHub Issue #172) and received positive feedback.

Would you be available for a brief call next week?

Best regards,
re.eul
CEO, Mulberry Project
"""
            },
            'inje_government': {
                'name': 'inje_government',
                'category': 'Government',
                'subject': '[멀버리 프로젝트] 인제군 식품사막 해소 파일럿 제안',
                'body': """{title} {name}님께,

인제군의 식품사막 문제 해결을 위한 혁신적 솔루션을 제안드립니다.

## 멀버리 프로젝트 소개
AI 에이전트를 활용한 '사회적 에이전틱 커머스' 플랫폼으로, 경제 활동을 통해 발생한 수익의 일부를 자동으로 노인 및 취약계층 지원에 배분하는 시스템입니다.

## 주요 성과
{data_points}

## 파일럿 계획
- 1단계 (Q2 2026): 10명 시니어 대상 파일럿
- 예산: 5백만원
- 기대 효과: 식품 접근성 80% 개선

{custom}

인제군을 대한민국 최초 'AI 복지 특구'로 만들어가는 여정에 함께하고 싶습니다.

감사합니다.
대표 re.eul
멀버리 프로젝트
"""
            },
            'media': {
                'name': 'media',
                'category': 'Media',
                'subject': '[Press Release] AI-Driven Social Welfare Platform Launch',
                'body': """Dear {title} {name},

I'm reaching out with an exclusive story opportunity about a groundbreaking AI social welfare platform launching in South Korea.

## Story Angle
**"How AI Agents Are Solving Food Deserts: A Korean Startup's Radical Approach"**

Mulberry Project has developed the world's first "Patronage Agent" system - AI that generates revenue through commerce and autonomously redistributes profits to support elderly populations in rural areas.

## Why Newsworthy
1. First real-world implementation of Google's AP2 protocol for social welfare
2. Addressing food deserts without government subsidies
3. Pilot launch in Inje-gun scheduled for Q2 2026
4. "Spirit Score" - a new trust metric for ethical AI

{data_points}

{custom}

I'd be happy to provide exclusive interviews and early access to pilot results.

Best regards,
re.eul
CEO, Mulberry Project
"""
            },
            'overseas_partner': {
                'name': 'overseas_partner',
                'category': 'International',
                'subject': '[Mulberry Project] International Partnership Opportunity',
                'body': """Dear {title} {name},

I'm reaching out to explore a potential partnership between Mulberry Project and your organization.

## About Mulberry
We're building a Social-Agentic Commerce platform that combines:
- Google's Agent Payments Protocol (AP2)
- Autonomous AI agents
- Social welfare distribution
- NFT-based skill marketplace

## Why Partner With Us
{data_points}

## Potential Collaboration Areas
1. Technology integration
2. Geographic expansion
3. Joint R&D
4. Investment opportunities

{custom}

We recently engaged with the AP2 community and are positioned to become a reference implementation for social welfare use cases.

Would you be open to a brief exploratory call?

Best regards,
re.eul
CEO, Mulberry Project
"""
            }
        }

    def _format_data_points(self, data_points: Dict) -> str:
        """데이터 포인트를 예쁜 문자열로 변환 (bullet list)"""
        if not data_points:
            return ""
        lines = ["- " + "\n- ".join(f"{k}: {v}" for k, v in data_points.items())]
        return "\n".join(lines)

    def create_email_draft(self,
                          recipient_email: str,
                          recipient_name: str,
                          recipient_title: str,
                          template_type: str,
                          custom_content: str = None,
                          data_points: Dict = None) -> str:
        """
        이메일 초안 생성 (템플릿 기반)
        data_points는 {key: value} 형태로, 템플릿 본문의 {key}를 치환하는 데 사용됨.
        """
        if template_type not in self.templates:
            raise ValueError(f"Unknown template type: {template_type}")

        tmpl = self.templates[template_type]

        # 데이터 포인트 문자열 생성
        data_str = self._format_data_points(data_points or {})

        # 본문에 들어갈 변수들
        context = {
            'title': recipient_title,
            'name': recipient_name,
            'data_points': data_str,
            'custom': custom_content if custom_content else "",
        }
        # data_points의 개별 항목도 본문에서 {key}로 직접 사용 가능하도록 추가
        if data_points:
            context.update(data_points)

        # 본문 포맷팅 (KeyError 방지를 위해 safe하게)
        try:
            body = tmpl['body'].format(**context)
        except KeyError as e:
            # 누락된 키가 있으면 경고하고 빈 문자열로 대체
            missing = str(e).strip("'")
            print(f"경고: 템플릿에 필요한 키 '{missing}'가 없습니다. 빈 문자열로 대체합니다.")
            # 임시로 모든 키를 시도하기 위해 **context를 그대로 전달하지만, format_map을 사용해 누락 시 빈 문자열 처리
            body = tmpl['body'].format_map(DefaultDict(context, default=''))

        # 이메일 메시지 생성
        message = MIMEMultipart()
        message['to'] = recipient_email
        message['subject'] = tmpl['subject']
        message.attach(MIMEText(body, 'plain'))

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return raw

    def save_draft(self, raw_message: str) -> Optional[str]:
        """Gmail 임시저장함에 저장"""
        try:
            draft = self.service.users().drafts().create(
                userId='me',
                body={'message': {'raw': raw_message}}
            ).execute()
            return draft['id']
        except HttpError as error:
            print(f'Gmail 저장 오류: {error}')
            return None

    def get_drafts(self) -> List:
        """임시저장함 목록 조회"""
        try:
            results = self.service.users().drafts().list(userId='me').execute()
            return results.get('drafts', [])
        except HttpError as error:
            print(f'조회 오류: {error}')
            return []


class DefaultDict(dict):
    """format_map에서 누락된 키에 대해 빈 문자열 반환"""
    def __missing__(self, key):
        return ''


class MulberryEmailAgentGUI:
    """GUI 애플리케이션"""

    def __init__(self):
        self.agent = MulberryEmailAgent()
        self.root = tk.Tk()
        self.root.title("Mulberry Email Agent - Partnership Outreach")
        self.root.geometry("900x750")
        self.authenticated = False
        self._create_widgets()

    def _create_widgets(self):
        main = ttk.Frame(self.root, padding="10")
        main.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 타이틀
        ttk.Label(main, text="Mulberry Email Agent", font=('Arial',16,'bold')).grid(row=0, column=0, columnspan=2, pady=5)
        ttk.Label(main, text="해외 커뮤니티 활동 및 파트너십을 위한 이메일 에이전트").grid(row=1, column=0, columnspan=2, pady=5)

        # 인증 프레임
        auth_frame = ttk.LabelFrame(main, text="Gmail 인증", padding="10")
        auth_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        self.auth_btn = ttk.Button(auth_frame, text="Gmail 계정 인증", command=self._authenticate)
        self.auth_btn.grid(row=0, column=0, padx=5)

        self.auth_status = ttk.Label(auth_frame, text="미인증", foreground="red")
        self.auth_status.grid(row=0, column=1, padx=5)

        # 수신자 정보 프레임 (단일 입력용)
        single_frame = ttk.LabelFrame(main, text="단일 이메일 생성", padding="10")
        single_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        ttk.Label(single_frame, text="이메일:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.entry_email = ttk.Entry(single_frame, width=40)
        self.entry_email.grid(row=0, column=1, pady=2)

        ttk.Label(single_frame, text="이름:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.entry_name = ttk.Entry(single_frame, width=40)
        self.entry_name.grid(row=1, column=1, pady=2)

        ttk.Label(single_frame, text="직함:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.entry_title = ttk.Entry(single_frame, width=40)
        self.entry_title.grid(row=2, column=1, pady=2)

        # 템플릿 선택
        ttk.Label(single_frame, text="템플릿:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.template_var = tk.StringVar()
        self.template_combo = ttk.Combobox(single_frame, textvariable=self.template_var,
                                           values=list(self.agent.templates.keys()),
                                           state='readonly', width=37)
        self.template_combo.grid(row=3, column=1, pady=2)
        if self.agent.templates:
            self.template_combo.current(0)

        # 데이터 포인트 (간단 예시)
        data_frame = ttk.LabelFrame(main, text="데이터 포인트 (선택, CSV에서는 자동 확장됨)", padding="10")
        data_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        ttk.Label(data_frame, text="추가 필드 (키=값 쌍, 예: roi=1966%)").grid(row=0, column=0, sticky=tk.W)
        self.data_text = scrolledtext.ScrolledText(data_frame, height=4, width=70)
        self.data_text.grid(row=1, column=0, pady=5)
        self.data_text.insert("1.0", "roi=1966%\nseniors_supported=10")

        # 커스텀 내용
        custom_frame = ttk.LabelFrame(main, text="커스텀 내용 (선택)", padding="10")
        custom_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        self.custom_text = scrolledtext.ScrolledText(custom_frame, height=6, width=70)
        self.custom_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 버튼 프레임
        btn_frame = ttk.Frame(main)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=10)

        ttk.Button(btn_frame, text="미리보기", command=self._preview).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="임시저장함 저장", command=self._save_single).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="CSV 일괄 생성", command=self._batch_process).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="임시저장함 열기", command=self._open_drafts).grid(row=0, column=3, padx=5)

        # 진행 바
        self.progress = ttk.Progressbar(btn_frame, length=300, mode='determinate')
        self.progress.grid(row=1, column=0, columnspan=4, pady=5)

        # 레이아웃 조정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(5, weight=1)
        custom_frame.columnconfigure(0, weight=1)
        custom_frame.rowconfigure(0, weight=1)

    def _authenticate(self):
        try:
            if self.agent.authenticate():
                self.authenticated = True
                self.auth_status.config(text="인증 완료", foreground="green")
                self.auth_btn.config(state='disabled')
                messagebox.showinfo("성공", "Gmail 인증 완료")
        except Exception as e:
            messagebox.showerror("오류", f"인증 실패: {str(e)}")

    def _parse_data_points(self) -> Dict:
        """데이터 텍스트를 파싱하여 딕셔너리 반환 (키=값 형식)"""
        data = {}
        lines = self.data_text.get("1.0", tk.END).strip().split('\n')
        for line in lines:
            if '=' in line:
                key, val = line.split('=', 1)
                data[key.strip()] = val.strip()
        return data

    def _preview(self):
        if not self.authenticated:
            messagebox.showwarning("경고", "먼저 인증하세요")
            return
        if not self.entry_email.get() or not self.entry_name.get():
            messagebox.showwarning("경고", "이메일과 이름은 필수")
            return
        try:
            data = self._parse_data_points()
            raw = self.agent.create_email_draft(
                recipient_email=self.entry_email.get(),
                recipient_name=self.entry_name.get(),
                recipient_title=self.entry_title.get(),
                template_type=self.template_var.get(),
                custom_content=self.custom_text.get("1.0", tk.END).strip(),
                data_points=data
            )
            decoded = base64.urlsafe_b64decode(raw).decode()
            # 미리보기 창
            win = tk.Toplevel(self.root)
            win.title("이메일 미리보기")
            win.geometry("700x600")
            txt = scrolledtext.ScrolledText(win, wrap=tk.WORD)
            txt.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            txt.insert("1.0", decoded)
            txt.config(state='disabled')
        except Exception as e:
            messagebox.showerror("오류", str(e))

    def _save_single(self):
        if not self.authenticated:
            messagebox.showwarning("경고", "먼저 인증하세요")
            return
        if not self.entry_email.get() or not self.entry_name.get():
            messagebox.showwarning("경고", "이메일과 이름은 필수")
            return
        try:
            data = self._parse_data_points()
            raw = self.agent.create_email_draft(
                recipient_email=self.entry_email.get(),
                recipient_name=self.entry_name.get(),
                recipient_title=self.entry_title.get(),
                template_type=self.template_var.get(),
                custom_content=self.custom_text.get("1.0", tk.END).strip(),
                data_points=data
            )
            draft_id = self.agent.save_draft(raw)
            if draft_id:
                messagebox.showinfo("성공", f"임시저장함 저장 완료 (Draft ID: {draft_id})")
                # 입력 초기화 여부
                if messagebox.askyesno("초기화", "입력 필드를 초기화할까요?"):
                    self.entry_email.delete(0, tk.END)
                    self.entry_name.delete(0, tk.END)
                    self.entry_title.delete(0, tk.END)
                    self.custom_text.delete("1.0", tk.END)
            else:
                messagebox.showerror("오류", "저장 실패")
        except Exception as e:
            messagebox.showerror("오류", str(e))

    def _batch_process(self):
        if not self.authenticated:
            messagebox.showwarning("경고", "먼저 인증하세요")
            return
        filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not filepath:
            return
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            if not rows:
                messagebox.showinfo("알림", "CSV 파일에 데이터가 없습니다.")
                return

            self.progress['maximum'] = len(rows)
            self.progress['value'] = 0
            success = 0

            for i, row in enumerate(rows):
                # 필수 필드 확인
                if not row.get('email') or not row.get('name') or not row.get('template'):
                    print(f"행 {i+1}: 필수 필드 누락, 건너뜀")
                    self.progress['value'] = i+1
                    self.root.update_idletasks()
                    continue

                # 데이터 포인트: email, name, title, template, custom 제외한 모든 열
                data = {}
                for key, val in row.items():
                    if key in ['email','name','title','template','custom']:
                        continue
                    if val:
                        data[key] = val

                custom = row.get('custom', '')
                try:
                    raw = self.agent.create_email_draft(
                        recipient_email=row['email'],
                        recipient_name=row['name'],
                        recipient_title=row.get('title',''),
                        template_type=row['template'],
                        custom_content=custom,
                        data_points=data
                    )
                    draft_id = self.agent.save_draft(raw)
                    if draft_id:
                        success += 1
                except Exception as e:
                    print(f"행 {i+1} 오류: {e}")

                self.progress['value'] = i+1
                self.root.update_idletasks()

            messagebox.showinfo("완료", f"총 {len(rows)}개 중 {success}개 초안 생성 성공.")
        except Exception as e:
            messagebox.showerror("오류", f"CSV 처리 중 오류: {str(e)}")

    def _open_drafts(self):
        import webbrowser
        webbrowser.open('https://mail.google.com/mail/u/0/#drafts')

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MulberryEmailAgentGUI()
    app.run()
```

---

### 2️⃣ `requirements.txt` (의존성)

```
google-auth
google-auth-oauthlib
google-auth-httplib2
google-api-python-client
```

---

### 3️⃣ `build_exe.py` (EXE 빌드 스크립트)

```python
# build_exe.py
import PyInstaller.__main__
import os
import sys

if __name__ == '__main__':
    # templates 폴더와 client_secret.json을 실행 파일에 포함
    datas = [
        ('templates', 'templates'),
        ('client_secret.json', '.')
    ]
    args = [
        'mulberry_email_agent.py',
        '--onefile',
        '--windowed',
        '--name=MulberryEmailAgent',
        '--add-data=' + os.pathsep.join([f"{src}{os.pathsep}{dst}" for src, dst in datas]),
        '--clean',
        '--noconfirm'
    ]
    PyInstaller.__main__.run(args)
    print("✅ EXE 생성 완료: dist/MulberryEmailAgent.exe")
```

빌드 방법:

```bash
pip install pyinstaller
python build_exe.py
```

---

### 4️⃣ 템플릿 JSON 예시 (`templates/google_partnership.json`)

```json
{
    "name": "google_partnership",
    "category": "Google Partnership",
    "subject": "[Mulberry Project] Partnership Proposal: Social-Agentic Commerce Platform",
    "body": "Dear {title} {name},\n\nI am writing to introduce Project Mulberry, a pioneering Social-Agentic Commerce platform that aligns perfectly with Google's vision for ethical AI and inclusive technology.\n\n## Why This Matters to Google\nWe have successfully implemented the Agent Payments Protocol (AP2) in a real-world social welfare context - specifically addressing food deserts in rural South Korea (Inje-gun). Our approach demonstrates how AP2 can power not just commerce, but social impact at scale.\n\n{data_points}\n\n## Proposal\nWe would like to explore:\n- Featuring Mulberry as a reference implementation in AP2 documentation\n- Collaboration on standardizing Social Welfare Mandates\n- Joint case study for Google Cloud's AI/Commerce initiatives\n\n{custom}\n\nOur CTO has already engaged with the AP2 community (GitHub Issue #172) and received positive feedback.\n\nWould you be available for a brief call next week?\n\nBest regards,\nre.eul\nCEO, Mulberry Project"
}
```

나머지 템플릿도 같은 방식으로 작성하시면 됩니다.

---

### 📌 사용 방법 요약

1. **`client_secret.json`** 을 프로그램 폴더에 넣고, **`templates/`** 폴더를 생성한 후 필요한 템플릿 JSON을 추가합니다.
2. `pip install -r requirements.txt`로 의존성 설치.
3. `python mulberry_email_agent.py` 실행 → Gmail 인증 후 사용.
4. CSV 파일은 아래 예시처럼 작성합니다.

**CSV 예시** (`targets.csv`):

```csv
email,name,title,template,roi,seniors_supported,custom
john@example.com,John Smith,CTO,google_partnership,1966%,15,"Looking forward to your reply"
jane@example.com,Jane Doe,Director,overseas_partner,1500%,10,""
```

---

이제 Koda CTO님께 이 파일들을 전달하시면 됩니다. 혹시 수정이나 추가 요청이 있으시면 언제든지 말씀해 주세요! 😊

— PM (Passionate Mentor)

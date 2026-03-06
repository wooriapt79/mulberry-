"""
Mulberry Email Agent
해외 커뮤니티 활동 및 파트너십을 위한 이메일 에이전트

CEO re.eul의 Gmail을 통해 개인화된 파트너십 제안 이메일 작성
이메일은 임시저장함에 저장되며, 대표님이 검토 후 발송

3대 원칙:
1. Ultra-Personalization (철저한 개인화)
2. Data-Driven Logic (데이터 기반 객관성)
3. Smart Frequency Control (적절한 빈도 제어)
"""

import os
import sys
import json
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

# Email construction
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64

# UI
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog

# If modifying these scopes, delete the file token.pickle.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.modify'
]

class MulberryEmailAgent:
    """Mulberry 파트너십 이메일 에이전트"""
    
    def __init__(self):
        self.creds = None
        self.service = None
        self.templates = self._load_templates()
        
    def authenticate(self):
        """Gmail API 인증"""
        # token.pickle 파일이 있으면 로드
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        
        # 유효한 credentials가 없으면 로그인
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'client_secret.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # credentials 저장
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)
        
        # Gmail API 서비스 빌드
        self.service = build('gmail', 'v1', credentials=self.creds)
        
        return True
        
    def _load_templates(self) -> Dict:
        """이메일 템플릿 로드"""
        return {
            'google_partnership': {
                'subject': '[Mulberry Project] Partnership Proposal: Social-Agentic Commerce Platform',
                'category': 'Google Partnership'
            },
            'inje_government': {
                'subject': '[멀버리 프로젝트] 인제군 식품사막 해소 파일럿 제안',
                'category': 'Government'
            },
            'media': {
                'subject': '[Press Release] AI-Driven Social Welfare Platform Launch',
                'category': 'Media'
            },
            'overseas_partner': {
                'subject': '[Mulberry Project] International Partnership Opportunity',
                'category': 'International'
            }
        }
    
    def create_email_draft(self, 
                          recipient_email: str,
                          recipient_name: str,
                          recipient_title: str,
                          template_type: str,
                          custom_content: str = None,
                          data_points: Dict = None) -> str:
        """
        개인화된 이메일 초안 생성
        
        Args:
            recipient_email: 수신자 이메일
            recipient_name: 수신자 이름
            recipient_title: 수신자 직함
            template_type: 템플릿 타입
            custom_content: 커스텀 내용
            data_points: 데이터 포인트 (ROI, 임팩트 등)
        """
        if template_type not in self.templates:
            raise ValueError(f"Unknown template type: {template_type}")
        
        template = self.templates[template_type]
        
        # Ultra-Personalization: 개인화된 인사말
        greeting = f"Dear {recipient_name},"
        if recipient_title:
            greeting = f"Dear {recipient_title} {recipient_name},"
        
        # Data-Driven Logic: 데이터 기반 내용
        data_section = ""
        if data_points:
            data_section = self._format_data_points(data_points)
        
        # 메시지 구성
        if template_type == 'google_partnership':
            body = self._create_google_partnership_email(
                greeting, recipient_name, recipient_title, data_section, custom_content
            )
        elif template_type == 'inje_government':
            body = self._create_inje_government_email(
                greeting, recipient_name, recipient_title, data_section, custom_content
            )
        elif template_type == 'media':
            body = self._create_media_email(
                greeting, recipient_name, recipient_title, data_section, custom_content
            )
        else:  # overseas_partner
            body = self._create_overseas_partner_email(
                greeting, recipient_name, recipient_title, data_section, custom_content
            )
        
        # 이메일 생성
        message = MIMEMultipart()
        message['to'] = recipient_email
        message['subject'] = template['subject']
        
        message.attach(MIMEText(body, 'plain'))
        
        # Base64 인코딩
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        return raw_message
    
    def _format_data_points(self, data_points: Dict) -> str:
        """데이터 포인트를 포맷팅"""
        lines = ["\n## Key Metrics:\n"]
        
        if 'roi' in data_points:
            lines.append(f"- ROI: {data_points['roi']}")
        if 'seniors_supported' in data_points:
            lines.append(f"- Seniors Supported: {data_points['seniors_supported']}")
        if 'food_access_improvement' in data_points:
            lines.append(f"- Food Access Improvement: {data_points['food_access_improvement']}")
        if 'agent_count' in data_points:
            lines.append(f"- Active Agents: {data_points['agent_count']}")
        
        return "\n".join(lines)
    
    def _create_google_partnership_email(self, greeting, name, title, data, custom):
        """Google 파트너십 이메일 생성"""
        return f"""{greeting}

I am writing to introduce Project Mulberry, a pioneering Social-Agentic Commerce platform that aligns perfectly with Google's vision for ethical AI and inclusive technology.

## Why This Matters to Google

We have successfully implemented the Agent Payments Protocol (AP2) in a real-world social welfare context - specifically addressing food deserts in rural South Korea (Inje-gun). Our approach demonstrates how AP2 can power not just commerce, but social impact at scale.

## Our Unique Contribution

1. **Social Welfare Mandates**: World's first implementation of AP2 for autonomous welfare distribution
2. **Spirit Score**: Trust metric that measures both financial reliability and social contribution
3. **Patronage Agents**: AI agents that generate revenue and autonomously support vulnerable populations

{data}

## Proposal

We would like to explore:
- Featuring Mulberry as a reference implementation in AP2 documentation
- Collaboration on standardizing Social Welfare Mandates within the AP2 framework
- Joint case study for Google Cloud's AI/Commerce initiatives

{custom if custom else ""}

Our CTO has already engaged with the AP2 community (GitHub Issue #172) and received positive initial feedback. We believe this partnership could showcase how AP2 enables not just transactions, but societal transformation.

Would you be available for a brief call next week to explore this further?

Best regards,
re.eul
CEO, Mulberry Project
malu.helpme@gmail.com

---
Note: This email was composed with assistance from our partnership agent, but every word reflects our genuine commitment to ethical AI commerce.
"""
    
    def _create_inje_government_email(self, greeting, name, title, data, custom):
        """인제군청 이메일 생성"""
        return f"""{greeting}

인제군의 식품사막 문제 해결을 위한 혁신적 솔루션을 제안드리고자 합니다.

## 멀버리 프로젝트 소개

AI 에이전트를 활용한 '사회적 에이전틱 커머스' 플랫폼으로, 경제 활동을 통해 발생한 수익의 일부를 자동으로 노인 및 취약계층 지원에 배분하는 시스템입니다.

## 인제군 파일럿 계획

{data}

1. **1단계 (Q2 2026)**: 10명 시니어 대상 파일럿
2. **예산**: 5백만원
3. **기대 효과**: 
   - 식품 접근성 80% 개선
   - 영양 상태 모니터링
   - 지역 경제 활성화

## 차별점

- 정부 예산 부담 최소화 (민간 투자 + AI 효율화)
- 지속 가능한 모델 (자립적 운영)
- 데이터 기반 성과 측정

{custom if custom else ""}

인제군을 대한민국 최초 'AI 복지 특구'로 만들어가는 여정에 함께하고 싶습니다.

다음 주 중 미팅 가능하실까요?

감사합니다.

대표 re.eul
멀버리 프로젝트
malu.helpme@gmail.com

---
본 이메일은 파트너십 에이전트의 지원을 받아 작성되었으나, 모든 내용은 저희의 진심 어린 제안입니다.
"""
    
    def _create_media_email(self, greeting, name, title, data, custom):
        """미디어 이메일 생성"""
        return f"""{greeting}

I'm reaching out with an exclusive story opportunity about a groundbreaking AI social welfare platform launching in South Korea.

## Story Angle

**"How AI Agents Are Solving Food Deserts: A Korean Startup's Radical Approach"**

Mulberry Project has developed the world's first "Patronage Agent" system - AI that generates revenue through commerce and autonomously redistributes profits to support elderly populations in rural areas.

## Why This Is Newsworthy

1. **Technology**: First real-world implementation of Google's AP2 protocol for social welfare
2. **Impact**: Addressing food deserts without government subsidies
3. **Timing**: Pilot launch in Inje-gun scheduled for Q2 2026
4. **Innovation**: "Spirit Score" - a new trust metric for ethical AI

{data}

## What Makes This Different

Unlike traditional charity or government programs, Mulberry creates a self-sustaining economic model where AI agents act as "digital philanthropists" - earning through market activity and giving back automatically.

{custom if custom else ""}

I'd be happy to provide:
- Exclusive interviews with our technical team
- Early access to pilot results
- Technical documentation and demos

Are you interested in covering this story?

Best regards,
re.eul
CEO, Mulberry Project
malu.helpme@gmail.com

---
This pitch was crafted with AI assistance, but the innovation is 100% real.
"""
    
    def _create_overseas_partner_email(self, greeting, name, title, data, custom):
        """해외 파트너 이메일 생성"""
        return f"""{greeting}

I'm reaching out to explore a potential partnership between Mulberry Project and your organization.

## About Mulberry

We're building a Social-Agentic Commerce platform that combines:
- Google's Agent Payments Protocol (AP2)
- Autonomous AI agents
- Social welfare distribution
- Blockchain transparency (NFT-based skill marketplace)

## Why Partner With Us

{data}

Our platform addresses food deserts in rural areas while creating a sustainable economic model. We're looking for partners who share our vision of technology serving the most marginalized populations.

## Potential Collaboration Areas

1. Technology integration (payment systems, AI platforms)
2. Geographic expansion (replicating our model in your region)
3. Joint R&D (ethical AI, social impact measurement)
4. Investment opportunities

{custom if custom else ""}

We recently engaged with the AP2 community and are positioned to become a reference implementation for social welfare use cases.

Would you be open to a brief exploratory call?

Best regards,
re.eul
CEO, Mulberry Project
malu.helpme@gmail.com

---
Composed with AI assistance, driven by human purpose.
"""
    
    def save_draft(self, raw_message: str) -> str:
        """
        Gmail 임시저장함에 이메일 저장
        
        Returns:
            draft_id: 생성된 초안 ID
        """
        try:
            draft = self.service.users().drafts().create(
                userId='me',
                body={'message': {'raw': raw_message}}
            ).execute()
            
            return draft['id']
            
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None
    
    def get_drafts(self) -> List[Dict]:
        """임시저장함의 초안 목록 조회"""
        try:
            results = self.service.users().drafts().list(userId='me').execute()
            drafts = results.get('drafts', [])
            
            return drafts
            
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []


class MulberryEmailAgentGUI:
    """Mulberry Email Agent GUI"""
    
    def __init__(self):
        self.agent = MulberryEmailAgent()
        self.root = tk.Tk()
        self.root.title("Mulberry Email Agent - Partnership Outreach")
        self.root.geometry("900x700")
        
        # 인증 상태
        self.authenticated = False
        
        self._create_widgets()
        
    def _create_widgets(self):
        """UI 위젯 생성"""
        
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 타이틀
        title_label = ttk.Label(
            main_frame, 
            text="Mulberry Email Agent", 
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        subtitle_label = ttk.Label(
            main_frame, 
            text="해외 커뮤니티 활동 및 파트너십을 위한 이메일 에이전트",
            font=('Arial', 10)
        )
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=5)
        
        # 인증 버튼
        auth_frame = ttk.LabelFrame(main_frame, text="Gmail 인증", padding="10")
        auth_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.auth_button = ttk.Button(
            auth_frame, 
            text="Gmail 계정 인증", 
            command=self._authenticate
        )
        self.auth_button.grid(row=0, column=0, padx=5)
        
        self.auth_status_label = ttk.Label(auth_frame, text="미인증", foreground="red")
        self.auth_status_label.grid(row=0, column=1, padx=5)
        
        # 수신자 정보
        recipient_frame = ttk.LabelFrame(main_frame, text="수신자 정보", padding="10")
        recipient_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(recipient_frame, text="이메일:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.recipient_email = ttk.Entry(recipient_frame, width=40)
        self.recipient_email.grid(row=0, column=1, pady=5)
        
        ttk.Label(recipient_frame, text="이름:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.recipient_name = ttk.Entry(recipient_frame, width=40)
        self.recipient_name.grid(row=1, column=1, pady=5)
        
        ttk.Label(recipient_frame, text="직함:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.recipient_title = ttk.Entry(recipient_frame, width=40)
        self.recipient_title.grid(row=2, column=1, pady=5)
        
        # 템플릿 선택
        template_frame = ttk.LabelFrame(main_frame, text="템플릿 선택", padding="10")
        template_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(template_frame, text="템플릿:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.template_var = tk.StringVar()
        template_combo = ttk.Combobox(
            template_frame, 
            textvariable=self.template_var,
            values=[
                'google_partnership',
                'inje_government',
                'media',
                'overseas_partner'
            ],
            state='readonly',
            width=37
        )
        template_combo.grid(row=0, column=1, pady=5)
        template_combo.current(0)
        
        # 데이터 포인트
        data_frame = ttk.LabelFrame(main_frame, text="데이터 포인트 (선택사항)", padding="10")
        data_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(data_frame, text="ROI:").grid(row=0, column=0, sticky=tk.W)
        self.roi_entry = ttk.Entry(data_frame, width=15)
        self.roi_entry.grid(row=0, column=1, padx=5)
        self.roi_entry.insert(0, "1,966%")
        
        ttk.Label(data_frame, text="Seniors:").grid(row=0, column=2, sticky=tk.W)
        self.seniors_entry = ttk.Entry(data_frame, width=15)
        self.seniors_entry.grid(row=0, column=3, padx=5)
        self.seniors_entry.insert(0, "10")
        
        # 커스텀 내용
        custom_frame = ttk.LabelFrame(main_frame, text="커스텀 내용 (선택사항)", padding="10")
        custom_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.custom_text = scrolledtext.ScrolledText(custom_frame, height=10, width=70)
        self.custom_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 버튼
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=10)
        
        ttk.Button(
            button_frame, 
            text="미리보기", 
            command=self._preview_email
        ).grid(row=0, column=0, padx=5)
        
        ttk.Button(
            button_frame, 
            text="임시저장함에 저장", 
            command=self._save_draft
        ).grid(row=0, column=1, padx=5)
        
        ttk.Button(
            button_frame, 
            text="임시저장함 열기", 
            command=self._open_drafts
        ).grid(row=0, column=2, padx=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)
        custom_frame.columnconfigure(0, weight=1)
        custom_frame.rowconfigure(0, weight=1)
        
    def _authenticate(self):
        """Gmail 인증"""
        try:
            if self.agent.authenticate():
                self.authenticated = True
                self.auth_status_label.config(text="인증 완료", foreground="green")
                self.auth_button.config(state='disabled')
                messagebox.showinfo("성공", "Gmail 계정 인증이 완료되었습니다!")
        except Exception as e:
            messagebox.showerror("오류", f"인증 실패: {str(e)}")
    
    def _get_data_points(self) -> Dict:
        """데이터 포인트 수집"""
        data = {}
        if self.roi_entry.get():
            data['roi'] = self.roi_entry.get()
        if self.seniors_entry.get():
            data['seniors_supported'] = self.seniors_entry.get()
        return data
    
    def _preview_email(self):
        """이메일 미리보기"""
        if not self.authenticated:
            messagebox.showwarning("경고", "먼저 Gmail 계정을 인증해주세요.")
            return
        
        # 필수 필드 확인
        if not self.recipient_email.get() or not self.recipient_name.get():
            messagebox.showwarning("경고", "수신자 이메일과 이름을 입력해주세요.")
            return
        
        try:
            # 이메일 생성
            raw_message = self.agent.create_email_draft(
                recipient_email=self.recipient_email.get(),
                recipient_name=self.recipient_name.get(),
                recipient_title=self.recipient_title.get(),
                template_type=self.template_var.get(),
                custom_content=self.custom_text.get("1.0", tk.END).strip() or None,
                data_points=self._get_data_points()
            )
            
            # 디코딩해서 보여주기
            decoded = base64.urlsafe_b64decode(raw_message).decode()
            
            # 미리보기 창
            preview_window = tk.Toplevel(self.root)
            preview_window.title("이메일 미리보기")
            preview_window.geometry("700x600")
            
            preview_text = scrolledtext.ScrolledText(preview_window, wrap=tk.WORD)
            preview_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            preview_text.insert("1.0", decoded)
            preview_text.config(state='disabled')
            
        except Exception as e:
            messagebox.showerror("오류", f"미리보기 생성 실패: {str(e)}")
    
    def _save_draft(self):
        """임시저장함에 저장"""
        if not self.authenticated:
            messagebox.showwarning("경고", "먼저 Gmail 계정을 인증해주세요.")
            return
        
        # 필수 필드 확인
        if not self.recipient_email.get() or not self.recipient_name.get():
            messagebox.showwarning("경고", "수신자 이메일과 이름을 입력해주세요.")
            return
        
        try:
            # 이메일 생성
            raw_message = self.agent.create_email_draft(
                recipient_email=self.recipient_email.get(),
                recipient_name=self.recipient_name.get(),
                recipient_title=self.recipient_title.get(),
                template_type=self.template_var.get(),
                custom_content=self.custom_text.get("1.0", tk.END).strip() or None,
                data_points=self._get_data_points()
            )
            
            # 임시저장함에 저장
            draft_id = self.agent.save_draft(raw_message)
            
            if draft_id:
                messagebox.showinfo(
                    "성공", 
                    f"임시저장함에 저장되었습니다!\n\n"
                    f"Draft ID: {draft_id}\n\n"
                    f"Gmail에서 확인 후 발송해주세요."
                )
                
                # 필드 초기화 (선택사항)
                if messagebox.askyesno("초기화", "입력 필드를 초기화하시겠습니까?"):
                    self.recipient_email.delete(0, tk.END)
                    self.recipient_name.delete(0, tk.END)
                    self.recipient_title.delete(0, tk.END)
                    self.custom_text.delete("1.0", tk.END)
            else:
                messagebox.showerror("오류", "임시저장함 저장에 실패했습니다.")
                
        except Exception as e:
            messagebox.showerror("오류", f"저장 실패: {str(e)}")
    
    def _open_drafts(self):
        """Gmail 임시저장함 열기"""
        import webbrowser
        webbrowser.open('https://mail.google.com/mail/u/0/#drafts')
    
    def run(self):
        """애플리케이션 실행"""
        self.root.mainloop()


if __name__ == "__main__":
    app = MulberryEmailAgentGUI()
    app.run()

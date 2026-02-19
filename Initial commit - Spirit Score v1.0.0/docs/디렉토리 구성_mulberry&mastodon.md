### mulberry-project/  # 구조

├── README.md # 전체 프로젝트 소개
├── .gitignore # Git 무시 파일
│
├── spirit-score/ # Spirit Score 기본 시스템
│ ├── src/
│ │ ├── spirit_score_engine.py
│ │ ├── activity_tracker.py
│ │ ├── api.py
│ │ └── realtime_updates.py
│ ├── database/
│ │ └── db_schema.sql
│ ├── tests/
│ ├── docker-compose.yml
│ ├── Dockerfile
│ ├── requirements.txt
│ └── README.md
│
├── mastodon-bots/ # Mastodon Bot 시스템 ← 새로!
│ ├── bots/
│ │ ├── **init**.py
│ │ ├── ceo_bot.py
│ │ ├── pm_bot.py
│ │ └── spirit_bot.py
│ ├── mulberry_bot_system.py # 통합 시스템
│ ├── test_simple.py # 간단 테스트
│ ├── .env.example # 토큰 템플릿 (실제 토큰 제외!)
│ ├── requirements.txt # Mastodon.py, python-dotenv
│ └── README.md # Mastodon Bot 가이드
│
└── docs/ # 문서
 ├── INSTALL.md
 ├── Mastodon_협업시스템_전환제안서.md
 └── Spirit_Score_최종보고서.pdf

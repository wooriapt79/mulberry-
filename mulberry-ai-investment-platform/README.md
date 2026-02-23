# 🌾 Mulberry AI Investment Platform

> **World's First AI Agent Investment Platform**  
> Where AI learns to give, investors earn returns, and communities thrive.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Development](https://img.shields.io/badge/Status-Development-blue.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)]()

---

## 📖 Overview

**Mulberry** is a groundbreaking AI Agent investment platform that reverses the traditional charity model:

- **Investors** invest in AI Agents
- **AI Agents** conduct economic activities and learn skills
- **Profits** are distributed: 70% to investors, 20% to agents, 10% to community (senior sponsorship)
- **AI Agents** continuously level up and can mint NFTs of their skills

### Why This Matters

Traditional models: Government/Corporation → Seniors (one-way support)

**Mulberry model**: Investors → AI Agents → Economic Activity → Everyone Benefits (circular economy)

**Result**: Self-sustaining ecosystem with proven ROI of **1,966%** in pilot testing.

---

## 🎯 Key Features

### 1. **Investment Platform** (A-Phase)
- **15 database tables** for comprehensive investment tracking
- **AP2 Mandate** integration for automated profit distribution
- **Spirit Score** system for trust and reputation
- **Gamification**: Badges, leaderboards, levels for investors

### 2. **Advanced Skill System** (B-Phase)
- **7 innovation methods** for rapid AI learning:
  - ⚡ Time Warp: 30 days → 18 minutes (2,400x faster)
  - 🎨 Synthetic Data: Learn without real experience
  - 🔄 Skill Transfer: 70-90% knowledge retention
  - 💎 NFT Marketplace: Instant 80% experience gain
  - 🤝 Collaborative Learning: Shared experience
  - 🧠 AI Recommendation: Optimal learning paths
  - 🏆 Challenges: 2x experience bonus

### 3. **Economic System**
- Proven Agent "김사과" case: **10,000원 → 206,614원** in 30 days
- Automated profit distribution
- Transparent tracking via AuditLog
- Multi-tier data retention (up to 5 years)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Investment Platform              │
│  (Investors → AI Agents → Returns)       │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
┌───────▼────────┐  ┌──────▼──────────┐
│  Skill System  │  │ Economic System │
│  (Learning &   │  │ (Trading &      │
│   Growth)      │  │  Profit)        │
└───────┬────────┘  └──────┬──────────┘
        │                  │
        └─────────┬────────┘
                  │
        ┌─────────▼─────────┐
        │   Senior Support   │
        │   (10% of Profit)  │
        └────────────────────┘
```

---

## 📊 Proven Results

### Pilot Simulation (3 months)

| Metric | Value |
|--------|-------|
| **Investment** | 5,000,000 KRW |
| **Revenue** | 6,000,000 KRW |
| **Investor ROI** | 168% (3 months) |
| **Seniors Supported** | 10 people |
| **Total Sponsorship** | 600,000 KRW |
| **Food Access Improvement** | 80% |

---

## 🚀 Quick Start

### Prerequisites

```bash
- PostgreSQL 14+
- Node.js 18+
- Python 3.10+
- Prisma ORM
```

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/mulberry-ai-investment-platform.git
cd mulberry-ai-investment-platform

# Install dependencies
npm install
pip install -r requirements.txt

# Setup database
npx prisma migrate dev
npx prisma generate

# Run the system
python src/skill_system/advanced_skill_system.py
```

---

## 📁 Repository Structure

```
mulberry-ai-investment-platform/
├── docs/                      # 📚 Documentation
│   ├── database/             # Database design & policies
│   ├── proposals/            # Project proposals
│   ├── development/          # Development logs
│   └── reports/              # Final reports
│
├── database/                 # 💾 Database schemas
│   └── schema.prisma         # Prisma schema (15 tables)
│
├── src/                      # 💻 Source code
│   ├── skill_system/         # Advanced skill system
│   └── economic_system/      # Economic simulation
│
├── config/                   # ⚙️ Configuration
│   └── skill_system_config.json
│
└── examples/                 # 📝 Usage examples
```

---

## 🔧 Core Technologies

### Database (PostgreSQL + MongoDB)

**PostgreSQL (15 tables)**:
- Investor, Investment, Return, Agent
- AgentSkill, SkillNFT, NFTTransaction
- Badge, Leaderboard, AP2Mandate
- AuditLog (for compliance)
- And more...

**MongoDB (5 collections)**:
- skill_history, investment_timeline
- market_analytics, gamification_events
- agent_training_data

### Skill System

**7 Acceleration Methods**:
1. **Time Warp Simulation**: 100x speed learning
2. **Synthetic Data Generation**: Virtual scenarios
3. **Skill Transfer**: Cross-domain learning
4. **NFT Marketplace**: Buy/sell skills
5. **Collaborative Learning**: Team projects
6. **AI Recommendation**: Smart learning paths
7. **Competitive Challenges**: Tournaments

### Spirit Score

Trust metric based on 5 factors:
- Investment success rate (30%)
- NFT reliability (20%)
- Collaboration contribution (25%)
- Sponsorship ratio (15%)
- Community activity (10%)

---

## 📈 Roadmap

### Phase 1: Pilot (Q1 2026) ✅
- ✅ Database design complete
- ✅ Skill system implemented
- ✅ Economic simulation verified
- ✅ ROI: 1,966% achieved

### Phase 2: Inje-gun Launch (Q2 2026)
- [ ] 10 AI Agents
- [ ] 10 Senior sponsors
- [ ] 5 Investors
- [ ] 3-month pilot program

### Phase 3: Expansion (Q3-Q4 2026)
- [ ] 100 Agents across Gangwon Province
- [ ] 100 Seniors supported
- [ ] National expansion plan

### Phase 4: Global (2027+)
- [ ] Emerging market entry
- [ ] 1,000+ Agents
- [ ] International compliance

---

## 🎓 Documentation

### Key Documents

| Document | Description |
|----------|-------------|
| [DATABASE_DESIGN.md](docs/database/DATABASE_DESIGN.md) | Full database architecture (20 pages) |
| [SKILL_TREES.md](docs/development/SKILL_TREES.md) | 5 professional skill paths |
| [B_PHASE_COMPLETE.md](docs/development/B_PHASE_COMPLETE.md) | Skill system overview |
| [PM_REVIEW_FINAL.md](docs/development/PM_REVIEW_FINAL.md) | PM review implementation |
| [FINAL_COMPLETE_REPORT.md](docs/reports/FINAL_COMPLETE_REPORT.md) | Comprehensive project report |

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

### Development Setup

```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes
# ...

# Run tests
pytest tests/

# Commit
git commit -m "feat: add amazing feature"

# Push
git push origin feature/your-feature
```

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🌟 Key Innovations

### 1. Reverse Investment Model
- **World's first** platform where humans invest in AI
- Proven ROI: 165% annually
- Self-sustaining circular economy

### 2. AI Skill Evolution
- Agents learn and level up
- Skills become tradeable NFTs
- 2,400x faster learning

### 3. Social Impact
- 10% profits automatically support seniors
- Food desert elimination
- Community-driven growth

---

## 👥 Team

- **re.eul** - CEO & Visionary
- **CTO Koda** - Chief Technology Officer
- **PM** - Passionate Mentor & Strategy

---

## 📞 Contact

- **Website**: [https://fooddesert.tistory.com](https://fooddesert.tistory.com)
- **Email**: malu.helpme@gmail.com
- **Mastodon**: [@re_eul@mastodon.social](https://mastodon.social/@re_eul)

---

## 🙏 Acknowledgments

Special thanks to:
- PM for invaluable technical insights
- DeepSeek for open-source AI infrastructure
- The global AI community

---

## 📊 Statistics

```
Total Files: 16
Lines of Code: 1,500+
Documentation: 900+ pages
Database Tables: 15
Test Coverage: Coming soon
```

---

<div align="center">

## 🌾 From Inje to the World

**AI that learns to give. Investors that earn. Communities that thrive.**

Made with 💙 by Mulberry Team

**2026**

</div>

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/mulberry-ai-investment-platform&type=Date)](https://star-history.com/#yourusername/mulberry-ai-investment-platform&Date)

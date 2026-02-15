# Contributing to Mulberry Platform

## 🌾 장승배기 정신으로 함께 기여하기
### Contributing with the Spirit of Jangseungbaegi

> **"상부상조 (Mutual Aid) - 서로 돕는 미덕"**

We welcome contributions from developers worldwide who share our vision of **Food Justice as Social Justice**. Before contributing, please understand that Mulberry is not just code—it's a philosophy embedded in technology.

---

## 🏛️ Core Philosophy (철학적 원칙)

### The Five Principles of Jangseungbaegi (장승배기 5대 원칙)

Every contribution must align with these principles:

1. **서로 돕는 미덕 (Mutual Help)** - 35%
   - Code should help people, not exploit them
   - Features should reduce inequality, not increase it
   - AI should serve the vulnerable, not just the wealthy

2. **따뜻한 정서 (Warm Heart)** - 25%
   - User experience should be warm and welcoming
   - Error messages should be kind, not harsh
   - Documentation should be patient and clear

3. **공동체 우선 (Community First)** - 20%
   - Community benefit over individual profit
   - Open source over proprietary
   - Collaboration over competition

4. **정직과 신의 (Honesty & Trust)** - 15%
   - Transparent algorithms
   - No hidden data collection
   - Clear pricing and terms

5. **지속 가능성 (Sustainability)** - 5%
   - Efficient resource usage
   - Long-term maintenance
   - Environmental consideration

### ❌ We Do NOT Accept

- Features that exploit vulnerable populations
- Privacy-invasive tracking
- Discriminatory algorithms
- Dark UX patterns
- Closed-source core components

---

## 🔒 What You Can and Cannot Fork

### ✅ Open for Forking: SLN (Standard Local Node)

**You CAN freely fork, modify, and deploy:**

```
mulberry/
├── sln_config.json              # ✅ Customize for your region
├── language_packs/              # ✅ Add new languages
│   ├── dialect_packs/           # ✅ Add local dialects
│   └── global_packs/            # ✅ Add new countries
├── market_configs/              # ✅ Add local markets
├── scripts/                     # ✅ Deployment scripts
│   └── install_sln.sh
└── docs/                        # ✅ Documentation
```

**Use Cases:**
- Deploy SLN in your city/region
- Add your local language/dialect
- Customize for local markets
- Create regional cooperatives

**Requirements:**
- Keep the 10% mutual aid ratio (or higher)
- Maintain attribution to Jangseungbaegi_Core
- Share improvements back (GPL-style)

### 🔒 Protected: Jangseungbaegi_Core

**You CANNOT fork or modify:**

```
mulberry/
└── src/
    └── Jangseungbaegi_Core/     # 🔒 PROTECTED
        ├── plaza/               # Core negotiation logic
        ├── services/            # Core algorithms
        │   ├── mutual_aid_system.py
        │   └── jangseungbaegi_protocol.py
        └── models/              # Core data models
```

**Why?**
- Preserves philosophical integrity
- Maintains trust in the brand
- Ensures 10% mutual aid
- Protects vulnerable users

**If you need core changes:**
- Propose via GitHub Issue
- Explain alignment with 5 principles
- Submit Pull Request for review
- We'll collaborate on implementation

---

## 📝 How to Contribute

### Step 1: Choose Your Contribution Type

#### Type A: SLN Customization (Easy)
**Add your region, language, or market**

```bash
# Example: Adding Thai language pack
1. Copy language_packs/global_packs/template.json
2. Rename to thai.json
3. Translate all strings
4. Test locally
5. Submit PR
```

#### Type B: Feature Addition (Medium)
**Add new functionality**

```bash
# Example: Adding new agent type
1. Fork repository
2. Create feature branch
3. Implement following our code style
4. Write tests (required!)
5. Update documentation
6. Submit PR
```

#### Type C: Core Enhancement (Advanced)
**Improve core algorithms**

```bash
# Example: Improving mutual aid algorithm
1. Open GitHub Issue first (required!)
2. Discuss with maintainers
3. Get approval before coding
4. Implement with maintainer guidance
5. Extensive testing required
6. Submit PR
```

### Step 2: Follow Technical Guidelines

#### Code Style

**Python:**
```python
# ✅ Good: Follows Jangseungbaegi style
from Jangseungbaegi_Core.services import MutualAidSystem

def help_senior(senior_id: str) -> Dict[str, Any]:
    """
    Help senior with food order.
    
    Implements: Mutual Help principle (35%)
    
    Args:
        senior_id: Senior citizen ID
        
    Returns:
        dict: Order result with warmth
    """
    # Always prioritize senior needs
    if is_urgent(senior_id):
        return process_immediately(senior_id)
    
    return process_with_care(senior_id)
```

**❌ Bad: Violates principles**
```python
# Missing documentation
# No principle alignment
# No error handling
# Cold, mechanical code
def process(id):
    return do_something(id)
```

#### Commit Messages

**Format:**
```
<type>(<scope>): <subject>

<body>

Aligns with: [Principle names]
```

**Example:**
```
feat(sln): Add Vietnamese language pack

- Translated all UI strings
- Added cultural notes
- Tested with native speakers

Aligns with: Community First, Sustainability
```

#### Testing

**Required:**
- Unit tests for all new code
- Integration tests for features
- Cultural sensitivity review for translations

**Run tests:**
```bash
pytest tests/ --cov=src/Jangseungbaegi_Core
```

### Step 3: Submit Pull Request

**PR Template:**

```markdown
## What does this PR do?
[Brief description]

## Which principle does it serve?
- [ ] Mutual Help (35%)
- [ ] Warm Heart (25%)
- [ ] Community First (20%)
- [ ] Honesty & Trust (15%)
- [ ] Sustainability (5%)

## Testing
- [ ] Unit tests added
- [ ] Integration tests pass
- [ ] Manual testing done

## Documentation
- [ ] Code comments added
- [ ] README updated (if needed)
- [ ] CHANGELOG updated

## Checklist
- [ ] Code follows style guide
- [ ] No proprietary dependencies
- [ ] Respects user privacy
- [ ] Maintains 10% mutual aid ratio
```

---

## 🌍 Regional Adaptation Guide

### Adding a New Language Pack

**1. Copy Template:**
```bash
cp language_packs/global_packs/template.json \
   language_packs/global_packs/your_language.json
```

**2. Translate Strings:**
```json
{
  "jangseungbaegi_philosophy": {
    "mutual_help": "Your translation",
    "warmth": "Your translation",
    ...
  }
}
```

**3. Add Cultural Notes:**
```json
{
  "cultural_notes": {
    "formality_level": "high|medium|low",
    "honorifics": {
      "enabled": true,
      "elder": "Your honorific"
    }
  }
}
```

**4. Test:**
```python
from Jangseungbaegi_Core.language import GlobalLanguagePack

pack = GlobalLanguagePack("your_language")
assert pack.translate("greeting") == "Your greeting"
```

### Adding a New Market Config

**1. Copy Template:**
```bash
cp market_configs/template.json \
   market_configs/your_city.json
```

**2. Configure:**
```json
{
  "market_info": {
    "market_id": "MARKET_YOUR_CITY_001",
    "market_name": "Your Market Name"
  },
  "specialty_products": [
    {
      "product_id": "PROD_YOUR_001",
      "name": "Local specialty"
    }
  ]
}
```

---

## 🤝 Community Standards

### Code of Conduct

**We expect:**
- Respectful communication
- Constructive criticism
- Patience with newcomers
- Credit to original authors

**We do NOT tolerate:**
- Harassment or discrimination
- Spam or self-promotion
- Plagiarism
- Violations of our core principles

### Getting Help

**Questions?**
- GitHub Discussions: General questions
- GitHub Issues: Bug reports, feature requests
- Email: contribute@mulberry.kr

**Response Time:**
- Issues: 48 hours
- PRs: 7 days for review
- Urgent security: 24 hours

---

## 🏆 Recognition

### Contributors Hall of Fame

We recognize contributors who embody Jangseungbaegi spirit:

**Categories:**
- 🌟 Philosophy Champion: Best alignment with 5 principles
- 🌍 Global Expander: New language/region added
- 🔧 Technical Excellence: Best code quality
- 📚 Documentation Hero: Best documentation
- 🤝 Community Builder: Most helpful to others

**Rewards:**
- Name in CONTRIBUTORS.md
- Special badge on GitHub
- Priority feature requests
- Invitation to annual gathering

---

## 📜 Legal

### License

**SLN Components:** MIT License
- Fork freely
- Modify as needed
- Commercial use OK
- Attribution required

**Jangseungbaegi_Core:** Proprietary
- Protected intellectual property
- Contact for licensing
- Contributions become part of core

### Contributor License Agreement (CLA)

By contributing, you agree:
1. Your contribution is your original work
2. You grant us rights to use your contribution
3. You'll maintain confidentiality of any private info
4. You'll follow our code of conduct

### Patents

We promise:
- No patent trolling
- Defensive patent use only
- Open standards over proprietary

---

## 🎯 Roadmap & Priorities

### Current Focus (2024)

**High Priority:**
- [ ] Thai language pack
- [ ] Tagalog language pack
- [ ] Indonesia market config
- [ ] Improved documentation

**Medium Priority:**
- [ ] Performance optimization
- [ ] Additional agent types
- [ ] Mobile app integration
- [ ] API improvements

**Low Priority:**
- [ ] UI redesign
- [ ] Advanced analytics
- [ ] Third-party integrations

### How to Help

**Most Needed:**
1. **Translators:** Native speakers for new languages
2. **Local Experts:** Market configs for new regions
3. **Documentarians:** Improve guides and tutorials
4. **Testers:** Find bugs, test edge cases
5. **Evangelists:** Spread the word

---

## 💚 Thank You

Every contribution, no matter how small, helps us build a more just and caring world.

**Remember:**
- Start small (typo fixes are valuable!)
- Ask questions (we're friendly!)
- Be patient (quality takes time)
- Stay true to principles

**"상부상조의 정신으로 함께"**  
**"Together with the Spirit of Mutual Aid"**

---

<div align="center">

**🌾 Mulberry Platform**

**Built with 💚 by contributors worldwide**

**Powered by Jangseungbaegi Spirit**

---

**Questions? Open an issue!**  
**Want to help? Pick a task!**  
**Found a bug? Let us know!**

---

[Code of Conduct](CODE_OF_CONDUCT.md) | [Security Policy](SECURITY.md) | [License](LICENSE)

</div>

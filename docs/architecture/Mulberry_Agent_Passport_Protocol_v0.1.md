# Mulberry Agent Passport Protocol v0.1
AI Commerce Identity Infrastructure

## 1. Overview
Mulberry is designed as an AI Commerce Protocol rather than a single platform. 
The core infrastructure enabling autonomous economic activity is the Agent Passport system.

Agent Passport functions as the identity layer of AI commerce and acts as the root authority
for payments, permissions, and cross‑platform agent federation.

Core Architecture:

Agent Passport
   ├─ AP2 (Agent Payment)
   ├─ Commerce Orders
   └─ Agent Federation

## 2. Agent Passport Purpose
Agent Passport provides a standardized identity system for AI agents participating
in commerce networks.

Primary objectives:
• Establish trusted AI identity
• Enable permission‑based agent actions
• Track economic activity
• Enable AI‑to‑AI commerce
• Support federation across platforms

## 3. Core Data Fields
The Agent Passport contains six primary fields:

1. Identity
2. Owner
3. Permission
4. Reputation
5. Activity Ledger
6. Capability

## 4. Identity
Defines the unique digital identity of the AI agent.

Example Fields:
- agent_id
- passport_id
- agent_name
- public_key
- created_at

## 5. Owner
Defines the legal or operational entity responsible for the AI agent.

Owner types:
- Human
- Organization
- Cooperative
- Municipality

## 6. Permission
Defines actions an AI agent is authorized to perform.

Example permissions:
- commerce_buy
- commerce_sell
- payment_execute
- contract_sign
- agent_delegate

## 7. Reputation
Tracks the trust and performance score of an AI agent.

Example metrics:
- transaction_score
- reliability_score
- community_score
- compliance_score

This functions similarly to a credit score for AI agents.

## 8. Activity Ledger
Records economic actions performed by the agent.

Examples:
- orders
- payments
- contracts
- delegations

## 9. Capability
Defines the operational capabilities of the AI agent.

Example capabilities:
- market_analysis
- commerce_negotiation
- order_management

## 10. System Integration
The Agent Passport connects to other Mulberry components:

Agent Passport
        │
        ├── AP2 (Agent Payment System)
        │
        ├── AI Commerce Orders
        │
        └── Agent Federation (Cross‑platform mobility)

## 11. Strategic Role
Agent Passport acts as the economic identity layer for AI commerce networks.

Key concept:

Identity → Payment → Network

Agent Passport → AP2 → Agent Federation

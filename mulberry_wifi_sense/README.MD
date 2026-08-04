# Mulberry WiFi Sense
## Privacy-first Spatial AI for Human Safety

> **Mulberry Spatial Safety System**
>
> Transforming WiFi signals into spatial intelligence through Edge AI,
> Human Approval, and Auditable Agent Collaboration.

---

# Vision

Mulberry WiFi Sense is an Edge AI project that utilizes WiFi Channel State
Information (CSI) to understand human presence, movement, and safety events
without relying on cameras.

Our vision is not simply to detect motion.

Our goal is to build a **Human-Centered Spatial Safety System**
where AI analyzes signals,
humans make final decisions,
and every action remains auditable.

---

# Why WiFi Sensing?

Traditional monitoring systems depend on cameras.

However, cameras introduce challenges including

- Privacy concerns
- Blind spots
- Low-light limitations
- Smoke and disaster environments
- Installation cost

Mulberry WiFi Sense explores an alternative approach.

Instead of recognizing images,

our AI interprets wireless signal changes.

This enables

- Human Presence Detection
- Motion Analysis
- Fall Suspicion Detection
- Indoor Spatial Awareness
- Privacy-preserving Safety Monitoring

---

# Project Philosophy

Mulberry WiFi Sense follows one simple principle.

> AI analyzes.
>
> Humans approve.
>
> Everything is recorded.

This philosophy is shared across every Mulberry project.

---

# System Architecture

```

ESP32 / WiFi AP
↓
CSI Collection
↓
Edge AI (Raspberry Pi)
↓
Motion / Fall Model
↓
Event Generation
↓
Mulberry Agent Gateway
↓
Human Approval
↓
AuditChainHead
↓
Digital Twin / Dashboard / External Systems

```

---

# Current MVP

Current repository provides an experimental simulation environment.

Included components

- CSI Reader
- CSI Collector
- Motion Detection
- Fall Detection
- Multi-modal Sensor
- Audio + CSI Fusion
- Privacy Controller
- Human Identifier (Research)
- LED Status
- Emergency Trigger Simulation

Current implementation is intended for

- Research
- Algorithm Validation
- UI Demonstration
- Edge AI Experiments

It is **NOT** intended for emergency response,
medical diagnosis,
or production deployment.

---

# Project Roadmap

## Phase 1

Simulation MVP

- CSI Simulation
- Motion Detection
- Fall Detection
- Privacy Control

---

## Phase 2

Real Hardware

- ESP32 CSI
- Raspberry Pi Edge
- Real-time CSI Pipeline

---

## Phase 3

Spatial Intelligence

- Indoor Position Estimation
- Multi-node Fusion
- Heat Map
- Digital Twin Integration

---

## Phase 4

Mulberry Spatial Safety Platform

- Agent Gateway
- Human Approval
- AuditChainHead
- Event Schema
- Smart City Integration

---

# Agent Formation

## KODA

Technical & Sensing Lead

Responsibilities

- CSI Collection
- Signal Processing
- AI Models
- Edge Optimization
- Performance Validation

---

## TRANG Manager

Validation & Scenario Lead

Responsibilities

- Scenario Design
- False Positive Analysis
- Timeline Reconstruction
- Pilot Planning
- Operational Validation

---

## Helix

Governance Lead

Responsibilities

- Human Approval
- AI Governance
- Privacy Policy
- Safety Rules
- Expansion Strategy

---

## KeBin

Audit & Integration

Responsibilities

- Event Schema
- AuditChainHead
- Gateway Integration
- Data Governance
- Traceability

---

## Luna

Human Interface

Responsibilities

- User Guidance
- Safety Communication
- Notification
- Human Interaction

---

# Future Integration

Mulberry WiFi Sense is designed to integrate with

- Mulberry Agent Gateway
- Raspberry Pi Edge Network
- Digital Twin Platforms
- Smart City Infrastructure
- Public Safety Systems
- Food Desert Monitoring
- AI Inje Initiative

The project is intentionally designed as an expandable platform,
not a standalone sensing application.

---

# Repository Structure

```

docs/
assets/
hardware/
demo/
models/
gateway/
events/
schemas/
tests/

```

---

# Privacy

Privacy is a core design principle.

The system is designed to minimize personal information processing.

Recommended deployment includes

- Human Approval
- Local Edge Processing
- Explicit User Consent
- Audit Logging
- Configurable Data Retention

---

# Disclaimer

This repository is an experimental research project.

Current implementation does **NOT**

- replace emergency responders
- replace medical professionals
- provide legally certified measurements

Human verification is always required.

---

# Mulberry Research Lab

Building Human-Centered Agent Ecosystems

AI analyzes.
Humans decide.
Everything is recorded.

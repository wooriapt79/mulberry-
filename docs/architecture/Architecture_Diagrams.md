# Mulberry Voice Protocol - Architecture Diagrams

## 1. Complete Revocation Flow

```mermaid
sequenceDiagram
    participant User as Sponsor/CSA
    participant Dashboard as Web Dashboard
    participant Cloud as Mandate Registry
    participant Twilio as Twilio Voice API
    participant PSTN as Phone Network
    participant Pi as Raspberry Pi (Edge)
    participant DB as Local SQLite

    User->>Dashboard: Click "Revoke Mandate"
    Dashboard->>Cloud: POST /api/mandates/{id}/revoke
    
    Note over Cloud: T+0.1s<br/>Update status to REVOKED
    
    Cloud->>Cloud: Generate DTMF command<br/>(with HMAC)
    Cloud->>Twilio: Place voice call
    
    Twilio->>PSTN: Dial Pi's number
    Note over PSTN: T+2-5s<br/>Call routing
    
    PSTN->>Pi: Incoming call
    Pi->>Pi: Auto-answer
    
    Twilio->>PSTN: Transmit DTMF tones<br/>*#01-12345678-9ABC##
    PSTN->>Pi: Audio (DTMF frequencies)
    
    Pi->>Pi: Decode DTMF
    Pi->>Pi: Verify HMAC
    
    alt HMAC Valid
        Pi->>DB: UPDATE mandates<br/>SET status='REVOKED'
        DB-->>Pi: Success
        
        Pi->>PSTN: TTS: "Mandate revoked"
        PSTN->>Twilio: Audio confirmation
        Twilio->>Cloud: Webhook: Success
        Cloud->>Dashboard: Update UI
        Dashboard->>User: ✅ Revocation confirmed
    else HMAC Invalid
        Pi->>Pi: Reject silently
        Pi->>PSTN: TTS: "Invalid command"
        PSTN->>Twilio: Audio error
        Twilio->>Cloud: Webhook: Failed
        Cloud->>Cloud: Schedule retry
    end
    
    Note over User,DB: Total Time: 8-15 seconds (typical)
```

## 2. System Architecture Overview

```mermaid
graph TB
    subgraph "Cloud Layer (GCP)"
        API[REST API]
        Registry[Mandate Registry<br/>PostgreSQL]
        Twilio[Twilio Integration]
        Webhook[Webhook Handler]
    end
    
    subgraph "Network Layer"
        Internet[Internet<br/>Data: 60% reliable]
        PSTN[PSTN Voice Network<br/>Voice: 95% reliable]
    end
    
    subgraph "Edge Layer (Inje-gun)"
        Pi[Raspberry Pi<br/>Python + Asterisk]
        Cache[SQLite Cache<br/>Mandates + Audit]
        Voice[Voice Interface<br/>DTMF + TTS]
    end
    
    subgraph "User Layer"
        Elder[Elderly User<br/>Basic Phone]
        Sponsor[Sponsor<br/>Web Dashboard]
    end
    
    Sponsor -->|HTTPS| API
    API -->|Write| Registry
    Registry -->|Trigger| Twilio
    Twilio -->|Voice Call| PSTN
    PSTN -->|Audio| Pi
    Pi -->|Query| Cache
    Pi -->|Update| Cache
    Pi <-->|Voice| Elder
    Pi -.->|Sync when online| Internet
    Internet -.->|API| Registry
    
    style Internet fill:#ffcccc
    style PSTN fill:#ccffcc
    style Pi fill:#cce5ff
```

## 3. Three-Layer Revocation Strategy

```mermaid
graph LR
    Revoke[Revoke<br/>Request]
    
    subgraph "Layer 1: IMMEDIATE"
        Online[Agent Online?]
        API[API Push<br/>&lt;10s]
    end
    
    subgraph "Layer 2: GRACE PERIOD"
        TimeCheck[Check Expiry]
        AutoExpire[Auto-Expire<br/>24-48h]
    end
    
    subgraph "Layer 3: VOICE FAILSAFE"
        Critical[Critical<br/>Revocation?]
        VoiceCall[Voice Call<br/>~3min]
    end
    
    Revoke --> Online
    Online -->|Yes| API
    Online -->|No| TimeCheck
    
    TimeCheck -->|Within validity| Critical
    TimeCheck -->|Expired| AutoExpire
    
    Critical -->|Yes| VoiceCall
    Critical -->|No| Wait[Wait for sync]
    
    API --> Success[Revoked]
    AutoExpire --> Success
    VoiceCall --> Success
    Wait -.-> API
    
    style API fill:#90EE90
    style AutoExpire fill:#FFD700
    style VoiceCall fill:#87CEEB
```

## 4. DTMF Command Structure

```mermaid
graph TD
    Start[DTMF Sequence]
    
    Prefix[Start Marker<br/>*#]
    Command[Command Code<br/>01 = REVOKE]
    Mandate[Mandate ID<br/>8 digits]
    HMAC[HMAC Token<br/>4 hex digits]
    Suffix[End Marker<br/>##]
    
    Start --> Prefix
    Prefix --> Command
    Command --> Mandate
    Mandate --> HMAC
    HMAC --> Suffix
    
    Suffix --> Parse[Parse & Verify]
    
    Parse -->|Valid| Execute[Execute Command]
    Parse -->|Invalid| Reject[Reject Silently]
    
    Execute --> Log[Audit Log]
    Reject --> SecurityLog[Security Alert]
    
    style Prefix fill:#E0E0E0
    style Suffix fill:#E0E0E0
    style HMAC fill:#FFB6C1
    style Execute fill:#90EE90
    style Reject fill:#FF6B6B
```

## 5. Security Layers

```mermaid
graph TB
    Incoming[Incoming Voice Call]
    
    subgraph "Layer 1: Caller ID"
        CallerCheck{Whitelisted<br/>Number?}
    end
    
    subgraph "Layer 2: DTMF Format"
        FormatCheck{Valid<br/>Format?}
    end
    
    subgraph "Layer 3: HMAC"
        HMACCheck{HMAC<br/>Valid?}
    end
    
    subgraph "Layer 4: Timing"
        TimingCheck{Within Time<br/>Window?}
    end
    
    subgraph "Layer 5: Business Logic"
        MandateCheck{Mandate<br/>Exists?}
    end
    
    Incoming --> CallerCheck
    CallerCheck -->|No| Reject1[Reject + Alert]
    CallerCheck -->|Yes| FormatCheck
    
    FormatCheck -->|No| Reject2[Reject]
    FormatCheck -->|Yes| HMACCheck
    
    HMACCheck -->|No| Reject3[Reject + Log]
    HMACCheck -->|Yes| TimingCheck
    
    TimingCheck -->|No| Reject4[Replay Attack]
    TimingCheck -->|Yes| MandateCheck
    
    MandateCheck -->|No| Reject5[Not Found]
    MandateCheck -->|Yes| Execute[Execute & Confirm]
    
    style Reject1 fill:#FF6B6B
    style Reject2 fill:#FF6B6B
    style Reject3 fill:#FF6B6B
    style Reject4 fill:#FF6B6B
    style Reject5 fill:#FF6B6B
    style Execute fill:#90EE90
```

## 6. Edge-Cloud Synchronization

```mermaid
stateDiagram-v2
    [*] --> Offline
    
    Offline --> OnlineCheck: Periodic Check
    OnlineCheck --> Online: Data Available
    OnlineCheck --> Offline: No Connection
    
    Online --> Sync: Start Sync
    Sync --> PullMandates: Download Updates
    PullMandates --> PushLogs: Upload Audit Logs
    PushLogs --> VoiceStandby: Sync Complete
    
    VoiceStandby --> VoiceRevoke: Incoming Call
    VoiceRevoke --> VoiceStandby: Processed
    
    VoiceStandby --> Offline: Connection Lost
    Online --> Offline: Timeout
    
    Offline --> VoiceOnly: Voice Call
    VoiceOnly --> Offline: Call Complete
    
    note right of VoiceOnly
        Voice works even
        when data is down!
    end note
    
    note right of Sync
        Opportunistic sync
        when connection available
    end note
```

## 7. Performance Comparison

```mermaid
graph LR
    subgraph "Data-Only Approach"
        D1[Revoke Request]
        D2[Wait for Connection]
        D3[API Call]
        D4[Success]
        
        D1 --> D2
        D2 -.->|30+ minutes| D3
        D3 --> D4
        
        D2 -.->|Often fails| Timeout[Timeout ❌]
    end
    
    subgraph "Voice Protocol"
        V1[Revoke Request]
        V2[Voice Call]
        V3[DTMF]
        V4[Success]
        
        V1 --> V2
        V2 -->|~15 seconds| V3
        V3 --> V4
    end
    
    Compare[Comparison:<br/>120x faster<br/>1.6x more reliable]
    
    style D2 fill:#FFB6C1
    style Timeout fill:#FF6B6B
    style V2 fill:#90EE90
    style V4 fill:#90EE90
```

## 8. Deployment Architecture

```mermaid
graph TB
    subgraph "Cloud Infrastructure (GCP)"
        LB[Load Balancer]
        API1[API Server 1]
        API2[API Server 2]
        DB[(PostgreSQL<br/>Mandate Registry)]
        Redis[(Redis<br/>Cache)]
        Queue[RabbitMQ<br/>Job Queue]
    end
    
    subgraph "Twilio"
        TwilioAPI[Voice API]
        TwilioNum[Phone Numbers]
    end
    
    subgraph "PSTN Network"
        Carrier[Telecom Carrier<br/>SK Telecom]
    end
    
    subgraph "Edge Site (Inje-gun)"
        Pi1[Pi Terminal 1]
        Pi2[Pi Terminal 2]
        PiN[Pi Terminal N]
    end
    
    LB --> API1
    LB --> API2
    API1 --> DB
    API2 --> DB
    API1 --> Redis
    API2 --> Redis
    API1 --> Queue
    API2 --> Queue
    
    Queue --> TwilioAPI
    TwilioAPI --> TwilioNum
    TwilioNum --> Carrier
    
    Carrier --> Pi1
    Carrier --> Pi2
    Carrier --> PiN
    
    style DB fill:#4A90E2
    style Redis fill:#FF6B6B
    style Queue fill:#F5A623
    style Carrier fill:#7ED321
```

## 9. Failure Recovery Flow

```mermaid
flowchart TD
    Start[Voice Call Initiated]
    
    Call{Call<br/>Answered?}
    
    Start --> Call
    
    Call -->|No| Wait1[Wait 30s]
    Wait1 --> Retry1{Retry<br/>Count < 3?}
    Retry1 -->|Yes| Start
    Retry1 -->|No| Escalate[Escalate to Human]
    
    Call -->|Yes| DTMF[Transmit DTMF]
    
    DTMF --> Decode{Decoded<br/>Successfully?}
    
    Decode -->|No| Wait2[Wait 5s]
    Wait2 --> DTMF
    
    Decode -->|Yes| Verify{HMAC<br/>Valid?}
    
    Verify -->|No| Log[Security Log]
    Log --> Retry2[New HMAC]
    Retry2 --> Start
    
    Verify -->|Yes| Execute[Execute Command]
    
    Execute --> Confirm{Confirmation<br/>Received?}
    
    Confirm -->|Yes| Success[✅ Success]
    Confirm -->|No| Retry3[Retry Confirmation]
    Retry3 --> Confirm
    
    Escalate --> Human[Human Operator Call]
    Human --> Manual[Manual Verification]
    
    style Success fill:#90EE90
    style Escalate fill:#FFB6C1
    style Log fill:#FF6B6B
```

---

## Usage Notes

These diagrams are in Mermaid format and can be rendered on:
- GitHub (natively supported)
- Mermaid Live Editor (https://mermaid.live)
- VS Code with Mermaid extension
- GitBook, Notion, Confluence (with plugins)

## Quick Start

1. Copy any diagram code block
2. Paste into Mermaid Live Editor
3. Export as PNG/SVG for presentations
4. Or embed directly in Markdown (GitHub renders automatically)

## Customization

To modify colors, add at the end of any diagram:
```
style NodeName fill:#HEXCOLOR
```

To add notes:
```
note right of NodeName
    Your note here
end note
```

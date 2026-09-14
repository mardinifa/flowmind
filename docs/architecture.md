# FlowMind System Architecture

## Overview

FlowMind is a human-in-the-loop loan-processing prototype for ClearPath
Capital. It separates document intake, business rules, qualitative risk,
decision routing, generated communication and human review into testable
components.

## Logical Flow

```mermaid
flowchart TD
    A[Application form or API] --> B[FastAPI]
    B --> C[PDF intake and validation]
    C --> D[Eligibility engine]
    D --> E[Risk and fraud assessment]
    E --> F{Decision router}
    F -->|Clear eligible and low risk| G[Conditional approval]
    F -->|Two or more clear failures| H[Decline notice]
    F -->|Uncertain, risky or contradictory| I[Human escalation]
    G --> J[Letter validator]
    H --> J
    J -->|Valid| K[Record autonomous action]
    J -->|Invalid| I
    I --> L[Streamlit officer dashboard]
    L --> M[Human decision]
    K --> N[SQLite or Supabase audit store]
    M --> N
```

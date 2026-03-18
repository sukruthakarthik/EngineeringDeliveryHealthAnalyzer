Your team's challenge is:

# Use Case: Engineering Delivery Health Analyzer
## Problem Statement
Engineering teams manage hundreds of tasks, bugs, and feature requests across sprints. Without analytics, it becomes difficult to identify delivery risks or bottlenecks.

## Objective
Create a dashboard that analyzes engineering work items and identifies delivery health indicators.

## Input Data
Example dataset:

issue_id | status | priority | days_open
JIRA-101 | Open | High | 10
JIRA-102 | In Progress | Medium | 5
JIRA-103 | Blocked | Critical | 12

## Possible sources:
• Sprint backlog data
• Issue tracking data
• Work item status

## Expected Output
• Delivery health score
• Bottleneck detection
• RAG status visualization
• Workload distribution insights


## Suggested Architecture
Issue Dataset
      ↓
Delivery Analytics Engine
      ↓
Risk Assessment Logic
      ↓
Health Scoring Model
      ↓
Engineering Dashboard

## Demo Idea
Dashboard showing delivery risk and blocked tasks.
Teams are free to choose their technology stack.
Teams are encouraged to make reasonable assumptions where details are not explicitly defined.
Please document assumptions clearly and proceed with implementation.

## CODATHON GUIDELINES
• Focus on building a working prototype rather than a production-grade system.
• Teams are encouraged to use GitHub Copilot extensively during development.
• Mock datasets are acceptable.
• Teams are free to choose their technology stack.
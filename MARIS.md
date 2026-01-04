# 🤖 Multi-Agent Resume Intelligence System (MARIS)

## Overview

MARIS is a collaborative AI system where multiple specialized agents reason, communicate, and verify each other's outputs. This architecture demonstrates advanced AI system design with task decomposition, orchestration, and trust mechanisms.

## 🏗️ Architecture

### Agent Communication Flow

```
User Input (Resume + Job)
        ↓
🧠 Resume Parser Agent
        ↓
📄 Job Analyzer Agent
        ↓
📊 Match Scoring Agent
        ↓
🔍 Skill Gap Agent
        ↓
🧪 Verification Agent
        ↓
Final Output (Score + Explanation + Confidence)
```

## 🤖 Agent Roles

### 1. Resume Parser Agent (`ResumeParser`)
**Responsibility**: Extract structured information from resumes
- Skills, tools, experience years
- Education level
- Job titles
- Experience keywords

**Tech**: spaCy NER, Rule-based extraction, JSON schema output

**Output**:
```json
{
  "skills": ["python", "javascript"],
  "experience_years": 5.0,
  "education_level": "Masters",
  "job_titles": ["Software Engineer"]
}
```

### 2. Job Requirement Analyzer Agent (`JobAnalyzer`)
**Responsibility**: Identify required vs preferred skills
- Categorize skills (required/preferred)
- Extract experience requirements
- Identify education requirements
- Determine role level

**Tech**: LLM-style analysis, Skill ontology mapping

**Output**:
```json
{
  "required_skills": ["python", "sql"],
  "preferred_skills": ["docker", "aws"],
  "experience_required": 3.0,
  "role_level": "Senior"
}
```

### 3. Match Scoring Agent (`MatchScoring`)
**Responsibility**: Compute fit score
- Weight different components
- Aggregate signals from other agents
- Compute semantic similarity

**Tech**: Embeddings, Cosine similarity, Ensemble scoring

**Output**:
```json
{
  "overall_score": 78.5,
  "section_scores": {
    "skills": 82.0,
    "experience": 75.0
  }
}
```

### 4. Skill Gap & Recommendation Agent (`SkillGap`)
**Responsibility**: Identify missing skills and suggest learning paths
- Missing required vs preferred skills
- Learning path generation
- Priority ranking

**Tech**: Skill knowledge graph, Graph traversal

**Output**:
```json
{
  "missing_required_skills": ["kubernetes"],
  "skill_coverage": 85.0,
  "learning_path": [...]
}
```

### 5. Verification & Bias Agent (`Verification`) ⭐ KEY INNOVATION
**Responsibility**: Validate and stress-test outputs
- Re-run scoring with perturbations
- Measure score stability
- Flag uncertain outputs
- Self-consistency checks

**Tech**: Perturbation testing, Self-consistency checks, Confidence scoring

**Output**:
```json
{
  "final_score": 78,
  "confidence_level": "High",
  "stability_index": 0.91,
  "warnings": []
}
```

## 📡 Communication Protocol

Agents communicate via structured JSON messages:

```python
@dataclass
class AgentMessage:
    agent: str              # Agent identifier
    output: Dict           # Structured output
    confidence: float       # 0.0 - 1.0
    reasoning: str         # Explanation
    evidence: List[str]    # Supporting evidence
```

## 🎯 Key Features

### 1. Task Decomposition
Each agent has a specialized role, making the system modular and maintainable.

### 2. Structured Communication
Agents communicate via JSON schemas, not raw text, ensuring reliability.

### 3. Verification & Trust
The Verification Agent provides:
- **Stability Index**: Score consistency across perturbations
- **Confidence Levels**: High/Medium/Low
- **Warnings**: Flags for uncertain outputs

### 4. Explainability
Each agent provides:
- Reasoning summaries
- Evidence used
- Confidence scores

### 5. Orchestration
The `AgentOrchestrator` coordinates:
- Agent execution order
- Data flow between agents
- Result aggregation
- Performance metrics

## 📊 Evaluation Metrics

| Metric | Meaning |
|--------|---------|
| Stability Index | Score consistency (0-1) |
| Agent Agreement Rate | Consensus between agents |
| Latency per Agent | System efficiency |
| Extraction Precision | NLP quality |
| Confidence Level | Overall trust in results |

## 🚀 Usage

### Basic Usage

```python
from src.agents.orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator()
results = orchestrator.run_pipeline(resume_text, job_text)

# Access results
match_score = results['match_score']
verification = results['verification']
agent_messages = results['agent_messages']
```

### With Matcher (Automatic)

```python
from src.matcher import ResumeJobMatcher

# Multi-agent is enabled by default
matcher = ResumeJobMatcher(use_multi_agent=True)
results = matcher.match(resume_text, job_text)

# Access multi-agent data
if 'multi_agent' in results:
    agent_reasoning = results['multi_agent']['agent_reasoning']
    verification = results['multi_agent']['verification']
```

## 🔬 Verification Agent Details

The Verification Agent performs:

1. **Stability Testing**:
   - Reorders resume sections
   - Compresses whitespace
   - Measures score variance

2. **Self-Consistency Checks**:
   - Validates score aligns with skill match ratio
   - Checks for logical consistency

3. **Confidence Assessment**:
   - High: Stability > 0.8, Consistent
   - Medium: Stability 0.6-0.8
   - Low: Stability < 0.6 or inconsistent

## 📈 Benefits Over Single-Agent System

1. **Modularity**: Each agent can be improved independently
2. **Reliability**: Verification agent catches errors
3. **Explainability**: Each agent explains its reasoning
4. **Scalability**: Easy to add new agents
5. **Trust**: Stability and confidence metrics

## 🎓 Resume-Worthy Highlights

This project demonstrates:
- ✅ Multi-agent AI systems
- ✅ Task decomposition & orchestration
- ✅ LLM tool usage patterns
- ✅ Explainable reasoning
- ✅ System-level AI architecture
- ✅ Trust & verification mechanisms

## 📝 Technical Stack

- **Language**: Python
- **Orchestration**: Custom controller
- **NLP**: spaCy
- **Embeddings**: Sentence-Transformers
- **Communication**: JSON message protocol
- **Verification**: Perturbation testing

---

**Built with ❤️ - Advanced Multi-Agent AI Architecture**

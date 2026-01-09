# 🎯 Supervisor Pattern - Documentation

## Qu'est-ce que le Supervisor Pattern ?

Le **Supervisor Pattern** est un pattern d'orchestration multi-agents où un agent "superviseur" intelligent décide quel agent spécialisé doit traiter une requête utilisateur.

---

## 🏗️ Architecture

```
                    ┌─────────────┐
                    │   User      │
                    │   Request   │
                    └──────┬──────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  Supervisor  │ ◄── LLM décide intelligemment
                    │   (LLM)      │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │                         │
              ▼                         ▼
       ┌─────────────┐         ┌──────────────┐
       │ Data Agent  │         │Support Agent │
       │  (Tools)    │         │  (Chat)      │
       └─────────────┘         └──────────────┘
```

---

## 📊 Comparaison : Avant vs Après

### **❌ Avant (Routing Manuel)**

```python
def decision_node(state):
    if "order" in message or "ticket" in message:
        return "data_agent"
    else:
        return "support_agent"
```

**Problèmes** :
- ❌ Logique hardcodée
- ❌ Difficile à maintenir avec beaucoup d'agents
- ❌ Pas d'apprentissage ou d'adaptation
- ❌ Keywords limités

### **✅ Après (Supervisor LLM-based)**

```python
supervisor = create_supervisor_node(["data_agent", "support_agent"])
# Le LLM analyse le contexte complet et décide intelligemment
```

**Avantages** :
- ✅ Décision intelligente basée sur le contexte
- ✅ Facile d'ajouter de nouveaux agents (juste config)
- ✅ Comprend les nuances du langage naturel
- ✅ Adaptable via prompt engineering

---

## 🚀 Comment ça fonctionne

### 1. **Le Supervisor reçoit la requête**
```python
user_input = "What's the status of order #123?"
```

### 2. **Le Supervisor analyse avec un LLM**
```python
system_prompt = """
Available agents:
- data_agent: Handles order status, ticket lookups
- support_agent: Handles general questions

Which agent should handle this request?
"""

# LLM response: "data_agent"
```

### 3. **Routing intelligent**
```python
state["next_step"] = "data_agent"  # Décidé par le LLM
```

### 4. **L'agent spécialisé traite**
```python
# data_agent exécute check_order_status(123)
```

---

## 🎯 Cas d'Usage

| Requête Utilisateur | Supervisor Décide | Agent Appelé |
|---------------------|-------------------|--------------|
| "Check order #456" | → data_agent | ✅ Data Agent |
| "I need help understanding my bill" | → support_agent | ✅ Support Agent |
| "What's ticket 789 about?" | → data_agent | ✅ Data Agent |
| "How does shipping work?" | → support_agent | ✅ Support Agent |
| "Show me my recent orders" | → data_agent | ✅ Data Agent |

---

## 📝 Configuration

### Définir les Agents Disponibles

```python
# ai/supervisor.py
CURRENT_AGENTS = [
    {
        "key": "data_agent",
        "name": "Data Retrieval Agent",
        "description": "Checks order status, retrieves ticket information"
    },
    {
        "key": "support_agent",
        "name": "Customer Support Agent",
        "description": "Provides general support and answers questions"
    }
]
```

### Utiliser dans le Graph

```python
# ai/graph.py
from .supervisor import create_supervisor_node

supervisor = create_supervisor_node(["data_agent", "support_agent"])
workflow.add_node("supervisor", supervisor)
workflow.add_edge(START, "supervisor")
```

---

## 🔧 Personnalisation

### Changer le Prompt du Supervisor

Modifier le system prompt dans `ai/supervisor.py` :

```python
system_prompt = f"""You are a supervisor managing specialized agents.

Available agents:
{agents_list}

CUSTOM RULES:
- Always route urgent requests to support_agent
- Route data queries to data_agent
- If unsure, default to support_agent

Respond with ONLY the agent name."""
```

### Ajouter un Nouvel Agent

```python
# 1. Créer le node function
def analytics_agent_node(state, config):
    # Logic here
    pass

# 2. Ajouter dans le graph
workflow.add_node("analytics_agent", analytics_agent_node)

# 3. Ajouter dans la liste du supervisor
supervisor = create_supervisor_node([
    "data_agent", 
    "support_agent", 
    "analytics_agent"  # ← Nouveau
])

# 4. Ajouter le routing
workflow.add_conditional_edges(
    "supervisor",
    route_from_supervisor,
    {
        "data_agent": "data_agent",
        "support_agent": "support_agent",
        "analytics_agent": "analytics_agent",  # ← Nouveau
        "end": END
    }
)
```

---

## 🎉 Avantages du Supervisor Pattern

### 1. **Scalabilité**
- Ajouter 10 agents = Juste config, pas de refactoring

### 2. **Intelligence**
- Le LLM comprend le contexte, pas juste des keywords

### 3. **Maintenance**
- Un seul point de routing (supervisor)
- Pas de if/else spaghetti code

### 4. **Flexibilité**
- Changer la logique = Changer le prompt
- Pas besoin de déploiement

### 5. **Observabilité**
- Les décisions du supervisor sont loggées
- Facile de débugger pourquoi un agent a été choisi

---

## 🔍 Debugging

### Voir les Décisions du Supervisor

```python
# Dans GraphExecutor.execute()
if node_name == "supervisor":
    decision = node_value["next_step"]
    logger.info(f"Supervisor decided: {decision}")
```

### Tester le Supervisor

```python
# Django shell
from ai.supervisor import create_supervisor_node
from ai.agents import AgentState
from langchain_core.messages import HumanMessage

supervisor = create_supervisor_node(["data_agent", "support_agent"])

state = {
    "messages": [HumanMessage(content="Check order 123")],
    "next_step": ""
}

result = supervisor(state, config={})
print(result["next_step"])  # → "data_agent"
```

---

## 📚 Références

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Multi-Agent Systems](https://python.langchain.com/docs/use_cases/multi_agent)
- Pattern inspiré de `archives/ai-demo/supervisors.py`

---

## ✅ Status

- ✅ Supervisor Pattern implémenté
- ✅ Intégré dans `ai/graph.py`
- ✅ Documentation complète
- 🔄 Prêt pour extension future

**Migration Status: ✅ COMPLETE**

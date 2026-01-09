# 🚀 Guide de Démarrage Rapide - Nouvelle Architecture

**Pour les développeurs rejoignant le projet après la migration**

---

## 📁 Nouvelle Structure

```
ai/
├── llms.py              # 🆕 Factory LLM centralisée
├── permissions.py       # 🆕 Système de permissions
├── tools/               # 🆕 Structure modulaire
│   ├── __init__.py
│   ├── order_tools.py   # Tools pour les commandes
│   ├── ticket_tools.py  # Tools pour les tickets
│   └── support_tools.py # Tools de support générique
├── services/
│   └── graph_executor.py  # 🔄 Propage user context
├── views.py             # 🔄 Extrait user_id
└── utils.py             # 🔄 Utilise llms.py
```

---

## 💡 Comment Ajouter un Nouveau Tool

### Étape 1: Créer le fichier
```python
# ai/tools/payment_tools.py
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from business.models import Payment
from ai.permissions import check_permission

@tool
def process_refund(order_id: int, amount: float, config: RunnableConfig = None) -> str:
    """Process a refund for an order."""
    # Extract user context
    user_id = None
    if config:
        user_id = config.get('configurable', {}).get('user_id')
    
    # Check permissions
    if not check_permission(user_id, "refund", "order"):
        return "You do not have permission to process refunds."
    
    # Business logic here
    return f"Refund of ${amount} processed for order {order_id}"

# Export
payment_tools = [process_refund]
```

### Étape 2: Exporter le module
```python
# ai/tools/__init__.py
from .payment_tools import payment_tools

__all__ = ['order_tools', 'ticket_tools', 'support_tools', 'payment_tools']
```

### Étape 3: Ajouter dans seed
```python
# ai/management/commands/seed_agents.py
tools = [
    # ...existing tools...
    {
        "key": "process_refund",
        "name": "Process Refund",
        "description": "Process a refund for an order",
        "python_path": "ai.tools.payment_tools.process_refund"
    }
]
```

### Étape 4: Lier à un agent
```python
# Dans seed_agents.py, section AgentTool
if "support_agent" in created_agents:
    support_agent = created_agents["support_agent"]
    refund_tool = created_tools["process_refund"]
    AgentTool.objects.create(
        agent=support_agent,
        tool=refund_tool,
        allowed=True
    )
```

---

## 🔐 Système de Permissions

### Utiliser les Permissions Existantes
```python
from ai.permissions import (
    check_user_can_access_order,
    check_user_can_access_ticket,
    check_permission,
    is_staff_user
)

# Check spécifique
if not check_user_can_access_order(user_id, order_id):
    return "Access denied"

# Check générique
if not check_permission(user_id, "delete", "order"):
    return "Access denied"

# Check staff
if not is_staff_user(user_id):
    return "Staff only"
```

### Ajouter une Nouvelle Permission
```python
# ai/permissions.py
def check_user_can_process_refund(user_id: int, order_id: int) -> bool:
    """Check if user can process refunds."""
    # Staff only
    if is_staff_user(user_id):
        return True
    
    # Or custom logic
    # ...
    return False
```

---

## 🧪 Comment Tester un Tool

### Test Manuel (Shell Django)
```bash
python manage.py shell
```

```python
from ai.tools.order_tools import check_order_status

# Sans permissions
result = check_order_status.invoke({'order_id': 1})
print(result)

# Avec permissions
config = {'configurable': {'user_id': 1}}
result = check_order_status.invoke({'order_id': 1}, config)
print(result)
```

### Test Unitaire (Pytest)
```python
# ai/tests.py
import pytest
from ai.tools.order_tools import check_order_status

@pytest.mark.django_db
def test_check_order_status_with_permissions():
    # Setup
    from business.models import Customer, Order
    customer = Customer.objects.create(name="Test", email="test@test.com")
    order = Order.objects.create(customer=customer, status="PENDING", total_amount=100)
    
    # Test owner access
    config = {'configurable': {'user_id': customer.id}}
    result = check_order_status.invoke({'order_id': order.id}, config)
    assert "PENDING" in result
    
    # Test non-owner access
    config = {'configurable': {'user_id': 9999}}
    result = check_order_status.invoke({'order_id': order.id}, config)
    assert "permission" in result.lower()
```

---

## 🔧 Configuration LLM

### Ajouter un Nouveau Provider
```python
# ai/llms.py
def get_llm_for_agent(agent):
    # ...existing code...
    
    elif provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        api_key = os.getenv("GOOGLE_API_KEY")
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            api_key=api_key
        )
```

### Utiliser dans un Agent
```python
# ai/agents.py
from ai.utils import get_llm, load_tools_for_agent
from langgraph.prebuilt import create_react_agent

def get_my_agent():
    llm = get_llm("my_agent")  # Charge depuis la DB
    tools = load_tools_for_agent("my_agent")
    
    return create_react_agent(
        model=llm,
        tools=tools,
        prompt="You are a helpful assistant."
    )
```

---

## 🐛 Debugging

### Voir les Tools Chargés
```python
from ai.utils import load_tools_for_agent
tools = load_tools_for_agent("data_agent")
for tool in tools:
    print(f"- {tool.name}: {tool.description}")
    print(f"  Path: {tool.func.__module__}.{tool.func.__name__}")
```

### Voir les Executions
```python
from ai.models import Execution, ExecutionStep, AgentMessage

# Dernière execution
exec = Execution.objects.latest('created_at')
print(f"Status: {exec.status}")
print(f"Thread: {exec.thread_id}")

# Steps
for step in exec.steps.all():
    print(f"- {step.node_name}: {step.status}")

# Messages
for msg in exec.messages.all():
    print(f"[{msg.role}] {msg.content[:100]}")
```

### Activer les Logs
```python
# config/settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'ai.services': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

---

## 📚 Documentation Complète

- `MIGRATION_COMPLETE.md` - Détails de la migration
- `TESTS_REPORT.md` - Rapport des tests
- `IMPROVEMENTS.md` - Liste des améliorations
- `IMPLEMENTATION_SUMMARY.md` - Résumé technique

---

## ❓ FAQ

### Q: Pourquoi `RunnableConfig` au lieu de kwargs?
**R**: C'est le pattern LangChain standard pour passer du contexte aux tools sans polluer la signature.

### Q: Comment gérer les permissions avec Django Users?
**R**: Actuellement, on assume `customer.id == user.id`. En production, ajoutez une FK `Customer.user` vers `User`.

### Q: Les tools peuvent-ils appeler d'autres tools?
**R**: Oui! Les tools peuvent s'appeler entre eux. Pensez à propager le `config`.

### Q: Comment gérer les tools asynchrones?
**R**: Utilisez `@tool` avec des fonctions `async def`. LangChain gère automatiquement.

---

## 🎯 Best Practices

1. **Toujours** ajouter `config: RunnableConfig = None` aux tools
2. **Toujours** vérifier les permissions avant d'exécuter une action
3. **Toujours** retourner des messages clairs (pas d'exceptions non catchées)
4. **Toujours** logger les actions sensibles
5. **Toujours** tester avec et sans user context

---

**Besoin d'aide?** Consultez les docs ou demandez à l'équipe! 🚀

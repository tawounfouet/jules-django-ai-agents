# Améliorations de l'Architecture AI - Inspirées de archives/ai-demo

Ce document décrit les améliorations majeures apportées au système AI suite à l'analyse du code dans `archives/ai-demo`.

## 📋 Résumé des Changements

### ✅ Implémenté

1. **Configuration LLM Centralisée** (`ai/llms.py`)
2. **Context Utilisateur via RunnableConfig** (tous les tools)
3. **Système de Permissions** (`ai/permissions.py`)
4. **Structure Modulaire des Tools** (`ai/tools/`)
5. **Logging Amélioré** (`ai/services/graph_executor.py`)
6. **Passage du user_id à travers la stack** (`ai/views.py` → `GraphExecutor`)

---

## 🏗️ Changements Détaillés

### 1. Configuration LLM Centralisée

**Fichier:** `ai/llms.py` (nouveau)

**Raison:** Séparer la logique de configuration des LLMs pour améliorer la maintenabilité.

**Avant:**
```python
# Dans ai/utils.py
def get_llm(agent_key: str):
    # ... 40 lignes de code pour configurer les LLMs
```

**Après:**
```python
# ai/llms.py
def get_llm_for_agent(agent):
    """Factory function to create LLM instances"""
    # Configuration centralisée
    
# ai/utils.py
def get_llm(agent_key: str):
    agent = Agent.objects.get(key=agent_key)
    return get_llm_for_agent(agent)
```

**Avantages:**
- Séparation des responsabilités
- Plus facile à tester
- Ajout de retry logic automatique
- Code réutilisable

---

### 2. Context Utilisateur via RunnableConfig

**Fichiers modifiés:**
- `ai/tools.py` → `ai/tools/*.py`
- `ai/services/graph_executor.py`
- `ai/views.py`

**Pattern inspiré de:** `archives/ai-demo/tools/documents.py`

**Avant:**
```python
@tool
def check_order_status(order_id: int) -> str:
    order = Order.objects.get(id=order_id)
    return f"Order {order_id} is {order.status}"
```

**Après:**
```python
@tool
def check_order_status(order_id: int, config: RunnableConfig = None) -> str:
    # Extract user context
    user_id = None
    if config:
        user_id = config.get('configurable', {}).get('user_id')
    
    # Check permissions
    if user_id and not check_user_can_access_order(user_id, order_id):
        return "Permission denied"
    
    order = Order.objects.get(id=order_id)
    return f"Order {order_id} is {order.status}"
```

**Flow du context:**
```
Request (user_id) 
  → views.py (extract user_id from request.user)
  → GraphExecutor.execute(user_id=user_id)
  → config = {"configurable": {"user_id": user_id}}
  → app.stream(inputs, config=config)
  → tools receive config via RunnableConfig
```

**Avantages:**
- Support des permissions au niveau des tools
- Audit trail (qui a fait quoi)
- Context propagé automatiquement par LangGraph

---

### 3. Système de Permissions

**Fichier:** `ai/permissions.py` (nouveau)

**Fonctions:**
- `check_user_can_access_order(user_id, order_id)`
- `check_user_can_access_ticket(user_id, ticket_id)`
- `is_staff_user(user_id)`
- `check_permission(user_id, action, resource)` (générique)

**Usage:**
```python
# Dans un tool
from ai.permissions import check_user_can_access_order

@tool
def check_order_status(order_id: int, config: RunnableConfig = None):
    user_id = config.get('configurable', {}).get('user_id')
    if user_id and not check_user_can_access_order(user_id, order_id):
        return "Permission denied"
    # ...
```

**Future Integration:**
- Django Guardian
- permit.io (comme dans ai-demo)
- Django Rules

---

### 4. Structure Modulaire des Tools

**Avant:**
```
ai/
  tools.py  # Tous les tools dans un seul fichier
```

**Après:**
```
ai/
  tools/
    __init__.py
    order_tools.py      # check_order_status
    ticket_tools.py     # get_ticket_info
    support_tools.py    # create_support_response
```

**Avantages:**
- Scalabilité (facile d'ajouter de nouveaux tools)
- Organisation par domaine métier
- Tests plus faciles
- Imports clairs: `from ai.tools import order_tools`

**Export pattern:**
```python
# ai/tools/order_tools.py
@tool
def check_order_status(...): ...

order_tools = [check_order_status]

# ai/tools/__init__.py
from .order_tools import order_tools
from .ticket_tools import ticket_tools
from .support_tools import support_tools
```

---

### 5. Logging Amélioré dans GraphExecutor

**Ajouts:**
- Import du module `logging`
- Logger dédié: `logger = logging.getLogger(__name__)`
- Try-catch au niveau des steps individuels
- `logger.error()` pour les erreurs de nodes
- `logger.exception()` pour les erreurs d'exécution globales

**Avant:**
```python
for event in app.stream(inputs, config=config):
    for node_name, node_value in event.items():
        # Pas de gestion d'erreur au niveau du node
        step = ExecutionStep.objects.create(...)
```

**Après:**
```python
for event in app.stream(inputs, config=config):
    for node_name, node_value in event.items():
        try:
            step = ExecutionStep.objects.create(...)
            # ... traitement
        except Exception as step_error:
            logger.error(f"Error in node {node_name}: {step_error}")
            ExecutionStep.objects.create(
                execution=execution,
                node_name=node_name,
                status="failed",
                output_payload={"error": str(step_error)}
            )
```

**Avantages:**
- Erreurs de nodes n'arrêtent pas l'exécution complète
- Meilleur debugging
- Logs structurés pour monitoring

---

## 🧪 Tests

Pour tester les nouvelles fonctionnalités:

```bash
# 1. Créer un utilisateur de test
python manage.py shell
>>> from users.models import User
>>> user = User.objects.create_user(username='testuser', password='test123')

# 2. Tester l'API avec authentification
curl -X POST http://localhost:8000/ai/trigger/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Check order 1 status"}'

# 3. Vérifier les logs
tail -f logs/django.log
```

---

## 🚀 Prochaines Étapes

### Court terme
- [ ] Ajouter des tests unitaires pour les permissions
- [ ] Documenter les tools dans l'admin Django
- [ ] Ajouter des metrics (temps d'exécution, taux d'erreur)

### Moyen terme
- [ ] Intégrer permit.io ou Django Guardian
- [ ] Ajouter des tools pour créer/modifier des orders
- [ ] Système de rate limiting par utilisateur

### Long terme
- [ ] Multi-tenancy (plusieurs organisations)
- [ ] Audit trail complet dans la DB
- [ ] Dashboard de monitoring des agents

---

## 📚 Références

- **Inspiration:** `archives/ai-demo/` (documents.py, graph_executor.py, llms.py)
- **LangChain RunnableConfig:** https://python.langchain.com/docs/how_to/configure
- **LangGraph Checkpointing:** https://langchain-ai.github.io/langgraph/how-tos/persistence/

---

## 🤝 Contribution

Pour ajouter un nouveau tool:

1. Créer le fichier dans `ai/tools/` (ex: `product_tools.py`)
2. Utiliser le decorator `@tool` avec `RunnableConfig`
3. Ajouter les checks de permissions si nécessaire
4. Exporter dans `ai/tools/__init__.py`
5. Ajouter le tool dans la DB via l'admin ou un fixture

Exemple:
```python
# ai/tools/product_tools.py
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

@tool
def search_products(query: str, config: RunnableConfig = None) -> str:
    """Search for products by name or description."""
    user_id = None
    if config:
        user_id = config.get('configurable', {}).get('user_id')
    
    # Implementation...
    return results

product_tools = [search_products]
```

# 📋 Plan de Migration : Anciens Tools → Nouveaux Tools Modulaires

## 🎯 Objectif
Migrer de `ai/tools.py` (ancien) vers `ai/tools/` (nouveau, modulaire) tout en maintenant la compatibilité.

---

## 📊 Statut Actuel

### ✅ Ce qui est fait :
- ✅ Nouvelle structure créée : `ai/tools/{order,ticket,support}_tools.py`
- ✅ Permissions ajoutées : `ai/permissions.py`
- ✅ LLM factory centralisée : `ai/llms.py`
- ✅ `RunnableConfig` ajouté aux nouveaux tools

### ⚠️ Ce qui dépend encore de `ai/tools.py` :
- `ai/management/commands/seed_agents.py` (ligne 57, 63)
- `ai/utils.py` → `load_tools_for_agent()` (import dynamique)
- Base de données : `Tool.python_path` pointe vers `ai.tools.X`

---

## 🔄 Stratégie : Backward Compatibility

### Option 1 : **Garder `ai/tools.py` comme Proxy (RECOMMANDÉ)**

Transformer `ai/tools.py` en point d'entrée qui importe depuis les nouveaux modules :

```python
# ai/tools.py - BACKWARD COMPATIBILITY LAYER
"""
Backward compatibility layer for existing tool references.
All new code should import from ai.tools.order_tools, etc.
"""
from .tools.order_tools import check_order_status
from .tools.ticket_tools import get_ticket_info
from .tools.support_tools import create_support_response

__all__ = ['check_order_status', 'get_ticket_info', 'create_support_response']
```

**Avantages** :
- ✅ Pas de migration de DB nécessaire
- ✅ Code existant continue de fonctionner
- ✅ Transition en douceur

---

## 📝 Étapes de Migration

### Phase 1 : Compatibilité (MAINTENANT)
1. ✅ Créer la structure modulaire `ai/tools/`
2. 🔄 Transformer `ai/tools.py` en proxy (voir ci-dessus)
3. ✅ Tester que les anciens imports fonctionnent

### Phase 2 : Migration Progressive (FUTUR)
1. Mettre à jour `seed_agents.py` pour pointer vers les nouveaux paths :
   ```python
   "python_path": "ai.tools.order_tools.check_order_status"
   ```
2. Créer une migration de données pour mettre à jour `Tool.python_path`
3. Mettre à jour les tests

### Phase 3 : Cleanup (OPTIONNEL)
1. Supprimer `ai/tools.py` une fois que tous les paths sont migrés
2. Ajouter un warning si quelqu'un importe depuis l'ancien chemin

---

## 🎬 Action Immédiate

Transformer `ai/tools.py` en proxy pour maintenir la compatibilité.

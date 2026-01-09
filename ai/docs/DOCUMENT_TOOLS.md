# 📄 Document Management Tools - Documentation

## Vue d'ensemble

Le module `document_tools.py` fournit un ensemble complet d'outils pour gérer les documents utilisateur dans l'application. Ces outils sont utilisés par le `document_agent` pour effectuer des opérations CRUD (Create, Read, Update, Delete) sur les documents.

---

## 🏗️ Architecture

```
User Request
    ↓
Supervisor (routes to document_agent)
    ↓
Document Agent (with document_tools)
    ↓
Document Tools (avec permissions check)
    ↓
Database (documents.models.Document)
```

---

## 🔧 Tools Disponibles

### 1. **search_query_documents**
```python
@tool
def search_query_documents(query: str, limit: int = 5, config: RunnableConfig = None) -> str
```

**Description** : Recherche des documents par mot-clé dans le titre ou le contenu.

**Paramètres** :
- `query` (str) : Mot-clé ou phrase à rechercher
- `limit` (int) : Nombre maximum de résultats (max 25, défaut 5)
- `config` (RunnableConfig) : Context utilisateur pour permissions

**Retour** : JSON liste des documents trouvés ou message d'erreur

**Exemple d'utilisation** :
```
User: "Search for documents about Python"
→ search_query_documents(query="Python", limit=10)
→ Returns: [{"id": 1, "title": "Python Tutorial"}, ...]
```

---

### 2. **list_documents**
```python
@tool
def list_documents(limit: int = 5, config: RunnableConfig = None) -> str
```

**Description** : Liste les documents les plus récents de l'utilisateur.

**Paramètres** :
- `limit` (int) : Nombre de documents à retourner (max 25, défaut 5)
- `config` (RunnableConfig) : Context utilisateur

**Retour** : JSON liste des documents

**Exemple** :
```
User: "Show me my recent documents"
→ list_documents(limit=10)
→ Returns: [{"id": 1, "title": "Doc 1"}, {"id": 2, "title": "Doc 2"}]
```

---

### 3. **get_document**
```python
@tool
def get_document(document_id: int, config: RunnableConfig = None) -> str
```

**Description** : Récupère les détails complets d'un document spécifique.

**Paramètres** :
- `document_id` (int) : ID du document
- `config` (RunnableConfig) : Context utilisateur

**Retour** : JSON avec titre, contenu, date de création

**Exemple** :
```
User: "Show me document 5"
→ get_document(document_id=5)
→ Returns: {"id": 5, "title": "...", "content": "...", "created_at": "..."}
```

---

### 4. **create_document**
```python
@tool
def create_document(title: str, content: str, config: RunnableConfig = None) -> str
```

**Description** : Crée un nouveau document pour l'utilisateur.

**Paramètres** :
- `title` (str) : Titre du document (max 120 caractères)
- `content` (str) : Contenu du document (long texte)
- `config` (RunnableConfig) : Context utilisateur (owner_id)

**Retour** : JSON du document créé

**Exemple** :
```
User: "Create a document titled 'Meeting Notes' with content '...'"
→ create_document(title="Meeting Notes", content="...")
→ Returns: {"id": 10, "title": "Meeting Notes", ...}
```

---

### 5. **update_document**
```python
@tool
def update_document(
    document_id: int, 
    title: str = None, 
    content: str = None, 
    config: RunnableConfig = None
) -> str
```

**Description** : Met à jour un document existant (titre et/ou contenu).

**Paramètres** :
- `document_id` (int) : ID du document à modifier
- `title` (str, optionnel) : Nouveau titre
- `content` (str, optionnel) : Nouveau contenu
- `config` (RunnableConfig) : Context utilisateur

**Retour** : JSON du document mis à jour

**Exemple** :
```
User: "Update document 5, change the title to 'New Title'"
→ update_document(document_id=5, title="New Title")
→ Returns: {"id": 5, "title": "New Title", ...}
```

---

### 6. **delete_document**
```python
@tool
def delete_document(document_id: int, config: RunnableConfig = None) -> str
```

**Description** : Supprime (soft delete) un document de l'utilisateur.

**Paramètres** :
- `document_id` (int) : ID du document à supprimer
- `config` (RunnableConfig) : Context utilisateur

**Retour** : Message de confirmation

**Exemple** :
```
User: "Delete document 3"
→ delete_document(document_id=3)
→ Returns: "Document 3 deleted successfully."
```

---

## 🔒 Permissions

Tous les tools vérifient les permissions via `check_permission(user_id, action, "document")`.

### Règles de Permissions

| Action | Utilisateur Authentifié | Staff | Anonyme |
|--------|------------------------|-------|---------|
| **read** | ✅ (ses docs) | ✅ (tous) | ❌ |
| **list** | ✅ (ses docs) | ✅ (tous) | ❌ |
| **create** | ✅ | ✅ | ❌ |
| **update** | ✅ (ses docs) | ✅ | ❌ |
| **delete** | ✅ (ses docs) | ✅ | ❌ |

**Note** : Les utilisateurs réguliers ne peuvent modifier/supprimer QUE leurs propres documents (vérification via `owner_id`).

---

## 🎯 Intégration avec le Document Agent

### Configuration dans seed_agents.py

```python
{
    "key": "document_agent",
    "name": "Document Agent",
    "role": "Document Management",
    "llm_provider": "openai",
    "llm_model": "gpt-4o",
    "temperature": 0.2,
    "system_prompt": "You are a document management agent..."
}
```

### Tools Liés

Les 6 document tools sont automatiquement liés au `document_agent` via `AgentTool`.

---

## 📝 Exemples de Conversations

### Exemple 1 : Créer un Document
```
User: "Create a new document called 'Project Ideas' with some brainstorming notes"

Supervisor → document_agent
Document Agent → create_document(
    title="Project Ideas",
    content="Brainstorming notes: ..."
)

Response: "Document created successfully: 
{
  'id': 15,
  'title': 'Project Ideas',
  'content': '...',
  'created_at': '2026-01-09 10:30:00'
}"
```

### Exemple 2 : Rechercher des Documents
```
User: "Find all my documents about AI"

Supervisor → document_agent
Document Agent → search_query_documents(query="AI", limit=10)

Response: "[
  {'id': 3, 'title': 'AI Research Notes'},
  {'id': 7, 'title': 'AI Project Plan'},
  {'id': 12, 'title': 'AI Meeting Summary'}
]"
```

### Exemple 3 : Mettre à Jour un Document
```
User: "Update document 5, add more content to it"

Supervisor → document_agent
Document Agent → get_document(document_id=5)  # Lire d'abord
Document Agent → update_document(
    document_id=5,
    content="Original content + new content"
)

Response: "Document updated successfully..."
```

---

## 🔧 Configuration Technique

### Database Schema
```python
# documents/models.py
class Document(models.Model):
    title = models.CharField(max_length=120)
    content = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Tool Registration in DB
```python
# Via seed_agents.py
Tool.objects.create(
    key="create_document",
    name="Create Document",
    description="Create a new document",
    python_path="ai.tools.document_tools.create_document"
)
```

---

## ⚙️ Différences avec ai-demo/documents.py

| Aspect | ai-demo (Ancien) | Notre Implémentation |
|--------|------------------|---------------------|
| **Permissions** | `permit.check()` (async) | `check_permission()` (sync) |
| **Return Type** | `list[dict]` | `str` (JSON) |
| **Error Handling** | `raise Exception` | Return error string |
| **Owner Field** | `owner_id` | `owner_id` (même) |
| **Soft Delete** | `active=False` | `active=False` (même) |

### Avantages de Notre Implémentation

✅ **Pas de dépendance externe** (pas besoin de permit.io)  
✅ **Return strings** pour meilleure compatibilité LLM  
✅ **Gestion d'erreurs gracieuse** (pas d'exceptions non catchées)  
✅ **Permissions extensibles** via `ai/permissions.py`  
✅ **Cohérent avec les autres tools** (order_tools, ticket_tools)

---

## 🚀 Tester les Document Tools

### Via Django Shell
```python
python manage.py shell

from ai.tools.document_tools import create_document, list_documents
from langchain_core.runnables import RunnableConfig

# Simuler un context utilisateur
config = {"configurable": {"user_id": 1}}

# Créer un document
result = create_document.invoke(
    {"title": "Test Doc", "content": "Hello World"},
    config=config
)
print(result)

# Lister les documents
result = list_documents.invoke({"limit": 5}, config=config)
print(result)
```

### Via API
```bash
curl -X POST http://localhost:8000/ai/trigger/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a document called Test with content Hello"
  }'
```

---

## 📊 Métriques & Monitoring

### Logs à Surveiller
- Nombre de documents créés par utilisateur
- Fréquence des recherches
- Documents les plus accédés
- Erreurs de permissions

### Exemple de Logging (Future)
```python
logger.info(f"User {user_id} created document {doc_id}")
logger.warning(f"Permission denied: User {user_id} tried to access doc {doc_id}")
```

---

## 🔜 Améliorations Futures

1. **Permissions Granulaires** : Intégrer avec permit.io ou django-guardian
2. **Versioning** : Historique des modifications de documents
3. **Partage** : Permettre le partage de documents entre utilisateurs
4. **Tags/Categories** : Organiser les documents par tags
5. **Full-Text Search** : Utiliser PostgreSQL full-text search ou Elasticsearch
6. **Export** : Exporter documents en PDF, Markdown, etc.

---

## ✅ Checklist de Validation

- ✅ `ai/tools/document_tools.py` créé
- ✅ 6 tools implémentés avec RunnableConfig
- ✅ Permissions vérifiées pour chaque tool
- ✅ `document_agent` créé dans agents.py
- ✅ Tools liés au document_agent dans seed_agents.py
- ✅ Supervisor mis à jour pour router vers document_agent
- ✅ Graph mis à jour avec document_agent node
- ✅ Documentation complète

**Status: ✅ READY FOR PRODUCTION**

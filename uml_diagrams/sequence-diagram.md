# Scalable LLM RAG Chatbot Sequence Diagram

This diagram illustrates the sequence of interactions between components when a user queries the chatbot.

```mermaid
sequenceDiagram
    participant User
    participant API as FastAPI Endpoint
    participant RAG as RAG Pipeline
    participant VDB as Vector Database
    participant LLM as LLM Service
    
    %% Regular RAG-enabled query flow
    User->>API: POST /chat (with use_rag=true)
    Note over API: Extract user message
    API->>RAG: generate_response(query, temperature, max_tokens)
    
    %% Retrieval phase
    RAG->>VDB: query(query_text, n_results)
    VDB-->>RAG: Return relevant documents
    
    alt No documents found
        RAG->>LLM: generate(query, temperature, max_tokens)
        LLM-->>RAG: Direct response (without context)
    else Documents found
        Note over RAG: Format context from documents
        Note over RAG: Create RAG prompt with context
        RAG->>LLM: generate(enhanced_prompt, temperature, max_tokens)
        LLM-->>RAG: Context-aware response
    end
    
    RAG-->>API: Return response and documents
    API-->>User: JSON response with answer and sources
    
    %% Direct LLM query without RAG
    User->>API: POST /chat (with use_rag=false)
    Note over API: Extract user message
    API->>LLM: generate(query, temperature, max_tokens)
    LLM-->>API: Direct response
    API-->>User: JSON response with answer only
    
    %% Health check flow
    User->>API: GET /health
    API-->>User: Status 200 OK
    
    %% Document addition flow
    User->>API: POST /documents
    API->>VDB: add_documents(documents)
    VDB-->>API: Success/failure status
    API-->>User: Document addition status
```

## Sequence Description

### RAG-Enabled Query Flow
1. User sends a chat request with `use_rag=true`
2. API extracts the user message
3. RAG Pipeline receives the query
4. Vector Database is queried for relevant documents
5. If documents are found:
   - RAG Pipeline formats the context
   - RAG Pipeline creates an enhanced prompt
   - LLM Service generates a context-aware response
6. If no documents are found:
   - LLM Service generates a direct response without context
7. Response (and any retrieved documents) are returned to the user

### Direct LLM Query Flow (without RAG)
1. User sends a chat request with `use_rag=false`
2. API extracts the user message
3. LLM Service directly generates a response
4. Response is returned to the user

### Health Check Flow
1. User sends a GET request to /health
2. API returns status 200 OK

### Document Addition Flow
1. User sends documents to be added to the vector database
2. Vector Database Service stores the documents
3. Success/failure status is returned to the user 
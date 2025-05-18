# Scalable LLM RAG Chatbot Class Diagram

This diagram illustrates the main classes and their relationships in the Scalable LLM RAG Chatbot project.

```mermaid
classDiagram
    %% Main API Models
    class ChatMessage {
        +String role
        +String content
    }
    
    class ChatRequest {
        +List~ChatMessage~ messages
        +Boolean use_rag
        +Float temperature
        +Int max_tokens
    }
    
    class ChatResponse {
        +String response
        +List~Dict~ retrieved_documents
    }
    
    class DocumentBatch {
        +List~Document~ documents
    }
    
    class Document {
        +String id
        +String text
        +Dict metadata
    }
    
    class DocumentResponse {
        +Boolean success
        +Int count
        +String message
    }
    
    %% Main Service Classes
    class RAGPipeline {
        -LLMService llm_service
        -VectorDBService vector_db_service
        +generate_response(query, temperature, max_tokens, n_results)
        -_format_context(documents)
        -_create_rag_prompt(query, context)
    }
    
    class VectorDBService {
        -Client client
        -String collection_name
        -Collection collection
        -EmbeddingModel embedding_model
        +add_documents(documents)
        +query(query_text, n_results)
        +shutdown()
        -_load_embedding_model()
        -_get_or_create_collection()
    }
    
    class LLMService {
        -String model_id
        -Engine engine
        +generate(prompt, temperature, max_tokens, system_prompt)
        +shutdown()
    }
    
    class SimpleLLMService {
        -Dict responses
        +generate(prompt, temperature, max_tokens, system_prompt)
        +shutdown()
    }
    
    %% Load Testing Class
    class ChatbotUser {
        -List conversation_history
        +on_start()
        +ask_question()
        +health_check()
        +ask_without_rag()
    }
    
    %% Relationships
    RAGPipeline --> LLMService: uses
    RAGPipeline --> VectorDBService: uses
    
    ChatRequest --> ChatMessage: contains
    ChatResponse --> Document: may contain
    DocumentBatch --> Document: contains
    
    ChatbotUser ..> ChatRequest: creates
    ChatbotUser ..> ChatResponse: processes
    
    %% Inheritance/Implementation
    LLMService <|-- SimpleLLMService: implements
```

## Class Descriptions

### API Models
- **ChatMessage**: Represents a message in the conversation with role and content
- **ChatRequest**: Encapsulates a request to the chat endpoint with messages and parameters
- **ChatResponse**: Contains the response from the chatbot and any retrieved documents
- **Document**: Represents a document in the vector database with text and metadata
- **DocumentBatch**: A collection of documents to be added to the vector database
- **DocumentResponse**: Response after adding documents to the vector database

### Core Services
- **RAGPipeline**: Orchestrates the RAG process, combining document retrieval with LLM generation
- **VectorDBService**: Manages interactions with the vector database, including document storage and retrieval
- **LLMService**: Interface for generating text from a large language model
- **SimpleLLMService**: A simplified implementation of LLMService with predefined responses

### Load Testing
- **ChatbotUser**: Simulates user behavior for load testing the chatbot API

### Key Relationships
- The RAGPipeline combines the LLMService and VectorDBService to provide enhanced responses
- ChatbotUser creates ChatRequests and processes ChatResponses during load testing
- API models are used to structure data exchange between components 
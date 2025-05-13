import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

// Define types
interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface RetrievedDocument {
  text: string;
  metadata: any;
  id: string;
  distance?: number;
}

interface ChatResponse {
  response: string;
  retrieved_documents?: RetrievedDocument[];
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [useRag, setUseRag] = useState(true);
  const [retrievedDocs, setRetrievedDocs] = useState<RetrievedDocument[]>([]);
  const [showDocs, setShowDocs] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    // Add user message to chat
    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    
    try {
      // Send request to API
      const response = await axios.post<ChatResponse>(`${apiUrl}/chat`, {
        messages: [...messages, userMessage],
        use_rag: useRag,
        temperature: 0.7,
        max_tokens: 1024
      });
      
      // Add assistant response to chat
      const assistantMessage: Message = { 
        role: 'assistant', 
        content: response.data.response 
      };
      setMessages(prev => [...prev, assistantMessage]);
      
      // Store retrieved documents if available
      if (response.data.retrieved_documents) {
        setRetrievedDocs(response.data.retrieved_documents);
      } else {
        setRetrievedDocs([]);
      }
      
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, there was an error processing your request. Please try again.' 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-blue-600 text-white p-4 shadow-md">
        <div className="container mx-auto">
          <h1 className="text-2xl font-bold">RAG Chatbot</h1>
          <p className="text-sm">Powered by Mistral-7B</p>
        </div>
      </header>

      {/* Main content */}
      <main className="flex flex-1 container mx-auto p-4 md:p-6">
        {/* Chat section */}
        <div className="flex flex-col flex-1 bg-white rounded-lg shadow-lg overflow-hidden">
          {/* Messages area */}
          <div className="flex-1 p-4 overflow-y-auto">
            {messages.length === 0 ? (
              <div className="flex items-center justify-center h-full text-gray-400">
                <div className="text-center">
                  <h2 className="text-xl font-semibold mb-2">Welcome to RAG Chatbot!</h2>
                  <p>Start a conversation by typing a message below.</p>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((message, index) => (
                  <div 
                    key={index} 
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div 
                      className={`max-w-3/4 p-3 rounded-lg ${
                        message.role === 'user' 
                          ? 'bg-blue-500 text-white rounded-br-none' 
                          : 'bg-gray-200 text-gray-800 rounded-bl-none'
                      }`}
                    >
                      <ReactMarkdown>{message.content}</ReactMarkdown>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-200 text-gray-800 p-3 rounded-lg rounded-bl-none">
                      <div className="flex space-x-2">
                        <div className="w-2 h-2 rounded-full bg-gray-500 animate-bounce"></div>
                        <div className="w-2 h-2 rounded-full bg-gray-500 animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        <div className="w-2 h-2 rounded-full bg-gray-500 animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* Input area */}
          <div className="border-t p-4">
            <form onSubmit={handleSubmit} className="flex space-x-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type your message..."
                className="flex-1 border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isLoading}
              />
              <button
                type="submit"
                className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-blue-300"
                disabled={isLoading || !input.trim()}
              >
                Send
              </button>
            </form>
            <div className="flex items-center mt-2">
              <label className="flex items-center text-sm text-gray-600">
                <input
                  type="checkbox"
                  checked={useRag}
                  onChange={() => setUseRag(!useRag)}
                  className="mr-2"
                />
                Use RAG (Retrieval-Augmented Generation)
              </label>
              {retrievedDocs.length > 0 && (
                <button
                  onClick={() => setShowDocs(!showDocs)}
                  className="ml-auto text-sm text-blue-500 hover:underline"
                >
                  {showDocs ? 'Hide' : 'Show'} retrieved documents
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Retrieved documents panel (conditionally shown) */}
        {showDocs && retrievedDocs.length > 0 && (
          <div className="w-80 ml-4 bg-white rounded-lg shadow-lg overflow-hidden hidden md:block">
            <div className="p-4 bg-gray-100 border-b">
              <h2 className="font-semibold">Retrieved Documents</h2>
            </div>
            <div className="p-4 overflow-y-auto max-h-[calc(100vh-200px)]">
              {retrievedDocs.map((doc, index) => (
                <div key={index} className="mb-4 p-3 bg-gray-50 rounded border">
                  <div className="text-xs text-gray-500 mb-1">
                    {doc.metadata?.source || `Document ${index + 1}`}
                  </div>
                  <div className="text-sm">{doc.text}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-gray-200 p-4 text-center text-gray-600 text-sm">
        Scalable LLM RAG Chatbot with Kubernetes - Master's Project Demo
      </footer>
    </div>
  );
} 
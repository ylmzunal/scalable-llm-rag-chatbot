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
  const inputRef = useRef<HTMLInputElement>(null);
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input field when component loads
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    // Add user message to chat
    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    
    try {
      console.log(`Sending request to API: ${apiUrl}/chat`);
      
      // Send request to API with explicit timeout
      const response = await axios.post<ChatResponse>(
        `${apiUrl}/chat`, 
        {
          messages: [...messages, userMessage],
          use_rag: useRag,
          temperature: 0.7,
          max_tokens: 1024
        },
        {
          timeout: 30000, // 30 seconds timeout
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        }
      );
      
      console.log("API response received:", response.data);
      
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
      
      // Log more detailed error information
      if (axios.isAxiosError(error)) {
        console.error('Axios error details:', {
          status: error.response?.status,
          statusText: error.response?.statusText,
          data: error.response?.data,
          message: error.message
        });
      }
      
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, there was an error processing your request. Please try again.' 
      }]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-gradient-to-r from-indigo-700 to-blue-600 text-white p-5 shadow-lg">
        <div className="container mx-auto max-w-6xl flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">RAG Chatbot</h1>
            <p className="text-indigo-100 mt-1">AI-Powered Knowledge Assistant</p>
          </div>
          <div className="hidden md:block">
            <span className="bg-indigo-800 py-1 px-3 rounded-full text-xs font-medium">
              Powered by TinyLlama
            </span>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 container mx-auto max-w-6xl p-4 md:p-6">
        <div className="flex flex-col md:flex-row gap-6 h-full">
          {/* Chat section */}
          <div className="flex flex-col flex-1 bg-white rounded-xl shadow-xl overflow-hidden border border-gray-100">
            {/* Messages area */}
            <div className="flex-1 p-6 overflow-y-auto" style={{ minHeight: "450px", maxHeight: "70vh" }}>
              {messages.length === 0 ? (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center max-w-md p-6 rounded-xl bg-indigo-50 border border-indigo-100">
                    <div className="w-16 h-16 bg-gradient-to-r from-indigo-500 to-blue-500 rounded-full mx-auto mb-4 flex items-center justify-center">
                      <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                        <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-0.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd"></path>
                      </svg>
                    </div>
                    <h2 className="text-xl font-bold text-gray-800 mb-2">Welcome to the RAG Assistant</h2>
                    <p className="text-gray-600 mb-4">Ask me anything or try these examples:</p>
                    <div className="space-y-2 text-left">
                      <button 
                        onClick={() => setInput("What is a RAG chatbot?")}
                        className="w-full text-left p-2 rounded-lg border border-indigo-200 bg-white hover:bg-indigo-50 transition text-sm text-gray-700"
                      >
                        What is a RAG chatbot?
                      </button>
                      <button 
                        onClick={() => setInput("Explain how Kubernetes helps with scaling AI applications")}
                        className="w-full text-left p-2 rounded-lg border border-indigo-200 bg-white hover:bg-indigo-50 transition text-sm text-gray-700"
                      >
                        Explain how Kubernetes helps with scaling AI applications
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="space-y-6">
                  {messages.map((message, index) => (
                    <div 
                      key={index} 
                      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div 
                        className={`max-w-[80%] p-4 rounded-xl shadow-sm ${
                          message.role === 'user' 
                            ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white' 
                            : 'bg-white border border-gray-200 text-gray-800'
                        }`}
                      >
                        <ReactMarkdown className="prose max-w-none">{message.content}</ReactMarkdown>
                      </div>
                    </div>
                  ))}
                  {isLoading && (
                    <div className="flex justify-start">
                      <div className="bg-white border border-gray-200 p-4 rounded-xl shadow-sm">
                        <div className="flex space-x-2 items-center">
                          <div className="text-gray-500 text-sm">Thinking</div>
                          <div className="flex">
                            <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce"></div>
                            <div className="w-2 h-2 rounded-full bg-indigo-500 animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                            <div className="w-2 h-2 rounded-full bg-indigo-600 animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
              )}
            </div>

            {/* Input area */}
            <div className="border-t border-gray-200 bg-gray-50 p-4">
              <form onSubmit={handleSubmit} className="flex flex-col space-y-3">
                <div className="flex space-x-2">
                  <input
                    ref={inputRef}
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Type your question..."
                    className="flex-1 border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition"
                    disabled={isLoading}
                  />
                  <button
                    type="submit"
                    className="bg-gradient-to-r from-indigo-600 to-blue-500 text-white px-6 py-3 rounded-lg hover:from-indigo-700 hover:to-blue-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
                    disabled={isLoading || !input.trim()}
                  >
                    <span className="flex items-center justify-center">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
                      </svg>
                    </span>
                  </button>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <label className="flex items-center text-gray-600 select-none">
                    <input
                      type="checkbox"
                      checked={useRag}
                      onChange={() => setUseRag(!useRag)}
                      className="mr-2 h-4 w-4 text-indigo-600 focus:ring-indigo-500 rounded border-gray-300"
                    />
                    Use RAG (Retrieval-Augmented Generation)
                  </label>
                  {retrievedDocs.length > 0 && (
                    <button
                      type="button"
                      onClick={() => setShowDocs(!showDocs)}
                      className="text-indigo-600 hover:text-indigo-800 transition font-medium focus:outline-none"
                    >
                      {showDocs ? 'Hide sources' : 'View sources'} ({retrievedDocs.length})
                    </button>
                  )}
                </div>
              </form>
            </div>
          </div>

          {/* Retrieved documents panel */}
          <div 
            className={`w-full md:w-96 bg-white rounded-xl shadow-xl overflow-hidden border border-gray-100 transition-all duration-300 ${
              showDocs && retrievedDocs.length > 0 ? 'opacity-100 max-h-[70vh]' : 'opacity-0 max-h-0 md:opacity-100 md:max-h-[70vh] hidden md:block'
            }`}
          >
            <div className="p-4 bg-indigo-50 border-b border-indigo-100">
              <h2 className="font-bold text-gray-800 flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 text-indigo-600" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M7 3a1 1 0 000 2h6a1 1 0 100-2H7zM4 7a1 1 0 011-1h10a1 1 0 110 2H5a1 1 0 01-1-1zM2 11a2 2 0 012-2h12a2 2 0 012 2v4a2 2 0 01-2 2H4a2 2 0 01-2-2v-4z" />
                </svg>
                Knowledge Sources
              </h2>
            </div>
            {retrievedDocs.length > 0 ? (
              <div className="p-4 overflow-y-auto" style={{maxHeight: "calc(70vh - 50px)"}}>
                {retrievedDocs.map((doc, index) => (
                  <div key={index} className="mb-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                    <div className="text-xs font-medium text-indigo-600 mb-2 flex items-center">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
                      </svg>
                      {doc.metadata?.source || `Source ${index + 1}`}
                    </div>
                    <div className="text-sm text-gray-700 bg-white p-3 rounded border border-gray-200">{doc.text}</div>
                    {doc.distance !== undefined && (
                      <div className="mt-2 text-xs text-gray-500">
                        Relevance: {(1 - doc.distance).toFixed(3)}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center text-gray-500">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 mx-auto mb-2 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p className="text-sm">No sources available for this response</p>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-6 text-center text-gray-600">
        <div className="container mx-auto">
          <p className="text-sm">Scalable LLM RAG Chatbot with Kubernetes - Master's Project Demo</p>
          <div className="flex justify-center mt-3 space-x-4">
            <a href="#" className="text-gray-500 hover:text-indigo-600 transition">
              <span className="text-xs bg-gray-100 px-2 py-1 rounded">Documentation</span>
            </a>
            <a href="#" className="text-gray-500 hover:text-indigo-600 transition">
              <span className="text-xs bg-gray-100 px-2 py-1 rounded">GitHub</span>
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
} 
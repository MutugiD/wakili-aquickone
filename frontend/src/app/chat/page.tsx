'use client';
import { useEffect, useState, useRef } from 'react';
import Link from 'next/link';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant' | 'file';
  content: string;
  timestamp: Date;
  fileUrl?: string;
  fileName?: string;
  fileSize?: number;
  fileBackendPath?: string;
  processed?: boolean;
}

type BackendChatMessage = {
  type: string;
  content: string;
  [key: string]: unknown;
};

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  status: 'uploading' | 'uploaded' | 'error';
  progress?: number;
  error?: string;
}

export default function ChatPage() {
  const [chatId, setChatId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [chatList, setChatList] = useState<string[]>([]);
  const [loadingChats, setLoadingChats] = useState(true);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [chatNames, setChatNames] = useState<Record<string, string>>({});

  // Load chat names from localStorage
  useEffect(() => {
    const savedNames = localStorage.getItem('chatNames');
    if (savedNames) {
      setChatNames(JSON.parse(savedNames));
    }
  }, []);

  // Save chat names to localStorage
  const saveChatName = (chatId: string, name: string) => {
    const newNames = { ...chatNames, [chatId]: name };
    setChatNames(newNames);
    localStorage.setItem('chatNames', JSON.stringify(newNames));
  };

  // Generate chat name from first message
  const generateChatName = (message: string): string => {
    const words = message.split(' ').slice(0, 5);
    return words.join(' ') + (message.length > 50 ? '...' : '');
  };

  // Fetch chat list on mount
  useEffect(() => {
    fetch('http://localhost:8000/agent/chats')
      .then(res => res.json())
      .then(async data => {
        const chats = data.chats || [];
        setChatList(chats);
        setLoadingChats(false);
        if (chats.length > 0) {
          setChatId(chats[0]);
        } else {
          // Auto-create a new chat if none exist
          const res = await fetch('http://localhost:8000/agent/chat', { method: 'POST' });
          const newData = await res.json();
          setChatId(newData.chat_id);
          setChatList([newData.chat_id]);
        }
      });
  }, []);

  // Load chat history when chatId changes
  useEffect(() => {
    if (!chatId) return;
    fetch(`http://localhost:8000/agent/chat/${chatId}/history`)
      .then(res => res.json())
      .then(data => {
        if (data.history && Array.isArray(data.history)) {
          const chatMessages = data.history.map((msg: BackendChatMessage, idx: number) => ({
            id: String(idx),
            type: msg.type === 'human' ? 'user' : 'assistant',
            content: msg.content,
            timestamp: new Date(),
          }));
          setMessages(chatMessages);

          // Generate chat name from first message if not already named
          if (chatMessages.length > 0 && !chatNames[chatId]) {
            const firstMessage = chatMessages[0].content;
            const generatedName = generateChatName(firstMessage);
            saveChatName(chatId, generatedName);
          }
        } else {
          setMessages([]);
        }
      });
  }, [chatId, chatNames]);

  // Start a new chat
  const startNewChat = async () => {
    const res = await fetch('http://localhost:8000/agent/chat', { method: 'POST' });
    const data = await res.json();
    setChatId(data.chat_id);
    setMessages([]);
    setChatList((prev) => [data.chat_id, ...prev]);
  };

  // File upload handlers
  const handleFileSelect = (files: FileList) => {
    const newFiles: UploadedFile[] = Array.from(files).map(file => ({
      id: Date.now() + Math.random().toString(),
      name: file.name,
      size: file.size,
      status: 'uploading',
      progress: 0
    }));
    setUploadedFiles(prev => [...prev, ...newFiles]);
    uploadFiles(Array.from(files), newFiles);
  };

  const uploadFiles = async (files: File[], fileObjects: UploadedFile[]) => {
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const fileObj = fileObjects[i];
      const formData = new FormData();
      formData.append('file', file);
      try {
        const response = await fetch('http://localhost:8000/documents/upload', {
          method: 'POST',
          body: formData,
        });
        if (response.ok) {
          const data = await response.json();
          setUploadedFiles(prev =>
            prev.map(f =>
              f.id === fileObj.id
                ? { ...f, status: 'uploaded', progress: 100 }
                : f
          )
        );
        // Use only the filename for download and agent processing
        const filename = data.filename;
        const fileMsg: ChatMessage = {
          id: Date.now().toString() + Math.random(),
          type: 'file',
          content: '',
          timestamp: new Date(),
          fileUrl: `/documents/${filename}`,
          fileName: filename,
          fileSize: file.size,
          fileBackendPath: filename,
          processed: true,
        };
        setMessages((prev: ChatMessage[]) => [
          ...prev,
          fileMsg,
        ]);
        // Auto-process: send only the filename to the agent
        autoProcessFile(fileMsg);
      } else {
        setUploadedFiles(prev =>
          prev.map(f =>
            f.id === fileObj.id
              ? { ...f, status: 'error', error: 'Upload failed' }
              : f
          )
        );
      }
    } catch (error) {
      setUploadedFiles(prev =>
        prev.map(f =>
          f.id === fileObj.id
            ? { ...f, status: 'error', error: 'Network error' }
            : f
        )
      );
    }
  }
};

const autoProcessFile = async (fileMsg: ChatMessage) => {
  if (!chatId || !fileMsg.fileBackendPath) return;
  setIsLoading(true);
  // Send only the filename to the agent
  const agentPath = fileMsg.fileBackendPath;
  try {
    const response = await fetch(`http://localhost:8000/agent/chat/${chatId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: `summarize document: ${agentPath}`
      }),
    });
    const data = await response.json();
    setMessages(prev => [
      ...prev,
      {
        id: Date.now().toString() + Math.random(),
        type: 'assistant',
        content: data.response || 'No response from agent.',
        timestamp: new Date(),
      },
    ]);
  } catch {
    setMessages(prev => [
      ...prev,
      {
        id: Date.now().toString() + Math.random(),
        type: 'assistant',
        content: 'Error processing file. Please try again.',
        timestamp: new Date(),
      },
    ]);
  } finally {
    setIsLoading(false);
  }
};

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !chatId) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);

    // Generate chat name from first message if this is the first message
    if (messages.length === 0 && !chatNames[chatId]) {
      const generatedName = generateChatName(inputMessage);
      saveChatName(chatId, generatedName);
    }

    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch(`http://localhost:8000/agent/chat/${chatId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
        }),
      });

      const data = await response.json();

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: data.response || 'Sorry, I could not process your request.',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'Sorry, there was an error processing your request. Please try again.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const getChatDisplayName = (chatId: string): string => {
    return chatNames[chatId] || `${chatId.slice(0, 8)}...${chatId.slice(-4)}`;
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar for chat list */}
      <aside className="w-64 bg-white border-r flex flex-col">
        <div className="p-4 border-b flex items-center justify-between">
          <span className="font-bold text-lg">Cases</span>
          <button
            className="bg-blue-600 text-white px-3 py-1 rounded text-xs hover:bg-blue-700"
            onClick={startNewChat}
          >
            + New Case
          </button>
        </div>
        <div className="flex-1 overflow-y-auto">
          {loadingChats ? (
            <div className="p-4 text-gray-400">Loading cases...</div>
          ) : chatList.length === 0 ? (
            <div className="p-4 text-gray-400">No cases yet.</div>
          ) : (
            <ul>
              {chatList.map((id) => (
                <li key={id}>
                  <button
                    className={`w-full text-left px-4 py-2 font-sans font-medium rounded transition-colors duration-150 ${chatId === id ? 'bg-blue-100 text-blue-900' : 'hover:bg-blue-50 text-gray-700'}`}
                    onClick={() => setChatId(id)}
                  >
                    {getChatDisplayName(id)}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </aside>

      {/* Main chat area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-6">
              <div className="flex items-center">
                <Link href="/" className="text-2xl font-bold text-gray-900 hover:text-blue-600">
                  Wakili Quick1
                </Link>
                <span className="ml-2 text-sm text-gray-500">Legal Chat</span>
              </div>
              <nav className="flex space-x-8">
                <Link href="/upload" className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">
                  Document Upload
                </Link>
                <Link href="/chat" className="text-blue-600 px-3 py-2 rounded-md text-sm font-medium">
                  Legal Chat
                </Link>
                <Link href="/research" className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">
                  Legal Research
                </Link>
              </nav>
            </div>
          </div>
        </header>

        {/* Chat ID Display */}
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pt-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs text-gray-500">Case ID:</span>
            <span className="text-xs font-mono bg-gray-200 px-2 py-1 rounded select-all border border-gray-300">{chatId}</span>
          </div>
        </div>

        {/* Chat Interface */}
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 flex flex-col">
          <div className="bg-white rounded-lg shadow-lg h-[600px] flex flex-col">
            {/* Chat Header */}
            <div className="bg-blue-600 text-white px-6 py-4 rounded-t-lg">
              <h2 className="text-lg font-semibold">Legal Assistant</h2>
              <p className="text-blue-100 text-sm">Ask me anything about Kenyan law and legal procedures</p>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.length === 0 && (
                <div className="text-center text-gray-500 py-8">
                  <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                  </div>
                  <p className="text-lg font-medium mb-2">Welcome to Wakili Quick1</p>
                  <p>Start by asking a legal question or uploading case documents above.</p>
                  <ul className="mt-2 text-sm space-y-1">
                    <li>• Legal procedures and requirements</li>
                    <li>• Document analysis and advice</li>
                    <li>• Research on Kenyan laws</li>
                    <li>• Legal document drafting</li>
                  </ul>
                </div>
              )}

              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {message.type === 'file' ? (
                    <div className="max-w-xs lg:max-w-md px-4 py-2 rounded-lg bg-yellow-50 border border-yellow-200 text-gray-900 flex flex-col">
                      <span className="font-semibold text-sm mb-1">📎 File Uploaded</span>
                      <a
                        href={message.fileUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 underline text-xs break-all"
                      >
                        {message.fileName}
                      </a>
                      <span className="text-xs text-gray-500">{(message.fileSize! / 1024).toFixed(1)} KB</span>
                      <span className="text-xs text-gray-400 mt-1">{message.timestamp.toLocaleTimeString()}</span>
                    </div>
                  ) : message.type === 'assistant' ? (
                    <div className="max-w-xs lg:max-w-md px-4 py-2 rounded-lg bg-gray-100 text-gray-900">
                      <div className="prose prose-sm max-w-none prose-a:text-blue-600 prose-a:underline prose-h2:text-lg prose-h3:text-base prose-strong:text-blue-800 prose-li:my-1 prose-table:text-xs prose-table:my-2 prose-th:bg-gray-200 prose-td:bg-gray-50 prose-blockquote:border-l-4 prose-blockquote:border-blue-300 prose-blockquote:pl-4 prose-blockquote:text-gray-600">
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            a: (props) => (
                              <a {...props} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline" />
                            ),
                          }}
                        >
                          {message.content}
                        </ReactMarkdown>
                      </div>
                      <p className="text-xs mt-1 text-gray-500">{message.timestamp.toLocaleTimeString()}</p>
                    </div>
                  ) : (
                    <div className="max-w-xs lg:max-w-md px-4 py-2 rounded-lg bg-blue-600 text-white">
                      <p className="text-sm">{message.content}</p>
                      <p className="text-xs mt-1 text-blue-100">{message.timestamp.toLocaleTimeString()}</p>
                    </div>
                  )}
                </div>
              ))}

              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 text-gray-900 max-w-xs lg:max-w-md px-4 py-2 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                      <span className="text-sm text-gray-500">Thinking...</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Input and Upload */}
            <div className="border-t p-4 flex space-x-4 items-center">
              <button
                className={`w-10 h-10 flex items-center justify-center rounded-full bg-gray-100 hover:bg-blue-100 border border-gray-300 text-xl text-gray-600 focus:outline-none`}
                onClick={() => fileInputRef.current?.click()}
                title="Upload case documents"
                type="button"
              >
                <span className="sr-only">Upload</span>
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 16V4m0 0l-4 4m4-4l4 4M4 20h16" />
                </svg>
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept=".pdf,.docx,.doc,.jpg,.jpeg,.png"
                  className="hidden"
                  onChange={(e) => e.target.files && handleFileSelect(e.target.files)}
                />
              </button>
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask a legal question..."
                className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent font-sans text-base text-gray-900"
                style={{ fontFamily: 'Inter, Arial, Helvetica, sans-serif' }}
                disabled={isLoading || !chatId}
              />
              <button
                onClick={() => { sendMessage(); }}
                disabled={isLoading || !inputMessage.trim() || !chatId}
                className={`px-6 py-2 rounded-lg font-medium transition-colors font-sans text-base ${isLoading || !inputMessage.trim() || !chatId ? 'bg-gray-200 text-gray-600 cursor-not-allowed' : 'bg-blue-600 text-white hover:bg-blue-700'}`}
                style={{ fontFamily: 'Inter, Arial, Helvetica, sans-serif' }}
              >
                Send
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
import React from 'react';
import { 
  ask, 
  getSavedManagerId, 
  getChats, 
  createChat, 
  deleteChat, 
  getChatHistory, 
  type ChatSession 
} from './api/client';
import { useManager } from './context/ManagerContext';
import Header from './components/Header';
import WelcomeScreen from './components/WelcomeScreen';
import ChatMessages from './components/ChatMessages';
import ChatInput from './components/ChatInput';
import ChatSidebar from './components/ChatSidebar';

type Message = {
  role: 'user' | 'assistant';
  content: string;
};

const FPLChatbot = () => {
  const [messages, setMessages] = React.useState<Message[]>([]);
  const [input, setInput] = React.useState<string>('');
  const [isLoading, setIsLoading] = React.useState<boolean>(false);
  const [showSuggestions, setShowSuggestions] = React.useState<boolean>(true);
  
  // Sidebar & Session State
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(false);
  const [sessions, setSessions] = React.useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = React.useState<string | null>(null);

  const messagesEndRef = React.useRef<HTMLDivElement | null>(null);

  const [theme, setTheme] = React.useState<'dark' | 'light'>(() => {
    if (typeof window !== 'undefined') {
      return (localStorage.getItem('fpl_theme') as 'dark' | 'light') || 'dark';
    }
    return 'dark';
  });

  const {
    managerId,
    setManagerId,
    managerData,
    isLoading: managerLoading,
    error: managerError,
    handleManagerSubmit,
    clearManager,
  } = useManager();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    localStorage.setItem('fpl_theme', newTheme);
  };

  React.useEffect(() => {
    if (theme === 'light') {
      document.documentElement.classList.add('light');
    } else {
      document.documentElement.classList.remove('light');
    }
  }, [theme]);

  React.useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load chat sessions on mount
  React.useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const data = await getChats();
      setSessions(data);
    } catch (err) {
      console.error("Failed to load sessions", err);
    }
  };

  const loadSessionHistory = async (sessionId: string) => {
    setIsLoading(true);
    try {
      const data = await getChatHistory(sessionId);
      const mappedMessages: Message[] = data.history.map((msg: any) => ({
        role: msg.type === 'HumanMessage' ? 'user' : 'assistant',
        content: msg.content
      }));
      setMessages(mappedMessages);
      setShowSuggestions(mappedMessages.length === 0);
    } catch (err) {
        console.error("Failed to load history", err);
    } finally {
        setIsLoading(false);
    }
  };

  const handleNewChat = () => {
      setCurrentSessionId(null);
      setMessages([]);
      setShowSuggestions(true);
      setIsSidebarOpen(false);
  };

  const handleSelectSession = (sessionId: string) => {
      if (sessionId === currentSessionId) {
          setIsSidebarOpen(false);
          return;
      }
      setCurrentSessionId(sessionId);
      loadSessionHistory(sessionId);
      setIsSidebarOpen(false);
  };

  const handleDeleteChat = async (sessionId: string, e: React.MouseEvent) => {
      e.stopPropagation();
      if (!window.confirm("Delete this chat?")) return;
      try {
          await deleteChat(sessionId);
          setSessions(prev => prev.filter(s => s.session_id !== sessionId));
          if (currentSessionId === sessionId) {
              handleNewChat();
          }
      } catch (err) {
          console.error("Failed to delete chat", err);
      }
  };

  const handleSend = async (text: string = input) => {
    if (!text.trim() || isLoading) return;

    setShowSuggestions(false);
    const userMessage: Message = { role: 'user', content: text };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      let activeSessionId = currentSessionId;
      
      // Create session if first message
      if (!activeSessionId) {
          const newSession = await createChat();
          activeSessionId = newSession.session_id;
          setCurrentSessionId(activeSessionId);
          loadSessions(); 
      }

      const managerId = getSavedManagerId();
      const res = await ask({ query: text, session_id: activeSessionId!, manager_id: managerId });
      
      const botResponse: Message = { role: 'assistant', content: res.answer };
      setMessages(prev => [...prev, botResponse]);
      
      loadSessions();
      
    } catch (err: any) {
      const botResponse: Message = {
        role: 'assistant',
        content: `Sorry, I couldn't process that. ${err?.message ?? ''}`.trim(),
      };
      setMessages(prev => [...prev, botResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (text: string) => {
    handleSend(text);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const isDark = theme === 'dark';

  return (
    <div className={`min-h-screen transition-colors duration-300 ${isDark ? 'bg-slate-950' : 'bg-slate-50'}`}>
      <ChatSidebar 
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        sessions={sessions}
        currentSessionId={currentSessionId}
        onSelectSession={handleSelectSession}
        onNewChat={handleNewChat}
        onDeleteChat={handleDeleteChat}
        isDark={isDark}
      />
      
      <Header
        theme={theme}
        toggleTheme={toggleTheme}
        managerData={managerData}
        managerId={managerId || ''}
        setManagerId={setManagerId}
        managerLoading={managerLoading}
        managerError={managerError}
        handleManagerSubmit={handleManagerSubmit}
        clearManager={clearManager}
        onMenuClick={() => setIsSidebarOpen(true)}
      />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-4 sm:py-8 flex flex-col min-h-[calc(100vh-72px)]">
        {messages.length === 0 ? (
          <WelcomeScreen
            managerName={managerData?.name}
            showSuggestions={showSuggestions}
            onSuggestionClick={handleSuggestionClick}
            isDark={isDark}
          />
        ) : (
          <ChatMessages
            messages={messages}
            isLoading={isLoading}
            isDark={isDark}
            messagesEndRef={messagesEndRef}
          />
        )}

        <ChatInput
          input={input}
          setInput={setInput}
          isLoading={isLoading}
          onSend={handleSend}
          onKeyPress={handleKeyPress}
          isDark={isDark}
        />
      </div>
    </div>
  );
};

export default FPLChatbot;
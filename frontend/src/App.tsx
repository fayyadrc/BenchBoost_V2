import React from 'react';
import { Link } from 'react-router-dom';
import { Send, Users, TrendingUp, BarChart3, Target, Calendar, Zap, Loader, User, Trophy, X, Moon, Sun, MessageSquare, ArrowUp } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { ask, getOrCreateSessionId, getSavedManagerId } from './api/client';
import { useManager } from './context/ManagerContext';

type Message = {
  role: 'user' | 'assistant';
  content: string;
};

type IconComponent = React.ComponentType<React.SVGProps<SVGSVGElement>>;

const FPLChatbot = () => {
  const [messages, setMessages] = React.useState<Message[]>([]);
  const [input, setInput] = React.useState<string>('');
  const [isLoading, setIsLoading] = React.useState<boolean>(false);
  const [showSuggestions, setShowSuggestions] = React.useState<boolean>(true);
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

  const suggestions: Array<{ icon: IconComponent; text: string; color: string }> = [
    { icon: Users, text: 'Who should I captain this gameweek?', color: '#FF6B35' },
    { icon: TrendingUp, text: 'Analyze my team for next 3 fixtures', color: '#00A878' },
    { icon: BarChart3, text: 'Best differentials under £7m', color: '#004E89' },
    { icon: Target, text: 'Transfer recommendations', color: '#E63946' },
    { icon: Calendar, text: 'Best fixture runs', color: '#9B59B6' },
    { icon: Zap, text: 'Template team weaknesses', color: '#F39C12' }
  ];

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

  const handleSend = async (text: string = input) => {
    if (!text.trim() || isLoading) return;

    setShowSuggestions(false);
    const userMessage: Message = { role: 'user', content: text };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const sessionId = getOrCreateSessionId();
      const managerId = getSavedManagerId();
      const res = await ask({ query: text, session_id: sessionId, manager_id: managerId });
      const botResponse: Message = { role: 'assistant', content: res.answer };
      setMessages(prev => [...prev, botResponse]);
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
    <div className={`min-h-screen transition-colors duration-300 ${isDark ? 'bg-slate-950' : 'bg-slate-50'
      }`}>
      {/* Header - Editorial Style */}
      <header className={`border-b-2 ${isDark ? 'border-white/20 bg-slate-950' : 'border-slate-900 bg-white'}`}>
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <h1 className={`text-2xl font-black uppercase tracking-tighter ${isDark ? 'text-white' : 'text-slate-900'
                }`}>
                Bench<span className={isDark ? 'text-blue-600' : 'text-blue-600'} style={isDark ? { color: '#003566' } : {}}>Boost</span>
              </h1>

              <div className={`h-8 w-px ${isDark ? 'bg-white/20' : 'bg-slate-300'}`} />

              <Link
                to="/manager"
                className={`px-4 py-2 border-2 font-bold uppercase text-xs tracking-wide transition-all hover:scale-105 ${isDark
                  ? 'border-white/20 text-white hover:bg-white hover:text-slate-900'
                  : 'border-slate-900 text-slate-900 hover:bg-slate-900 hover:text-white'
                  }`}
              >
                <span className="flex items-center gap-2">
                  <User className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">Manager</span>
                </span>
              </Link>
            </div>

            {/* Right Side */}
            <div className="flex items-center gap-3">
              {managerData ? (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className={`flex items-center gap-4 px-5 py-3 border-2 ${isDark ? 'border-white/20 bg-slate-900' : 'border-slate-900 bg-white'
                    }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="text-sm">
                      <p className={`font-black uppercase ${isDark ? 'text-white' : 'text-slate-900'}`}>
                        {managerData.team_name}
                      </p>
                      <p className={`text-xs ${isDark ? 'text-white/50' : 'text-slate-500'}`}>
                        {managerData.name}
                      </p>
                    </div>
                  </div>
                  <div className={`h-8 w-px ${isDark ? 'bg-white/20' : 'bg-slate-300'}`} />
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-1.5">
                      <Trophy className="w-4 h-4 text-yellow-500" />
                      <span className={`font-mono text-sm font-bold ${isDark ? 'text-white/80' : 'text-slate-600'}`}>
                        {managerData.overall_rank?.toLocaleString() ?? 'N/A'}
                      </span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <ArrowUp className="w-4 h-4 text-green-500" />
                      <span className={`font-mono text-sm font-bold ${isDark ? 'text-white/80' : 'text-slate-600'}`}>
                        {managerData.gameweek_points}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={clearManager}
                    className={`p-1.5 transition-colors ${isDark ? 'hover:bg-white/10' : 'hover:bg-slate-100'}`}
                    title="Clear manager"
                  >
                    <X className={`w-4 h-4 ${isDark ? 'text-white/60' : 'text-slate-400'}`} />
                  </button>
                </motion.div>
              ) : (
                <form onSubmit={handleManagerSubmit} className="flex items-center gap-3">
                  <input
                    type="text"
                    value={managerId}
                    onChange={(e) => setManagerId(e.target.value)}
                    placeholder="FPL ID"
                    className={`border-2 px-4 py-2.5 text-sm font-bold uppercase w-36 focus:outline-none transition-all ${isDark
                      ? 'bg-slate-900 border-white/20 text-white placeholder-white/30'
                      : 'bg-white border-slate-900 text-slate-900 placeholder-slate-400 focus:border-blue-600'
                      }`}
                    style={isDark ? { borderColor: 'rgba(255, 255, 255, 0.2)' } : {}}
                    onFocus={(e) => isDark && (e.target.style.borderColor = '#003566')}
                    onBlur={(e) => isDark && (e.target.style.borderColor = 'rgba(255, 255, 255, 0.2)')}
                    disabled={managerLoading}
                  />
                  <button
                    type="submit"
                    disabled={!managerId.trim() || managerLoading}
                    className={`px-5 py-2.5 text-sm font-black uppercase transition-all disabled:opacity-30 ${isDark
                      ? 'text-white'
                      : 'bg-slate-900 text-white hover:bg-slate-800'
                      }`}
                    style={isDark ? { backgroundColor: '#003566', borderColor: '#003566' } : {}}
                    onMouseEnter={(e) => isDark && !managerLoading && managerId.trim() && (e.currentTarget.style.backgroundColor = '#004080')}
                    onMouseLeave={(e) => isDark && (e.currentTarget.style.backgroundColor = '#003566')}
                  >
                    {managerLoading ? <Loader className="w-4 h-4 animate-spin" /> : 'Load'}
                  </button>
                </form>
              )}

              <button
                onClick={toggleTheme}
                className={`p-2 border-2 transition-all hover:scale-105 ${isDark
                  ? 'border-white/20 text-white hover:border-white/40'
                  : 'border-slate-900 text-slate-900 hover:bg-slate-900 hover:text-white'
                  }`}
              >
                {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <AnimatePresence>
            {managerError && (
              <motion.p
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="text-red-500 text-xs mt-2 font-bold uppercase"
              >
                {managerError}
              </motion.p>
            )}
          </AnimatePresence>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-6 py-8 flex flex-col min-h-[calc(100vh-72px)]">
        {messages.length === 0 ? (
          <motion.div
            className="flex-1 flex flex-col"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            {/* Greeting - Brutalist */}
            <motion.div
              className="mb-12"
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.5 }}
            >
              <div className={`border-l-4 pl-4 ${isDark ? '' : 'border-blue-600'}`} style={isDark ? { borderLeftColor: '#003566' } : {}}>
                <h2 className={`text-4xl font-black uppercase tracking-tighter ${isDark ? 'text-white' : 'text-slate-900'
                  }`}>
                  Hello,
                </h2>
                <p className={`text-2xl font-bold uppercase ${isDark ? 'text-white/60' : 'text-slate-500'
                  }`}>
                  {managerData?.name?.split(' ')[0] || 'Manager'}
                </p>
              </div>
            </motion.div>

            <div className="flex-grow"></div>

            {/* Suggestions - Compact Cards */}
            {showSuggestions && (
              <motion.div
                className="grid grid-cols-1 md:grid-cols-3 gap-3 w-full mb-8"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4, duration: 0.5 }}
              >
                <AnimatePresence>
                  {suggestions.slice(0, 3).map((suggestion, idx) => (
                    <motion.button
                      key={idx}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.1 * idx, duration: 0.4 }}
                      whileHover={{ y: -2 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => handleSuggestionClick(suggestion.text)}
                      className={`group cursor-pointer text-left border-l-4 p-4 transition-all ${isDark
                        ? 'bg-slate-900 hover:bg-slate-800 border-white/20'
                        : 'bg-white hover:bg-slate-50 border-slate-900'
                        }`}
                      style={{ borderLeftColor: suggestion.color }}
                    >
                      <div className="flex items-start gap-3">
                        <div
                          className="flex items-center justify-center w-8 h-8 shrink-0"
                          style={{ backgroundColor: suggestion.color }}
                        >
                          <suggestion.icon className="w-4 h-4 text-white" />
                        </div>
                        <p className={`text-sm font-bold leading-tight ${isDark ? 'text-white/90' : 'text-slate-700'
                          }`}>
                          {suggestion.text}
                        </p>
                      </div>
                    </motion.button>
                  ))}
                </AnimatePresence>
              </motion.div>
            )}
          </motion.div>
        ) : (
          <motion.div
            className="flex-1 overflow-y-auto mb-6 space-y-4 pr-2"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.4 }}
          >
            <AnimatePresence mode="popLayout">
              {messages.map((msg, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.3 }}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`px-4 py-3 ${msg.role === 'user'
                      ? `max-w-xs lg:max-w-md xl:max-w-lg border-2 text-white ${isDark ? '' : 'bg-slate-900 border-slate-800'}`
                      : `max-w-full lg:max-w-2xl xl:max-w-3xl border-2 ${isDark ? 'bg-slate-900 text-white border-white/20' : 'bg-white text-slate-900 border-slate-200'
                      }`
                      }`}
                    style={msg.role === 'user' && isDark ? { backgroundColor: '#003566', borderColor: '#003566' } : msg.role === 'user' ? { backgroundColor: '#1e293b', borderColor: '#0f172a' } : {}}
                  >
                    {msg.role === 'assistant' ? (
                      <div className={`text-sm leading-relaxed break-words prose prose-sm max-w-none ${isDark ? 'prose-invert' : ''
                        }`}>
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            p: ({ node, ...props }) => <p className={`mb-3 last:mb-0 ${isDark ? 'text-white/90' : 'text-slate-700'}`} {...props} />,
                            ul: ({ node, ...props }) => (
                              <ul className={`list-disc pl-5 space-y-1 mb-3 ${isDark ? 'text-white/90' : 'text-slate-700'}`} {...props} />
                            ),
                            ol: ({ node, ...props }) => (
                              <ol className={`list-decimal pl-5 space-y-1 mb-3 ${isDark ? 'text-white/90' : 'text-slate-700'}`} {...props} />
                            ),
                            li: ({ node, ...props }) => (
                              <li className={`pl-1 ${isDark ? 'text-white/90' : 'text-slate-700'}`} {...props} />
                            ),
                            strong: ({ node, ...props }) => (
                              <strong className={`font-black ${isDark ? 'text-white' : 'text-slate-900'}`} {...props} />
                            ),
                            em: ({ node, ...props }) => (
                              <em className={`italic ${isDark ? 'text-white/80' : 'text-slate-600'}`} {...props} />
                            ),
                            h1: ({ node, ...props }) => (
                              <h1 className={`text-xl font-black uppercase mb-3 mt-4 first:mt-0 ${isDark ? 'text-white' : 'text-slate-900'}`} {...props} />
                            ),
                            h2: ({ node, ...props }) => (
                              <h2 className={`text-lg font-black uppercase mb-2 mt-4 first:mt-0 ${isDark ? 'text-white' : 'text-slate-900'}`} {...props} />
                            ),
                            h3: ({ node, ...props }) => (
                              <h3 className={`text-base font-bold mb-2 mt-3 first:mt-0 ${isDark ? 'text-white' : 'text-slate-900'}`} {...props} />
                            ),
                            table: ({ node, ...props }) => (
                              <div className={`overflow-x-auto my-4 border-2 ${isDark ? 'border-white/20' : 'border-slate-200'}`}>
                                <table className="w-full text-left text-sm" {...props} />
                              </div>
                            ),
                            thead: ({ node, ...props }) => (
                              <thead className={`font-black uppercase text-xs ${isDark ? 'bg-white/10 text-white' : 'bg-slate-100 text-slate-900'}`} {...props} />
                            ),
                            tbody: ({ node, ...props }) => (
                              <tbody className={`divide-y-2 ${isDark ? 'divide-white/10' : 'divide-slate-200'}`} {...props} />
                            ),
                            tr: ({ node, ...props }) => (
                              <tr className={`transition-colors ${isDark ? 'hover:bg-white/5' : 'hover:bg-slate-50'}`} {...props} />
                            ),
                            th: ({ node, ...props }) => (
                              <th className={`px-3 py-2 font-black whitespace-nowrap ${isDark ? 'text-white' : 'text-slate-900'}`} {...props} />
                            ),
                            td: ({ node, ...props }) => (
                              <td className={`px-3 py-2 whitespace-nowrap font-mono text-xs ${isDark ? 'text-white/90' : 'text-slate-700'}`} {...props} />
                            ),
                            code: ({ node, className, children, ...props }) => {
                              const isInline = !className;
                              return isInline ? (
                                <code className={`px-1.5 py-0.5 text-xs font-mono border ${isDark ? 'bg-white/10 text-emerald-400 border-white/20' : 'bg-slate-100 text-emerald-600 border-slate-200'
                                  }`} {...props}>
                                  {children}
                                </code>
                              ) : (
                                <code className={`block p-3 text-xs font-mono overflow-x-auto border-2 ${isDark ? 'bg-black/40 text-white/90 border-white/20' : 'bg-slate-100 text-slate-800 border-slate-200'
                                  }`} {...props}>
                                  {children}
                                </code>
                              );
                            },
                            pre: ({ node, ...props }) => (
                              <pre className="my-3" {...props} />
                            ),
                            blockquote: ({ node, ...props }) => (
                              <blockquote className={`border-l-4 border-blue-500 pl-4 my-3 italic ${isDark ? 'text-white/80' : 'text-slate-600'}`} {...props} />
                            ),
                            hr: ({ node, ...props }) => (
                              <hr className={`my-4 border-2 ${isDark ? 'border-white/20' : 'border-slate-200'}`} {...props} />
                            ),
                            a: ({ node, ...props }) => (
                              <a className="text-blue-500 hover:text-blue-400 underline underline-offset-2 font-bold" {...props} />
                            ),
                          }}
                        >
                          {msg.content}
                        </ReactMarkdown>
                      </div>
                    ) : (
                      <p className="text-sm font-medium leading-relaxed whitespace-pre-wrap break-words">
                        {msg.content}
                      </p>
                    )}
                  </div>
                </motion.div>
              ))}

              {isLoading && (
                <motion.div
                  key="loading"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.3 }}
                  className="flex justify-start"
                >
                  <div className={`px-4 py-3 border-2 ${isDark ? 'bg-slate-900 text-white border-white/20' : 'bg-white text-slate-900 border-slate-200'
                    }`}>
                    <div className="flex items-center gap-2">
                      <Loader className={`w-4 h-4 animate-spin ${isDark ? 'text-white' : 'text-slate-600'}`} />
                      <span className={`text-sm font-bold uppercase ${isDark ? 'text-white/60' : 'text-slate-500'}`}>
                        Analyzing...
                      </span>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
            <div ref={messagesEndRef} />
          </motion.div>
        )}

        {/* Input - Brutalist */}
        <motion.div
          className="shrink-0"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.4 }}
        >
          <div className={`border-2 transition-all ${isDark
            ? 'bg-slate-900 border-white/20'
            : 'bg-white border-slate-900 focus-within:border-blue-600'
            }`}
            style={isDark ? { borderColor: 'rgba(255, 255, 255, 0.2)' } : {}}
            onFocus={(e) => isDark && (e.currentTarget.style.borderColor = '#003566')}
            onBlur={(e) => isDark && (e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.2)')}>
            <div className="flex items-center gap-3 p-4">
              <MessageSquare className={`w-5 h-5 shrink-0 ${isDark ? 'text-white/40' : 'text-slate-400'}`} />
              <textarea
                className={`flex-1 bg-transparent border-none outline-none resize-none text-sm font-medium max-h-32 ${isDark ? 'text-white placeholder-white/30' : 'text-slate-900 placeholder-slate-400'
                  }`}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about FPL strategy..."
                rows={1}
                disabled={isLoading}
              />
              <button
                onClick={() => handleSend()}
                disabled={!input.trim() || isLoading}
                className={`shrink-0 flex items-center justify-center w-10 h-10 border-2 transition-all ${input.trim() && !isLoading
                  ? isDark
                    ? 'text-white'
                    : 'bg-slate-900 border-slate-800 text-white hover:bg-slate-800'
                  : isDark
                    ? 'bg-white/5 border-white/10 text-white/20 cursor-not-allowed'
                    : 'bg-slate-100 border-slate-200 text-slate-300 cursor-not-allowed'
                  }`}
                style={input.trim() && !isLoading && isDark ? { backgroundColor: '#003566', borderColor: '#003566' } : {}}
                onMouseEnter={(e) => input.trim() && !isLoading && isDark && (e.currentTarget.style.backgroundColor = '#004080')}
                onMouseLeave={(e) => input.trim() && !isLoading && isDark && (e.currentTarget.style.backgroundColor = '#003566')}
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default FPLChatbot;
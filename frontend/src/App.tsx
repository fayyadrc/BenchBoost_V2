import React from 'react';
import { Send, Users, TrendingUp, BarChart3, Target, Calendar, Zap, Loader, User, Trophy, Wallet, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { ask, getOrCreateSessionId, getManagerInfo } from './api/client';
import type { ManagerData } from './api/client';

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
  
  // Manager state
  const [managerId, setManagerId] = React.useState<string>('');
  const [managerData, setManagerData] = React.useState<ManagerData | null>(null);
  const [managerLoading, setManagerLoading] = React.useState<boolean>(false);
  const [managerError, setManagerError] = React.useState<string>('');

  const suggestions: Array<{ icon: IconComponent; text: string }> = [
    { icon: Users, text: 'Who should I captain this gameweek?' },
    { icon: TrendingUp, text: 'Analyze my team selection for the next 3 fixtures' },
    { icon: BarChart3, text: 'Best differential options under £7m' },
    { icon: Target, text: 'Transfer recommendations based on form' },
    { icon: Calendar, text: 'Which players have the best fixture run?' },
    { icon: Zap, text: 'Show me template team weaknesses' }
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

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
      const res = await ask({ query: text, session_id: sessionId });
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

  const handleManagerSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!managerId.trim() || managerLoading) return;
    
    setManagerLoading(true);
    setManagerError('');
    
    try {
      const id = parseInt(managerId.trim(), 10);
      if (isNaN(id)) {
        throw new Error('Please enter a valid numeric ID');
      }
      const data = await getManagerInfo(id);
      setManagerData(data);
      localStorage.setItem('fpl_manager_id', managerId.trim());
    } catch (err: any) {
      setManagerError(err?.message || 'Failed to fetch manager data');
      setManagerData(null);
    } finally {
      setManagerLoading(false);
    }
  };

  const clearManager = () => {
    setManagerData(null);
    setManagerId('');
    setManagerError('');
    localStorage.removeItem('fpl_manager_id');
  };

  // Load saved manager ID on mount
  React.useEffect(() => {
    const savedId = localStorage.getItem('fpl_manager_id');
    if (savedId) {
      setManagerId(savedId);
      getManagerInfo(parseInt(savedId, 10))
        .then(setManagerData)
        .catch(() => localStorage.removeItem('fpl_manager_id'));
    }
  }, []);

  return (
    <div className="min-h-screen bg-transparent text-white font-sans">
      {/* Navbar */}
      <nav className="sticky top-0 z-50 bg-black/40 backdrop-blur-md border-b border-white/10">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex items-center justify-between gap-4">
            {/* Logo */}
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <span className="text-lg font-bold text-white hidden sm:block">BenchBoost</span>
            </div>

            {/* Manager ID Input / Display */}
            <div className="flex items-center gap-3">
              {managerData ? (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="flex items-center gap-3 bg-white/10 rounded-xl px-4 py-2 border border-white/10"
                >
                  <div className="flex items-center gap-2">
                    <User className="w-4 h-4 text-blue-400" />
                    <div className="text-sm">
                      <p className="font-semibold text-white">{managerData.team_name}</p>
                      <p className="text-white/60 text-xs">{managerData.name}</p>
                    </div>
                  </div>
                  <div className="h-8 w-px bg-white/20" />
                  <div className="flex items-center gap-4 text-xs">
                    <div className="flex items-center gap-1">
                      <Trophy className="w-3.5 h-3.5 text-yellow-400" />
                      <span className="text-white/80">{managerData.overall_rank?.toLocaleString() ?? 'N/A'}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <TrendingUp className="w-3.5 h-3.5 text-green-400" />
                      <span className="text-white/80">{managerData.overall_points} pts</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Wallet className="w-3.5 h-3.5 text-emerald-400" />
                      <span className="text-white/80">£{managerData.team_value.toFixed(1)}m</span>
                    </div>
                  </div>
                  <button
                    onClick={clearManager}
                    className="p-1 hover:bg-white/10 rounded-full transition-colors ml-1"
                    title="Clear manager"
                  >
                    <X className="w-4 h-4 text-white/60 hover:text-white" />
                  </button>
                </motion.div>
              ) : (
                <form onSubmit={handleManagerSubmit} className="flex items-center gap-2">
                  <div className="relative">
                    <input
                      type="text"
                      value={managerId}
                      onChange={(e) => setManagerId(e.target.value)}
                      placeholder="Enter FPL ID"
                      className="bg-white/10 border border-white/20 rounded-lg px-3 py-1.5 text-sm text-white placeholder-white/40 w-32 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all"
                      disabled={managerLoading}
                    />
                    {managerLoading && (
                      <div className="absolute right-2 top-1/2 -translate-y-1/2">
                        <Loader className="w-4 h-4 text-white/60 animate-spin" />
                      </div>
                    )}
                  </div>
                  <button
                    type="submit"
                    disabled={!managerId.trim() || managerLoading}
                    className="bg-blue-600 hover:bg-blue-500 disabled:bg-white/10 disabled:text-white/40 text-white text-sm px-3 py-1.5 rounded-lg font-medium transition-colors"
                  >
                    Load
                  </button>
                </form>
              )}
            </div>
          </div>
          
          {/* Manager Error */}
          <AnimatePresence>
            {managerError && (
              <motion.p
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="text-red-400 text-xs mt-2 text-right"
              >
                {managerError}
              </motion.p>
            )}
          </AnimatePresence>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col min-h-[calc(100vh-72px)]">
        {messages.length === 0 ? (
          <motion.div
            className="flex-1 flex flex-col"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            {/* Greeting */}
            <motion.div 
              className="mb-16"
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.5 }}
            >
              <div>
                <h1 className="text-3xl font-bold text-white">Greetings,</h1>
                <p className="text-3xl font-bold text-white/80">manager</p>
              </div>
            </motion.div>

            {/* Spacer to push suggestions down */}
            <div className="flex-grow"></div>

            {/* Suggestions */}
            {showSuggestions && (
              <motion.div
                className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full mb-8"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4, duration: 0.5 }}
              >
                <AnimatePresence>
                  {suggestions.slice(0, 3).map((suggestion, idx) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.1 * idx, duration: 0.4 }}
                      whileHover={{ y: -4, boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)' }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => handleSuggestionClick(suggestion.text)}
                      className="group cursor-pointer"
                    >
                      <div className="relative overflow-hidden rounded-2xl bg-black/20 border border-white/10 p-5 h-40 flex flex-col justify-between hover:border-white/30 hover:bg-black/30 transition-all duration-300 shadow-sm hover:shadow-lg backdrop-blur-sm">
                        <div className="shrink-0">
                            <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-white/10 group-hover:bg-white/20 transition-all duration-300">
                              <suggestion.icon className="w-5 h-5 text-white" />
                            </div>
                          </div>
                        <p className="text-md font-semibold text-white/90 group-hover:text-white transition-colors duration-300">
                          {suggestion.text}
                        </p>
                      </div>
                    </motion.div>
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
                    className={`px-4 py-3 rounded-2xl ${
                      msg.role === 'user'
                        ? 'max-w-xs lg:max-w-md xl:max-w-lg bg-blue-600 text-white'
                        : 'max-w-full lg:max-w-2xl xl:max-w-3xl bg-black/20 text-white border border-white/10 backdrop-blur-sm'
                    }`}
                  >
                    {msg.role === 'assistant' ? (
                      <div className="text-sm leading-relaxed break-words prose prose-invert prose-sm max-w-none">
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            p: ({node, ...props}) => <p className="mb-3 last:mb-0 text-white/90" {...props} />,
                            ul: ({ node, ...props }) => (
                              <ul className="list-disc pl-5 space-y-1 mb-3 text-white/90" {...props} />
                            ),
                            ol: ({ node, ...props }) => (
                              <ol className="list-decimal pl-5 space-y-1 mb-3 text-white/90" {...props} />
                            ),
                            li: ({ node, ...props }) => (
                              <li className="pl-1 text-white/90" {...props} />
                            ),
                            strong: ({ node, ...props }) => (
                              <strong className="font-bold text-white" {...props} />
                            ),
                            em: ({ node, ...props }) => (
                              <em className="italic text-white/80" {...props} />
                            ),
                            h1: ({ node, ...props }) => (
                              <h1 className="text-xl font-bold text-white mb-3 mt-4 first:mt-0" {...props} />
                            ),
                            h2: ({ node, ...props }) => (
                              <h2 className="text-lg font-bold text-white mb-2 mt-4 first:mt-0" {...props} />
                            ),
                            h3: ({ node, ...props }) => (
                              <h3 className="text-base font-semibold text-white mb-2 mt-3 first:mt-0" {...props} />
                            ),
                            table: ({ node, ...props }) => (
                              <div className="overflow-x-auto my-4 rounded-lg border border-white/20">
                                <table className="w-full text-left text-sm" {...props} />
                              </div>
                            ),
                            thead: ({ node, ...props }) => (
                              <thead className="bg-white/10 text-white font-semibold" {...props} />
                            ),
                            tbody: ({ node, ...props }) => (
                              <tbody className="divide-y divide-white/10" {...props} />
                            ),
                            tr: ({ node, ...props }) => (
                              <tr className="hover:bg-white/5 transition-colors" {...props} />
                            ),
                            th: ({ node, ...props }) => (
                              <th className="px-3 py-2 text-white font-semibold whitespace-nowrap" {...props} />
                            ),
                            td: ({ node, ...props }) => (
                              <td className="px-3 py-2 text-white/90 whitespace-nowrap" {...props} />
                            ),
                            code: ({ node, className, children, ...props }) => {
                              const isInline = !className;
                              return isInline ? (
                                <code className="bg-white/10 text-emerald-400 px-1.5 py-0.5 rounded text-xs font-mono" {...props}>
                                  {children}
                                </code>
                              ) : (
                                <code className="block bg-black/40 p-3 rounded-lg text-xs font-mono overflow-x-auto text-white/90" {...props}>
                                  {children}
                                </code>
                              );
                            },
                            pre: ({ node, ...props }) => (
                              <pre className="my-3" {...props} />
                            ),
                            blockquote: ({ node, ...props }) => (
                              <blockquote className="border-l-4 border-blue-500 pl-4 my-3 text-white/80 italic" {...props} />
                            ),
                            hr: ({ node, ...props }) => (
                              <hr className="my-4 border-white/20" {...props} />
                            ),
                            a: ({ node, ...props }) => (
                              <a className="text-blue-400 hover:text-blue-300 underline underline-offset-2" {...props} />
                            ),
                          }}
                        >
                          {msg.content}
                        </ReactMarkdown>
                      </div>
                    ) : (
                      <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">
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
                  <div className="bg-black/20 text-white border border-white/10 px-5 py-3 rounded-2xl backdrop-blur-sm">
                    <div className="flex items-center gap-2">
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                      >
                        <Loader className="w-4 h-4 text-white" />
                      </motion.div>
                      <span className="text-sm font-medium text-white/60">Analyzing...</span>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
            <div ref={messagesEndRef} />
          </motion.div>
        )}

        <motion.div
          className="shrink-0"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.4 }}
        >
          <div className="relative">
            <div className="bg-black/20 border border-white/10 rounded-2xl shadow-lg backdrop-blur-sm focus-within:ring-2 focus-within:ring-white/30 focus-within:border-white/30 transition-all duration-300">
              <div className="flex items-center gap-3 p-4">
                <textarea
                  className="flex-1 bg-transparent border-none outline-none resize-none text-white placeholder-white/40 text-sm font-medium max-h-32"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Or type your message here..."
                  rows={1}
                  disabled={isLoading}
                />
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => handleSend()}
                  disabled={!input.trim() || isLoading}
                  className={`shrink-0 flex items-center justify-center w-10 h-10 rounded-full transition-all duration-300 ${
                    input.trim() && !isLoading
                      ? 'bg-blue-500 text-white'
                      : 'bg-white/10 text-white/40 cursor-not-allowed'
                  }`}
                >
                  <Send className="w-5 h-5" />
                </motion.button>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default FPLChatbot;
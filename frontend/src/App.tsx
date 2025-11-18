import React from 'react';
import { Send, Users, TrendingUp, BarChart3, Target, Calendar, Zap, Loader } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { ask, getOrCreateSessionId } from './api/client';

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

  return (
    <div className="min-h-screen bg-black text-white">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col min-h-screen">
        {messages.length === 0 ? (
          <motion.div
            className="flex-1 flex flex-col items-center justify-center text-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.2, duration: 0.5 }}
            >
              <div className="mb-8">
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-white/10 backdrop-blur-sm border border-white/20 shadow-lg mb-6">
                  <Zap className="w-10 h-10 text-white" />
                </div>
                <h1 className="text-5xl sm:text-6xl font-bold text-white mb-4">
                  FPL Manager
                </h1>
                <p className="text-lg text-white/60 font-medium">
                  Your AI-powered Fantasy Premier League assistant
                </p>
              </div>
            </motion.div>

            {showSuggestions && (
              <motion.div
                className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-2xl mt-12"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4, duration: 0.5 }}
              >
                <AnimatePresence>
                  {suggestions.map((suggestion, idx) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.1 * idx, duration: 0.4 }}
                      whileHover={{ y: -4, boxShadow: '0 20px 25px -5px rgba(255, 255, 255, 0.1)' }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => handleSuggestionClick(suggestion.text)}
                      className="group cursor-pointer"
                    >
                      <div className="relative overflow-hidden rounded-2xl bg-white/5 border border-white/10 p-5 hover:border-white/30 hover:bg-white/10 transition-all duration-300 shadow-sm hover:shadow-lg backdrop-blur-sm">
                        <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/0 to-white/0 group-hover:from-white/5 group-hover:via-white/5 group-hover:to-white/5 transition-all duration-300" />
                        <div className="relative flex items-start gap-4">
                          <div className="flex-shrink-0 mt-1">
                            <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-white/10 group-hover:bg-white/20 transition-all duration-300">
                              <suggestion.icon className="w-5 h-5 text-white" />
                            </div>
                          </div>
                          <p className="text-sm font-medium text-white/80 group-hover:text-white transition-colors duration-300 line-clamp-2">
                            {suggestion.text}
                          </p>
                        </div>
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
                    className={`max-w-xs lg:max-w-md xl:max-w-lg px-5 py-3 rounded-2xl ${
                      msg.role === 'user'
                        ? 'bg-white/10 text-white border border-white/20 shadow-lg backdrop-blur-sm'
                        : 'bg-white/5 text-white border border-white/10 shadow-md backdrop-blur-sm'
                    }`}
                  >
                    <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">
                      {msg.content}
                    </p>
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
                  <div className="bg-white/5 text-white border border-white/10 px-5 py-3 rounded-2xl shadow-md backdrop-blur-sm">
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
          className="flex-shrink-0"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.4 }}
        >
          <div className="relative">
            <div className="bg-white/5 border border-white/10 rounded-2xl shadow-lg hover:shadow-xl hover:border-white/20 transition-all duration-300 focus-within:ring-2 focus-within:ring-white/30 focus-within:border-white/30 backdrop-blur-sm">
              <div className="flex items-end gap-3 p-4">
                <textarea
                  className="flex-1 bg-transparent border-none outline-none resize-none text-white placeholder-white/40 text-sm font-medium max-h-32"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask a question or make a request..."
                  rows={1}
                  disabled={isLoading}
                />
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => handleSend()}
                  disabled={!input.trim() || isLoading}
                  className={`flex-shrink-0 flex items-center justify-center w-10 h-10 rounded-full transition-all duration-300 ${
                    input.trim() && !isLoading
                      ? 'bg-white text-black shadow-lg hover:shadow-xl'
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
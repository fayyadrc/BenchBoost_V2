import React from 'react';
import { Send, Users, TrendingUp, BarChart3, Target, Calendar, Zap, Loader } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
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
    <div className="min-h-screen bg-transparent text-white font-sans">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col min-h-screen">
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
                    className={`max-w-xs lg:max-w-md xl:max-w-lg px-4 py-2 rounded-xl ${
                      msg.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-black/20 text-white border border-white/10 backdrop-blur-sm'
                    }`}
                  >
                    {msg.role === 'assistant' ? (
                      <div className="text-sm leading-relaxed whitespace-pre-wrap break-words space-y-1">
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            p: ({node, ...props}) => <p className="mb-0" {...props} />,
                            ul: ({ node, ...props }) => (
                              <ul className="list-disc pl-5 space-y-1" {...props} />
                            ),
                            ol: ({ node, ...props }) => (
                              <ol className="list-decimal pl-5 space-y-1" {...props} />
                            ),
                            li: ({ node, ...props }) => (
                              <li className="pl-1" {...props} />
                            ),
                            strong: ({ node, ...props }) => (
                              <strong className="font-semibold" {...props} />
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
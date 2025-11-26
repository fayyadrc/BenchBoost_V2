import React from 'react';
import { motion } from 'framer-motion';
import { Send, MessageSquare } from 'lucide-react';

interface ChatInputProps {
    input: string;
    setInput: (value: string) => void;
    isLoading: boolean;
    onSend: () => void;
    onKeyPress: (e: React.KeyboardEvent<HTMLTextAreaElement>) => void;
    isDark: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({
    input,
    setInput,
    isLoading,
    onSend,
    onKeyPress,
    isDark,
}) => {
    return (
        <motion.div
            className="shrink-0"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.4 }}
        >
            <div
                className={`border-2 transition-all ${isDark
                        ? 'bg-slate-900 border-white/20'
                        : 'bg-white border-slate-900 focus-within:border-blue-600'
                    }`}
                style={isDark ? { borderColor: 'rgba(255, 255, 255, 0.2)' } : {}}
                onFocus={(e) => isDark && (e.currentTarget.style.borderColor = '#003566')}
                onBlur={(e) => isDark && (e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.2)')}
            >
                <div className="flex items-center gap-3 p-4">
                    <MessageSquare className={`w-5 h-5 shrink-0 ${isDark ? 'text-white/40' : 'text-slate-400'}`} />
                    <textarea
                        className={`flex-1 bg-transparent border-none outline-none resize-none text-sm font-medium max-h-32 ${isDark ? 'text-white placeholder-white/30' : 'text-slate-900 placeholder-slate-400'
                            }`}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={onKeyPress}
                        placeholder="Ask about FPL strategy..."
                        rows={1}
                        disabled={isLoading}
                    />
                    <button
                        onClick={onSend}
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
    );
};

export default ChatInput;

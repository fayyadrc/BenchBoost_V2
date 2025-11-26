import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Loader } from 'lucide-react';
import MessageBubble from './MessageBubble';

type Message = {
    role: 'user' | 'assistant';
    content: string;
};

interface ChatMessagesProps {
    messages: Message[];
    isLoading: boolean;
    isDark: boolean;
    messagesEndRef: React.RefObject<HTMLDivElement | null>;
}

const ChatMessages: React.FC<ChatMessagesProps> = ({
    messages,
    isLoading,
    isDark,
    messagesEndRef,
}) => {
    return (
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
                    >
                        <MessageBubble role={msg.role} content={msg.content} isDark={isDark} />
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
                        <div className={`px-4 py-3 border-2 ${isDark ? 'bg-slate-900 text-white border-white/20' : 'bg-white text-slate-900 border-slate-200'}`}>
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
    );
};

export default ChatMessages;

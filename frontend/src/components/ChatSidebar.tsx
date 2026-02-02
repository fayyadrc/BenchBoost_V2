import React from 'react';
import { X, MessageSquare, Plus, Trash2 } from 'lucide-react';
import type { ChatSession } from '../api/client';
import { motion, AnimatePresence } from 'framer-motion';

interface ChatSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  sessions: ChatSession[];
  currentSessionId: string | null;
  onSelectSession: (id: string) => void;
  onNewChat: () => void;
  onDeleteChat: (id: string, e: React.MouseEvent) => void;
  isDark: boolean;
}

const ChatSidebar: React.FC<ChatSidebarProps> = ({
  isOpen,
  onClose,
  sessions,
  currentSessionId,
  onSelectSession,
  onNewChat,
  onDeleteChat,
  isDark
}) => {
  return (
    <>
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop for mobile */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.5 }}
              exit={{ opacity: 0 }}
              onClick={onClose}
              className="fixed inset-0 z-40 bg-black/50 lg:bg-transparent"
            />
            {/* Sidebar */}
            <motion.div
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
              className={`fixed left-0 top-0 bottom-0 z-50 w-80 flex flex-col border-r shadow-2xl
                ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-slate-200'}
              `}
            >
              {/* Header */}
              <div className={`p-5 flex items-center justify-between border-b ${isDark ? 'border-slate-800' : 'border-slate-100'}`}>
                <h2 className={`font-semibold text-lg ${isDark ? 'text-white' : 'text-slate-900'}`}>Chat History</h2>
                <button
                  onClick={onClose}
                  className={`p-2 rounded-lg transition-colors
                    ${isDark ? 'text-slate-400 hover:bg-slate-800 hover:text-white' : 'text-slate-500 hover:bg-slate-100 hover:text-slate-900'}
                  `}
                >
                  <X size={20} />
                </button>
              </div>

              {/* New Chat Button */}
              <div className="p-4">
                <button
                  onClick={onNewChat}
                  className={`w-full group flex items-center justify-center gap-2 px-4 py-3.5 rounded-xl border transition-all duration-200 shadow-sm
                    ${isDark 
                      ? 'bg-blue-600 border-blue-500 text-white hover:bg-blue-500 hover:shadow-blue-900/30' 
                      : 'bg-white border-slate-200 text-slate-700 hover:border-blue-300 hover:text-blue-600 hover:shadow-md'
                    }
                  `}
                >
                  <Plus size={20} className={isDark ? "" : "text-blue-500 group-hover:text-blue-600"} />
                  <span className="font-semibold">New Chat</span>
                </button>
              </div>

              {/* Session List */}
              <div className="flex-1 overflow-y-auto px-4 pb-4 space-y-1">
                <div className={`text-xs font-semibold uppercase tracking-wider mb-2 px-2 ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
                    Recent
                </div>
                {sessions.map((session) => (
                  <button
                    key={session.session_id}
                    onClick={() => onSelectSession(session.session_id)}
                    className={`group w-full flex items-center justify-between p-3 rounded-lg text-left transition-all duration-200
                       ${currentSessionId === session.session_id
                         ? (isDark ? 'bg-slate-800 text-blue-400 shadow-sm' : 'bg-blue-50 text-blue-700 shadow-sm border border-blue-100')
                         : (isDark 
                             ? 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200' 
                             : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                           )
                       }
                    `}
                  >
                    <div className="flex items-center gap-3 overflow-hidden min-w-0">
                      <MessageSquare size={18} className={`shrink-0 ${currentSessionId === session.session_id ? 'opacity-100' : 'opacity-70'}`} />
                      <div className="flex flex-col min-w-0">
                          <span className="truncate text-sm font-medium">
                            {session.title || 'New Chat'}
                          </span>
                          <span className={`text-[10px] truncate ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>
                             {new Date(session.updated_at).toLocaleDateString()}
                          </span>
                      </div>
                    </div>
                    <div
                        onClick={(e) => onDeleteChat(session.session_id, e)}
                        className={`opacity-0 group-hover:opacity-100 p-1.5 rounded-md transition-all
                            ${isDark ? 'hover:bg-red-900/30 text-slate-500 hover:text-red-400' : 'hover:bg-red-50 text-slate-400 hover:text-red-600'}
                        `}
                    >
                        <Trash2 size={14} />
                    </div>
                  </button>
                ))}
                
                {sessions.length === 0 && (
                   <div className={`text-center py-12 flex flex-col items-center gap-3 ${isDark ? 'text-slate-600' : 'text-slate-400'}`}>
                      <MessageSquare size={32} className="opacity-20" />
                      <span className="text-sm">No recent conversations</span>
                   </div>
                )}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
};

export default ChatSidebar;

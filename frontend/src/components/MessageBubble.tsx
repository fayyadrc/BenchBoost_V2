import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MessageBubbleProps {
    role: 'user' | 'assistant';
    content: string;
    isDark: boolean;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ role, content, isDark }) => {
    return (
        <div className={`flex ${role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
                className={`px-4 py-3 ${role === 'user'
                    ? `max-w-xs lg:max-w-md xl:max-w-lg border-2 text-white ${isDark ? '' : 'bg-slate-900 border-slate-800'}`
                    : `max-w-full lg:max-w-2xl xl:max-w-3xl border-2 ${isDark ? 'bg-slate-900 text-white border-white/20' : 'bg-white text-slate-900 border-slate-200'
                    }`
                    }`}
                style={role === 'user' && isDark ? { backgroundColor: '#003566', borderColor: '#003566' } : role === 'user' ? { backgroundColor: '#1e293b', borderColor: '#0f172a' } : {}}
            >
                {role === 'assistant' ? (
                    <div className={`text-sm leading-relaxed break-words prose prose-sm max-w-none ${isDark ? 'prose-invert' : ''}`}>
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
                                        <code className={`px-1.5 py-0.5 text-xs font-mono border ${isDark ? 'bg-white/10 text-emerald-400 border-white/20' : 'bg-slate-100 text-emerald-600 border-slate-200'}`} {...props}>
                                            {children}
                                        </code>
                                    ) : (
                                        <code className={`block p-3 text-xs font-mono overflow-x-auto border-2 ${isDark ? 'bg-black/40 text-white/90 border-white/20' : 'bg-slate-100 text-slate-800 border-slate-200'}`} {...props}>
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
                            {content}
                        </ReactMarkdown>
                    </div>
                ) : (
                    <p className="text-sm font-medium leading-relaxed whitespace-pre-wrap break-words">
                        {content}
                    </p>
                )}
            </div>
        </div>
    );
};

export default MessageBubble;

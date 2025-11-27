import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bell, RefreshCw } from 'lucide-react';
import { getPlayerNews } from '../api/client';

export const NewsDropdown: React.FC<{ isDark: boolean }> = ({ isDark }) => {
    const [isOpen, setIsOpen] = React.useState(false);
    const [news, setNews] = React.useState<any[]>([]);
    const [loading, setLoading] = React.useState(false);

    const fetchNews = async () => {
        setLoading(true);
        try {
            const data = await getPlayerNews();
            setNews(data);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="relative">
            <button
                onClick={() => {
                    setIsOpen(!isOpen);
                    if (!isOpen && news.length === 0) fetchNews();
                }}
                className={`p-2 rounded-full border-2 transition-all hover:scale-105 ${isDark
                    ? 'border-white/20 text-white hover:border-white/40'
                    : 'border-slate-900 text-slate-900 hover:bg-slate-900 hover:text-white'
                    }`}
            >
                <Bell className="w-4 h-4" />
            </button>

            <AnimatePresence>
                {isOpen && (
                    <>
                        <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: 10 }}
                            className={`absolute right-0 mt-2 w-80 max-h-96 overflow-y-auto z-50 rounded-lg shadow-2xl border-2 ${isDark ? 'bg-slate-900 border-white/20' : 'bg-white border-slate-900'
                                }`}
                        >
                            <div className={`p-3 border-b-2 font-black uppercase text-sm flex justify-between items-center ${isDark ? 'border-white/10 text-white' : 'border-slate-100 text-slate-900'}`}>
                                <span>Latest Updates</span>
                                <button onClick={() => fetchNews()} disabled={loading}>
                                    <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
                                </button>
                            </div>

                            {loading && news.length === 0 ? (
                                <div className="p-8 text-center">
                                    <RefreshCw className={`w-6 h-6 mx-auto mb-2 animate-spin ${isDark ? 'text-white/40' : 'text-slate-400'}`} />
                                    <p className={`text-xs uppercase font-bold ${isDark ? 'text-white/40' : 'text-slate-400'}`}>Loading updates...</p>
                                </div>
                            ) : news.length === 0 ? (
                                <div className="p-8 text-center">
                                    <p className={`text-xs uppercase font-bold ${isDark ? 'text-white/40' : 'text-slate-400'}`}>No recent updates found</p>
                                </div>
                            ) : (
                                <div className="divide-y divide-dashed" style={{ borderColor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)' }}>
                                    {news.map((item, i) => (
                                        <div key={i} className={`p-3 hover:bg-white/5 transition-colors`}>
                                            <div className="flex justify-between items-start mb-1">
                                                <span className={`text-xs font-black uppercase ${isDark ? 'text-white' : 'text-slate-900'}`}>
                                                    {item.player}
                                                </span>
                                                <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded text-white ${item.type === 'price_change'
                                                    ? (item.movement === 'risen' ? 'bg-green-500' : 'bg-red-500')
                                                    : 'bg-yellow-500'
                                                    }`}>
                                                    {item.type === 'price_change' ? (item.movement === 'risen' ? 'RISE' : 'FALL') : 'NEWS'}
                                                </span>
                                            </div>
                                            <p className={`text-xs ${isDark ? 'text-white/70' : 'text-slate-600'}`}>
                                                {item.type === 'price_change'
                                                    ? `${item.movement === 'risen' ? 'Price rose' : 'Price fell'} to ${item.price_text}`
                                                    : item.status}
                                            </p>
                                            <p className={`text-[10px] mt-1 ${isDark ? 'text-white/30' : 'text-slate-400'}`}>
                                                {item.date}
                                            </p>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </motion.div>
                    </>
                )}
            </AnimatePresence>
        </div>
    );
};

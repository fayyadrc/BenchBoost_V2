import React from 'react';
import { Link } from 'react-router-dom';
import { User, Moon, Sun } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ManagerInfo from './ManagerInfo';
import ManagerForm from './ManagerForm';

interface HeaderProps {
    theme: 'dark' | 'light';
    toggleTheme: () => void;
    managerData: any;
    managerId: string;
    setManagerId: (id: string) => void;
    managerLoading: boolean;
    managerError: string | null;
    handleManagerSubmit: (e: React.FormEvent) => void;
    clearManager: () => void;
}

const Header: React.FC<HeaderProps> = ({
    theme,
    toggleTheme,
    managerData,
    managerId,
    setManagerId,
    managerLoading,
    managerError,
    handleManagerSubmit,
    clearManager,
}) => {
    const isDark = theme === 'dark';

    return (
        <header className={`border-b-2 ${isDark ? 'border-white/20 bg-slate-950' : 'border-slate-900 bg-white'}`}>
            <div className="max-w-4xl mx-auto px-3 sm:px-6 py-3 sm:py-4">
                <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-2 sm:gap-6">
                        <h1 className={`text-lg sm:text-2xl font-black uppercase tracking-tighter ${isDark ? 'text-white' : 'text-slate-900'}`}>
                            Bench<span className={isDark ? 'text-blue-600' : 'text-blue-600'} style={isDark ? { color: '#003566' } : {}}>Boost</span>
                        </h1>

                        <div className={`hidden sm:block h-8 w-px ${isDark ? 'bg-white/20' : 'bg-slate-300'}`} />

                        <Link
                            to="/manager"
                            className={`px-2 sm:px-4 py-1.5 sm:py-2 border-2 font-bold uppercase text-xs tracking-wide transition-all hover:scale-105 ${isDark
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
                    <div className="flex items-center gap-2 sm:gap-3">
                        {managerData ? (
                            <ManagerInfo
                                managerData={managerData}
                                isDark={isDark}
                                clearManager={clearManager}
                            />
                        ) : (
                            <ManagerForm
                                managerId={managerId}
                                setManagerId={setManagerId}
                                managerLoading={managerLoading}
                                handleManagerSubmit={handleManagerSubmit}
                                isDark={isDark}
                            />
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
    );
};

export default Header;

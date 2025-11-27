import React from 'react';
import { motion } from 'framer-motion';
import { Trophy, ArrowUp, X, ChevronRight } from 'lucide-react';
import { Link } from 'react-router-dom';

interface ManagerInfoProps {
    managerData: {
        team_name: string;
        name: string;
        overall_rank?: number;
        gameweek_points: number;
    };
    isDark: boolean;
    clearManager: () => void;
}

const ManagerInfo: React.FC<ManagerInfoProps> = ({ managerData, isDark, clearManager }) => {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex items-center gap-2 sm:gap-4"
        >
            <div className="hidden md:flex items-center gap-3">
                <Link
                    to="/manager"
                    className={`group flex items-center gap-3 px-3 py-1.5 rounded-lg transition-all ${isDark ? 'bg-white/10 hover:bg-white/20' : 'bg-slate-100 hover:bg-slate-200'
                        }`}
                >
                    <div className="text-sm text-right">
                        <p className={`font-black uppercase ${isDark ? 'text-white' : 'text-slate-900'}`}>
                            {managerData.team_name}
                        </p>
                        <p className={`text-xs ${isDark ? 'text-white/50' : 'text-slate-500'}`}>
                            {managerData.name}
                        </p>
                    </div>
                    <ChevronRight className={`w-4 h-4 transition-all ${isDark ? 'text-white/50' : 'text-slate-400'
                        }`} />
                </Link>
            </div>
            <div className={`hidden md:block h-8 w-px ${isDark ? 'bg-white/20' : 'bg-slate-300'}`} />

            {/* Stats - always visible */}
            <div className="flex items-center gap-2 sm:gap-4">
                <div className="flex items-center gap-1 sm:gap-1.5">
                    <Trophy className="w-3.5 sm:w-4 h-3.5 sm:h-4 text-yellow-500" />
                    <span className={`font-mono text-xs sm:text-sm font-bold ${isDark ? 'text-white/80' : 'text-slate-600'}`}>
                        {managerData.overall_rank?.toLocaleString() ?? 'N/A'}
                    </span>
                </div>
                <div className="flex items-center gap-1 sm:gap-1.5">
                    <ArrowUp className="w-3.5 sm:w-4 h-3.5 sm:h-4 text-green-500" />
                    <span className={`font-mono text-xs sm:text-sm font-bold ${isDark ? 'text-white/80' : 'text-slate-600'}`}>
                        {managerData.gameweek_points}
                    </span>
                </div>
            </div>
            <button
                onClick={clearManager}
                className={`p-1 sm:p-1.5 transition-colors ${isDark ? 'hover:bg-white/10' : 'hover:bg-slate-100'}`}
                title="Clear manager"
            >
                <X className={`w-3.5 sm:w-4 h-3.5 sm:h-4 ${isDark ? 'text-white/60' : 'text-slate-400'}`} />
            </button>
        </motion.div>
    );
};

export default ManagerInfo;

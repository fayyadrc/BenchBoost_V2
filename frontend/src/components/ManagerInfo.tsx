import React from 'react';
import { motion } from 'framer-motion';
import { Trophy, ArrowUp, X } from 'lucide-react';

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
            className={`flex items-center gap-2 sm:gap-4 px-2 sm:px-5 py-2 sm:py-3 border-2 ${isDark ? 'border-white/20 bg-slate-900' : 'border-slate-900 bg-white'
                }`}
        >
            {/* Team/Manager names - hidden on mobile */}
            <div className="hidden md:flex items-center gap-3">
                <div className="text-sm">
                    <p className={`font-black uppercase ${isDark ? 'text-white' : 'text-slate-900'}`}>
                        {managerData.team_name}
                    </p>
                    <p className={`text-xs ${isDark ? 'text-white/50' : 'text-slate-500'}`}>
                        {managerData.name}
                    </p>
                </div>
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

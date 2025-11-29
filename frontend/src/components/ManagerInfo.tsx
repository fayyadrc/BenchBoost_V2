import React from 'react';
import { X, Trophy, ArrowUp } from 'lucide-react';

interface ManagerInfoProps {
    managerData: {
        name: string;
        id: number | string;
        overall_rank?: number | null;
        gameweek_points?: number;
    };
    isDark: boolean;
    clearManager: () => void;
}

const ManagerInfo: React.FC<ManagerInfoProps> = ({ managerData, isDark, clearManager }) => {
    return (
        <div className={`inline-flex items-center gap-2 rounded-full border-2 px-3 py-1.5 transition-all hover:scale-105 group ${isDark
            ? 'border-white/10 bg-slate-900/30 backdrop-blur-sm hover:border-white/30'
            : 'border-slate-200 bg-slate-50 hover:border-slate-300 hover:shadow-md'
            }`}>
            <div className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold ${isDark ? 'bg-blue-500 text-white' : 'bg-blue-600 text-white'
                }`}>
                {managerData.name.split(' ').map(n => n[0]).join('')}
            </div>
            <div className="flex items-center gap-2">
                <span className={`text-sm font-medium ${isDark ? 'text-white' : 'text-slate-900'}`}>
                    {managerData.name}
                </span>
                <span className={`text-xs font-mono ${isDark ? 'text-white/40' : 'text-slate-400'}`}>
                    •
                </span>
                <span className={`text-xs font-mono ${isDark ? 'text-white/60' : 'text-slate-600'}`}>
                    {managerData.id}
                </span>
            </div>

            {/* Stats Divider */}
            <div className={`w-px h-4 mx-1 ${isDark ? 'bg-white/10' : 'bg-slate-200'}`} />

            {/* Stats */}
            <div className="flex items-center gap-3">
                <div className="flex items-center gap-1.5" title="Overall Rank">
                    <Trophy className="w-3 h-3 text-yellow-500" />
                    <span className={`text-xs font-mono font-bold ${isDark ? 'text-white/80' : 'text-slate-600'}`}>
                        {managerData.overall_rank?.toLocaleString() ?? '-'}
                    </span>
                </div>
                <div className="flex items-center gap-1.5" title="Gameweek Points">
                    <ArrowUp className="w-3 h-3 text-green-500" />
                    <span className={`text-xs font-mono font-bold ${isDark ? 'text-white/80' : 'text-slate-600'}`}>
                        {managerData.gameweek_points ?? 0}
                    </span>
                </div>
            </div>

            <button
                onClick={clearManager}
                className={`ml-1 opacity-0 group-hover:opacity-100 transition-all ${isDark ? 'text-red-400 hover:text-red-300' : 'text-red-500 hover:text-red-600'
                    }`}
                aria-label="Clear manager"
            >
                <X className="w-3.5 h-3.5" />
            </button>
        </div>
    );
};

export default ManagerInfo;

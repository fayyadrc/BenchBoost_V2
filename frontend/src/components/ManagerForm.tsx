import React from 'react';
import { Loader } from 'lucide-react';

interface ManagerFormProps {
    managerId: string;
    setManagerId: (id: string) => void;
    managerLoading: boolean;
    handleManagerSubmit: (e: React.FormEvent) => void;
    isDark: boolean;
}

const ManagerForm: React.FC<ManagerFormProps> = ({
    managerId,
    setManagerId,
    managerLoading,
    handleManagerSubmit,
    isDark,
}) => {
    return (
        <form onSubmit={handleManagerSubmit} className="flex items-center gap-2 sm:gap-3">
            <input
                type="text"
                value={managerId}
                onChange={(e) => setManagerId(e.target.value)}
                placeholder="FPL ID"
                className={`border-2 px-2 sm:px-4 py-1.5 sm:py-2.5 text-xs sm:text-sm font-bold uppercase w-24 sm:w-36 focus:outline-none transition-all rounded-full ${isDark
                    ? 'bg-slate-900 border-white/20 text-white placeholder-white/30'
                    : 'bg-white border-slate-900 text-slate-900 placeholder-slate-400 focus:border-blue-600'
                    }`}
                style={isDark ? { borderColor: 'rgba(255, 255, 255, 0.2)' } : {}}
                onFocus={(e) => isDark && (e.target.style.borderColor = '#003566')}
                onBlur={(e) => isDark && (e.target.style.borderColor = 'rgba(255, 255, 255, 0.2)')}
                disabled={managerLoading}
            />
            <button
                type="submit"
                disabled={!managerId.trim() || managerLoading}
                className={`px-3 sm:px-5 py-1.5 sm:py-2.5 text-xs sm:text-sm font-black uppercase transition-all disabled:opacity-30 rounded-full ${isDark
                    ? 'text-white'
                    : 'bg-slate-900 text-white hover:bg-slate-800'
                    }`}
                style={isDark ? { backgroundColor: '#003566', borderColor: '#003566' } : {}}
                onMouseEnter={(e) => isDark && !managerLoading && managerId.trim() && (e.currentTarget.style.backgroundColor = '#004080')}
                onMouseLeave={(e) => isDark && (e.currentTarget.style.backgroundColor = '#003566')}
            >
                {managerLoading ? <Loader className="w-3.5 sm:w-4 h-3.5 sm:h-4 animate-spin" /> : 'Load'}
            </button>
        </form>
    );
};

export default ManagerForm;

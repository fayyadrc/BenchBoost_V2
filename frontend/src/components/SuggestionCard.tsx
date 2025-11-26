import React from 'react';
import { motion } from 'framer-motion';

interface SuggestionCardProps {
    icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
    text: string;
    color: string;
    onClick: () => void;
    isDark: boolean;
    index: number;
}

const SuggestionCard: React.FC<SuggestionCardProps> = ({
    icon: Icon,
    text,
    color,
    onClick,
    isDark,
    index,
}) => {
    return (
        <motion.button
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 * index, duration: 0.4 }}
            whileHover={{ y: -2 }}
            whileTap={{ scale: 0.98 }}
            onClick={onClick}
            className={`group cursor-pointer text-left border-l-4 p-4 transition-all ${isDark
                    ? 'bg-slate-900 hover:bg-slate-800 border-white/20'
                    : 'bg-white hover:bg-slate-50 border-slate-900'
                }`}
            style={{ borderLeftColor: color }}
        >
            <div className="flex items-start gap-3">
                <div
                    className="flex items-center justify-center w-8 h-8 shrink-0"
                    style={{ backgroundColor: color }}
                >
                    <Icon className="w-4 h-4 text-white" />
                </div>
                <p className={`text-sm font-bold leading-tight ${isDark ? 'text-white/90' : 'text-slate-700'}`}>
                    {text}
                </p>
            </div>
        </motion.button>
    );
};

export default SuggestionCard;

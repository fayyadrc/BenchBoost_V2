import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Users, TrendingUp, BarChart3, Target, Calendar, Zap } from 'lucide-react';
import SuggestionCard from './SuggestionCard';

interface WelcomeScreenProps {
    managerName?: string;
    showSuggestions: boolean;
    onSuggestionClick: (text: string) => void;
    isDark: boolean;
}

const WelcomeScreen: React.FC<WelcomeScreenProps> = ({
    managerName,
    showSuggestions,
    onSuggestionClick,
    isDark,
}) => {
    const suggestions = [
        { icon: Users, text: 'Who should I captain this gameweek?', color: '#FF6B35' },
        { icon: TrendingUp, text: 'Analyze my team for next 3 fixtures', color: '#00A878' },
        { icon: BarChart3, text: 'Best differentials under £7m', color: '#004E89' },
        { icon: Target, text: 'Transfer recommendations', color: '#E63946' },
        { icon: Calendar, text: 'Best fixture runs', color: '#9B59B6' },
        { icon: Zap, text: 'Template team weaknesses', color: '#F39C12' }
    ];

    return (
        <motion.div
            className="flex-1 flex flex-col"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
        >
            {/* Greeting - Brutalist */}
            <motion.div
                className="mb-12"
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2, duration: 0.5 }}
            >
                <div className={`border-l-4 pl-4 ${isDark ? '' : 'border-blue-600'}`} style={isDark ? { borderLeftColor: '#003566' } : {}}>
                    <h2 className={`text-4xl font-black uppercase tracking-tighter ${isDark ? 'text-white' : 'text-slate-900'}`}>
                        Hello,
                    </h2>
                    <p className={`text-2xl font-bold uppercase ${isDark ? 'text-white/60' : 'text-slate-500'}`}>
                        {managerName?.split(' ')[0] || 'Manager'}
                    </p>
                </div>
            </motion.div>

            <div className="flex-grow"></div>

            {/* Suggestions - Compact Cards */}
            {showSuggestions && (
                <motion.div
                    className="grid grid-cols-1 md:grid-cols-3 gap-3 w-full mb-8"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.4, duration: 0.5 }}
                >
                    <AnimatePresence>
                        {suggestions.slice(0, 3).map((suggestion, idx) => (
                            <SuggestionCard
                                key={idx}
                                icon={suggestion.icon}
                                text={suggestion.text}
                                color={suggestion.color}
                                onClick={() => onSuggestionClick(suggestion.text)}
                                isDark={isDark}
                                index={idx}
                            />
                        ))}
                    </AnimatePresence>
                </motion.div>
            )}
        </motion.div>
    );
};

export default WelcomeScreen;

import React from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  User, Trophy, TrendingUp, Wallet, X, Moon, Sun,
  ArrowLeft, Shield, Target, Activity, Minus, RefreshCw, BarChart2, AlertTriangle,
} from 'lucide-react';
import { useManager } from '../context/ManagerContext';
import type { PlayerPick } from '../api/client';

// --- Helper Functions ---

const getPositionStyle = (pos: string) => {
  const styles = {
    GKP: { bg: '#FF6B35', border: '#FF8C61', text: 'GK' },
    DEF: { bg: '#004E89', border: '#1A6FA8', text: 'DF' },
    MID: { bg: '#00A878', border: '#2DBB94', text: 'MD' },
    FWD: { bg: '#E63946', border: '#F15A63', text: 'FW' },
  };
  return styles[pos as keyof typeof styles] || styles.MID;
};

const getAvailabilityStatus = (chance: number | null | undefined, news: string | undefined) => {
  if (chance === null || chance === undefined) {
    if (news && news.length > 0) return { color: 'bg-red-500', text: '!', fullText: news };
    return { color: 'bg-green-500', text: '', fullText: 'Available' };
  }
  if (chance === 100) return { color: 'bg-green-500', text: '', fullText: 'Available' };
  if (chance >= 75) return { color: 'bg-yellow-400', text: '75%', fullText: news || '75% Chance of Playing' };
  if (chance >= 50) return { color: 'bg-orange-400', text: '50%', fullText: news || '50% Chance of Playing' };
  if (chance >= 25) return { color: 'bg-orange-600', text: '25%', fullText: news || '25% Chance of Playing' };
  return { color: 'bg-red-600', text: '0%', fullText: news || 'Injured/Suspended' };
};

// --- Components ---

const PlayerDetailModal: React.FC<{ player: PlayerPick | null; onClose: () => void; isDark: boolean }> = ({ player, onClose, isDark }) => {
  if (!player) return null;

  const posStyle = getPositionStyle(player.position_name || 'MID');
  const position = player.position_name || 'MID';

  // Configuration for stats based on position
  const STAT_CONFIG: Record<string, { key: { label: string; key: keyof PlayerPick }[]; advanced: { label: string; key: keyof PlayerPick; color: string }[] }> = {
    FWD: {
      key: [
        { label: 'Goals', key: 'goals_scored' },
        { label: 'Assists', key: 'assists' },
        { label: 'Bonus', key: 'bonus' },
        { label: 'BPS', key: 'bps' },
        { label: 'PPG', key: 'points_per_game' },
        { label: 'Form', key: 'form' },
      ],
      advanced: [
        { label: 'Threat', key: 'threat', color: 'text-cyan-500' },
        { label: 'xG', key: 'expected_goals', color: 'text-blue-500' },
        { label: 'xA', key: 'expected_assists', color: 'text-green-500' },
        { label: 'xGI', key: 'expected_goal_involvements', color: 'text-purple-500' },
        { label: 'ICT Index', key: 'ict_index', color: 'text-orange-500' },
        { label: 'Influence', key: 'influence', color: 'text-yellow-500' },
      ]
    },
    MID: {
      key: [
        { label: 'Goals', key: 'goals_scored' },
        { label: 'Assists', key: 'assists' },
        { label: 'Clean Sheets', key: 'clean_sheets' },
        { label: 'Bonus', key: 'bonus' },
        { label: 'BPS', key: 'bps' },
        { label: 'Form', key: 'form' },
        { label: 'PPG', key: 'points_per_game' },
        { label: 'Conceded', key: 'goals_conceded' },
      ],
      advanced: [
        { label: 'Creativity', key: 'creativity', color: 'text-pink-500' },
        { label: 'Influence', key: 'influence', color: 'text-yellow-500' },
        { label: 'xG', key: 'expected_goals', color: 'text-blue-500' },
        { label: 'xA', key: 'expected_assists', color: 'text-green-500' },
        { label: 'xGI', key: 'expected_goal_involvements', color: 'text-purple-500' },
        { label: 'ICT Index', key: 'ict_index', color: 'text-orange-500' },
      ]
    },
    GKP: {
      key: [
        { label: 'Clean Sheets', key: 'clean_sheets' },
        { label: 'Saves', key: 'saves' },
        { label: 'Penalties Saved', key: 'penalties_saved' },
        { label: 'Conceded', key: 'goals_conceded' },
        { label: 'Bonus', key: 'bonus' },
        { label: 'BPS', key: 'bps' },
      ],
      advanced: [
        { label: 'xGC', key: 'expected_goals_conceded', color: 'text-red-500' },
        { label: 'Influence', key: 'influence', color: 'text-yellow-500' },
        { label: 'ICT Index', key: 'ict_index', color: 'text-orange-500' },
      ]
    },
    DEF: {
      key: [
        { label: 'Clean Sheets', key: 'clean_sheets' },
        { label: 'Goals', key: 'goals_scored' },
        { label: 'Assists', key: 'assists' },
        { label: 'Conceded', key: 'goals_conceded' },
        { label: 'Bonus', key: 'bonus' },
        { label: 'BPS', key: 'bps' },
      ],
      advanced: [
        { label: 'xGC', key: 'expected_goals_conceded', color: 'text-red-500' },
        { label: 'xGI', key: 'expected_goal_involvements', color: 'text-purple-500' },
        { label: 'Influence', key: 'influence', color: 'text-yellow-500' },
        { label: 'Creativity', key: 'creativity', color: 'text-pink-500' },
        { label: 'Threat', key: 'threat', color: 'text-cyan-500' },
        { label: 'ICT Index', key: 'ict_index', color: 'text-orange-500' },
      ]
    }
  };

  const stats = STAT_CONFIG[position] || STAT_CONFIG.MID;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm" onClick={onClose}>
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        onClick={(e) => e.stopPropagation()}
        className={`w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-lg shadow-2xl border-2 ${isDark ? 'bg-slate-900 border-white/20' : 'bg-white border-slate-900'}`}
      >
        {/* Header */}
        <div className="relative p-6 border-b-2" style={{ borderColor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)' }}>
          <button
            onClick={onClose}
            className={`absolute top-4 right-4 p-2 rounded-full transition-colors ${isDark ? 'hover:bg-white/10 text-white' : 'hover:bg-slate-100 text-slate-900'}`}
          >
            <X className="w-6 h-6" />
          </button>

          <div className="flex items-center gap-4">
            <div className="flex items-center justify-center w-16 h-16 rounded-lg text-white font-black text-2xl shadow-lg"
              style={{ backgroundColor: posStyle.bg }}>
              {player.points}
            </div>
            <div>
              <h2 className={`text-2xl font-black uppercase tracking-tight ${isDark ? 'text-white' : 'text-slate-900'}`}>
                {player.full_name || player.player_name}
              </h2>
              <div className="flex items-center gap-3 mt-1">
                <span className={`px-2 py-0.5 rounded text-xs font-bold text-white`} style={{ backgroundColor: posStyle.bg }}>
                  {posStyle.text}
                </span>
                <span className={`text-sm font-bold uppercase ${isDark ? 'text-white/60' : 'text-slate-500'}`}>
                  {player.team_name}
                </span>
                <span className={`text-sm font-bold ${isDark ? 'text-white/60' : 'text-slate-500'}`}>
                  £{player.price?.toFixed(1)}m
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-8">
          {/* Key Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'Form', value: player.form },
              { label: 'Selected By', value: `${player.selected_by_percent}%` },
              { label: 'ICT Index', value: player.ict_index },
              { label: 'Total Points', value: player.total_points },
            ].map((stat, i) => (
              <div key={i} className={`p-3 rounded border ${isDark ? 'bg-white/5 border-white/10' : 'bg-slate-50 border-slate-200'}`}>
                <div className={`text-xs font-bold uppercase mb-1 ${isDark ? 'text-white/50' : 'text-slate-500'}`}>
                  {stat.label}
                </div>
                <div className={`text-xl font-black ${isDark ? 'text-white' : 'text-slate-900'}`}>
                  {stat.value}
                </div>
              </div>
            ))}
          </div>

          {/* Detailed Stats Grid */}
          <div>
            <h3 className={`text-lg font-black uppercase mb-4 ${isDark ? 'text-white' : 'text-slate-900'}`}>
              Season Stats
            </h3>
            <div className={`grid grid-cols-2 md:grid-cols-3 gap-x-8 gap-y-4 p-6 rounded-lg border ${isDark ? 'bg-white/5 border-white/10' : 'bg-slate-50 border-slate-200'}`}>
              {stats.key.map((stat, i) => (
                <div key={i} className="flex justify-between items-center border-b border-dashed pb-2 last:border-0" style={{ borderColor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)' }}>
                  <span className={`text-sm ${isDark ? 'text-white/70' : 'text-slate-600'}`}>{stat.label}</span>
                  <span className={`font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>{player[stat.key] as React.ReactNode}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Advanced Stats (xG, xA, etc) */}
          <div>
            <h3 className={`text-lg font-black uppercase mb-4 ${isDark ? 'text-white' : 'text-slate-900'}`}>
              Advanced Metrics
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {stats.advanced.map((stat, i) => (
                <div key={i} className={`p-4 rounded border flex items-center justify-between ${isDark ? 'bg-white/5 border-white/10' : 'bg-slate-50 border-slate-200'}`}>
                  <span className={`text-sm font-bold uppercase ${isDark ? 'text-white/70' : 'text-slate-600'}`}>
                    {stat.label}
                  </span>
                  <span className={`text-xl font-black ${stat.color}`}>
                    {player[stat.key] as React.ReactNode}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

const PlayerCard: React.FC<{ player: PlayerPick; isDark: boolean; posStyle: any; onOpenDetails: () => void }> = ({ player, isDark, posStyle, onOpenDetails }) => {
  return (
    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-4 w-64 z-50 hidden group-hover:block pointer-events-auto">
      <div className={`p-3 shadow-2xl border-2 ${isDark ? 'bg-slate-900 border-white/20' : 'bg-white border-slate-900'}`}>
        {/* Header */}
        <div className="flex justify-between items-start mb-3 border-b pb-2" style={{ borderColor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)' }}>
          <div>
            <h4 className={`text-sm font-black uppercase ${isDark ? 'text-white' : 'text-slate-900'}`}>
              {player.full_name || player.player_name}
            </h4>
            <div className="flex items-center gap-2 mt-1">
              <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-sm text-white`} style={{ backgroundColor: posStyle.bg }}>
                {posStyle.text}
              </span>
              <span className={`text-[10px] font-medium ${isDark ? 'text-white/60' : 'text-slate-500'}`}>
                {player.team_name}
              </span>
            </div>
          </div>
          <div className="text-right">
            <div className={`text-lg font-black ${isDark ? 'text-white' : 'text-slate-900'}`}>
              {player.points}
            </div>
            <div className={`text-[9px] uppercase font-bold ${isDark ? 'text-white/40' : 'text-slate-400'}`}>
              Points
            </div>
          </div>
        </div>

        {/* Injury/Status News */}
        {player.news && (
          <div className={`mb-3 p-2 rounded border-l-2 ${isDark ? 'bg-red-500/10 border-red-500' : 'bg-red-50 border-red-500'}`}>
            <div className="flex items-start gap-2">
              <AlertTriangle className="w-3 h-3 text-red-500 mt-0.5 shrink-0" />
              <p className={`text-[10px] font-medium leading-tight ${isDark ? 'text-red-200' : 'text-red-800'}`}>
                {player.news}
              </p>
            </div>
          </div>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-3 gap-2 mb-3">
          <div className={`p-1.5 border ${isDark ? 'border-white/10 bg-white/5' : 'border-slate-100 bg-slate-50'}`}>
            <div className={`text-[9px] uppercase font-bold mb-0.5 ${isDark ? 'text-white/40' : 'text-slate-400'}`}>Form</div>
            <div className={`text-xs font-black ${isDark ? 'text-white' : 'text-slate-900'}`}>{player.form}</div>
          </div>
          <div className={`p-1.5 border ${isDark ? 'border-white/10 bg-white/5' : 'border-slate-100 bg-slate-50'}`}>
            <div className={`text-[9px] uppercase font-bold mb-0.5 ${isDark ? 'text-white/40' : 'text-slate-400'}`}>Price</div>
            <div className={`text-xs font-black ${isDark ? 'text-white' : 'text-slate-900'}`}>£{player.price?.toFixed(1)}</div>
          </div>
          <div className={`p-1.5 border ${isDark ? 'border-white/10 bg-white/5' : 'border-slate-100 bg-slate-50'}`}>
            <div className={`text-[9px] uppercase font-bold mb-0.5 ${isDark ? 'text-white/40' : 'text-slate-400'}`}>Selected</div>
            <div className={`text-xs font-black ${isDark ? 'text-white' : 'text-slate-900'}`}>{player.selected_by_percent}%</div>
          </div>
        </div>

        {/* Fixtures */}
        {player.fixtures && player.fixtures.length > 0 && (
          <div className="mb-3">
            <div className={`text-[9px] uppercase font-bold mb-1.5 ${isDark ? 'text-white/40' : 'text-slate-400'}`}>
              Upcoming Fixtures
            </div>
            <div className="space-y-1">
              {player.fixtures.map((fix, i) => (
                <div key={i} className="flex items-center justify-between text-[10px]">
                  <div className="flex items-center gap-2">
                    <span className={`font-bold w-3 ${isDark ? 'text-white/60' : 'text-slate-500'}`}>
                      {fix.is_home ? 'H' : 'A'}
                    </span>
                    <span className={`font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                      {fix.opponent_short}
                    </span>
                  </div>
                  <div className={`px-1.5 py-0.5 font-bold text-white rounded-sm text-[9px]`}
                    style={{
                      backgroundColor: fix.difficulty <= 2 ? '#00A878' : fix.difficulty <= 3 ? '#E0E0E0' : fix.difficulty <= 4 ? '#FF6B35' : '#E63946',
                      color: fix.difficulty === 3 ? '#333' : 'white'
                    }}>
                    {fix.difficulty}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Full Stats Button */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onOpenDetails();
          }}
          className={`w-full py-2 flex items-center justify-center gap-2 text-[10px] font-black uppercase tracking-wide transition-colors ${isDark
            ? 'bg-white text-slate-900 hover:bg-white/90'
            : 'bg-slate-900 text-white hover:bg-slate-800'}`}
        >
          <BarChart2 className="w-3 h-3" />
          Full Stats
        </button>
      </div>
      {/* Arrow */}
      <div className={`absolute left-1/2 -translate-x-1/2 top-full w-0 h-0 border-l-[8px] border-l-transparent border-r-[8px] border-r-transparent border-t-[8px] ${isDark ? 'border-t-slate-900' : 'border-t-slate-900'}`} />
    </div>
  );
};

const TacticalPlayer: React.FC<{ player: PlayerPick; index: number; isDark: boolean; onOpenDetails: () => void }> = ({ player, index, isDark, onOpenDetails }) => {
  const posStyle = getPositionStyle(player.position_name || 'MID');
  const status = getAvailabilityStatus(player.chance_of_playing, player.news);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: index * 0.05 }}
      className="relative flex flex-col items-center group"
    >
      {/* Connection line effect */}
      <div className={`absolute -bottom-8 left-1/2 w-0.5 h-8 ${isDark ? 'bg-white/10' : 'bg-slate-300'
        } group-hover:bg-blue-500 transition-colors`} />

      {/* Player circle */}
      <div className="relative">
        <div
          className="w-16 h-16 rounded-sm rotate-45 flex items-center justify-center shadow-lg transition-all group-hover:scale-110"
          style={{ backgroundColor: posStyle.bg }}
        >
          <div className="-rotate-45 text-center">
            <div className="text-white font-black text-xl leading-none">
              {player.points}
            </div>
            <div className="text-white/80 text-[9px] font-bold uppercase tracking-wider">
              {posStyle.text}
            </div>
          </div>
        </div>

        {/* Captain badge */}
        {player.is_captain && (
          <div className="absolute -top-1 -right-1 w-5 h-5 bg-yellow-400 text-black font-black text-xs flex items-center justify-center rounded-sm shadow-md">
            C
          </div>
        )}
        {player.is_vice_captain && (
          <div className="absolute -top-1 -right-1 w-5 h-5 bg-slate-400 text-white font-black text-xs flex items-center justify-center rounded-sm shadow-md">
            V
          </div>
        )}

        {/* Availability Badge */}
        {status.text && (
          <div
            className={`absolute -bottom-1 -right-1 px-1 min-w-[1.25rem] h-5 ${status.color} text-white font-black text-[10px] flex items-center justify-center rounded-sm shadow-md z-10`}
            title={status.fullText}
          >
            {status.text}
          </div>
        )}
      </div>

      {/* Player name */}
      <div className="mt-2 text-center max-w-[90px]">
        <p className={`text-xs font-bold uppercase tracking-tight truncate ${isDark ? 'text-white' : 'text-slate-900'
          }`}>
          {player.player_name?.split(' ').pop()}
        </p>
        <p className={`text-[10px] font-medium ${isDark ? 'text-white/50' : 'text-slate-500'
          }`}>
          {player.team_short}
        </p>
      </div>

      <PlayerCard
        player={player}
        isDark={isDark}
        posStyle={posStyle}
        onOpenDetails={onOpenDetails}
      />
    </motion.div>
  );
};

// Tactical Formation View - More like a real match analysis
const FormationView: React.FC<{ players: PlayerPick[]; isDark: boolean }> = ({ players, isDark }) => {
  const [selectedPlayer, setSelectedPlayer] = React.useState<PlayerPick | null>(null);

  const gkp = players.filter(p => p.position_name === 'GKP');
  const def = players.filter(p => p.position_name === 'DEF');
  const mid = players.filter(p => p.position_name === 'MID');
  const fwd = players.filter(p => p.position_name === 'FWD');

  return (
    <div className="relative py-8">
      {/* Tactical grid lines */}
      <div className="absolute inset-0 opacity-20">
        <div className={`absolute top-0 left-0 right-0 h-px ${isDark ? 'bg-white' : 'bg-slate-400'}`} />
        <div className={`absolute bottom-0 left-0 right-0 h-px ${isDark ? 'bg-white' : 'bg-slate-400'}`} />
        <div className={`absolute top-0 bottom-0 left-1/2 w-px ${isDark ? 'bg-white' : 'bg-slate-400'}`} />
      </div>

      <div className="relative space-y-12">
        {/* Forwards */}
        <div className="flex justify-center gap-12">
          {fwd.map((player, i) => (
            <TacticalPlayer key={player.element} player={player} index={i} isDark={isDark} onOpenDetails={() => setSelectedPlayer(player)} />
          ))}
        </div>

        {/* Midfielders */}
        <div className="flex justify-center gap-8">
          {mid.map((player, i) => (
            <TacticalPlayer key={player.element} player={player} index={i + fwd.length} isDark={isDark} onOpenDetails={() => setSelectedPlayer(player)} />
          ))}
        </div>

        {/* Defenders */}
        <div className="flex justify-center gap-6">
          {def.map((player, i) => (
            <TacticalPlayer key={player.element} player={player} index={i + fwd.length + mid.length} isDark={isDark} onOpenDetails={() => setSelectedPlayer(player)} />
          ))}
        </div>

        {/* Goalkeeper */}
        <div className="flex justify-center">
          {gkp.map((player, i) => (
            <TacticalPlayer key={player.element} player={player} index={i + fwd.length + mid.length + def.length} isDark={isDark} onOpenDetails={() => setSelectedPlayer(player)} />
          ))}
        </div>
      </div>

      <AnimatePresence>
        {selectedPlayer && (
          <PlayerDetailModal
            player={selectedPlayer}
            isDark={isDark}
            onClose={() => setSelectedPlayer(null)}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

// Bench player card - more compact and data-focused
const BenchPlayer: React.FC<{ player: PlayerPick; index: number; isDark: boolean }> = ({ player, index, isDark }) => {
  const [showDetails, setShowDetails] = React.useState(false);
  const posStyle = getPositionStyle(player.position_name || 'MID');
  const status = getAvailabilityStatus(player.chance_of_playing, player.news);

  return (
    <>
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: index * 0.1 }}
        className={`relative group flex items-center gap-3 p-2 border-l-4 ${isDark ? 'bg-white/5 hover:bg-white/10' : 'bg-slate-50 hover:bg-slate-100'
          } transition-colors`}
        style={{ borderLeftColor: posStyle.bg }}
      >
        <div className="absolute bottom-full left-10 mb-2 z-50 hidden group-hover:block">
          <PlayerCard
            player={player}
            isDark={isDark}
            posStyle={posStyle}
            onOpenDetails={() => setShowDetails(true)}
          />
        </div>
        <div className="flex items-center justify-center w-8 h-8 rounded-sm text-white font-bold text-sm"
          style={{ backgroundColor: posStyle.bg }}>
          {player.points}
        </div>

        <div className="flex-1 min-w-0">
          <p className={`text-sm font-bold truncate ${isDark ? 'text-white' : 'text-slate-900'}`}>
            {player.player_name}
          </p>
          <p className={`text-xs ${isDark ? 'text-white/50' : 'text-slate-500'}`}>
            {player.team_short} • £{player.price?.toFixed(1)}m
            {status.text && (
              <span className={`ml-2 px-1.5 py-0.5 rounded-sm text-[10px] font-bold text-white ${status.color}`} title={status.fullText}>
                {status.text === '!' ? 'Suspended/Injured' : status.text}
              </span>
            )}
          </p>
        </div>

        <div className={`text-xs font-mono ${isDark ? 'text-white/40' : 'text-slate-400'}`}>
          {posStyle.text}
        </div>
      </motion.div>

      <AnimatePresence>
        {showDetails && (
          <PlayerDetailModal
            player={player}
            isDark={isDark}
            onClose={() => setShowDetails(false)}
          />
        )}
      </AnimatePresence>
    </>
  );
};

// --- Main Page Component ---

const ManagerPage: React.FC = () => {
  const [theme, setTheme] = React.useState<'dark' | 'light'>(() => {
    if (typeof window !== 'undefined') {
      return (localStorage.getItem('fpl_theme') as 'dark' | 'light') || 'dark';
    }
    return 'dark';
  });

  const {
    managerId,
    setManagerId,
    managerData,
    managerTeam,
    isLoading: managerLoading,
    teamLoading,
    error: managerError,
    handleManagerSubmit,
    refreshTeam,
    clearManager,
  } = useManager();

  const isDark = theme === 'dark';

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    localStorage.setItem('fpl_theme', newTheme);
  };

  React.useEffect(() => {
    if (theme === 'light') {
      document.documentElement.classList.add('light');
    } else {
      document.documentElement.classList.remove('light');
    }
  }, [theme]);

  return (
    <div className={`min-h-screen transition-colors duration-300 ${isDark ? 'bg-slate-950' : 'bg-slate-50'
      }`}>
      {/* Header - More editorial/magazine style */}
      <header className={`border-b-2 ${isDark ? 'border-white/20 bg-slate-950' : 'border-slate-900 bg-white'}`}>
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <Link
                to="/"
                className={`flex items-center gap-2 font-bold uppercase tracking-tight hover:opacity-70 transition-opacity ${isDark ? 'text-white' : 'text-slate-900'
                  }`}
              >
                <ArrowLeft className="w-5 h-5" />
                <span className="hidden sm:inline">Back</span>
              </Link>

              <div className={`h-8 w-px ${isDark ? 'bg-white/20' : 'bg-slate-300'}`} />

              <h1 className={`text-2xl font-black uppercase tracking-tighter ${isDark ? 'text-white' : 'text-slate-900'
                }`}>
                Manager <span className={isDark ? 'text-blue-600' : 'text-blue-600'} style={isDark ? { color: '#003566' } : {}}>Info</span>
              </h1>
            </div>

            <button
              onClick={toggleTheme}
              className={`p-2 rounded-sm border-2 transition-all hover:scale-105 ${isDark
                ? 'border-white/20 text-white hover:border-white/40'
                : 'border-slate-900 text-slate-900 hover:bg-slate-900 hover:text-white'
                }`}
            >
              {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Manager ID Input */}
        {!managerData && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center justify-center min-h-[60vh]"
          >
            <div className={`mb-8 p-8 border-4 ${isDark ? 'border-white/20' : 'border-slate-900'
              }`}>
              <User className={`w-16 h-16 ${isDark ? 'text-white/60' : 'text-slate-400'}`} />
            </div>

            <h2 className={`text-4xl font-black uppercase tracking-tighter mb-3 ${isDark ? 'text-white' : 'text-slate-900'
              }`}>
              Load Manager
            </h2>
            <p className={`text-sm uppercase tracking-wide mb-8 ${isDark ? 'text-white/50' : 'text-slate-500'
              }`}>
              Enter your FPL ID to begin analysis
            </p>

            <form onSubmit={handleManagerSubmit} className="w-full max-w-md space-y-4">
              <input
                type="text"
                value={managerId}
                onChange={(e) => setManagerId(e.target.value)}
                placeholder="Manager ID"
                className={`w-full border-2 px-6 py-4 text-center text-xl font-bold uppercase tracking-wider focus:outline-none transition-all ${isDark
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
                className={`w-full py-4 font-black uppercase tracking-wider transition-all disabled:opacity-30 ${isDark
                  ? 'text-white'
                  : 'bg-slate-900 text-white hover:bg-slate-800'
                  }`}
                style={isDark ? { backgroundColor: '#003566' } : {}}
                onMouseEnter={(e) => isDark && !managerLoading && managerId.trim() && (e.currentTarget.style.backgroundColor = '#004080')}
                onMouseLeave={(e) => isDark && (e.currentTarget.style.backgroundColor = '#003566')}
              >
                {managerLoading ? (
                  <span className="flex items-center justify-center gap-2">
                    <RefreshCw className="w-5 h-5 animate-spin" />
                    Loading
                  </span>
                ) : (
                  'Analyze'
                )}
              </button>
            </form>

            <AnimatePresence>
              {managerError && (
                <motion.p
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="text-red-500 text-sm mt-4 font-bold uppercase"
                >
                  {managerError}
                </motion.p>
              )}
            </AnimatePresence>
          </motion.div>
        )}

        {/* Manager Dashboard */}
        {managerData && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-6"
          >
            {/* Manager Header - Asymmetric layout */}
            <div className={`border-2 p-6 ${isDark ? 'border-white/20 bg-slate-900' : 'border-slate-900 bg-white'
              }`}>
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div className="flex-1">
                  <div className="flex items-baseline gap-3 mb-2">
                    <h2 className={`text-3xl font-black uppercase tracking-tighter ${isDark ? 'text-white' : 'text-slate-900'
                      }`}>
                      {managerData.team_name}
                    </h2>
                    <span className={`text-sm font-bold uppercase ${isDark ? 'text-white/50' : 'text-slate-500'
                      }`}>
                      {managerData.name}
                    </span>
                  </div>

                  {/* Stats in a row - brutalist style */}
                  <div className="flex flex-wrap gap-4 mt-4">
                    <div className={`flex items-center gap-2 px-3 py-1 border ${isDark ? 'border-yellow-500/50 bg-yellow-500/10' : 'border-yellow-600 bg-yellow-50'
                      }`}>
                      <Trophy className="w-4 h-4 text-yellow-500" />
                      <span className={`text-xs font-bold uppercase ${isDark ? 'text-white/60' : 'text-slate-600'}`}>
                        Rank
                      </span>
                      <span className={`text-lg font-black ${isDark ? 'text-white' : 'text-slate-900'}`}>
                        {managerData.overall_rank?.toLocaleString() ?? 'N/A'}
                      </span>
                    </div>

                    <div className={`flex items-center gap-2 px-3 py-1 border ${isDark ? 'border-green-500/50 bg-green-500/10' : 'border-green-600 bg-green-50'
                      }`}>
                      <TrendingUp className="w-4 h-4 text-green-500" />
                      <span className={`text-xs font-bold uppercase ${isDark ? 'text-white/60' : 'text-slate-600'}`}>
                        Points
                      </span>
                      <span className={`text-lg font-black ${isDark ? 'text-white' : 'text-slate-900'}`}>
                        {managerData.overall_points}
                      </span>
                    </div>

                    <div
                      className={`flex items-center gap-2 px-3 py-1 border ${isDark ? 'border-white/20' : 'border-blue-600 bg-blue-50'}`}
                      style={isDark ? { backgroundColor: 'rgba(0, 53, 102, 0.1)', borderColor: 'rgba(0, 53, 102, 0.5)' } : {}}
                    >
                      <Wallet className="w-4 h-4 text-blue-500" />
                      <span className={`text-xs font-bold uppercase ${isDark ? 'text-white/60' : 'text-slate-600'}`}>
                        Value
                      </span>
                      <span className={`text-lg font-black ${isDark ? 'text-white' : 'text-slate-900'}`}>
                        £{managerData.team_value.toFixed(1)}m
                      </span>
                    </div>

                    <div className={`flex items-center gap-2 px-3 py-1 border ${isDark ? 'border-purple-500/50 bg-purple-500/10' : 'border-purple-600 bg-purple-50'
                      }`}>
                      <Activity className="w-4 h-4 text-purple-500" />
                      <span className={`text-xs font-bold uppercase ${isDark ? 'text-white/60' : 'text-slate-600'}`}>
                        Bank
                      </span>
                      <span className={`text-lg font-black ${isDark ? 'text-white' : 'text-slate-900'}`}>
                        £{managerData.bank.toFixed(1)}m
                      </span>
                    </div>
                  </div>
                </div>

                <button
                  onClick={clearManager}
                  className={`px-6 py-3 border-2 font-bold uppercase tracking-wide transition-all hover:scale-105 ${isDark
                    ? 'border-white/20 text-white hover:bg-white hover:text-slate-900'
                    : 'border-slate-900 text-slate-900 hover:bg-slate-900 hover:text-white'
                    }`}
                >
                  <X className="w-4 h-4 inline mr-2" />
                  Change
                </button>
              </div>
            </div>


            <div className="flex flex-col lg:grid lg:grid-cols-3 gap-6">

              <div className="lg:col-span-1 space-y-6 order-2 lg:order-1">
                {managerTeam && (
                  <>
                    {/* Gameweek Header */}
                    <div
                      className={`border-2 p-6 ${isDark ? 'border-white/20' : 'border-blue-600 bg-blue-50'}`}
                      style={isDark ? { backgroundColor: 'rgba(0, 53, 102, 0.1)', borderColor: 'rgba(0, 53, 102, 0.5)' } : {}}
                    >
                      <div className="flex items-center justify-between mb-4">
                        <h3 className={`text-2xl font-black uppercase ${isDark ? 'text-white' : 'text-slate-900'
                          }`}>
                          GW {managerTeam.event}
                        </h3>
                        <button
                          onClick={refreshTeam}
                          disabled={teamLoading}
                          className={`p-2 border transition-all ${isDark ? 'border-white/20 hover:bg-white/10' : 'border-slate-300 hover:bg-slate-100'
                            }`}
                        >
                          <Activity className={`w-4 h-4 ${teamLoading ? 'animate-spin' : ''}`} />
                        </button>
                      </div>

                      <div className="space-y-3">
                        <div>
                          <div className={`text-xs font-bold uppercase mb-1 ${isDark ? 'text-white/60' : 'text-slate-600'
                            }`}>
                            Points
                          </div>
                          <div className={`text-5xl font-black ${isDark ? 'text-white' : 'text-slate-900'
                            }`}>
                            {managerTeam.points}
                          </div>
                        </div>

                        <div className="grid grid-cols-2 gap-3">
                          <div>
                            <div className={`text-xs font-bold uppercase mb-1 ${isDark ? 'text-white/60' : 'text-slate-600'
                              }`}>
                              Rank
                            </div>
                            <div className={`text-xl font-black ${isDark ? 'text-white' : 'text-slate-900'
                              }`}>
                              {managerTeam.rank?.toLocaleString() ?? 'N/A'}
                            </div>
                          </div>

                          <div>
                            <div className={`text-xs font-bold uppercase mb-1 ${isDark ? 'text-white/60' : 'text-slate-600'
                              }`}>
                              Transfers
                            </div>
                            <div className={`text-xl font-black ${isDark ? 'text-white' : 'text-slate-900'
                              }`}>
                              {managerTeam.event_transfers}
                              {managerTeam.event_transfers_cost > 0 && (
                                <span className="text-red-500 text-sm ml-1">
                                  -{managerTeam.event_transfers_cost}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>

                        {managerTeam.active_chip && (
                          <div className={`mt-4 p-2 border-2 text-center ${isDark ? 'border-purple-500 bg-purple-500/20' : 'border-purple-600 bg-purple-100'
                            }`}>
                            <span className="text-sm font-black uppercase text-purple-500">
                              {managerTeam.active_chip}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Bench */}
                    <div className={`border-2 p-4 ${isDark ? 'border-white/20 bg-slate-900' : 'border-slate-900 bg-white'
                      }`}>
                      <h3 className={`text-sm font-black uppercase mb-4 flex items-center gap-2 ${isDark ? 'text-white/80' : 'text-slate-700'
                        }`}>
                        <Minus className="w-4 h-4" />
                        Bench
                      </h3>
                      <div className="space-y-2">
                        {managerTeam.bench.map((player, i) => (
                          <BenchPlayer key={player.element} player={player} index={i} isDark={isDark} />
                        ))}
                      </div>
                    </div>

                    {/* Auto Subs Alert */}
                    {managerTeam.automatic_subs.length > 0 && (
                      <div className={`border-2 p-4 ${isDark ? 'border-orange-500 bg-orange-500/10' : 'border-orange-600 bg-orange-50'
                        }`}>
                        <p className="text-sm font-bold uppercase text-orange-500">
                          {managerTeam.automatic_subs.length} Auto-Sub(s)
                        </p>
                      </div>
                    )}
                  </>
                )}

                {/* Leagues */}
                {managerData.leagues.length > 0 && (
                  <div className={`border-2 p-4 ${isDark ? 'border-white/20 bg-slate-900' : 'border-slate-900 bg-white'
                    }`}>
                    <h3 className={`text-sm font-black uppercase mb-4 ${isDark ? 'text-white/80' : 'text-slate-700'
                      }`}>
                      Leagues
                    </h3>
                    <div className="space-y-2">
                      {managerData.leagues.slice(0, 5).map((league) => (
                        <div
                          key={league.id}
                          className={`flex items-center justify-between p-2 border-l-2 ${isDark ? 'bg-white/5' : 'border-blue-600 bg-slate-50'}`}
                          style={isDark ? { borderLeftColor: '#003566' } : {}}
                        >
                          <span className={`text-xs font-bold truncate flex-1 ${isDark ? 'text-white' : 'text-slate-900'}`}>
                            {league.name}
                          </span>
                          <span className={`text-xs font-mono ml-2 ${isDark ? 'text-white/50' : 'text-slate-500'}`}>
                            #{league.rank.toLocaleString()}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Right Column - Pitch */}
              <div className="lg:col-span-2 order-1 lg:order-2">
                {managerTeam ? (
                  <div className={`border-2 p-6 ${isDark ? 'border-white/20 bg-gradient-to-b from-green-950 to-green-900' : 'border-slate-900 bg-gradient-to-b from-green-100 to-green-200'
                    }`}>
                    <div className="flex items-center justify-between mb-6">
                      <h3 className={`text-xl font-black uppercase flex items-center gap-2 ${isDark ? 'text-white' : 'text-slate-900'
                        }`}>
                        <Shield className="w-5 h-5" />
                        Starting XI
                      </h3>
                      <div className={`px-4 py-2 border-2 ${isDark ? 'border-white/30 bg-white/10' : 'border-slate-900 bg-white'
                        }`}>
                        <span className={`text-sm font-bold uppercase ${isDark ? 'text-white/60' : 'text-slate-600'
                          }`}>
                          Total:{' '}
                        </span>
                        <span className={`text-2xl font-black ${isDark ? 'text-white' : 'text-slate-900'
                          }`}>
                          {managerTeam.points}
                        </span>
                      </div>
                    </div>

                    <FormationView players={managerTeam.starting_xi} isDark={isDark} />
                  </div>
                ) : (
                  <div className={`border-2 p-12 flex items-center justify-center ${isDark ? 'border-white/20 bg-slate-900' : 'border-slate-900 bg-white'
                    }`}>
                    <div className="text-center">
                      <Target className={`w-12 h-12 mx-auto mb-4 ${isDark ? 'text-white/20' : 'text-slate-300'
                        }`} />
                      <p className={`text-sm font-bold uppercase ${isDark ? 'text-white/40' : 'text-slate-400'
                        }`}>
                        Loading formation...
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default ManagerPage;

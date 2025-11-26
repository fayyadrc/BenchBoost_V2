import React from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  User, Trophy, TrendingUp, Wallet, Loader, X, Moon, Sun,
  ArrowLeft, Shield, Target, Activity, Minus, RefreshCw,
} from 'lucide-react';
import { useManager } from '../context/ManagerContext';
import type { PlayerPick } from '../api/client';

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

  // Position styling with unique approach
  const getPositionStyle = (pos: string) => {
    const styles = {
      GKP: { bg: '#FF6B35', border: '#FF8C61', text: 'GK' },
      DEF: { bg: '#004E89', border: '#1A6FA8', text: 'DF' },
      MID: { bg: '#00A878', border: '#2DBB94', text: 'MD' },
      FWD: { bg: '#E63946', border: '#F15A63', text: 'FW' },
    };
    return styles[pos as keyof typeof styles] || styles.MID;
  };

  // Tactical Formation View - More like a real match analysis
  const FormationView: React.FC<{ players: PlayerPick[]; isDark: boolean }> = ({ players, isDark }) => {
    const gkp = players.filter(p => p.position_name === 'GKP');
    const def = players.filter(p => p.position_name === 'DEF');
    const mid = players.filter(p => p.position_name === 'MID');
    const fwd = players.filter(p => p.position_name === 'FWD');

    const TacticalPlayer: React.FC<{ player: PlayerPick; index: number }> = ({ player, index }) => {
      const posStyle = getPositionStyle(player.position_name || 'MID');

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
        </motion.div>
      );
    };

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
              <TacticalPlayer key={player.element} player={player} index={i} />
            ))}
          </div>

          {/* Midfielders */}
          <div className="flex justify-center gap-8">
            {mid.map((player, i) => (
              <TacticalPlayer key={player.element} player={player} index={i + fwd.length} />
            ))}
          </div>

          {/* Defenders */}
          <div className="flex justify-center gap-6">
            {def.map((player, i) => (
              <TacticalPlayer key={player.element} player={player} index={i + fwd.length + mid.length} />
            ))}
          </div>

          {/* Goalkeeper */}
          <div className="flex justify-center">
            {gkp.map((player, i) => (
              <TacticalPlayer key={player.element} player={player} index={i + fwd.length + mid.length + def.length} />
            ))}
          </div>
        </div>
      </div>
    );
  };

  // Bench player card - more compact and data-focused
  const BenchPlayer: React.FC<{ player: PlayerPick; index: number }> = ({ player, index }) => {
    const posStyle = getPositionStyle(player.position_name || 'MID');

    return (
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: index * 0.1 }}
        className={`flex items-center gap-3 p-2 border-l-4 ${isDark ? 'bg-white/5 hover:bg-white/10' : 'bg-slate-50 hover:bg-slate-100'
          } transition-colors`}
        style={{ borderLeftColor: posStyle.bg }}
      >
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
          </p>
        </div>

        <div className={`text-xs font-mono ${isDark ? 'text-white/40' : 'text-slate-400'}`}>
          {posStyle.text}
        </div>
      </motion.div>
    );
  };

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
                Manager <span className={isDark ? 'text-blue-600' : 'text-blue-600'} style={isDark ? { color: '#003566' } : {}}>Data</span>
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

            {/* Main Grid - Asymmetric */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Column - Gameweek Info */}
              <div className="lg:col-span-1 space-y-6">
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
                          <BenchPlayer key={player.element} player={player} index={i} />
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
              <div className="lg:col-span-2">
                {managerTeam ? (
                  <div className={`border-2 p-6 ${isDark ? 'border-white/20 bg-gradient-to-b from-green-950 to-green-900' : 'border-slate-900 bg-gradient-to-b from-green-100 to-green-200'
                    }`}>
                    <div className="flex items-center justify-between mb-6">
                      <h3 className={`text-xl font-black uppercase flex items-center gap-2 ${isDark ? 'text-white' : 'text-slate-900'
                        }`}>
                        <Shield className="w-5 h-5" />
                        Formation
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

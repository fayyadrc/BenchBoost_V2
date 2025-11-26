import React from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  User, Trophy, TrendingUp, Wallet, Zap, Loader, X, Moon, Sun,
  ArrowLeft, Users, Star, Armchair, RefreshCw, Coins, Award
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

  // Manager state from shared context
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

  const positionColors: Record<string, string> = {
    GKP: 'bg-yellow-500',
    DEF: 'bg-green-500',
    MID: 'bg-blue-500',
    FWD: 'bg-red-500',
  };

  // Formation View Component
  const FormationView: React.FC<{ players: PlayerPick[]; isDark: boolean }> = ({ players, isDark }) => {
    // Group players by position
    const gkp = players.filter(p => p.position_name === 'GKP');
    const def = players.filter(p => p.position_name === 'DEF');
    const mid = players.filter(p => p.position_name === 'MID');
    const fwd = players.filter(p => p.position_name === 'FWD');

    const FormationPlayer: React.FC<{ player: PlayerPick }> = ({ player }) => (
      <div className="flex flex-col items-center">
        <div className={`relative w-14 h-14 rounded-full flex items-center justify-center text-white font-bold text-sm ${
          positionColors[player.position_name || 'MID'] || 'bg-slate-500'
        } ${player.is_captain ? 'ring-2 ring-yellow-400' : ''} ${player.is_vice_captain ? 'ring-2 ring-slate-400' : ''}`}>
          {player.points}
          {(player.is_captain || player.is_vice_captain) && (
            <div className={`absolute -top-1 -right-1 w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
              player.is_captain ? 'bg-yellow-500 text-black' : 'bg-slate-500 text-white'
            }`}>
              {player.is_captain ? 'C' : 'V'}
            </div>
          )}
        </div>
        <p className={`text-xs font-medium mt-1 text-center truncate max-w-[80px] ${isDark ? 'text-white' : 'text-slate-900'}`}>
          {player.player_name}
        </p>
        <p className={`text-[10px] ${isDark ? 'text-white/60' : 'text-slate-500'}`}>
          {player.team_short}
        </p>
      </div>
    );

    return (
      <div className="space-y-6">
        {/* Goalkeeper */}
        <div className="flex justify-center">
          {gkp.map(player => (
            <FormationPlayer key={player.element} player={player} />
          ))}
        </div>
        {/* Defenders */}
        <div className="flex justify-center gap-6">
          {def.map(player => (
            <FormationPlayer key={player.element} player={player} />
          ))}
        </div>
        {/* Midfielders */}
        <div className="flex justify-center gap-6">
          {mid.map(player => (
            <FormationPlayer key={player.element} player={player} />
          ))}
        </div>
        {/* Forwards */}
        <div className="flex justify-center gap-8">
          {fwd.map(player => (
            <FormationPlayer key={player.element} player={player} />
          ))}
        </div>
      </div>
    );
  };

  const PlayerCard: React.FC<{ player: PlayerPick; isBench?: boolean; isDark?: boolean }> = ({ player, isBench = false, isDark: isDarkProp }) => {
    const dark = isDarkProp ?? isDark;
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className={`relative rounded-xl p-3 border transition-all ${
          dark
            ? 'bg-white/5 border-white/10 hover:bg-white/10'
            : 'bg-white border-slate-200 hover:bg-slate-50 shadow-sm'
        } ${isBench ? 'opacity-70' : ''}`}
      >
        {/* Captain/Vice Badge */}
        {(player.is_captain || player.is_vice_captain) && (
          <div className={`absolute -top-2 -right-2 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
            player.is_captain ? 'bg-yellow-500 text-black' : 'bg-slate-500 text-white'
          }`}>
            {player.is_captain ? 'C' : 'V'}
          </div>
        )}

        <div className="flex items-center gap-3">
          {/* Position Badge */}
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-white font-bold text-xs ${
            positionColors[player.position_name || 'MID'] || 'bg-slate-500'
          }`}>
            {player.position_name || '?'}
          </div>

          {/* Player Info */}
          <div className="flex-1 min-w-0">
            <p className={`font-semibold ${dark ? 'text-white' : 'text-slate-900'}`}>
              {player.player_name}
            </p>
            <p className={`text-xs ${dark ? 'text-white/60' : 'text-slate-500'}`}>
              {player.team_short} • £{player.price?.toFixed(1)}m
            </p>
          </div>

          {/* Points */}
          <div className="text-right">
            <p className={`text-lg font-bold ${
              player.points > 0 
                ? dark ? 'text-green-400' : 'text-green-600'
                : dark ? 'text-white/60' : 'text-slate-400'
            }`}>
              {player.points}
            </p>
            <p className={`text-xs ${dark ? 'text-white/40' : 'text-slate-400'}`}>pts</p>
          </div>
        </div>
      </motion.div>
    );
  };

  return (
    <div className={`min-h-screen bg-background text-foreground font-sans transition-colors duration-300`}>
      {/* Navbar */}
      <nav className={`sticky top-0 z-50 backdrop-blur-md border-b transition-colors duration-300 ${
        isDark ? 'bg-black/40 border-white/10' : 'bg-white/80 border-slate-200'
      }`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex items-center justify-between gap-4">
            {/* Logo & Back */}
            <div className="flex items-center gap-3">
              <Link
                to="/"
                className={`p-2 rounded-lg transition-colors ${
                  isDark ? 'hover:bg-white/10' : 'hover:bg-slate-100'
                }`}
              >
                <ArrowLeft className={`w-5 h-5 ${isDark ? 'text-white' : 'text-slate-700'}`} />
              </Link>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <Zap className="w-5 h-5 text-white" />
                </div>
                <span className={`text-lg font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                  Manager Dashboard
                </span>
              </div>
            </div>

            {/* Theme Toggle */}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={toggleTheme}
              className={`p-2 rounded-lg transition-colors ${
                isDark ? 'bg-white/10 hover:bg-white/20 text-white' : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
              }`}
              title={`Switch to ${isDark ? 'light' : 'dark'} mode`}
            >
              {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </motion.button>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Manager ID Input (if no manager loaded) */}
        {!managerData && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center justify-center min-h-[60vh]"
          >
            <div className={`w-20 h-20 rounded-2xl flex items-center justify-center mb-6 ${
              isDark ? 'bg-white/10' : 'bg-slate-100'
            }`}>
              <User className={`w-10 h-10 ${isDark ? 'text-white/60' : 'text-slate-400'}`} />
            </div>
            <h2 className={`text-2xl font-bold mb-2 ${isDark ? 'text-white' : 'text-slate-900'}`}>
              Enter Your FPL Manager ID
            </h2>
            <p className={`text-sm mb-6 ${isDark ? 'text-white/60' : 'text-slate-500'}`}>
              Find your ID in the FPL website URL when viewing your team
            </p>

            <form onSubmit={handleManagerSubmit} className="flex flex-col items-center gap-4 w-full max-w-sm">
              <input
                type="text"
                value={managerId}
                onChange={(e) => setManagerId(e.target.value)}
                placeholder="e.g., 1234567"
                className={`w-full border rounded-xl px-4 py-3 text-center text-lg focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all ${
                  isDark
                    ? 'bg-white/10 border-white/20 text-white placeholder-white/40'
                    : 'bg-white border-slate-300 text-slate-900 placeholder-slate-400'
                }`}
                disabled={managerLoading}
              />
              <button
                type="submit"
                disabled={!managerId.trim() || managerLoading}
                className={`w-full bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-xl font-semibold transition-colors flex items-center justify-center gap-2 ${
                  isDark ? 'disabled:bg-white/10 disabled:text-white/40' : 'disabled:bg-slate-200 disabled:text-slate-400'
                }`}
              >
                {managerLoading ? (
                  <>
                    <Loader className="w-5 h-5 animate-spin" />
                    Loading...
                  </>
                ) : (
                  'Load Manager Data'
                )}
              </button>
            </form>

            <AnimatePresence>
              {managerError && (
                <motion.p
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="text-red-400 text-sm mt-4"
                >
                  {managerError}
                </motion.p>
              )}
            </AnimatePresence>
          </motion.div>
        )}

        {/* Manager Data Display */}
        {managerData && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-6"
          >
            {/* Two Column Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Left Column - Manager Info, Leagues & Stats */}
              <div className="lg:col-span-4 space-y-6">
                {/* Manager Header */}
                <div className={`rounded-2xl border p-6 ${
                  isDark ? 'bg-white/5 border-white/10' : 'bg-white border-slate-200 shadow-sm'
                }`}>
                  <div className="flex flex-col gap-4">
                    <div className="flex items-center gap-4">
                      <div className={`w-16 h-16 rounded-2xl flex items-center justify-center ${
                        isDark ? 'bg-gradient-to-br from-blue-500/20 to-purple-500/20' : 'bg-gradient-to-br from-blue-100 to-purple-100'
                      }`}>
                        <User className={`w-8 h-8 ${isDark ? 'text-blue-400' : 'text-blue-600'}`} />
                      </div>
                      <div className="flex-1">
                        <h1 className={`text-xl font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                          {managerData.team_name}
                        </h1>
                        <p className={`text-sm ${isDark ? 'text-white/60' : 'text-slate-500'}`}>
                          {managerData.name}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={clearManager}
                      className={`flex items-center justify-center gap-2 px-4 py-2 rounded-lg transition-colors w-full ${
                        isDark ? 'bg-white/10 hover:bg-white/20 text-white' : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                      }`}
                    >
                      <X className="w-4 h-4" />
                      Change Manager
                    </button>
                  </div>

                  {/* Stats Grid */}
                  <div className="grid grid-cols-2 gap-3 mt-6">
                    <div className={`rounded-xl p-3 ${isDark ? 'bg-white/5' : 'bg-slate-50'}`}>
                      <div className="flex items-center gap-2 mb-1">
                        <Trophy className="w-3.5 h-3.5 text-yellow-500" />
                        <span className={`text-xs ${isDark ? 'text-white/60' : 'text-slate-500'}`}>Rank</span>
                      </div>
                      <p className={`text-lg font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                        {managerData.overall_rank?.toLocaleString() ?? 'N/A'}
                      </p>
                    </div>

                    <div className={`rounded-xl p-3 ${isDark ? 'bg-white/5' : 'bg-slate-50'}`}>
                      <div className="flex items-center gap-2 mb-1">
                        <TrendingUp className="w-3.5 h-3.5 text-green-500" />
                        <span className={`text-xs ${isDark ? 'text-white/60' : 'text-slate-500'}`}>Points</span>
                      </div>
                      <p className={`text-lg font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                        {managerData.overall_points}
                      </p>
                    </div>

                    <div className={`rounded-xl p-3 ${isDark ? 'bg-white/5' : 'bg-slate-50'}`}>
                      <div className="flex items-center gap-2 mb-1">
                        <Wallet className="w-3.5 h-3.5 text-emerald-500" />
                        <span className={`text-xs ${isDark ? 'text-white/60' : 'text-slate-500'}`}>Value</span>
                      </div>
                      <p className={`text-lg font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                        £{managerData.team_value.toFixed(1)}m
                      </p>
                    </div>

                    <div className={`rounded-xl p-3 ${isDark ? 'bg-white/5' : 'bg-slate-50'}`}>
                      <div className="flex items-center gap-2 mb-1">
                        <Coins className="w-3.5 h-3.5 text-blue-500" />
                        <span className={`text-xs ${isDark ? 'text-white/60' : 'text-slate-500'}`}>Bank</span>
                      </div>
                      <p className={`text-lg font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                        £{managerData.bank.toFixed(1)}m
                      </p>
                    </div>
                  </div>

                  {/* Gameweek Stats Section */}
                  {managerTeam && (
                    <>
                      <div className={`flex items-center justify-between mt-6 mb-3`}>
                        <div className="flex items-center gap-2">
                          <Users className={`w-4 h-4 ${isDark ? 'text-blue-400' : 'text-blue-600'}`} />
                          <h3 className={`font-semibold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                            Gameweek {managerTeam.event}
                          </h3>
                          {managerTeam.active_chip && (
                            <span className="px-2 py-0.5 bg-purple-500 text-white text-xs font-bold rounded-full uppercase">
                              {managerTeam.active_chip}
                            </span>
                          )}
                        </div>
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={refreshTeam}
                          disabled={teamLoading}
                          className={`p-2 rounded-lg transition-colors ${
                            isDark ? 'bg-white/10 hover:bg-white/20' : 'bg-slate-100 hover:bg-slate-200'
                          }`}
                        >
                          <RefreshCw className={`w-4 h-4 ${teamLoading ? 'animate-spin' : ''} ${
                            isDark ? 'text-white' : 'text-slate-700'
                          }`} />
                        </motion.button>
                      </div>

                      <div className="grid grid-cols-2 gap-3">
                        <div className={`rounded-xl p-3 ${isDark ? 'bg-white/5' : 'bg-slate-50'}`}>
                          <div className="flex items-center gap-2 mb-1">
                            <Star className="w-3.5 h-3.5 text-yellow-500" />
                            <span className={`text-xs ${isDark ? 'text-white/60' : 'text-slate-500'}`}>GW Points</span>
                          </div>
                          <p className={`text-lg font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                            {managerTeam.points}
                          </p>
                        </div>

                        <div className={`rounded-xl p-3 ${isDark ? 'bg-white/5' : 'bg-slate-50'}`}>
                          <div className="flex items-center gap-2 mb-1">
                            <Trophy className="w-3.5 h-3.5 text-orange-500" />
                            <span className={`text-xs ${isDark ? 'text-white/60' : 'text-slate-500'}`}>GW Rank</span>
                          </div>
                          <p className={`text-lg font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                            {managerTeam.rank?.toLocaleString() ?? 'N/A'}
                          </p>
                        </div>

                        <div className={`rounded-xl p-3 ${isDark ? 'bg-white/5' : 'bg-slate-50'}`}>
                          <div className="flex items-center gap-2 mb-1">
                            <RefreshCw className="w-3.5 h-3.5 text-purple-500" />
                            <span className={`text-xs ${isDark ? 'text-white/60' : 'text-slate-500'}`}>Transfers</span>
                          </div>
                          <p className={`text-lg font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                            {managerTeam.event_transfers}
                            {managerTeam.event_transfers_cost > 0 && (
                              <span className="text-red-400 text-sm ml-1">(-{managerTeam.event_transfers_cost})</span>
                            )}
                          </p>
                        </div>

                            
                      </div>
                    </>
                  )}
                </div>

                {/* Leagues */}
                {managerData.leagues.length > 0 && (
                  <div className={`rounded-2xl border p-6 ${
                    isDark ? 'bg-white/5 border-white/10' : 'bg-white border-slate-200 shadow-sm'
                  }`}>
                    <div className="flex items-center gap-2 mb-4">
                      <Award className={`w-5 h-5 ${isDark ? 'text-purple-400' : 'text-purple-600'}`} />
                      <h2 className={`text-lg font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                        Leagues
                      </h2>
                    </div>
                    <div className="space-y-2">
                      {managerData.leagues.map((league) => (
                        <div
                          key={league.id}
                          className={`flex items-center justify-between p-3 rounded-xl ${
                            isDark ? 'bg-white/5' : 'bg-slate-50'
                          }`}
                        >
                          <span className={`font-medium text-sm ${isDark ? 'text-white' : 'text-slate-900'}`}>
                            {league.name}
                          </span>
                          <span className={`text-xs ${isDark ? 'text-white/60' : 'text-slate-500'}`}>
                            #{league.rank.toLocaleString()}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Auto Subs */}
                {managerTeam && managerTeam.automatic_subs.length > 0 && (
                  <div className={`rounded-2xl border p-4 ${
                    isDark ? 'bg-orange-500/10 border-orange-500/20' : 'bg-orange-50 border-orange-200'
                  }`}>
                    <p className={`text-sm ${isDark ? 'text-orange-400' : 'text-orange-600'}`}>
                      <strong>Auto-subs:</strong> {managerTeam.automatic_subs.length} substitution(s) made
                    </p>
                  </div>
                )}
              </div>

              {/* Right Column - Formation & Bench */}
              <div className="lg:col-span-8 space-y-6">
                {managerTeam ? (
                  <>
                    {/* Football Pitch */}
                    <div className={`rounded-2xl border p-6 ${
                      isDark ? 'bg-gradient-to-b from-green-900/20 to-green-800/20 border-white/10' : 'bg-gradient-to-b from-green-50 to-green-100 border-slate-200 shadow-sm'
                    }`}>
                      <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center gap-2">
                          <Star className={`w-4 h-4 ${isDark ? 'text-yellow-400' : 'text-yellow-500'}`} />
                          <h3 className={`font-semibold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                            Starting XI
                          </h3>
                        </div>
                        <div className={`flex items-center gap-2 px-4 py-2 rounded-xl ${
                          isDark ? 'bg-white/10' : 'bg-white/80 shadow-sm'
                        }`}>
                          <span className={`text-sm ${isDark ? 'text-white/60' : 'text-slate-500'}`}>GW Points</span>
                          <span className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                            {managerTeam.points}
                          </span>
                        </div>
                      </div>
                      
                      {/* Formation Display */}
                      <FormationView players={managerTeam.starting_xi} isDark={isDark} />
                    </div>

                    {/* Bench */}
                    <div className={`rounded-2xl border p-6 ${
                      isDark ? 'bg-white/5 border-white/10' : 'bg-white border-slate-200 shadow-sm'
                    }`}>
                      <div className="flex items-center gap-2 mb-4">
                        <Armchair className={`w-4 h-4 ${isDark ? 'text-slate-400' : 'text-slate-500'}`} />
                        <h3 className={`font-semibold ${isDark ? 'text-white/80' : 'text-slate-700'}`}>
                          Bench
                        </h3>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                        {managerTeam.bench.map((player) => (
                          <PlayerCard key={player.element} player={player} isBench isDark={isDark} />
                        ))}
                      </div>
                    </div>
                  </>
                ) : (
                  <div className={`rounded-2xl border p-12 flex items-center justify-center ${
                    isDark ? 'bg-white/5 border-white/10' : 'bg-white border-slate-200 shadow-sm'
                  }`}>
                    <div className="text-center">
                      <Users className={`w-12 h-12 mx-auto mb-4 ${isDark ? 'text-white/20' : 'text-slate-300'}`} />
                      <p className={`${isDark ? 'text-white/40' : 'text-slate-400'}`}>
                        Loading team data...
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

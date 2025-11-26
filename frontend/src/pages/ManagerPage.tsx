import React from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  User, Trophy, TrendingUp, Wallet, Zap, Loader, X, Moon, Sun,
  ArrowLeft, Users, Star, Armchair, RefreshCw, Coins, Award
} from 'lucide-react';
import { getManagerInfo, getManagerTeam } from '../api/client';
import type { ManagerData, ManagerTeam, PlayerPick } from '../api/client';

const ManagerPage: React.FC = () => {
  // Theme state
  const [theme, setTheme] = React.useState<'dark' | 'light'>(() => {
    if (typeof window !== 'undefined') {
      return (localStorage.getItem('fpl_theme') as 'dark' | 'light') || 'dark';
    }
    return 'dark';
  });

  // Manager state
  const [managerId, setManagerId] = React.useState<string>('');
  const [managerData, setManagerData] = React.useState<ManagerData | null>(null);
  const [managerTeam, setManagerTeam] = React.useState<ManagerTeam | null>(null);
  const [managerLoading, setManagerLoading] = React.useState<boolean>(false);
  const [teamLoading, setTeamLoading] = React.useState<boolean>(false);
  const [managerError, setManagerError] = React.useState<string>('');

  const isDark = theme === 'dark';

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    localStorage.setItem('fpl_theme', newTheme);
  };

  // Apply theme to document
  React.useEffect(() => {
    if (theme === 'light') {
      document.documentElement.classList.add('light');
    } else {
      document.documentElement.classList.remove('light');
    }
  }, [theme]);

  // Load saved manager ID on mount
  React.useEffect(() => {
    const savedId = localStorage.getItem('fpl_manager_id');
    if (savedId) {
      setManagerId(savedId);
      loadManagerData(savedId);
    }
  }, []);

  const loadManagerData = async (id: string) => {
    setManagerLoading(true);
    setManagerError('');

    try {
      const numId = parseInt(id, 10);
      if (isNaN(numId)) {
        throw new Error('Please enter a valid numeric ID');
      }

      const [info, team] = await Promise.all([
        getManagerInfo(numId),
        getManagerTeam(numId),
      ]);

      setManagerData(info);
      setManagerTeam(team);
      localStorage.setItem('fpl_manager_id', id);
    } catch (err: any) {
      setManagerError(err?.message || 'Failed to fetch manager data');
      setManagerData(null);
      setManagerTeam(null);
    } finally {
      setManagerLoading(false);
    }
  };

  const handleManagerSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!managerId.trim() || managerLoading) return;
    await loadManagerData(managerId.trim());
  };

  const refreshTeam = async () => {
    if (!managerData || teamLoading) return;
    setTeamLoading(true);
    try {
      const team = await getManagerTeam(managerData.id);
      setManagerTeam(team);
    } catch (err: any) {
      setManagerError(err?.message || 'Failed to refresh team');
    } finally {
      setTeamLoading(false);
    }
  };

  const clearManager = () => {
    setManagerData(null);
    setManagerTeam(null);
    setManagerId('');
    setManagerError('');
    localStorage.removeItem('fpl_manager_id');
  };

  const positionColors: Record<string, string> = {
    GKP: 'bg-yellow-500',
    DEF: 'bg-green-500',
    MID: 'bg-blue-500',
    FWD: 'bg-red-500',
  };

  const PlayerCard: React.FC<{ player: PlayerPick; isBench?: boolean }> = ({ player, isBench = false }) => (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`relative rounded-xl p-3 border transition-all ${
        isDark
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
          <p className={`font-semibold truncate ${isDark ? 'text-white' : 'text-slate-900'}`}>
            {player.player_name}
          </p>
          <p className={`text-xs ${isDark ? 'text-white/60' : 'text-slate-500'}`}>
            {player.team_short} • £{player.price?.toFixed(1)}m
          </p>
        </div>

        {/* Points */}
        <div className="text-right">
          <p className={`text-lg font-bold ${
            player.points > 0 
              ? isDark ? 'text-green-400' : 'text-green-600'
              : isDark ? 'text-white/60' : 'text-slate-400'
          }`}>
            {player.points}
          </p>
          <p className={`text-xs ${isDark ? 'text-white/40' : 'text-slate-400'}`}>pts</p>
        </div>
      </div>
    </motion.div>
  );

  return (
    <div className={`min-h-screen bg-background text-foreground font-sans transition-colors duration-300`}>
      {/* Navbar */}
      <nav className={`sticky top-0 z-50 backdrop-blur-md border-b transition-colors duration-300 ${
        isDark ? 'bg-black/40 border-white/10' : 'bg-white/80 border-slate-200'
      }`}>
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
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

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
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
            {/* Manager Header */}
            <div className={`rounded-2xl border p-6 ${
              isDark ? 'bg-white/5 border-white/10' : 'bg-white border-slate-200 shadow-sm'
            }`}>
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                  <div className={`w-16 h-16 rounded-2xl flex items-center justify-center ${
                    isDark ? 'bg-gradient-to-br from-blue-500/20 to-purple-500/20' : 'bg-gradient-to-br from-blue-100 to-purple-100'
                  }`}>
                    <User className={`w-8 h-8 ${isDark ? 'text-blue-400' : 'text-blue-600'}`} />
                  </div>
                  <div>
                    <h1 className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                      {managerData.team_name}
                    </h1>
                    <p className={`${isDark ? 'text-white/60' : 'text-slate-500'}`}>
                      {managerData.name}
                    </p>
                  </div>
                </div>
                <button
                  onClick={clearManager}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                    isDark ? 'bg-white/10 hover:bg-white/20 text-white' : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                  }`}
                >
                  <X className="w-4 h-4" />
                  Change Manager
                </button>
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
                <div className={`rounded-xl p-4 ${isDark ? 'bg-white/5' : 'bg-slate-50'}`}>
                  <div className="flex items-center gap-2 mb-1">
                    <Trophy className="w-4 h-4 text-yellow-500" />
                    <span className={`text-xs ${isDark ? 'text-white/60' : 'text-slate-500'}`}>Overall Rank</span>
                  </div>
                  <p className={`text-xl font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                    {managerData.overall_rank?.toLocaleString() ?? 'N/A'}
                  </p>
                </div>

                <div className={`rounded-xl p-4 ${isDark ? 'bg-white/5' : 'bg-slate-50'}`}>
                  <div className="flex items-center gap-2 mb-1">
                    <TrendingUp className="w-4 h-4 text-green-500" />
                    <span className={`text-xs ${isDark ? 'text-white/60' : 'text-slate-500'}`}>Total Points</span>
                  </div>
                  <p className={`text-xl font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                    {managerData.overall_points}
                  </p>
                </div>

                <div className={`rounded-xl p-4 ${isDark ? 'bg-white/5' : 'bg-slate-50'}`}>
                  <div className="flex items-center gap-2 mb-1">
                    <Wallet className="w-4 h-4 text-emerald-500" />
                    <span className={`text-xs ${isDark ? 'text-white/60' : 'text-slate-500'}`}>Team Value</span>
                  </div>
                  <p className={`text-xl font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                    £{managerData.team_value.toFixed(1)}m
                  </p>
                </div>

                <div className={`rounded-xl p-4 ${isDark ? 'bg-white/5' : 'bg-slate-50'}`}>
                  <div className="flex items-center gap-2 mb-1">
                    <Coins className="w-4 h-4 text-blue-500" />
                    <span className={`text-xs ${isDark ? 'text-white/60' : 'text-slate-500'}`}>Bank</span>
                  </div>
                  <p className={`text-xl font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                    £{managerData.bank.toFixed(1)}m
                  </p>
                </div>
              </div>
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
                      <span className={`font-medium ${isDark ? 'text-white' : 'text-slate-900'}`}>
                        {league.name}
                      </span>
                      <span className={`text-sm ${isDark ? 'text-white/60' : 'text-slate-500'}`}>
                        Rank: <span className="font-semibold">{league.rank.toLocaleString()}</span>
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Current Team */}
            {managerTeam && (
              <div className={`rounded-2xl border p-6 ${
                isDark ? 'bg-white/5 border-white/10' : 'bg-white border-slate-200 shadow-sm'
              }`}>
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <Users className={`w-5 h-5 ${isDark ? 'text-blue-400' : 'text-blue-600'}`} />
                    <h2 className={`text-lg font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                      Gameweek {managerTeam.event} Squad
                    </h2>
                    {managerTeam.active_chip && (
                      <span className="px-2 py-0.5 bg-purple-500 text-white text-xs font-bold rounded-full uppercase">
                        {managerTeam.active_chip}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-3">
                    <div className={`text-right ${isDark ? 'text-white/60' : 'text-slate-500'}`}>
                      <span className="text-sm">GW Points: </span>
                      <span className={`text-lg font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                        {managerTeam.points}
                      </span>
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
                </div>

                {/* GW Stats */}
                <div className="grid grid-cols-3 gap-4 mb-6">
                  <div className={`rounded-xl p-3 text-center ${isDark ? 'bg-white/5' : 'bg-slate-50'}`}>
                    <p className={`text-xs ${isDark ? 'text-white/60' : 'text-slate-500'}`}>GW Rank</p>
                    <p className={`font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                      {managerTeam.rank?.toLocaleString() ?? 'N/A'}
                    </p>
                  </div>
                  <div className={`rounded-xl p-3 text-center ${isDark ? 'bg-white/5' : 'bg-slate-50'}`}>
                    <p className={`text-xs ${isDark ? 'text-white/60' : 'text-slate-500'}`}>Transfers</p>
                    <p className={`font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                      {managerTeam.event_transfers}
                      {managerTeam.event_transfers_cost > 0 && (
                        <span className="text-red-400 text-sm ml-1">(-{managerTeam.event_transfers_cost})</span>
                      )}
                    </p>
                  </div>
                  <div className={`rounded-xl p-3 text-center ${isDark ? 'bg-white/5' : 'bg-slate-50'}`}>
                    <p className={`text-xs ${isDark ? 'text-white/60' : 'text-slate-500'}`}>Total Points</p>
                    <p className={`font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                      {managerTeam.total_points}
                    </p>
                  </div>
                </div>

                {/* Starting XI */}
                <div className="mb-6">
                  <div className="flex items-center gap-2 mb-3">
                    <Star className={`w-4 h-4 ${isDark ? 'text-yellow-400' : 'text-yellow-500'}`} />
                    <h3 className={`font-semibold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                      Starting XI
                    </h3>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {managerTeam.starting_xi.map((player) => (
                      <PlayerCard key={player.element} player={player} />
                    ))}
                  </div>
                </div>

                {/* Bench */}
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <Armchair className={`w-4 h-4 ${isDark ? 'text-slate-400' : 'text-slate-500'}`} />
                    <h3 className={`font-semibold ${isDark ? 'text-white/80' : 'text-slate-700'}`}>
                      Bench
                    </h3>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                    {managerTeam.bench.map((player) => (
                      <PlayerCard key={player.element} player={player} isBench />
                    ))}
                  </div>
                </div>

                {/* Auto Subs */}
                {managerTeam.automatic_subs.length > 0 && (
                  <div className={`mt-4 p-3 rounded-xl ${isDark ? 'bg-orange-500/10' : 'bg-orange-50'}`}>
                    <p className={`text-sm ${isDark ? 'text-orange-400' : 'text-orange-600'}`}>
                      <strong>Auto-subs:</strong> {managerTeam.automatic_subs.length} substitution(s) made
                    </p>
                  </div>
                )}
              </div>
            )}
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default ManagerPage;

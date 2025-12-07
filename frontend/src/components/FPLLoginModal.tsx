import React, { useState } from 'react';
import { X, Mail, Chrome, Cookie, AlertCircle, Loader2, HelpCircle } from 'lucide-react';
import { fplLogin, fplLoginGoogle, fplLoginCookie, type FPLLoginResponse } from '../api/client';

type LoginMethod = 'email' | 'google' | 'cookie';

interface FPLLoginModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess: (response: FPLLoginResponse) => void;
    isDark: boolean;
}

const FPLLoginModal: React.FC<FPLLoginModalProps> = ({ isOpen, onClose, onSuccess, isDark }) => {
    const [loginMethod, setLoginMethod] = useState<LoginMethod>('email');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [cookieValue, setCookieValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [showCookieHelp, setShowCookieHelp] = useState(false);

    if (!isOpen) return null;

    const handleEmailLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!email.trim() || !password.trim()) return;

        setIsLoading(true);
        setError(null);

        try {
            const response = await fplLogin(email, password);
            onSuccess(response);
            onClose();
        } catch (err: any) {
            setError(err.message || 'Login failed. Please check your credentials.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleGoogleLogin = async () => {
        setIsLoading(true);
        setError(null);

        try {
            const response = await fplLoginGoogle();
            onSuccess(response);
            onClose();
        } catch (err: any) {
            setError(err.message || 'Google login failed. Make sure you\'re running the app locally.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleCookieLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!cookieValue.trim()) return;

        setIsLoading(true);
        setError(null);

        try {
            const response = await fplLoginCookie(cookieValue);
            onSuccess(response);
            onClose();
        } catch (err: any) {
            setError(err.message || 'Invalid cookie. Please make sure you copied the correct value.');
        } finally {
            setIsLoading(false);
        }
    };

    const bgClass = isDark ? 'bg-slate-900' : 'bg-white';
    const textClass = isDark ? 'text-white' : 'text-slate-900';
    const mutedClass = isDark ? 'text-white/60' : 'text-slate-500';
    const borderClass = isDark ? 'border-white/20' : 'border-slate-200';
    const inputBgClass = isDark ? 'bg-slate-800 text-white placeholder-white/40' : 'bg-slate-50 text-slate-900 placeholder-slate-400';
    const tabActiveClass = isDark ? 'bg-blue-600 text-white' : 'bg-blue-600 text-white';
    const tabInactiveClass = isDark ? 'bg-slate-800 text-white/60 hover:text-white' : 'bg-slate-100 text-slate-600 hover:text-slate-900';

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/50 backdrop-blur-sm"
                onClick={onClose}
            />

            {/* Modal */}
            <div className={`relative w-full max-w-md rounded-2xl ${bgClass} border-2 ${borderClass} shadow-2xl`}>
                {/* Header */}
                <div className={`flex items-center justify-between p-4 border-b ${borderClass}`}>
                    <h2 className={`text-lg font-bold ${textClass}`}>Sign in to FPL</h2>
                    <button
                        onClick={onClose}
                        className={`p-1 rounded-full hover:bg-slate-500/20 transition-colors ${mutedClass}`}
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Login Method Tabs */}
                <div className="flex gap-1 p-4 pb-0">
                    <button
                        onClick={() => setLoginMethod('email')}
                        className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${loginMethod === 'email' ? tabActiveClass : tabInactiveClass
                            }`}
                    >
                        <Mail className="w-4 h-4" />
                        Email
                    </button>
                    <button
                        onClick={() => setLoginMethod('google')}
                        className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${loginMethod === 'google' ? tabActiveClass : tabInactiveClass
                            }`}
                    >
                        <Chrome className="w-4 h-4" />
                        Google
                    </button>
                    <button
                        onClick={() => setLoginMethod('cookie')}
                        className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${loginMethod === 'cookie' ? tabActiveClass : tabInactiveClass
                            }`}
                    >
                        <Cookie className="w-4 h-4" />
                        Cookie
                    </button>
                </div>

                {/* Content */}
                <div className="p-4">
                    {error && (
                        <div className="flex items-start gap-2 p-3 mb-4 rounded-lg bg-red-500/10 border border-red-500/30">
                            <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
                            <p className="text-sm text-red-500">{error}</p>
                        </div>
                    )}

                    {/* Email/Password Login */}
                    {loginMethod === 'email' && (
                        <form onSubmit={handleEmailLogin} className="space-y-4">
                            <p className={`text-sm ${mutedClass}`}>
                                Sign in with your FPL account email and password.
                            </p>
                            <div>
                                <label className={`block text-sm font-medium mb-1 ${textClass}`}>
                                    Email
                                </label>
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="your@email.com"
                                    className={`w-full px-3 py-2 rounded-lg border ${borderClass} ${inputBgClass} focus:outline-none focus:ring-2 focus:ring-blue-500`}
                                    disabled={isLoading}
                                />
                            </div>
                            <div>
                                <label className={`block text-sm font-medium mb-1 ${textClass}`}>
                                    Password
                                </label>
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="••••••••"
                                    className={`w-full px-3 py-2 rounded-lg border ${borderClass} ${inputBgClass} focus:outline-none focus:ring-2 focus:ring-blue-500`}
                                    disabled={isLoading}
                                />
                            </div>
                            <button
                                type="submit"
                                disabled={isLoading || !email.trim() || !password.trim()}
                                className="w-full py-2.5 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
                            >
                                {isLoading ? (
                                    <>
                                        <Loader2 className="w-4 h-4 animate-spin" />
                                        Signing in...
                                    </>
                                ) : (
                                    'Sign in'
                                )}
                            </button>
                        </form>
                    )}

                    {/* Google Login */}
                    {loginMethod === 'google' && (
                        <div className="space-y-4">
                            <p className={`text-sm ${mutedClass}`}>
                                Sign in with your Google account. A browser window will open for you to complete the login.
                            </p>
                            <div className={`p-3 rounded-lg ${isDark ? 'bg-yellow-500/10 border border-yellow-500/30' : 'bg-yellow-50 border border-yellow-200'}`}>
                                <p className={`text-sm ${isDark ? 'text-yellow-400' : 'text-yellow-700'}`}>
                                    <strong>Note:</strong> Google login only works when the app is running locally. For deployed versions, use the Cookie method instead.
                                </p>
                            </div>
                            <button
                                onClick={handleGoogleLogin}
                                disabled={isLoading}
                                className="w-full py-2.5 rounded-lg bg-white text-slate-900 font-medium border border-slate-300 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
                            >
                                {isLoading ? (
                                    <>
                                        <Loader2 className="w-4 h-4 animate-spin" />
                                        Opening browser...
                                    </>
                                ) : (
                                    <>
                                        <svg className="w-5 h-5" viewBox="0 0 24 24">
                                            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                                            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                                            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                                            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                                        </svg>
                                        Sign in with Google
                                    </>
                                )}
                            </button>
                        </div>
                    )}

                    {/* Cookie Login */}
                    {loginMethod === 'cookie' && (
                        <form onSubmit={handleCookieLogin} className="space-y-4">
                            <div className="flex items-start justify-between">
                                <p className={`text-sm ${mutedClass}`}>
                                    Paste your FPL authentication cookie from your browser.
                                </p>
                                <button
                                    type="button"
                                    onClick={() => setShowCookieHelp(!showCookieHelp)}
                                    className={`p-1 rounded-full hover:bg-slate-500/20 transition-colors ${mutedClass}`}
                                >
                                    <HelpCircle className="w-4 h-4" />
                                </button>
                            </div>

                            {showCookieHelp && (
                                <div className={`p-3 rounded-lg text-sm space-y-2 ${isDark ? 'bg-slate-800' : 'bg-slate-100'}`}>
                                    <p className={`font-medium ${textClass}`}>How to get your cookie:</p>
                                    <ol className={`list-decimal list-inside space-y-1 ${mutedClass}`}>
                                        <li>Log in to <a href="https://fantasy.premierleague.com" target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">fantasy.premierleague.com</a></li>
                                        <li>Open Developer Tools (F12 or Cmd+Option+I)</li>
                                        <li>Go to Application → Cookies → fantasy.premierleague.com</li>
                                        <li>Find the <code className="px-1 py-0.5 rounded bg-slate-700 text-white text-xs">pl_profile</code> cookie</li>
                                        <li>Copy its value and paste it below</li>
                                    </ol>
                                </div>
                            )}

                            <div>
                                <label className={`block text-sm font-medium mb-1 ${textClass}`}>
                                    Cookie Value
                                </label>
                                <textarea
                                    value={cookieValue}
                                    onChange={(e) => setCookieValue(e.target.value)}
                                    placeholder="pl_profile=eyJzIjog... (paste full cookie here)"
                                    rows={3}
                                    className={`w-full px-3 py-2 rounded-lg border ${borderClass} ${inputBgClass} focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-xs`}
                                    disabled={isLoading}
                                />
                            </div>
                            <button
                                type="submit"
                                disabled={isLoading || !cookieValue.trim()}
                                className="w-full py-2.5 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
                            >
                                {isLoading ? (
                                    <>
                                        <Loader2 className="w-4 h-4 animate-spin" />
                                        Validating...
                                    </>
                                ) : (
                                    'Verify & Sign in'
                                )}
                            </button>
                        </form>
                    )}
                </div>

                {/* Footer */}
                <div className={`p-4 border-t ${borderClass}`}>
                    <p className={`text-xs text-center ${mutedClass}`}>
                        Your credentials are sent directly to FPL's official servers.
                        We never store your password.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default FPLLoginModal;

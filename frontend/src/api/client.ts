export type QueryRequest = {
  query: string;
  session_id?: string;
  manager_id?: number;
  tools?: string[];
};

export type QueryResponse = {
  answer: string;
  raw_output?: unknown;
};

export type ManagerData = {
  id: number;
  name: string;
  team_name: string;
  overall_rank: number | null;
  overall_points: number;
  gameweek_points: number;
  team_value: number;
  bank: number;
  total_transfers: number;
  leagues: Array<{
    id: number;
    name: string;
    rank: number;
  }>;
};

export type PlayerPick = {
  element: number;
  position: number;
  is_captain: boolean;
  is_vice_captain: boolean;
  multiplier: number;
  player_name: string;
  full_name?: string;
  team_name?: string;
  team_short?: string;
  element_type?: number;
  position_name?: string;
  points: number;
  base_points?: number;
  price?: number;
  selected_by_percent?: string;
  photo?: string;
};

export type AutomaticSub = {
  entry: number;
  element_in: number;
  element_out: number;
  event: number;
};

export type ManagerTeam = {
  entry_id: number;
  event: number;
  active_chip: string | null;
  points: number;
  total_points: number;
  rank: number | null;
  overall_rank: number | null;
  bank: number;
  value: number;
  event_transfers: number;
  event_transfers_cost: number;
  starting_xi: PlayerPick[];
  bench: PlayerPick[];
  automatic_subs: AutomaticSub[];
};

const jsonHeaders = {
  'Content-Type': 'application/json',
};

const API_BASE = ''; 

// Generic fetch wrapper with error handling
async function apiFetch<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, options);
  if (!res.ok) {
    const detail = await res.text().catch(() => '');
    throw new Error(`API error ${res.status}: ${detail || res.statusText}`);
  }
  return res.json();
}

export async function health(): Promise<{ status: string }> {
  return apiFetch('/api/health', { method: 'GET' });
}

export async function getManagerInfo(entryId: number): Promise<ManagerData> {
  return apiFetch(`/api/manager/${entryId}`, { method: 'GET' });
}

export async function getManagerTeam(entryId: number, event?: number): Promise<ManagerTeam> {
  const url = event 
    ? `/api/manager/${entryId}/team?event=${event}`
    : `/api/manager/${entryId}/team`;
  return apiFetch(url, { method: 'GET' });
}

export async function ask(req: QueryRequest): Promise<QueryResponse> {
  return apiFetch('/api/query', {
    method: 'POST',
    headers: jsonHeaders,
    body: JSON.stringify(req),
  });
}

export function getOrCreateSessionId(): string {
  const key = 'fpl_session_id';
  let sid = localStorage.getItem(key);
  if (!sid) {
    sid = `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
    localStorage.setItem(key, sid);
  }
  return sid;
}

export function getSavedManagerId(): number | undefined {
  const saved = localStorage.getItem('fpl_manager_id');
  if (saved) {
    const id = parseInt(saved, 10);
    return isNaN(id) ? undefined : id;
  }
  return undefined;
}

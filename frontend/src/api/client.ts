export type QueryRequest = {
  query: string;
  session_id?: string;
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

const jsonHeaders = {
  'Content-Type': 'application/json',
};

const API_BASE = ''; // rely on Vite proxy in dev

export async function health(): Promise<{ status: string }> {
  const res = await fetch(`${API_BASE}/api/health`, { method: 'GET' });
  if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
  return res.json();
}

export async function getManagerInfo(entryId: number): Promise<ManagerData> {
  const res = await fetch(`${API_BASE}/api/manager/${entryId}`, { method: 'GET' });
  if (!res.ok) {
    const detail = await res.text().catch(() => '');
    throw new Error(`API error ${res.status}: ${detail || res.statusText}`);
  }
  return res.json();
}

export async function ask(req: QueryRequest): Promise<QueryResponse> {
  const res = await fetch(`${API_BASE}/api/query`, {
    method: 'POST',
    headers: jsonHeaders,
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const detail = await res.text().catch(() => '');
    throw new Error(`API error ${res.status}: ${detail || res.statusText}`);
  }
  return res.json();
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

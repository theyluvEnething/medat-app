const SUPABASE_URL = 'https://twjqntyxvpkwbxbyaxzb.supabase.co'
const SUPABASE_ANON_KEY =
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3anFudHl4dnBrd2J4YnlheHpiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkyMjY5MjUsImV4cCI6MjA5NDgwMjkyNX0.wqjTBcbCsoBBYmxfNpCygSxeVEM3Pr7DTKs9LGkDrdw'

export interface LeaderboardEntry {
  id: string
  username: string
  total_score: number
  questions_solved: number
  questions_correct: number
  created_at: string
}

async function supabaseFetch<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const url = `${SUPABASE_URL}/rest/v1/${path}`
  const res = await fetch(url, {
    ...options,
    headers: {
      apikey: SUPABASE_ANON_KEY,
      Authorization: `Bearer ${SUPABASE_ANON_KEY}`,
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })
  if (!res.ok) {
    throw new Error(`Supabase error: ${res.status} ${res.statusText}`)
  }
  return res.json() as Promise<T>
}

export async function fetchLeaderboard(): Promise<LeaderboardEntry[]> {
  return supabaseFetch<LeaderboardEntry[]>(
    'leaderboard?select=*&order=total_score.desc',
  )
}

export async function upsertUserScore(
  username: string,
  totalScore: number,
  questionsSolved: number,
  questionsCorrect: number,
): Promise<void> {
  // Try update first, if row doesn't exist, insert via upsert
  await supabaseFetch('leaderboard', {
    method: 'POST',
    headers: {
      Prefer: 'resolution=merge-duplicates',
    },
    body: JSON.stringify({
      username,
      total_score: totalScore,
      questions_solved: questionsSolved,
      questions_correct: questionsCorrect,
    }),
  })
}

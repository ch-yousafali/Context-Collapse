import React, { useState, useEffect, useCallback } from 'react'
import { 
  Zap, RefreshCw, Archive, Eye, EyeOff, Filter, 
  ExternalLink, MessageSquare, TrendingUp, Clock,
  ChevronRight, X, Terminal, Radio, Shield, Cpu,
  Globe, Database, Smartphone, Code2, Briefcase, Package
} from 'lucide-react'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5001'

const CATEGORY_ICONS = {
  'Frontend': Code2,
  'Backend': Cpu,
  'AI/ML': Terminal,
  'DevOps': Globe,
  'Security': Shield,
  'Mobile': Smartphone,
  'Database': Database,
  'Career': Briefcase,
  'Release': Package,
  'Other': Radio
}

const CATEGORY_COLORS = {
  'Frontend': 'text-cyan-400 bg-cyan-400/10 border-cyan-400/20',
  'Backend': 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20',
  'AI/ML': 'text-violet-400 bg-violet-400/10 border-violet-400/20',
  'DevOps': 'text-amber-400 bg-amber-400/10 border-amber-400/20',
  'Security': 'text-red-400 bg-red-400/10 border-red-400/20',
  'Mobile': 'text-pink-400 bg-pink-400/10 border-pink-400/20',
  'Database': 'text-blue-400 bg-blue-400/10 border-blue-400/20',
  'Career': 'text-orange-400 bg-orange-400/10 border-orange-400/20',
  'Release': 'text-green-400 bg-green-400/10 border-green-400/20',
  'Other': 'text-slate-400 bg-slate-400/10 border-slate-400/20'
}

const IMPACT_COLORS = {
  10: 'bg-red-500 text-white border-red-400',
  9: 'bg-orange-500 text-white border-orange-400',
  8: 'bg-amber-500 text-slate-900 border-amber-400',
  7: 'bg-yellow-500 text-slate-900 border-yellow-400',
  6: 'bg-lime-500 text-slate-900 border-lime-400',
  5: 'bg-emerald-500 text-slate-900 border-emerald-400',
  4: 'bg-teal-500 text-white border-teal-400',
  3: 'bg-cyan-500 text-slate-900 border-cyan-400',
  2: 'bg-sky-500 text-white border-sky-400',
  1: 'bg-slate-500 text-white border-slate-400'
}

function ImpactBadge({ score }) {
  const colorClass = IMPACT_COLORS[score] || IMPACT_COLORS[5]
  return (
    <div className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-bold font-mono border ${colorClass}`}>
      <TrendingUp size={12} />
      {score}/10
    </div>
  )
}

function CategoryBadge({ category }) {
  const Icon = CATEGORY_ICONS[category] || Radio
  const colorClass = CATEGORY_COLORS[category] || CATEGORY_COLORS['Other']
  return (
    <div className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-medium border ${colorClass}`}>
      <Icon size={12} />
      {category}
    </div>
  )
}

function SourceLink({ source }) {
  return (
    <a 
      href={source.url}
      target="_blank"
      rel="noopener noreferrer"
      className="flex items-center gap-2 p-2.5 rounded-lg bg-slate-800/50 hover:bg-slate-800 border border-slate-700/50 hover:border-slate-600 transition-all group"
    >
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono text-slate-400">{source.platform}</span>
          {source.engagement_metrics && source.engagement_metrics !== 'RSS Feed' && (
            <span className="text-xs text-slate-500 flex items-center gap-1">
              <MessageSquare size={10} />
              {source.engagement_metrics}
            </span>
          )}
        </div>
        <p className="text-sm text-slate-300 truncate group-hover:text-slate-100 transition-colors">
          {source.title}
        </p>
      </div>
      <ExternalLink size={14} className="text-slate-500 group-hover:text-slate-300 shrink-0" />
    </a>
  )
}

function StoryDrawer({ story, onClose, onArchive }) {
  if (!story) return null

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <div 
        className="absolute inset-0 bg-slate-950/60 backdrop-blur-sm"
        onClick={onClose}
      />
      <div className="relative w-full max-w-lg bg-slate-900 border-l border-slate-800 h-full overflow-y-auto slide-in">
        <div className="sticky top-0 z-10 bg-slate-900/95 backdrop-blur border-b border-slate-800 p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <ImpactBadge score={story.impact_score} />
            <CategoryBadge category={story.category} />
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => onArchive(story.id)}
              className="p-2 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
              title="Archive"
            >
              <Archive size={18} />
            </button>
            <button
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
            >
              <X size={18} />
            </button>
          </div>
        </div>

        <div className="p-6 space-y-6">
          <div>
            <h2 className="text-2xl font-bold text-slate-100 leading-tight mb-3">
              {story.unified_title}
            </h2>
            <div className="flex items-center gap-2 text-xs text-slate-500 font-mono">
              <Clock size={12} />
              {new Date(story.timestamp).toLocaleString()}
            </div>
          </div>

          <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2 text-amber-400">
              <Zap size={16} />
              <span className="text-xs font-bold uppercase tracking-wider">TL;DR</span>
            </div>
            <p className="text-slate-300 leading-relaxed text-sm">
              {story.tldr}
            </p>
          </div>

          {story.key_terms && story.key_terms.length > 0 && (
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">Key Terms</h3>
              <div className="flex flex-wrap gap-2">
                {story.key_terms.map((term, i) => (
                  <span 
                    key={i}
                    className="px-2.5 py-1 rounded-md bg-slate-800 text-slate-300 text-xs font-mono border border-slate-700"
                  >
                    {term}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">
              Sources ({story.sources?.length || 0})
            </h3>
            <div className="space-y-2">
              {story.sources?.map((source, i) => (
                <SourceLink key={i} source={source} />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function HeroStory({ story, onClick }) {
  const glowClass = story.impact_score >= 10 ? 'impact-glow-10' : 
                    story.impact_score >= 9 ? 'impact-glow-9' : 'impact-glow-8'

  return (
    <div 
      onClick={() => onClick(story)}
      className={`relative overflow-hidden rounded-2xl border border-slate-700/50 bg-gradient-to-br from-slate-800/80 to-slate-900/80 p-6 cursor-pointer story-card ${glowClass}`}
    >
      <div className="absolute top-0 right-0 p-4">
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono text-slate-500 uppercase tracking-wider">Top Impact</span>
          <ImpactBadge score={story.impact_score} />
        </div>
      </div>

      <div className="mt-8">
        <CategoryBadge category={story.category} />
        <h1 className="mt-4 text-3xl md:text-4xl font-bold text-slate-100 leading-tight">
          {story.unified_title}
        </h1>
        <p className="mt-4 text-slate-400 text-lg leading-relaxed max-w-3xl">
          {story.tldr}
        </p>

        <div className="mt-6 flex items-center gap-4">
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <MessageSquare size={14} />
            <span>{story.sources?.length || 0} sources</span>
          </div>
          <div className="flex items-center gap-1 text-sm text-slate-500">
            <span className="text-slate-600">Click to read more</span>
            <ChevronRight size={14} className="text-slate-600" />
          </div>
        </div>
      </div>

      <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-amber-500/50 to-transparent" />
    </div>
  )
}

function StoryCard({ story, onClick }) {
  return (
    <div 
      onClick={() => onClick(story)}
      className="group relative rounded-xl border border-slate-800 bg-slate-900/50 hover:bg-slate-800/50 p-4 cursor-pointer story-card"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <CategoryBadge category={story.category} />
            <ImpactBadge score={story.impact_score} />
          </div>
          <h3 className="text-base font-semibold text-slate-200 group-hover:text-slate-100 transition-colors line-clamp-2">
            {story.unified_title}
          </h3>
          <p className="mt-2 text-sm text-slate-500 line-clamp-2 leading-relaxed">
            {story.tldr}
          </p>
          <div className="mt-3 flex items-center gap-3 text-xs text-slate-600">
            <span className="flex items-center gap-1">
              <MessageSquare size={12} />
              {story.sources?.length || 0} sources
            </span>
            <span className="flex items-center gap-1">
              <Clock size={12} />
              {new Date(story.timestamp).toLocaleDateString()}
            </span>
          </div>
        </div>
        <ChevronRight size={16} className="text-slate-700 group-hover:text-slate-500 shrink-0 mt-1 transition-colors" />
      </div>
    </div>
  )
}

function ControlBar({ onSync, isSyncing, minScore, setMinScore, showArchived, setShowArchived, stats }) {
  return (
    <div className="sticky top-0 z-40 glass-panel border-b border-slate-800">
      <div className="max-w-6xl mx-auto px-4 py-3 flex flex-wrap items-center gap-4">
        <div className="flex items-center gap-2">
          <Terminal size={20} className="text-amber-500" />
          <span className="font-bold text-slate-100 tracking-tight">Context-Collapse</span>
          <span className="text-xs font-mono text-slate-600 bg-slate-800 px-1.5 py-0.5 rounded">v1.0</span>
        </div>

        <div className="flex-1" />

        <div className="flex items-center gap-4 text-xs font-mono text-slate-500">
          {stats && (
            <>
              <span className="flex items-center gap-1">
                <Radio size={12} className="text-emerald-500" />
                {stats.unread} unread
              </span>
              <span className="flex items-center gap-1">
                <Archive size={12} className="text-slate-600" />
                {stats.archived} archived
              </span>
              <span className="flex items-center gap-1">
                <TrendingUp size={12} className="text-amber-500" />
                avg {stats.avg_impact}
              </span>
            </>
          )}
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Filter size={14} className="text-slate-500" />
            <span className="text-xs text-slate-500">Min Impact:</span>
            <input
              type="range"
              min="1"
              max="10"
              value={minScore}
              onChange={(e) => setMinScore(parseInt(e.target.value))}
              className="w-24 accent-amber-500"
            />
            <span className="text-xs font-mono font-bold text-amber-500 w-4">{minScore}</span>
          </div>

          <button
            onClick={() => setShowArchived(!showArchived)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              showArchived 
                ? 'bg-slate-700 text-slate-200' 
                : 'bg-slate-800 text-slate-500 hover:text-slate-300'
            }`}
          >
            {showArchived ? <Eye size={14} /> : <EyeOff size={14} />}
            {showArchived ? 'Show All' : 'Hide Archived'}
          </button>

          <button
            onClick={onSync}
            disabled={isSyncing}
            className="flex items-center gap-2 px-4 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-900 text-sm font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <RefreshCw size={14} className={isSyncing ? 'animate-spin' : ''} />
            {isSyncing ? 'Syncing...' : 'Sync Now'}
          </button>
        </div>
      </div>
    </div>
  )
}

function App() {
  const [stories, setStories] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [isSyncing, setIsSyncing] = useState(false)
  const [selectedStory, setSelectedStory] = useState(null)
  const [minScore, setMinScore] = useState(1)
  const [showArchived, setShowArchived] = useState(false)
  const [error, setError] = useState(null)

  const fetchStories = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const params = new URLSearchParams({
        min_score: minScore.toString(),
        include_archived: showArchived.toString()
      })
      const res = await fetch(`${API_BASE}/api/stories?${params}`)
      if (!res.ok) throw new Error('Failed to fetch stories')
      const data = await res.json()
      setStories(data.stories || [])
    } catch (err) {
      setError(err.message)
      console.error('Fetch error:', err)
    } finally {
      setLoading(false)
    }
  }, [minScore, showArchived])

  const fetchStats = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/stats`)
      if (res.ok) {
        const data = await res.json()
        setStats(data)
      }
    } catch (err) {
      console.error('Stats error:', err)
    }
  }, [])

  const handleSync = async () => {
    setIsSyncing(true)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/api/sync`, { method: 'POST' })
      if (!res.ok) throw new Error('Sync failed')
      await fetchStories()
      await fetchStats()
    } catch (err) {
      setError(err.message)
      console.error('Sync error:', err)
    } finally {
      setIsSyncing(false)
    }
  }

  const handleArchive = async (storyId) => {
    try {
      await fetch(`${API_BASE}/api/stories/${storyId}/archive`, { method: 'POST' })
      setSelectedStory(null)
      await fetchStories()
      await fetchStats()
    } catch (err) {
      console.error('Archive error:', err)
    }
  }

  useEffect(() => {
    fetchStories()
    fetchStats()
  }, [fetchStories, fetchStats])

  const heroStory = stories[0]
  const feedStories = stories.slice(1)

  return (
    <div className="min-h-screen bg-slate-950">
      <ControlBar 
        onSync={handleSync}
        isSyncing={isSyncing}
        minScore={minScore}
        setMinScore={setMinScore}
        showArchived={showArchived}
        setShowArchived={setShowArchived}
        stats={stats}
      />

      <main className="max-w-6xl mx-auto px-4 py-8 space-y-8">
        {error && (
          <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-red-400 text-sm">
            <div className="flex items-center gap-2">
              <Shield size={16} />
              <span className="font-semibold">Error:</span>
              <span>{error}</span>
            </div>
            <p className="mt-1 text-xs text-red-400/70 ml-6">
              Make sure the Flask backend is running on port 5001
            </p>
          </div>
        )}

        {loading && stories.length === 0 ? (
          <div className="flex items-center justify-center py-20">
            <div className="flex items-center gap-3 text-slate-500">
              <RefreshCw size={20} className="animate-spin" />
              <span className="font-mono text-sm">Loading intelligence feed...</span>
            </div>
          </div>
        ) : stories.length === 0 ? (
          <div className="text-center py-20">
            <Radio size={48} className="mx-auto text-slate-700 mb-4" />
            <h2 className="text-xl font-semibold text-slate-400">No stories found</h2>
            <p className="mt-2 text-sm text-slate-600">
              Try lowering the impact score filter or click "Sync Now" to fetch fresh data.
            </p>
          </div>
        ) : (
          <>
            {heroStory && (
              <section>
                <div className="flex items-center gap-2 mb-4">
                  <Zap size={16} className="text-amber-500" />
                  <h2 className="text-sm font-bold uppercase tracking-wider text-slate-500">Top Story</h2>
                </div>
                <HeroStory story={heroStory} onClick={setSelectedStory} />
              </section>
            )}

            {feedStories.length > 0 && (
              <section>
                <div className="flex items-center gap-2 mb-4">
                  <Terminal size={16} className="text-slate-500" />
                  <h2 className="text-sm font-bold uppercase tracking-wider text-slate-500">
                    The Feed ({feedStories.length})
                  </h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {feedStories.map((story) => (
                    <StoryCard 
                      key={story.id} 
                      story={story} 
                      onClick={setSelectedStory} 
                    />
                  ))}
                </div>
              </section>
            )}
          </>
        )}
      </main>

      <footer className="border-t border-slate-800/50 mt-12 py-6">
        <div className="max-w-6xl mx-auto px-4 flex items-center justify-between text-xs text-slate-600 font-mono">
          <span>Context-Collapse v1.0 // Self-hosted Intelligence</span>
          <span>Built for developers, by developers</span>
        </div>
      </footer>

      <StoryDrawer 
        story={selectedStory} 
        onClose={() => setSelectedStory(null)}
        onArchive={handleArchive}
      />
    </div>
  )
}

export default App
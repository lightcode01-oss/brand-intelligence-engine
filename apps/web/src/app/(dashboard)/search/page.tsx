'use client';

import React, { useState, useEffect } from 'react';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { apiClient } from '@/lib/api/client';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Search, Loader2, Clock, Layers, Folder, Heart, Sparkles } from 'lucide-react';

interface SearchProject {
  id: string;
  prompt: string;
  created_at: string;
}

interface SearchName {
  id: string;
  name_string: string;
  style: string;
}

interface SearchCollection {
  id: string;
  name: string;
  description?: string;
}

interface SearchFavorite {
  id: string;
  name_id: string;
  name_string: string;
}

interface SearchResults {
  projects: SearchProject[];
  names: SearchName[];
  collections: SearchCollection[];
  favorites: SearchFavorite[];
}

export default function SearchPage() {
  const workspace = useWorkspaceStore();
  const workspaceId = workspace.activeWorkspace?.id;

  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<SearchResults | null>(null);
  const [recents, setRecents] = useState<string[]>([]);

  const fetchRecents = async () => {
    if (!workspaceId) return;
    try {
      const res = await apiClient.get(`/search/recent?workspace_id=${workspaceId}`);
      setRecents(res.data?.data || []);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchRecents();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [workspaceId]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || !workspaceId) return;
    setLoading(true);
    try {
      const res = await apiClient.get(`/search/?workspace_id=${workspaceId}&q=${query}`);
      setResults(res.data?.data || null);
      fetchRecents();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRecentClick = (term: string) => {
    setQuery(term);
    setLoading(true);
    apiClient.get(`/search/?workspace_id=${workspaceId}&q=${term}`)
      .then((res) => setResults(res.data?.data || null))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <Search className="h-6 w-6 text-indigo-600 animate-pulse" /> Workspace Intelligence Search
        </h1>
        <p className="text-sm text-slate-500 mt-1">Fuzzy match query projects, candidates names, collections, and favorites.</p>
      </div>

      {/* Search Input Box */}
      <Card className="border-indigo-100 dark:border-indigo-950/40 bg-white/60 dark:bg-slate-950/60 backdrop-blur-md shadow-lg">
        <CardContent className="pt-6">
          <form onSubmit={handleSearch} className="flex gap-2">
            <div className="relative flex-1">
              <Input
                placeholder="Search prompt terms, name styles, or collections folders..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full pl-4"
              />
            </div>
            <Button type="submit" disabled={loading} className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700">
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
              <span>Search</span>
            </Button>
          </form>

          {/* Recent Searches */}
          {recents.length > 0 && (
            <div className="mt-4 flex flex-wrap items-center gap-2 text-xs">
              <span className="text-slate-400 flex items-center gap-1"><Clock className="h-3 w-3" /> Recent:</span>
              {recents.map((term, i) => (
                <button
                  key={i}
                  onClick={() => handleRecentClick(term)}
                  className="px-2.5 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-indigo-50 dark:hover:bg-indigo-950/20 hover:text-indigo-600 transition duration-150"
                >
                  {term}
                </button>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Results Rendering */}
      {loading && (
        <div className="flex justify-center items-center py-20">
          <Loader2 className="h-10 w-10 animate-spin text-indigo-600" />
        </div>
      )}

      {!loading && results && (
        <div className="space-y-6">
          {/* Projects Results */}
          {results.projects?.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-2">
                  <Layers className="h-4 w-4 text-indigo-600" /> Brainstorming Projects ({results.projects.length})
                </CardTitle>
              </CardHeader>
              <CardContent className="divide-y divide-slate-100 dark:divide-slate-800">
                {results.projects.map((p: SearchProject) => (
                  <div key={p.id} className="py-3 flex justify-between items-center hover:bg-slate-50/50 dark:hover:bg-slate-900/20 px-2 rounded-lg transition">
                    <div>
                      <p className="font-medium text-slate-800 dark:text-slate-200">{p.prompt}</p>
                      <span className="text-xxs text-slate-400">Created: {new Date(p.created_at).toLocaleDateString()}</span>
                    </div>
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={() => window.location.href = `/projects/${p.id}/generate`}
                    >
                      Open Campaign
                    </Button>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Names Results */}
          {results.names?.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-emerald-600" /> Generated Candidates ({results.names.length})
                </CardTitle>
              </CardHeader>
              <CardContent className="grid gap-3 sm:grid-cols-2">
                {results.names.map((n: SearchName) => (
                  <div key={n.id} className="p-4 rounded-xl border border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-950 flex justify-between items-center">
                    <div>
                      <p className="font-bold text-lg text-slate-900 dark:text-white">{n.name_string}</p>
                      <span className="text-xxs text-slate-400 capitalize">{n.style} style</span>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Collections Results */}
          {results.collections?.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-2">
                  <Folder className="h-4 w-4 text-amber-500" /> Folders Collections ({results.collections.length})
                </CardTitle>
              </CardHeader>
              <CardContent className="divide-y divide-slate-100 dark:divide-slate-800">
                {results.collections.map((c: SearchCollection) => (
                  <div key={c.id} className="py-3 px-2 flex justify-between items-center">
                    <div>
                      <p className="font-semibold text-slate-800 dark:text-slate-200">{c.name}</p>
                      {c.description && <p className="text-xs text-slate-500">{c.description}</p>}
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Favorites Results */}
          {results.favorites?.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-2">
                  <Heart className="h-4 w-4 text-red-500" /> Starred Favorites ({results.favorites.length})
                </CardTitle>
              </CardHeader>
              <CardContent className="grid gap-3 sm:grid-cols-2">
                {results.favorites.map((f: SearchFavorite) => (
                  <div key={f.id} className="p-4 rounded-xl border border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-950 flex items-center gap-2">
                    <Heart className="h-4 w-4 text-red-500 fill-red-500" />
                    <p className="font-bold text-slate-800 dark:text-slate-200">{f.name_string}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Empty Results Placeholder */}
          {results.projects?.length === 0 && results.names?.length === 0 && results.collections?.length === 0 && results.favorites?.length === 0 && (
            <div className="text-center py-20 text-slate-400">
              No matching workspace entities found. Try different keywords!
            </div>
          )}
        </div>
      )}
    </div>
  );
}

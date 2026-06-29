'use client';

import React, { useState, useEffect } from 'react';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { apiClient } from '@/lib/api/client';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Heart, Loader2, Copy, Sparkles } from 'lucide-react';

interface FavoriteItem {
  id: string;
  name_id: string;
  name_ref?: {
    id: string;
    name_string: string;
    style: string;
  };
}

export default function FavoritesPage() {
  const workspace = useWorkspaceStore();
  const workspaceId = workspace.activeWorkspace?.id;

  const [favorites, setFavorites] = useState<FavoriteItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState<string | null>(null);

  const fetchFavorites = async () => {
    if (!workspaceId) return;
    setLoading(true);
    try {
      const res = await apiClient.get(`/favorites?workspace_id=${workspaceId}`);
      setFavorites(res.data?.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFavorites();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [workspaceId]);

  const handleCopy = (name: string) => {
    navigator.clipboard.writeText(name);
    setCopied(name);
    setTimeout(() => setCopied(null), 2000);
  };

  const handleUnfavorite = async (nameId: string) => {
    if (!workspaceId) return;
    try {
      await apiClient.post(`/names/${nameId}/favorite?workspace_id=${workspaceId}`);
      setFavorites((prev) => prev.filter((f) => f.name_id !== nameId));
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <Heart className="h-6 w-6 text-red-500 fill-red-500" /> Starred Candidates
        </h1>
        <p className="text-sm text-slate-500 mt-1">Your saved brand name concepts inside the active workspace.</p>
      </div>

      {loading ? (
        <div className="flex justify-center items-center py-20">
          <Loader2 className="h-10 w-10 animate-spin text-indigo-600" />
        </div>
      ) : favorites.length === 0 ? (
        <Card className="py-20 text-center text-slate-400">
          <CardContent>
            You have no starred names in this workspace. 
            Go to project campaign workflows to star name suggestions.
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {favorites.map((fav) => {
            const nameString = fav.name_ref?.name_string || 'SuggestedName';
            const styleName = fav.name_ref?.style || 'Abstract';
            return (
              <Card 
                key={fav.id} 
                className="border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-950 shadow-sm hover:shadow-md transition hover:-translate-y-0.5 duration-200"
              >
                <CardContent className="p-5 flex justify-between items-center">
                  <div>
                    <h3 className="font-bold text-xl text-slate-900 dark:text-white flex items-center gap-2">
                      <Sparkles className="h-4 w-4 text-indigo-500" /> {nameString}
                    </h3>
                    <span className="text-xxs text-slate-400 capitalize">{styleName} style</span>
                  </div>
                  <div className="flex gap-2">
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      onClick={() => handleCopy(nameString)}
                      className="h-8 w-8 p-0"
                    >
                      <Copy className="h-4 w-4 text-slate-500" />
                    </Button>
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      onClick={() => handleUnfavorite(fav.name_id)}
                      className="h-8 w-8 p-0"
                    >
                      <Heart className="h-4 w-4 fill-red-500 text-red-500" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {copied && (
        <div className="fixed bottom-6 right-6 px-4 py-2 bg-indigo-600 text-white rounded-lg shadow-lg text-sm animate-fade-in">
          Copied &quot;{copied}&quot; to clipboard!
        </div>
      )}
    </div>
  );
}

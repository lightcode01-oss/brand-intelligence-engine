'use client';

import React, { useState, useEffect } from 'react';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { apiClient } from '@/lib/api/client';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Field } from '@/components/forms/Field';
import { Folder, Loader2, Plus, Trash2, Copy, Sparkles } from 'lucide-react';

interface CollectionItem {
  id: string;
  workspace_id: string;
  name: string;
  description: string | null;
}

interface CollectionItemPayload {
  id: string;
  collection_id: string;
  name_id: string;
  name_ref?: {
    id: string;
    name_string: string;
    style: string;
  };
}

export default function CollectionsPage() {
  const workspace = useWorkspaceStore();
  const workspaceId = workspace.activeWorkspace?.id;

  const [collections, setCollections] = useState<CollectionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');

  // Items lookup for active collection
  const [selectedCol, setSelectedCol] = useState<CollectionItem | null>(null);
  const [colItems, setColItems] = useState<CollectionItemPayload[]>([]);
  const [loadingItems, setLoadingItems] = useState(false);

  const fetchCollections = async () => {
    if (!workspaceId) return;
    setLoading(true);
    try {
      const res = await apiClient.get(`/collections?workspace_id=${workspaceId}`);
      setCollections(res.data?.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCollections();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [workspaceId]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !workspaceId) return;
    setCreating(true);
    try {
      const res = await apiClient.post(`/collections?workspace_id=${workspaceId}`, {
        name,
        description
      });
      setCollections((prev) => [...prev, res.data?.data]);
      setName('');
      setDescription('');
    } catch (err) {
      console.error(err);
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await apiClient.delete(`/collections/${id}`);
      setCollections((prev) => prev.filter((c) => c.id !== id));
      if (selectedCol?.id === id) {
        setSelectedCol(null);
        setColItems([]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleSelectCollection = async (col: CollectionItem) => {
    setSelectedCol(col);
    setLoadingItems(true);
    try {
      const res = await apiClient.get(`/collections/${col.id}/items`);
      setColItems(res.data?.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingItems(false);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <Folder className="h-6 w-6 text-amber-500 fill-amber-500/20" /> Collections Manager
        </h1>
        <p className="text-sm text-slate-500 mt-1">Group name suggestions in categorized folders for your naming campaigns.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left Side: Create Folder & Folders List */}
        <div className="lg:col-span-1 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-semibold">New Collection Folder</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreate} className="space-y-4">
                <Field label="Folder Name">
                  <Input
                    placeholder="e.g. Fintech Ideas, Healthcare Names"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                  />
                </Field>
                <Field label="Description (Optional)">
                  <Input
                    placeholder="Short description..."
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                  />
                </Field>
                <Button type="submit" disabled={creating} className="w-full flex items-center justify-center gap-2 bg-indigo-600">
                  {creating ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
                  <span>Create Folder</span>
                </Button>
              </form>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-semibold">Folders List</CardTitle>
            </CardHeader>
            <CardContent className="p-0 divide-y divide-slate-100 dark:divide-slate-800">
              {loading ? (
                <div className="flex justify-center py-6">
                  <Loader2 className="h-6 w-6 animate-spin text-indigo-600" />
                </div>
              ) : collections.length === 0 ? (
                <div className="text-center py-10 text-xs text-slate-400">No collection folders created.</div>
              ) : (
                collections.map((col) => (
                  <div 
                    key={col.id} 
                    className={`flex items-center justify-between p-4 cursor-pointer hover:bg-slate-50/50 dark:hover:bg-slate-900/10 transition ${selectedCol?.id === col.id ? 'bg-indigo-50/30 dark:bg-indigo-950/10' : ''}`}
                    onClick={() => handleSelectCollection(col)}
                  >
                    <div className="flex items-center gap-3">
                      <Folder className={`h-5 w-5 ${selectedCol?.id === col.id ? 'text-indigo-600' : 'text-slate-400'}`} />
                      <div>
                        <p className="font-semibold text-sm text-slate-800 dark:text-slate-200">{col.name}</p>
                      </div>
                    </div>
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(col.id);
                      }}
                      className="p-1 rounded text-slate-400 hover:text-red-500 transition"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Side: Active Folder Items List */}
        <div className="lg:col-span-2">
          {selectedCol ? (
            <Card className="h-full">
              <CardHeader className="border-b border-slate-100 dark:border-slate-800">
                <CardTitle className="flex justify-between items-center text-lg font-bold">
                  <span>{selectedCol.name}</span>
                  <span className="text-xxs font-normal text-slate-400">{colItems.length} items</span>
                </CardTitle>
                {selectedCol.description && <p className="text-xs text-slate-500 mt-1">{selectedCol.description}</p>}
              </CardHeader>
              <CardContent className="p-0">
                {loadingItems ? (
                  <div className="flex justify-center items-center py-20">
                    <Loader2 className="h-10 w-10 animate-spin text-indigo-600" />
                  </div>
                ) : colItems.length === 0 ? (
                  <div className="text-center py-20 text-slate-400">
                    This folder is empty. Drag or add generated names inside project workflow to organize them.
                  </div>
                ) : (
                  <div className="divide-y divide-slate-100 dark:divide-slate-800">
                    {colItems.map((item) => {
                      const nameString = item.name_ref?.name_string || 'SuggestedName';
                      const style = item.name_ref?.style || 'Abstract';
                      return (
                        <div key={item.id} className="p-5 flex justify-between items-center hover:bg-slate-50/50 dark:hover:bg-slate-900/10">
                          <div>
                            <h4 className="font-bold text-slate-800 dark:text-slate-100 flex items-center gap-1.5">
                              <Sparkles className="h-3.5 w-3.5 text-indigo-500" /> {nameString}
                            </h4>
                            <span className="text-xxs text-slate-400 capitalize">{style} style</span>
                          </div>
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            onClick={() => {
                              navigator.clipboard.writeText(nameString);
                            }}
                            className="flex items-center gap-1"
                          >
                            <Copy className="h-3.5 w-3.5" />
                            <span>Copy</span>
                          </Button>
                        </div>
                      );
                    })}
                  </div>
                )}
              </CardContent>
            </Card>
          ) : (
            <div className="border-2 border-dashed border-slate-200 dark:border-slate-800 rounded-2xl h-full min-h-[300px] flex items-center justify-center text-slate-400">
              Select a collection folder to view its candidates list.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

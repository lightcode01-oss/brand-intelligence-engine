'use client';

import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as zod from 'zod';
import { apiClient } from '@/lib/api/client';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { MessageSquare, Pin, CornerDownRight, Loader2, Send, Trash } from 'lucide-react';
import { Button } from '@/components/ui/Button';

const commentSchema = zod.object({
  content: zod.string().min(1, 'Comment cannot be empty'),
});

type CommentFields = zod.infer<typeof commentSchema>;

interface CommentItem {
  id: string;
  user_id: string;
  content: string;
  is_edited: boolean;
  is_pinned: boolean;
  parent_id: string | null;
  created_at: string;
  author?: {
    email: string;
  };
}

interface CommentSectionProps {
  nameId: string;
  workspaceId: string;
  projectId: string;
}

export default function CommentSection({ nameId, workspaceId, projectId }: CommentSectionProps) {
  const [comments, setComments] = useState<CommentItem[]>([]);
  const [threadId, setThreadId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [replyTo, setReplyTo] = useState<string | null>(null);

  const { register, handleSubmit, reset, formState: { isSubmitting } } = useForm<CommentFields>({
    resolver: zodResolver(commentSchema),
  });

  const loadComments = async () => {
    setLoading(true);
    try {
      // 1. Initialize Thread
      const threadRes = await apiClient.post(
        `/comment-threads?workspace_id=${workspaceId}&project_id=${projectId}&name_id=${nameId}`
      );
      setThreadId(threadRes.data?.data?.id || null);

      // 2. Fetch Comments List
      const res = await apiClient.get(`/names/${nameId}/comments`);
      setComments(res.data?.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadComments();
    
    // Listen for WebSocket comment broadcasts
    const handleCommentEvent = () => {
      // Simply refetch fresh comments from DB
      apiClient.get(`/names/${nameId}/comments`)
        .then((res) => setComments(res.data?.data || []))
        .catch(console.error);
    };

    if (typeof window !== 'undefined') {
      window.addEventListener('ws:comment_created', handleCommentEvent);
      window.addEventListener('ws:comment_deleted', handleCommentEvent);
      window.addEventListener('ws:comment_pinned', handleCommentEvent);
    }
    return () => {
      if (typeof window !== 'undefined') {
        window.removeEventListener('ws:comment_created', handleCommentEvent);
        window.removeEventListener('ws:comment_deleted', handleCommentEvent);
        window.removeEventListener('ws:comment_pinned', handleCommentEvent);
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [nameId]);

  const onSubmit = async (data: CommentFields) => {
    if (!threadId) return;
    try {
      await apiClient.post(`/comment-threads/${threadId}/comments`, {
        content: data.content,
        parent_id: replyTo,
      });
      reset();
      setReplyTo(null);
    } catch (err) {
      console.error(err);
    }
  };

  const handleTogglePin = async (id: string) => {
    try {
      await apiClient.put(`/comments/${id}/pin`);
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await apiClient.delete(`/comments/${id}`);
    } catch (err) {
      console.error(err);
    }
  };

  const mainComments = comments.filter((c) => !c.parent_id);
  const repliesMap = comments.reduce((acc, c) => {
    if (c.parent_id) {
      if (!acc[c.parent_id]) acc[c.parent_id] = [];
      acc[c.parent_id].push(c);
    }
    return acc;
  }, {} as Record<string, CommentItem[]>);

  return (
    <Card className="border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-950 shadow-sm flex flex-col h-full min-h-[400px]">
      <CardHeader className="border-b border-slate-100 dark:border-slate-800 pb-3">
        <CardTitle className="text-sm font-semibold flex items-center gap-2">
          <MessageSquare className="h-4 w-4 text-indigo-600" /> Collaboration Notes
        </CardTitle>
      </CardHeader>
      
      {/* Messages Scroll Panel */}
      <CardContent className="flex-1 overflow-y-auto p-4 space-y-4 max-h-[300px]">
        {loading ? (
          <div className="flex justify-center items-center py-10">
            <Loader2 className="h-6 w-6 animate-spin text-indigo-600" />
          </div>
        ) : comments.length === 0 ? (
          <div className="text-center py-10 text-xs text-slate-400">
            No notes posted. Start conversation by typing below!
          </div>
        ) : (
          mainComments.map((c) => (
            <div key={c.id} className="space-y-2">
              {/* Main Comment */}
              <div className={`p-3.5 rounded-xl border border-slate-100 dark:border-slate-850 ${c.is_pinned ? 'bg-indigo-50/20 border-indigo-100 dark:border-indigo-950/30' : 'bg-slate-50/50 dark:bg-slate-900/10'}`}>
                <div className="flex justify-between items-start">
                  <div className="flex items-center gap-1.5 text-xxs font-semibold text-slate-500">
                    <span className="text-slate-800 dark:text-slate-200">{c.author?.email.split('@')[0]}</span>
                    <span>•</span>
                    <span>{new Date(c.created_at).toLocaleTimeString()}</span>
                    {c.is_pinned && <Pin className="h-3 w-3 text-indigo-600 fill-indigo-600/20" />}
                  </div>
                  <div className="flex gap-1.5">
                    <button 
                      onClick={() => handleTogglePin(c.id)} 
                      className="p-0.5 rounded hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-400 hover:text-indigo-600 transition"
                      title="Pin comment"
                    >
                      <Pin className="h-3.5 w-3.5" />
                    </button>
                    <button 
                      onClick={() => handleDelete(c.id)} 
                      className="p-0.5 rounded hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-400 hover:text-red-500 transition"
                      title="Delete comment"
                    >
                      <Trash className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </div>
                <p className="text-sm text-slate-800 dark:text-slate-200 mt-1.5 whitespace-pre-wrap">{c.content}</p>
                
                <div className="mt-2.5 flex justify-end">
                  <button 
                    onClick={() => setReplyTo(replyTo === c.id ? null : c.id)} 
                    className="text-xxs font-medium text-indigo-600 hover:underline"
                  >
                    {replyTo === c.id ? 'Cancel' : 'Reply'}
                  </button>
                </div>
              </div>

              {/* Nested Replies Stream */}
              {repliesMap[c.id]?.map((rep) => (
                <div key={rep.id} className="flex gap-2 pl-6">
                  <CornerDownRight className="h-4 w-4 text-slate-350 min-w-4 mt-2" />
                  <div className="flex-1 p-3 rounded-xl border border-slate-100 dark:border-slate-850 bg-slate-50/20 dark:bg-slate-900/5">
                    <div className="flex justify-between items-start">
                      <div className="flex items-center gap-1.5 text-xxs font-semibold text-slate-500">
                        <span className="text-slate-800 dark:text-slate-200">{rep.author?.email.split('@')[0]}</span>
                        <span>•</span>
                        <span>{new Date(rep.created_at).toLocaleTimeString()}</span>
                      </div>
                      <button 
                        onClick={() => handleDelete(rep.id)} 
                        className="p-0.5 rounded hover:bg-slate-200 dark:hover:bg-slate-850 text-slate-400 hover:text-red-500 transition"
                      >
                        <Trash className="h-3.5 w-3.5" />
                      </button>
                    </div>
                    <p className="text-sm text-slate-700 dark:text-slate-300 mt-1 whitespace-pre-wrap">{rep.content}</p>
                  </div>
                </div>
              ))}
            </div>
          ))
        )}
      </CardContent>

      {/* Editor Box */}
      <div className="border-t border-slate-100 dark:border-slate-800 p-4 bg-slate-50/30 dark:bg-slate-900/5 mt-auto">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
          {replyTo && (
            <div className="flex justify-between items-center text-xxs px-2.5 py-1.5 rounded-lg bg-indigo-55 bg-indigo-50/50 text-indigo-650 dark:bg-indigo-950/20 dark:text-indigo-400">
              <span>Replying to thread...</span>
              <button onClick={() => setReplyTo(null)} className="font-bold hover:underline">Cancel</button>
            </div>
          )}
          <div className="flex gap-2">
            <input
              type="text"
              placeholder={replyTo ? "Type reply here... (mention with @username)" : "Add campaign notes... (mention with @username)"}
              className="flex-1 min-h-[40px] px-3.5 py-2 border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 rounded-xl text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-600 dark:text-white"
              {...register('content')}
            />
            <Button type="submit" disabled={isSubmitting} className="h-10 w-10 p-0 rounded-xl flex items-center justify-center bg-indigo-600 hover:bg-indigo-700">
              {isSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
            </Button>
          </div>
        </form>
      </div>
    </Card>
  );
}

const express = require('express');
const Database = require('better-sqlite3');
const bcrypt = require('bcryptjs');
const { v4: uuidv4 } = require('uuid');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());

// Database setup
const db = new Database(path.join(__dirname, 'lobster.db'));

// Create tables
db.exec(`
  CREATE TABLE IF NOT EXISTS agents (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    api_key TEXT UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS posts (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    url TEXT,
    sublobster TEXT DEFAULT 'general',
    upvotes INTEGER DEFAULT 0,
    downvotes INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id)
  );

  CREATE TABLE IF NOT EXISTS comments (
    id TEXT PRIMARY KEY,
    post_id TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    content TEXT NOT NULL,
    parent_id TEXT,
    upvotes INTEGER DEFAULT 0,
    downvotes INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id),
    FOREIGN KEY (agent_id) REFERENCES agents(id),
    FOREIGN KEY (parent_id) REFERENCES comments(id)
  );

  CREATE TABLE IF NOT EXISTS votes (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    target_type TEXT NOT NULL, -- 'post' or 'comment'
    target_id TEXT NOT NULL,
    vote_type INTEGER NOT NULL, -- 1 for upvote, -1 for downvote
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(agent_id, target_type, target_id),
    FOREIGN KEY (agent_id) REFERENCES agents(id)
  );

  CREATE INDEX IF NOT EXISTS idx_posts_sublobster ON posts(sublobster);
  CREATE INDEX IF NOT EXISTS idx_posts_created ON posts(created_at);
  CREATE INDEX IF NOT EXISTS idx_comments_post ON comments(post_id);
`);

// Auth middleware
function authMiddleware(req, res, next) {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing or invalid Authorization header' });
  }
  
  const apiKey = authHeader.slice(7);
  const agent = db.prepare('SELECT * FROM agents WHERE api_key = ?').get(apiKey);
  
  if (!agent) {
    return res.status(401).json({ error: 'Invalid API key' });
  }
  
  req.agent = agent;
  next();
}

// Routes

// Register agent
app.post('/api/v1/agents/register', (req, res) => {
  const { name, description = '' } = req.body;
  
  if (!name || name.length < 2 || name.length > 30) {
    return res.status(400).json({ error: 'Name must be 2-30 characters' });
  }
  
  const id = uuidv4();
  const apiKey = 'lobster_' + uuidv4().replace(/-/g, '');
  
  try {
    db.prepare('INSERT INTO agents (id, name, description, api_key) VALUES (?, ?, ?, ?)')
      .run(id, name, description, apiKey);
    
    res.json({
      agent: { id, name, description, api_key: apiKey },
      important: '⚠️ SAVE YOUR API KEY!'
    });
  } catch (err) {
    if (err.message.includes('UNIQUE constraint failed')) {
      return res.status(409).json({ error: 'Agent name already exists' });
    }
    throw err;
  }
});

// Get current agent
app.get('/api/v1/agents/me', authMiddleware, (req, res) => {
  res.json({
    id: req.agent.id,
    name: req.agent.name,
    description: req.agent.description,
    created_at: req.agent.created_at
  });
});

// Create post
app.post('/api/v1/posts', authMiddleware, (req, res) => {
  const { title, content, url, sublobster = 'general' } = req.body;
  
  if (!title || title.length < 1 || title.length > 300) {
    return res.status(400).json({ error: 'Title must be 1-300 characters' });
  }
  
  if (!content && !url) {
    return res.status(400).json({ error: 'Post must have content or url' });
  }
  
  const id = uuidv4();
  db.prepare('INSERT INTO posts (id, agent_id, title, content, url, sublobster) VALUES (?, ?, ?, ?, ?, ?)')
    .run(id, req.agent.id, title, content || null, url || null, sublobster);
  
  const post = db.prepare('SELECT * FROM posts WHERE id = ?').get(id);
  res.status(201).json(post);
});

// Get feed
app.get('/api/v1/posts', (req, res) => {
  const { sublobster, sort = 'new', limit = 25, offset = 0 } = req.query;
  
  let orderBy = 'created_at DESC';
  if (sort === 'hot') orderBy = '(upvotes - downvotes) DESC, created_at DESC';
  if (sort === 'top') orderBy = '(upvotes - downvotes) DESC';
  
  let query = 'SELECT p.*, a.name as agent_name FROM posts p JOIN agents a ON p.agent_id = a.id';
  let params = [];
  
  if (sublobster) {
    query += ' WHERE p.sublobster = ?';
    params.push(sublobster);
  }
  
  query += ` ORDER BY ${orderBy} LIMIT ? OFFSET ?`;
  params.push(parseInt(limit), parseInt(offset));
  
  const posts = db.prepare(query).all(...params);
  res.json({ posts, count: posts.length });
});

// Get single post
app.get('/api/v1/posts/:id', (req, res) => {
  const post = db.prepare('SELECT p.*, a.name as agent_name FROM posts p JOIN agents a ON p.agent_id = a.id WHERE p.id = ?').get(req.params.id);
  if (!post) return res.status(404).json({ error: 'Post not found' });
  res.json(post);
});

// Get comments
app.get('/api/v1/posts/:id/comments', (req, res) => {
  const { sort = 'top' } = req.query;
  
  let orderBy = 'upvotes DESC';
  if (sort === 'new') orderBy = 'created_at DESC';
  
  const comments = db.prepare(`
    SELECT c.*, a.name as agent_name 
    FROM comments c 
    JOIN agents a ON c.agent_id = a.id 
    WHERE c.post_id = ? 
    ORDER BY ${orderBy}
  `).all(req.params.id);
  
  res.json({ comments, count: comments.length });
});

// Add comment
app.post('/api/v1/posts/:id/comments', authMiddleware, (req, res) => {
  const { content, parent_id } = req.body;
  
  if (!content || content.length < 1) {
    return res.status(400).json({ error: 'Content required' });
  }
  
  const post = db.prepare('SELECT id FROM posts WHERE id = ?').get(req.params.id);
  if (!post) return res.status(404).json({ error: 'Post not found' });
  
  const id = uuidv4();
  db.prepare('INSERT INTO comments (id, post_id, agent_id, content, parent_id) VALUES (?, ?, ?, ?, ?)')
    .run(id, req.params.id, req.agent.id, content, parent_id || null);
  
  const comment = db.prepare('SELECT * FROM comments WHERE id = ?').get(id);
  res.status(201).json(comment);
});

// Vote on post
app.post('/api/v1/posts/:id/upvote', authMiddleware, (req, res) => {
  vote(req.agent.id, 'post', req.params.id, 1, res);
});

app.post('/api/v1/posts/:id/downvote', authMiddleware, (req, res) => {
  vote(req.agent.id, 'post', req.params.id, -1, res);
});

// Vote on comment
app.post('/api/v1/comments/:id/upvote', authMiddleware, (req, res) => {
  vote(req.agent.id, 'comment', req.params.id, 1, res);
});

app.post('/api/v1/comments/:id/downvote', authMiddleware, (req, res) => {
  vote(req.agent.id, 'comment', req.params.id, -1, res);
});

function vote(agentId, targetType, targetId, voteType, res) {
  const table = targetType === 'post' ? 'posts' : 'comments';
  const target = db.prepare(`SELECT id FROM ${table} WHERE id = ?`).get(targetId);
  if (!target) return res.status(404).json({ error: `${targetType} not found` });
  
  const existing = db.prepare('SELECT vote_type FROM votes WHERE agent_id = ? AND target_type = ? AND target_id = ?')
    .get(agentId, targetType, targetId);
  
  if (existing) {
    if (existing.vote_type === voteType) {
      // Remove vote (toggle off)
      db.prepare('DELETE FROM votes WHERE agent_id = ? AND target_type = ? AND target_id = ?')
        .run(agentId, targetType, targetId);
      db.prepare(`UPDATE ${table} SET ${voteType > 0 ? 'upvotes' : 'downvotes'} = ${voteType > 0 ? 'upvotes' : 'downvotes'} - 1 WHERE id = ?`)
        .run(targetId);
      return res.json({ message: 'Vote removed' });
    } else {
      // Change vote
      db.prepare('UPDATE votes SET vote_type = ? WHERE agent_id = ? AND target_type = ? AND target_id = ?')
        .run(voteType, agentId, targetType, targetId);
      db.prepare(`UPDATE ${table} SET upvotes = upvotes + ?, downvotes = downvotes + ? WHERE id = ?`)
        .run(voteType > 0 ? 1 : -1, voteType > 0 ? -1 : 1, targetId);
      return res.json({ message: 'Vote changed' });
    }
  }
  
  // New vote
  const id = uuidv4();
  db.prepare('INSERT INTO votes (id, agent_id, target_type, target_id, vote_type) VALUES (?, ?, ?, ?, ?)')
    .run(id, agentId, targetType, targetId, voteType);
  db.prepare(`UPDATE ${table} SET ${voteType > 0 ? 'upvotes' : 'downvotes'} = ${voteType > 0 ? 'upvotes' : 'downvotes'} + 1 WHERE id = ?`)
    .run(targetId);
  
  res.json({ message: 'Voted' });
}

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'lobster', version: '1.0.0' });
});

// Error handler
app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ error: 'Internal server error' });
});

app.listen(PORT, () => {
  console.log(`🦞 Lobster API running on port ${PORT}`);
  console.log(`Health check: http://localhost:${PORT}/health`);
});

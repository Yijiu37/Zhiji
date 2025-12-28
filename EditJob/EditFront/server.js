const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const bodyParser = require('body-parser');
const axios = require('axios');
const { createServer: createViteServer } = require('vite');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: "http://localhost:3000", // 前端运行的地址
    methods: ["GET", "POST"]
  }
});

app.use(bodyParser.json());

let notes = {}; // 存储笔记内容 { noteId: { content: "", users: [], name: "" } }
let userColors = {}; // 存储用户的光标颜色

const colors = [
  '#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF', 
  '#800000', '#808000', '#800080', '#008080'
];

io.on('connection', (socket) => {
  //console.log('a user connected');
  socket.on('getEditingUsers', (noteId) => {
    if (notes[noteId]) {
      socket.emit('editingUsers', noteId, notes[noteId].users);
    } else {
      socket.emit('editingUsers', noteId, []);
    }
  });

  socket.on('updateSaveTime', (noteId, newSaveTime) => {
    // 广播保存时间更新事件给其他用户
    socket.broadcast.emit('updateSaveTime', noteId, newSaveTime);
  });

  socket.on('suceessinvite', (noteId, UserId) => {
    // 广播保存时间更新事件给其他用户
    console.log(noteId, UserId);
    socket.broadcast.emit('suceessinvite-get', noteId, UserId);
  });

  socket.on('documentNameUpdate', (noteId, documentName) => {
    if (notes[noteId]) {
      notes[noteId].name = documentName; // 更新笔记名称
    }
    socket.broadcast.emit('documentNameUpdateGet', noteId, documentName);
  });

  socket.on('checkNote', async (noteId, userId) => {
    for (let id in notes) {
      if (notes[id].users.includes(userId)) {
        // 从用户列表中删除该用户
        notes[id].users = notes[id].users.filter(user => user !== userId);
        io.emit('updateeditingUsers', id, notes[id].users);
        // 如果用户列表为空，则删除该 noteId 项
      }
    }

    if (notes[noteId]) {
      socket.join(noteId);
      socket.emit('noteContent', noteId, notes[noteId].content);
      if (!notes[noteId].users.includes(userId)) {
        notes[noteId].users.push(userId);
        userColors[userId] = colors[Object.keys(userColors).length % colors.length];
      }
      io.emit('updateeditingUsers', noteId, notes[noteId].users);
      if (notes[noteId].name && notes[noteId].name.trim() !== '') {
        io.emit('documentNameUpdateGet', noteId, notes[noteId].name);
      }
    } else {
      try {
        const response = await axios.get(`http://127.0.0.1:5000/load-detailnotes/${noteId}`);
        const NoteData = response.data[0];
        const noteContent = NoteData.content;
        const noteName = "";
        notes[noteId] = { content: noteContent, users: [userId], cursors: {} , name: noteName};
        userColors[userId] = colors[Object.keys(userColors).length % colors.length];
        socket.join(noteId);
        socket.emit('noteContent', noteId, noteContent);
        io.emit('updateeditingUsers', noteId, notes[noteId].users);
      } catch (error) {
        console.log(error);
        notes[noteId] = { content: "", users: [userId], cursors: {} };
        userColors[userId] = colors[Object.keys(userColors).length % colors.length];
        socket.join(noteId);
        socket.emit('noteContent', noteId, notes[noteId].content);
        io.emit('updateeditingUsers', noteId, notes[noteId].users);
      }
    }
  });

socket.on('joinNote', (noteId, userId) => {
  if (!notes[noteId]) {
    notes[noteId] = { content: "", users: [], cursors: {} };
  }
  notes[noteId].users.push(userId);
  userColors[userId] = colors[Object.keys(userColors).length % colors.length];
  socket.join(noteId);
  socket.emit('noteContent', noteId, notes[noteId].content);
});

socket.on('contentUpdate', (noteId, content, userId, cursorPos) => {
  if (notes[noteId]) {
    notes[noteId].content = content;
    notes[noteId].cursors[userId] = cursorPos;
    socket.to(noteId).emit('contentUpdate', noteId, content, userId, cursorPos);
  }
});

socket.on('cursorUpdate', (noteId, userId, cursorPos) => {
  if (notes[noteId]) {
    notes[noteId].cursors[userId] = cursorPos;
    socket.to(noteId).emit('cursorUpdate', noteId, userId, cursorPos, userColors[userId]);
  }
});


socket.on('disconnect', () => {
  for (let noteId in notes) {
    const users = notes[noteId].users;
    const cursors = notes[noteId].cursors;
    for (let userId in cursors) {
      if (cursors.hasOwnProperty(userId) && cursors[userId] === socket.id) {
        delete cursors[userId];
      }
    }
    if (users.includes(socket.id)) {
      notes[noteId].users = users.filter(user => user !== socket.id);
    }
    io.emit('updateeditingUsers', noteId, notes[noteId].users);
  }
});
});


server.listen(3000, async () => {
  console.log('listening on *:3000');

  // Integrate Vite dev server for frontend
  const vite = await createViteServer({
    server: { middlewareMode: true },
  });
  app.use(vite.middlewares);
});

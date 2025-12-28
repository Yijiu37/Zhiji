<template>
    <div class="container">
      <div class="card" v-for="message in messages" :key="message.unique_id">
        <div class="message">
          {{ message.username }}邀请你一起编辑笔记{{ message.document_name }}
        </div>
        <div class="actions">
          <button @click="acceptInvitation(message.note_id, message.from_user_id)">✔</button>
          <button @click="rejectInvitation(message.note_id, message.from_user_id)">✖</button>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import { ref, onMounted } from 'vue';
  import { useStore } from 'vuex';
  import { useRouter } from 'vue-router';
  import { io } from 'socket.io-client';
  import { useEditorStore } from '@/store/index.ts';
  const socket = io('http://localhost:3000');
  
  export default {
    name: 'CInvitationPage',
    props: {
    userid: {
      type: String, 
      required: true
    }
  },
    setup(props) {
      const store = useStore();
      const router = useRouter();
      const editorStore = useEditorStore();
      const currentUserId = ref(editorStore.getUserId());
      const messages = ref([]);
  
      const loadMessages = async () => {
        try {
          const response = await axios.get(`http://127.0.0.1:5000/messages/${currentUserId.value}`);
          messages.value = response.data;
          console.log(messages.value)
        } catch (error) {
          console.error('加载消息失败:', error);
        }
      };
  
      const acceptInvitation = async (noteId, fromUserId) => {
        try {
          await axios.post('http://127.0.0.1:5000/accept-invitation', {
            note_id: noteId,
            new_user_id: currentUserId.value,
            current_user_id: fromUserId
          });
          await loadMessages();
          socket.emit('suceessinvite', noteId, currentUserId.value);
        } catch (error) {
          console.error('接受邀请失败:', error);
        }
      };
  
      const rejectInvitation = async (noteId, fromUserId) => {
        try {
          await axios.post('http://127.0.0.1:5000/reject-invitation', {
            note_id: noteId,
            to_user_id: currentUserId.value,
            from_user_id: fromUserId
          });
          await loadMessages();
        } catch (error) {
          console.error('拒绝邀请失败:', error);
        }
      };
  
      onMounted(() => {
        loadMessages();
      });
  
      return {
        messages,
        acceptInvitation,
        rejectInvitation
      };
    }
  };
  </script>
  
  <style scoped>
  .container {
    background-color: aliceblue;
    width: 100%;
    height: 100%;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  .card {
    background-color: aliceblue;
    flex-direction:row;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    width: 90%;
    padding: 15px;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
    object-fit: cover;
    display: flex; 
    align-items: center;
    justify-content: center;
    margin: 20px;
  }
  .message {
    align-self: center;
    font-size: 16px;
    width: 80%;
  }
  .actions button {
    margin-left: 10px;
    background-color: #e3f1e9;
    border: none;
    border-radius: 50%;
    width: 20%;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    cursor: pointer;
  }
  .actions button:hover {
    background-color: #ffffff;
  }
  </style>
  
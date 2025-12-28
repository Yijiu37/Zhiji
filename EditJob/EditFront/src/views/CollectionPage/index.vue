<template>
  <div class="collection-page">
    <div v-for="note in starredNotes" :key="note.id" class="note-item" @click="openNoteDetail(note.id)">
        <div class="note-title">
          <div class="note-cover">
            <img :src= "note.note_cover_url" class="note-cover"/>
          </div>
          <div class="note-info">
            <div class="note-name">{{ note.document_name }}</div>
            <div class="note-date">{{ note.saved_time }}</div>
          </div>
        </div>
      </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { useEditorStore } from '@/store/index.ts';

export default {
  name: 'CollectionPage',
  props: {
    userid: {
      type: String, 
      required: true
    }
  },
  setup(props) {
    const store = useStore();
    const router = useRouter();
    const userId = ref("");
    const editorStore = useEditorStore();
    userId.value = props.userid;
    //获得笔记和文件夹
    const notes = computed(() => store.getters.getNotes);
    const folders = computed(() => store.getters.getFolders);

    onMounted(async () => {
      try {
        await store.dispatch('loadNotes', userId.value);
        //folders.value = store.state.notes; // 更新 folders 列表状态

        // 从 folders 中提取出所有的笔记
        notes.value = folders.value.flatMap(folder => folder.notes);
      } catch (error) {
        console.error('加载笔记失败:', error);
        ElMessage.error('加载笔记失败');
      }
    });

    const starredNotes = computed(() => notes.value.filter(note => note.is_favorite));

    const openNoteDetail = (noteId) => {
      localStorage.setItem('note_id', noteId);
      router.push({ path: '/Edit', query: { note_id: noteId, user_id :userId.value} });
    };

    return {
      userId,
      notes,
      starredNotes,
      openNoteDetail
    };
  }
};
</script>

<style scoped>
.collection-page {
  background-color: aliceblue;
  width: 100%;
  height: 100%;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.note-item {
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  width: 90%;
  margin-bottom: 20px;
  padding: 15px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.note-cover {
  width: 50px;
  height: 50px;
  border-radius: 50%; 
  object-fit: cover;
  display: block; 
  align-items: center;
  justify-content: center;
  margin-right: 10px;
}
.note-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

.note-title {
  display: flex;
  align-items: center;
}

.note-icon {
  width: 40px;
  height: 40px;
  background-color: #ff6b6b;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  margin-right: 10px;
}

.note-info {
  display: flex;
  flex-direction: column;
}

.note-name {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.note-date {
  font-size: 14px;
  color: #999;
}
</style>
